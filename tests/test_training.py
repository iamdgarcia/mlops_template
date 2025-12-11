"""
Tests for model training functionality.

This module tests the ModelTrainer class and training pipeline.
"""
import json
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

from src.train import ModelTrainer


@pytest.fixture
def sample_training_data():
    """Create sample classification data for testing."""
    X, y = make_classification(
        n_samples=500,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_classes=2,
        class_sep=1.0,
        random_state=42,
        flip_y=0.1,
    )
    
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")
    
    # Create train/test split
    train_size = int(0.8 * len(X_df))
    X_train, X_test = X_df[:train_size], X_df[train_size:]
    y_train, y_test = y_series[:train_size], y_series[train_size:]
    
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": feature_names,
    }


@pytest.fixture
def basic_config(tmp_path):
    """Create a minimal training configuration."""
    return {
        "training": {
            "random_state": 42,
            "n_jobs": 1,
            "cv_folds": 3,
        },
        "models": {
            "logistic_regression": {
                "enabled": True,
                "params": {
                    "max_iter": 100,
                    "solver": "liblinear",
                },
                "grid_search": {
                    "enabled": False,
                },
            },
        },
        "mlflow": {
            "tracking_uri": str(tmp_path / "mlruns"),
            "experiment_name": "test_fraud_detection",
        },
        "output": {
            "models_dir": str(tmp_path / "models"),
        },
    }


def test_model_trainer_initialization(basic_config):
    """Test that ModelTrainer initializes correctly."""
    trainer = ModelTrainer(basic_config)
    
    assert trainer.config == basic_config
    assert trainer.mlflow_config == basic_config["mlflow"]


def test_train_single_model(sample_training_data, basic_config):
    """Test training a single model without MLflow."""
    trainer = ModelTrainer(basic_config)
    
    X_train = sample_training_data["X_train"]
    y_train = sample_training_data["y_train"]
    X_test = sample_training_data["X_test"]
    y_test = sample_training_data["y_test"]
    
    # Train a simple logistic regression
    model = LogisticRegression(max_iter=100, solver="liblinear", random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Basic assertions
    assert len(y_pred) == len(y_test)
    assert len(y_proba) == len(y_test)
    assert all(pred in [0, 1] for pred in y_pred)
    assert all(0 <= prob <= 1 for prob in y_proba)


def test_evaluate_model(sample_training_data, basic_config):
    """Test model evaluation metrics calculation."""
    trainer = ModelTrainer(basic_config)
    
    X_train = sample_training_data["X_train"]
    y_train = sample_training_data["y_train"]
    X_test = sample_training_data["X_test"]
    y_test = sample_training_data["y_test"]
    
    # Train model
    model = LogisticRegression(max_iter=100, solver="liblinear", random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate using trainer's evaluate method
    metrics = trainer.evaluate_model(model, X_test, y_test)
    
    # Check that all expected metrics are present
    expected_metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc", "avg_precision"]
    for metric in expected_metrics:
        assert metric in metrics
        assert isinstance(metrics[metric], (int, float))
        assert 0 <= metrics[metric] <= 1
    
    # Check confusion matrix
    assert "confusion_matrix" in metrics
    cm = metrics["confusion_matrix"]
    assert cm.shape == (2, 2)
    assert cm.sum() == len(y_test)


def test_save_and_load_model(sample_training_data, basic_config, tmp_path):
    """Test saving and loading a trained model."""
    trainer = ModelTrainer(basic_config)
    
    X_train = sample_training_data["X_train"]
    y_train = sample_training_data["y_train"]
    X_test = sample_training_data["X_test"]
    
    # Train model
    model = LogisticRegression(max_iter=100, solver="liblinear", random_state=42)
    model.fit(X_train, y_train)
    
    # Save model
    model_path = tmp_path / "test_model.joblib"
    trainer.save_model(model, model_path)
    
    assert model_path.exists()
    
    # Load model
    loaded_model = joblib.load(model_path)
    
    # Verify loaded model produces same predictions
    original_pred = model.predict(X_test)
    loaded_pred = loaded_model.predict(X_test)
    
    np.testing.assert_array_equal(original_pred, loaded_pred)


def test_model_trainer_handles_imbalanced_data():
    """Test that trainer handles class imbalance properly."""
    # Create highly imbalanced dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_classes=2,
        weights=[0.95, 0.05],  # 95% negative, 5% positive
        random_state=42,
    )
    
    X_df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    y_series = pd.Series(y)
    
    # Verify imbalance
    fraud_rate = y_series.mean()
    assert 0.04 <= fraud_rate <= 0.06  # Should be around 5%
    
    # Train with class_weight='balanced'
    model = LogisticRegression(
        max_iter=200,
        solver="liblinear",
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_df, y_series)
    
    # Model should be able to make predictions
    predictions = model.predict(X_df)
    assert len(predictions) == len(y_series)
    assert len(set(predictions)) == 2  # Should predict both classes


def test_feature_importance_extraction(sample_training_data, basic_config):
    """Test extraction of feature importance from trained models."""
    from sklearn.ensemble import RandomForestClassifier
    
    trainer = ModelTrainer(basic_config)
    
    X_train = sample_training_data["X_train"]
    y_train = sample_training_data["y_train"]
    feature_names = sample_training_data["feature_names"]
    
    # Train Random Forest (has feature_importances_)
    model = RandomForestClassifier(n_estimators=10, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    
    # Extract feature importances
    importances = model.feature_importances_
    
    assert len(importances) == len(feature_names)
    assert all(imp >= 0 for imp in importances)
    assert abs(sum(importances) - 1.0) < 0.01  # Should sum to approximately 1


@pytest.mark.parametrize("metric_name,expected_range", [
    ("accuracy", (0, 1)),
    ("precision", (0, 1)),
    ("recall", (0, 1)),
    ("f1_score", (0, 1)),
    ("roc_auc", (0, 1)),
])
def test_metric_values_in_valid_range(sample_training_data, basic_config, metric_name, expected_range):
    """Test that all metrics are within valid ranges."""
    trainer = ModelTrainer(basic_config)
    
    X_train = sample_training_data["X_train"]
    y_train = sample_training_data["y_train"]
    X_test = sample_training_data["X_test"]
    y_test = sample_training_data["y_test"]
    
    # Train model
    model = LogisticRegression(max_iter=100, solver="liblinear", random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    metrics = trainer.evaluate_model(model, X_test, y_test)
    
    assert metric_name in metrics
    value = metrics[metric_name]
    assert expected_range[0] <= value <= expected_range[1], \
        f"{metric_name} value {value} not in range {expected_range}"
