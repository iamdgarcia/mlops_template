"""Training pipeline orchestration utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import setup_logging
from ..train import ModelTrainer
from .data_pipeline import run_data_preparation, load_config


def _score_model(metrics: Dict[str, Any]) -> float:
    """Score a model dictionary using validation ROC AUC, falling back to train."""
    val_auc = metrics.get("val_roc_auc")
    return float(val_auc) if val_auc is not None else float(metrics.get("train_roc_auc", 0.0))


def run_training_pipeline(
    config: Optional[Dict[str, Any]] = None,
    *,
    regenerate_data: bool = False,
    persist_data: bool = True,
    save_model: bool = True,
) -> Dict[str, Any]:
    """Execute the full training workflow and return artefact metadata."""

    cfg = load_config(config)
    setup_logging(cfg)

    data_outputs = run_data_preparation(cfg, regenerate_data=regenerate_data, persist=persist_data)
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
        trainer.save_model(best_model, f"{best_model_name}_final_model", str(output_dir))
        model_artifact_path = output_dir / f"{best_model_name}_final_model.joblib"

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
