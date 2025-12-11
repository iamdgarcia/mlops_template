#!/usr/bin/env python3
"""Minimal FastAPI server for real-time predictions.

Usage:
  uvicorn scripts.minimal_serve:app --reload --port 8000

This example intentionally keeps the code small and focused so it can be
demonstrated live during the course. It reuses the InferencePipeline to ensure
the same feature engineering as training.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import ConfigManager
from src.inference import InferencePipeline, create_sample_transaction


class Transaction(BaseModel):
    # Keep fields minimal for the demo; extra keys are ignored by the pipeline
    amount: float
    merchant_category: str
    transaction_type: str
    location: str
    device_type: str
    hour_of_day: int
    day_of_week: int
    user_transaction_frequency: Optional[float] = 5.0
    user_avg_amount: Optional[float] = 100.0
    user_transaction_count: Optional[int] = 10

    class Config:
        extra = "allow"  # Allow additional fields (e.g., user_id)


app = FastAPI(title="Minimal Fraud Detection API", version="0.1.0")


def _load_pipeline() -> InferencePipeline:
    """Load inference pipeline with proper error handling.

    Returns:
        Configured InferencePipeline instance

    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If pipeline initialization fails
    """
    try:
        cfg = ConfigManager().get_serving_config()
        model_path = cfg.get("model", {}).get(
            "local_model_path", "models/random_forest_final_model.joblib"
        )
        return InferencePipeline(model_path=model_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Model file not found. Please ensure model is trained and saved. Error: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize inference pipeline: {e}")


pipeline: Optional[InferencePipeline] = None


@app.on_event("startup")
async def _startup() -> None:
    global pipeline
    pipeline = _load_pipeline()


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy" if (pipeline and pipeline.model) else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_info": pipeline.get_model_info() if pipeline else None,
    }


@app.post("/predict")
async def predict(txn: Transaction) -> Dict[str, Any]:
    if not pipeline or not pipeline.model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    result = pipeline.predict_single(txn.dict())
    return {
        "fraud_probability": result.get("fraud_probability"),
        "fraud_prediction": bool(result.get("fraud_prediction")),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/sample")
async def sample() -> Dict[str, Any]:
    return create_sample_transaction()
