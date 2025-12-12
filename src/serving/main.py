"""FastAPI application for serving the fraud detection model."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from ..config import ConfigManager, setup_logging
from ..inference import InferencePipeline, create_sample_transaction

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic schemas


class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant_category: str = Field(..., description="Merchant category")
    transaction_type: str = Field(..., description="Transaction type")
    location: str = Field(..., description="Transaction location")
    device_type: str = Field(..., description="Device type")
    hour_of_day: int = Field(..., ge=0, le=23, description="Hour of transaction")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week")

    user_id: Optional[str] = Field(None, description="User identifier")
    transaction_id: Optional[str] = Field(None, description="Transaction identifier")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of the transaction")
    device_id: Optional[str] = Field(None, description="Device identifier")

    user_transaction_frequency: Optional[float] = Field(
        None, ge=0, description="User transaction frequency"
    )
    user_avg_amount: Optional[float] = Field(None, ge=0, description="User average amount")
    user_transaction_count: Optional[int] = Field(None, ge=0, description="User transaction count")

    @field_validator("merchant_category")
    @classmethod
    def merchant_category_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("merchant_category must be provided")
        return value

    @field_validator("transaction_type")
    @classmethod
    def transaction_type_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("transaction_type must be provided")
        return value

    @field_validator("device_type")
    @classmethod
    def device_type_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("device_type must be provided")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        # Allow common placeholder values to pass through (will be replaced with defaults)
        if value.lower() in ["string", "null", "none", ""]:
            return None
        # Validate that it's a parseable datetime string
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        except (ValueError, AttributeError) as exc:
            raise ValueError(
                f"timestamp must be a valid ISO datetime string (e.g., '2024-01-01T12:00:00'), got: {value}"
            ) from exc


class PredictionResponse(BaseModel):
    fraud_probability: float
    is_fraud: bool
    risk_level: str
    prediction_id: str
    timestamp: str
    model_version: str
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    model_loaded: bool
    version: str
    uptime_seconds: float


# ---------------------------------------------------------------------------
# Application state

config: Dict[str, Any] = {}
inference_pipeline: Optional[InferencePipeline] = None
startup_time = datetime.utcnow()
prediction_count = 0
predictions_log: List[Dict[str, Any]] = []

# ---------------------------------------------------------------------------
# Utility helpers


def build_transaction_dataframe(request: TransactionRequest) -> pd.DataFrame:
    payload = request.model_dump()

    payload.setdefault("user_id", payload.get("user_id") or "anonymous_user")
    payload.setdefault("transaction_id", payload.get("transaction_id") or f"txn_{uuid4().hex[:12]}")
    payload.setdefault("timestamp", payload.get("timestamp") or datetime.utcnow().isoformat())
    payload.setdefault("device_id", payload.get("device_id") or f"device_{payload['user_id']}")

    # Provide defaults for optional context
    payload.setdefault(
        "user_transaction_frequency", payload.get("user_transaction_frequency") or 0.0
    )
    payload.setdefault("user_avg_amount", payload.get("user_avg_amount") or payload["amount"])
    payload.setdefault("user_transaction_count", payload.get("user_transaction_count") or 1)

    return pd.DataFrame([payload])


def determine_risk_level(fraud_probability: float) -> str:
    if fraud_probability < 0.3:
        return "low"
    if fraud_probability < 0.7:
        return "medium"
    return "high"


def log_prediction(prediction: Dict[str, Any]) -> None:
    global predictions_log
    predictions_log.append(prediction)

    if len(predictions_log) >= 100:
        save_predictions_log()


def save_predictions_log() -> None:
    global predictions_log

    if not predictions_log:
        return

    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "predictions.csv"

    df = pd.DataFrame(predictions_log)
    if log_path.exists():
        df.to_csv(log_path, mode="a", header=False, index=False)
    else:
        df.to_csv(log_path, index=False)

    logger.info("Persisted %d predictions to %s", len(predictions_log), log_path)
    predictions_log = []


def get_model_version() -> str:
    if inference_pipeline is None or inference_pipeline.model_metadata is None:
        return "unknown"
    metadata = inference_pipeline.model_metadata
    if metadata.get("source") == "mlflow":
        return metadata.get("uri", "unknown")
    return metadata.get("path", "unknown")


# ---------------------------------------------------------------------------
# FastAPI application setup

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection service",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    await load_resources()


async def load_resources() -> None:
    global config, inference_pipeline

    manager = ConfigManager()
    config = manager.get_serving_config()
    setup_logging(config)

    model_cfg = config.get("model", {})
    model_name = model_cfg.get("model_name")
    model_stage = model_cfg.get("model_stage", "production")
    local_path = model_cfg.get("local_model_path", "models/Random_Forest_final_model.joblib")

    pipeline: Optional[InferencePipeline] = None

    if model_cfg.get("use_mlflow", True) and model_name:
        try:
            uri = f"models:/{model_name}/{model_stage}" if model_stage else f"models:/{model_name}"
            pipeline = InferencePipeline(mlflow_model_uri=uri)
        except Exception as exc:  # noqa: BLE001
            logger.warning("MLflow model load failed (%s), falling back to local artefact", exc)

    if pipeline is None:
        if not Path(local_path).exists():
            raise FileNotFoundError(f"Model artefact not found at {local_path}")
        pipeline = InferencePipeline(model_path=local_path)

    inference_pipeline = pipeline
    logger.info("Inference pipeline initialised")


# ---------------------------------------------------------------------------
# API endpoints


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    return {
        "message": "Fraud Detection API",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
    model_loaded = inference_pipeline is not None and inference_pipeline.model is not None

    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        timestamp=datetime.utcnow().isoformat(),
        model_loaded=model_loaded,
        version=app.version,
        uptime_seconds=uptime_seconds,
    )


@app.get("/sample-transaction", response_model=Dict[str, Any])
async def sample_transaction() -> Dict[str, Any]:
    return create_sample_transaction()


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(
    transaction: TransactionRequest, background_tasks: BackgroundTasks
) -> PredictionResponse:
    global prediction_count

    if inference_pipeline is None or inference_pipeline.model is None:
        raise HTTPException(status_code=503, detail="Model not available")

    start_ts = datetime.utcnow()
    prediction_id = f"pred_{start_ts.strftime('%Y%m%d%H%M%S')}_{prediction_count}"
    prediction_count += 1

    raw_df = build_transaction_dataframe(transaction)
    predictions = inference_pipeline.predict_batch(raw_df, include_probabilities=True)
    record = predictions.iloc[0]

    fraud_probability = float(record.get("fraud_probability", 0.0))
    fraud_threshold = config.get("prediction", {}).get("fraud_threshold", 0.5)
    is_fraud = fraud_probability >= fraud_threshold
    risk_level = determine_risk_level(fraud_probability)

    processing_ms = (datetime.utcnow() - start_ts).total_seconds() * 1000

    background_tasks.add_task(
        log_prediction,
        {
            "prediction_id": prediction_id,
            "timestamp": start_ts.isoformat(),
            "amount": float(transaction.amount),
            "merchant_category": transaction.merchant_category,
            "transaction_type": transaction.transaction_type,
            "fraud_probability": fraud_probability,
            "is_fraud": is_fraud,
            "processing_time_ms": processing_ms,
        },
    )

    return PredictionResponse(
        fraud_probability=fraud_probability,
        is_fraud=is_fraud,
        risk_level=risk_level,
        prediction_id=prediction_id,
        timestamp=start_ts.isoformat(),
        model_version=get_model_version(),
        processing_time_ms=processing_ms,
    )


@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
    return {
        "total_predictions": prediction_count,
        "uptime_seconds": uptime_seconds,
        "predictions_per_second": prediction_count / uptime_seconds if uptime_seconds > 0 else 0.0,
        "model_loaded": inference_pipeline is not None and inference_pipeline.model is not None,
        "model_version": get_model_version(),
    }


@app.post("/save-logs")
async def persist_logs() -> Dict[str, Any]:
    try:
        save_predictions_log()
        return {"message": "Logs saved", "timestamp": datetime.utcnow().isoformat()}
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to save logs: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Local development entrypoint

if __name__ == "__main__":
    import uvicorn

    api_cfg = config.get("api", {}) if config else {}
    uvicorn.run(
        "src.serving.main:app",
        host=api_cfg.get("host", "0.0.0.0"),  # nosec B104 - Required for Docker container
        port=api_cfg.get("port", 8000),
        reload=api_cfg.get("reload", False),
        workers=api_cfg.get("workers", 1),
    )
