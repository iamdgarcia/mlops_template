import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from src.inference import InferencePipeline
from src.pipelines import run_data_preparation


def _small_config(tmp_path: Path) -> dict:
    return {
        "data": {
            "raw_data_path": str(tmp_path / "raw.csv"),
            "processed_data_path": str(tmp_path / "processed"),
            "test_size": 0.2,
            "validation_size": 0.2,
            "random_state": 42,
            "n_samples": 500,
            "fraud_rate": 0.05,
            "n_days": 30,
        },
        "features": {
            "target_column": "is_fraud",
            "exclude_columns": [],
        },
    }


def test_run_data_preparation_returns_expected_splits(tmp_path):
    config = _small_config(tmp_path)

    outputs = run_data_preparation(config, regenerate_data=True, persist=False)

    assert set(outputs.keys()) >= {"raw", "clean", "features", "feature_names", "splits"}
    assert len(outputs["raw"]) == config["data"]["n_samples"]
    assert len(outputs["feature_names"]) > 10

    splits = outputs["splits"]
    assert "train" in splits and "test" in splits

    X_train, y_train = splits["train"]
    X_test, y_test = splits["test"]

    # Rough sanity checks on split sizes
    assert X_train.shape[0] > X_test.shape[0]
    assert X_train.shape[1] == X_test.shape[1] == len(outputs["feature_names"])
    # Target should be binary
    assert set(y_train.unique()) <= {0, 1}


def test_inference_pipeline_predicts_single_row(tmp_path):
    pytest.importorskip("mlflow", reason="mlflow is required for inference pipeline tests")
    config = _small_config(tmp_path)
    outputs = run_data_preparation(config, regenerate_data=True, persist=False)

    feature_names = outputs["feature_names"]
    X_train, y_train = outputs["splits"]["train"]

    model = LogisticRegression(max_iter=200, class_weight="balanced", solver="liblinear")
    model.fit(X_train, y_train)

    model_path = tmp_path / "log_reg.joblib"
    joblib.dump(model, model_path)

    feature_store_path = tmp_path / "features.json"
    feature_store_path.write_text(json.dumps({"selected_features": feature_names}))

    pipeline = InferencePipeline(model_path=str(model_path), feature_store_path=feature_store_path)

    sample = outputs["raw"].iloc[0].to_dict()
    prediction = pipeline.predict_single(sample)

    assert "fraud_prediction" in prediction
    assert "fraud_probability" in prediction
    assert 0.0 <= prediction["fraud_probability"] <= 1.0
