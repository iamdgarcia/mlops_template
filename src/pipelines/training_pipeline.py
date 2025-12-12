"""Training pipeline orchestration utilities."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from ..config import setup_logging
from ..data_processing import DataProcessor
from ..train import ModelTrainer
from .data_pipeline import load_config, run_data_preparation


def _score_model(metrics: Dict[str, Any]) -> float:
    """Score a model dictionary using validation ROC AUC, falling back to train."""
    val_auc = metrics.get("val_roc_auc")
    return float(val_auc) if val_auc is not None else float(metrics.get("train_roc_auc", 0.0))


def load_preprocessed_splits(
    config: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Tuple[pd.DataFrame, pd.Series]], list]:
    """
    Load pre-processed train/val/test splits from disk for CI/CD environments.

    This function is optimized for CI/CD pipelines where data has already been
    prepared and artifacts are available. It skips data generation and feature
    engineering, directly loading the processed datasets.

    Args:
        config: Optional configuration dictionary

    Returns:
        Tuple of (splits_dict, feature_names) where splits_dict contains
        (X, y) tuples for each split
    """
    cfg = load_config(config)

    # Load feature metadata
    feature_metadata_path = Path("data/selected_features.json")
    if not feature_metadata_path.exists():
        raise FileNotFoundError(
            f"Feature metadata not found at {feature_metadata_path}. "
            "Ensure data pipeline has run and artifacts are available."
        )

    with open(feature_metadata_path) as f:
        metadata = json.load(f)
        feature_names = metadata.get("selected_features", metadata.get("features", []))

    # Load processed datasets
    data_processor = DataProcessor(cfg)
    datasets = data_processor.load_processed_data()

    if not datasets:
        raise FileNotFoundError(
            "No processed datasets found. Ensure data pipeline has run and "
            "artifacts are in data/processed/ directory."
        )

    # Prepare splits with feature separation
    target_column = cfg.get("features", {}).get("target_column", "is_fraud")
    splits: Dict[str, Tuple[pd.DataFrame, pd.Series]] = {}

    for split_name, df in datasets.items():
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in {split_name} dataset")

        # Get features that exist in both the metadata and the dataframe
        available_features = [f for f in feature_names if f in df.columns]

        X = df[available_features]
        y = df[target_column]
        splits[split_name] = (X, y)

    return splits, feature_names


def run_training_pipeline(
    config: Optional[Dict[str, Any]] = None,
    *,
    regenerate_data: bool = False,
    persist_data: bool = True,
    save_model: bool = True,
    use_preprocessed: bool = False,
) -> Dict[str, Any]:
    """
    Execute the full training workflow and return artefact metadata.

    Args:
        config: Optional configuration dictionary
        regenerate_data: Force regeneration of raw data
        persist_data: Save intermediate data artifacts
        save_model: Save the trained model to disk
        use_preprocessed: Use pre-processed data from disk (CI/CD mode).
                         When True, skips data generation and feature engineering.
                         Set via USE_PREPROCESSED_DATA env var or explicitly.

    Returns:
        Dictionary containing training results and metadata
    """

    cfg = load_config(config)
    setup_logging(cfg)

    # Check environment variable for CI/CD mode
    if use_preprocessed or os.getenv("USE_PREPROCESSED_DATA", "").lower() in ("1", "true", "yes"):
        print("📦 Using pre-processed data from artifacts (CI/CD mode)")
        splits, feature_names = load_preprocessed_splits(cfg)
        data_outputs = {
            "feature_names": feature_names,
            "splits": splits,
        }
    else:
        print("🔄 Running full data preparation pipeline")
        data_outputs = run_data_preparation(
            cfg, regenerate_data=regenerate_data, persist=persist_data
        )

    splits = data_outputs["splits"]

    X_train, y_train = splits["train"]
    val_split = splits.get("validation")
    test_split = splits.get("test")

    X_val, y_val = val_split if val_split else (None, None)

    trainer = ModelTrainer(cfg)
    trained_models = trainer.train_all_models(X_train, y_train, X_val, y_val)

    best_model_name = None
    best_model_metrics: Optional[Dict[str, Any]] = None
    best_model = None

    if trainer.model_metrics:
        best_model_name = max(
            trainer.model_metrics.keys(), key=lambda key: _score_model(trainer.model_metrics[key])
        )
        best_model_metrics = trainer.model_metrics.get(best_model_name)
        best_model = trainer.best_models.get(best_model_name)

    test_metrics: Optional[Dict[str, Any]] = None
    if best_model is not None and test_split is not None:
        X_test, y_test = test_split
        test_metrics = trainer.evaluate_on_test(
            best_model, X_test, y_test, model_name=best_model_name or "model"
        )

    model_artifact_path: Optional[Path] = None
    if save_model and best_model is not None and best_model_name is not None:
        output_dir = Path(cfg.get("models", {}).get("output_dir", "models"))
        output_dir.mkdir(parents=True, exist_ok=True)
        model_artifact_path = output_dir / f"{best_model_name}_final_model.joblib"
        trainer.save_model(best_model, str(model_artifact_path))

    summary = {
        "best_model": best_model_name,
        "best_model_metrics": best_model_metrics,
        "test_metrics": test_metrics,
        "feature_count": len(data_outputs["feature_names"]),
        "model_artifact": str(model_artifact_path) if model_artifact_path else None,
    }

    summary_path = Path("data/training_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    return {
        "trainer": trainer,
        "trained_models": trained_models,
        "best_model_name": best_model_name,
        "best_model_metrics": best_model_metrics,
        "test_metrics": test_metrics,
        "model_artifact_path": model_artifact_path,
        "summary_path": summary_path,
        "feature_names": data_outputs["feature_names"],
    }
