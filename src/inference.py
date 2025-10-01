"""Inference utilities for the fraud detection project."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import mlflow
import mlflow.pyfunc
import numpy as np
import pandas as pd

from src.features import FeatureEngineer

logger = logging.getLogger(__name__)

FEATURE_STORE_PATH = Path("data/selected_features.json")


def _load_feature_store(path: Path = FEATURE_STORE_PATH) -> List[str]:
    """Load the persisted feature list used during training."""
    if not path.exists():
        logger.warning("Feature store file not found; feature selection will use on-the-fly columns")
        return []

    try:
        payload = json.loads(path.read_text())
        features = payload.get("selected_features", [])
        if not isinstance(features, list):
            raise ValueError("selected_features must be a list")
        return features
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load feature metadata from %s: %s", path, exc)
        return []


class InferencePipeline:
    """Unified inference pipeline that reuses the training feature engineering path."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        mlflow_model_uri: Optional[str] = None,
        feature_store_path: Path = FEATURE_STORE_PATH,
    ) -> None:
        self.model: Optional[Any] = None
        self.feature_engineer = FeatureEngineer()
        self.feature_names: List[str] = _load_feature_store(feature_store_path)
        self.model_metadata: Dict[str, Any] = {}

        if model_path:
            self.load_model_from_file(model_path)
        elif mlflow_model_uri:
            self.load_model_from_mlflow(mlflow_model_uri)
        else:
            logger.warning("InferencePipeline instantiated without a model; call load_model_* explicitly")

    # ------------------------------------------------------------------
    # Model loading helpers

    def load_model_from_file(self, model_path: str) -> None:
        """Load a model artefact from disk."""
        try:
            self.model = joblib.load(model_path)
            self.model_metadata = {
                "source": "file",
                "path": model_path,
                "loaded_at": datetime.utcnow().isoformat(),
            }
            logger.info("Model loaded from %s", model_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load model from %s: %s", model_path, exc)
            raise

    def load_model_from_mlflow(self, model_uri: str) -> None:
        """Load a model from the MLflow Model Registry."""
        try:
            self.model = mlflow.pyfunc.load_model(model_uri)
            self.model_metadata = {
                "source": "mlflow",
                "uri": model_uri,
                "loaded_at": datetime.utcnow().isoformat(),
            }
            logger.info("Model loaded from MLflow URI %s", model_uri)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load model from MLflow (%s): %s", model_uri, exc)
            raise

    # ------------------------------------------------------------------
    # Pre-processing and prediction

    def preprocess_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering to raw transaction data."""
        if raw_data.empty:
            raise ValueError("Cannot preprocess an empty dataframe")

        engineered = self.feature_engineer.create_all_features(raw_data)
        feature_names = self.feature_names or self.feature_engineer.get_feature_names(engineered)

        missing_features = [feature for feature in feature_names if feature not in engineered.columns]
        if missing_features:
            logger.debug("Adding %d missing feature columns with zeros", len(missing_features))
            for column in missing_features:
                engineered[column] = 0

        return engineered[feature_names]

    def predict_batch(self, raw_data: pd.DataFrame, include_probabilities: bool = True) -> pd.DataFrame:
        """Run batch inference on a dataframe."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model_from_file or load_model_from_mlflow first.")

        processed = self.preprocess_data(raw_data)
        predictions = self.model.predict(processed)

        result = raw_data.copy()
        result["fraud_prediction"] = predictions
        result["prediction_timestamp"] = datetime.utcnow().isoformat()

        if include_probabilities:
            probabilities = self._infer_probabilities(processed)
            result["fraud_probability"] = probabilities[:, 1]
            result["confidence_score"] = probabilities.max(axis=1)

        logger.info("Generated %d predictions", len(result))
        return result

    def predict_single(self, transaction_data: Dict[str, Any], include_probabilities: bool = True) -> Dict[str, Any]:
        """Run inference on a single transaction represented as a dictionary."""
        single_df = pd.DataFrame([transaction_data])
        batch = self.predict_batch(single_df, include_probabilities=include_probabilities)
        return batch.iloc[0].to_dict()

    def _infer_probabilities(self, processed: pd.DataFrame) -> np.ndarray:
        """Return prediction probabilities, falling back to deterministic outputs."""
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(processed)
        if hasattr(self.model, "decision_function"):
            scores = self.model.decision_function(processed)
            return np.vstack([1 - scores, scores]).T
        logger.warning("Model does not expose probability scores; returning binary predictions")
        binary = self.model.predict(processed)
        return np.vstack([1 - binary, binary]).T

    # ------------------------------------------------------------------
    # Diagnostics

    def get_feature_importance(self, sample_data: Optional[pd.DataFrame] = None) -> Optional[Dict[str, float]]:
        """Return feature importance if the underlying model supports it."""
        if self.model is None:
            return None

        if sample_data is None:
            sample_data = pd.DataFrame([create_sample_transaction()])

        processed = self.preprocess_data(sample_data)
        feature_names = list(processed.columns)

        estimator = self._unwrap_model()

        try:
            if hasattr(estimator, "feature_importances_"):
                importances = estimator.feature_importances_
                return dict(zip(feature_names, importances))
            if hasattr(estimator, "coef_"):
                coef = estimator.coef_[0] if estimator.coef_.ndim > 1 else estimator.coef_
                return dict(zip(feature_names, np.abs(coef)))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to compute feature importance: %s", exc)
        return None

    def validate_input_data(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Lightweight validation for serving layer inputs."""
        issues: List[str] = []

        required_columns = ["amount", "hour_of_day", "day_of_week", "user_id"]
        missing = [col for col in required_columns if col not in data.columns]
        if missing:
            issues.append(f"Missing required columns: {missing}")

        if "amount" in data.columns:
            if not pd.api.types.is_numeric_dtype(data["amount"]):
                issues.append("'amount' must be numeric")
            elif (data["amount"] < 0).any():
                issues.append("'amount' contains negative values")

        if "hour_of_day" in data.columns and not data["hour_of_day"].between(0, 23).all():
            issues.append("'hour_of_day' must be within 0-23")

        if "day_of_week" in data.columns and not data["day_of_week"].between(0, 6).all():
            issues.append("'day_of_week' must be within 0-6")

        return len(issues) == 0, issues

    def get_model_info(self) -> Dict[str, Any]:
        """Expose model metadata for monitoring endpoints."""
        if self.model is None:
            return {"status": "no_model_loaded"}

        info: Dict[str, Any] = {
            "model_type": type(self.model).__name__,
            "metadata": self.model_metadata,
            "feature_count": len(self.feature_names),
        }

        estimator = self._unwrap_model()
        if hasattr(estimator, "n_estimators"):
            info["n_estimators"] = getattr(estimator, "n_estimators")
        if hasattr(estimator, "max_depth"):
            info["max_depth"] = getattr(estimator, "max_depth")

        return info

    def _unwrap_model(self) -> Any:
        """Return the underlying estimator for MLflow pyfunc wrappers."""
        estimator = self.model
        if hasattr(estimator, "_model_impl"):
            estimator = getattr(estimator._model_impl, "python_model", estimator)
        if hasattr(estimator, "unwrap_python_model"):
            estimator = estimator.unwrap_python_model()
        return estimator


class AutomatedRetrainingSystem:
    """Simplified placeholder for drift-triggered retraining logic."""

    def __init__(self, training_entrypoint: str, mlflow_experiment_name: str = "fraud_detection") -> None:
        self.training_entrypoint = training_entrypoint
        self.mlflow_experiment_name = mlflow_experiment_name
        self.retraining_history: List[Dict[str, Any]] = []

    def trigger_retraining(self, trigger_reason: str, training_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        logger.info("Starting automated retraining: %s", trigger_reason)
        record: Dict[str, Any] = {
            "trigger_timestamp": datetime.utcnow().isoformat(),
            "trigger_reason": trigger_reason,
            "status": "initiated",
        }

        try:
            import time

            time.sleep(2)  # Simulate retraining duration
            record["status"] = "completed"
            record["completion_timestamp"] = datetime.utcnow().isoformat()
            record["new_model_version"] = f"v{len(self.retraining_history) + 1}"
            record["training_samples"] = len(training_data) if training_data is not None else "unknown"
            logger.info("Automated retraining completed")
        except Exception as exc:  # noqa: BLE001
            record["status"] = "failed"
            record["error"] = str(exc)
            record["completion_timestamp"] = datetime.utcnow().isoformat()
            logger.error("Automated retraining failed: %s", exc)

        self.retraining_history.append(record)
        return record

    def get_retraining_history(self) -> List[Dict[str, Any]]:
        return list(self.retraining_history)

    def should_retrain(self, drift_report: Dict[str, Any]) -> Tuple[bool, str]:
        if self.retraining_history:
            last_trigger = datetime.fromisoformat(self.retraining_history[-1]["trigger_timestamp"])
            hours_since_last = (datetime.utcnow() - last_trigger).total_seconds() / 3600
            if hours_since_last < 24:
                return False, "Retraining already executed within the last day"

        if drift_report.get("overall_severity") == "CRITICAL":
            return True, "Critical drift detected"

        drift_percentage = drift_report.get("data_drift", {}).get("drift_percentage", 0)
        if drift_percentage > 60:
            return True, f"High drift percentage detected ({drift_percentage:.1f}%)"

        return False, "Drift levels within acceptable thresholds"


def create_sample_transaction() -> Dict[str, Any]:
    """Return a random-but-reasonable sample transaction for demos."""
    from datetime import datetime, timedelta
    import numpy as np
    import random
    merchant_categories = ['grocery', 'gas_station', 'restaurant', 'retail', 'online', 'entertainment']
    transaction_types = ['purchase', 'withdrawal', 'transfer', 'payment']
    locations = ['seattle_wa', 'portland_or', 'san_francisco_ca', 'los_angeles_ca', 'denver_co']
    device_types = ['mobile', 'desktop', 'atm', 'pos']
    rng = np.random.default_rng(seed=random.randint(0, 10000))
    hour_probs = np.array([0.02, 0.01, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06,
                           0.07, 0.08, 0.08, 0.07, 0.07, 0.08, 0.09, 0.08,
                           0.07, 0.06, 0.05, 0.04, 0.04, 0.03, 0.02, 0.02], dtype=float)
    hour_probs /= hour_probs.sum()
    hour = rng.choice(np.arange(24), p=hour_probs)
    is_suspicious = rng.random() < 0.05
    if is_suspicious:
        amount = rng.lognormal(7, 1.2)
        hour = rng.choice([0, 1, 2, 3, 22, 23])
        merchant_cat = rng.choice(['online', 'entertainment'])
        device_type = rng.choice(['atm', 'desktop'])
    else:
        amount = rng.lognormal(4, 0.9)
        merchant_cat = rng.choice(merchant_categories)
        device_type = rng.choice(device_types)
    return {
        'transaction_id': f'txn_{rng.integers(1, 1000000):06d}',
        'user_id': f'user_{rng.integers(1, 5000):05d}',
        'device_id': f'device_{rng.integers(1, 2000):05d}',
        'amount': float(np.round(amount, 2)),
        'merchant_category': merchant_cat,
        'transaction_type': rng.choice(transaction_types),
        'location': rng.choice(locations),
        'device_type': device_type,
        'hour_of_day': int(hour),
        'day_of_week': int(rng.integers(0, 7)),
        'user_transaction_frequency': float(rng.uniform(1, 20)),
        'user_avg_amount': float(rng.uniform(50, 300)),
        'user_transaction_count': int(rng.integers(1, 100)),
        'timestamp': datetime.now() - timedelta(hours=int(rng.integers(0, 720)))
    }


def load_production_inference_pipeline() -> InferencePipeline:
    """Load the production inference pipeline based on configuration defaults."""
    from src.config import ConfigManager  # Lazy import to avoid cycles

    manager = ConfigManager()
    serving_config = manager.get_serving_config()
    model_cfg = serving_config.get("model", {})

    mlflow_uri = model_cfg.get("registry_uri")
    model_stage = model_cfg.get("model_stage", "production")
    model_name = model_cfg.get("model_name")
    local_path = model_cfg.get("local_model_path", "models/Random_Forest_final_model.joblib")

    if model_cfg.get("use_mlflow", True) and model_name:
        try:
            uri = f"models:/{model_name}/{model_stage}" if model_stage else f"models:/{model_name}"
            return InferencePipeline(mlflow_model_uri=uri)
        except Exception:  # noqa: BLE001
            logger.warning("Falling back to local model artefact after MLflow load failure")

    if Path(local_path).exists():
        return InferencePipeline(model_path=local_path)

    raise FileNotFoundError("No available model artefact for inference")


__all__ = [
    "InferencePipeline",
    "AutomatedRetrainingSystem",
    "create_sample_transaction",
    "load_production_inference_pipeline",
]

