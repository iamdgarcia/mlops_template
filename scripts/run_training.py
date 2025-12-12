#!/usr/bin/env python3
"""Run only the model training pipeline."""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipelines import run_training_pipeline


def main() -> None:
    """Run the model training pipeline."""
    print("Starting model training pipeline...\n")

    training_result = run_training_pipeline(save_model=True)

    print(f"✓ Best model: {training_result['best_model_name']}")

    # Extract ROC AUC from metrics if available
    if training_result["best_model_metrics"]:
        val_roc_auc = training_result["best_model_metrics"].get("val_roc_auc")
        if val_roc_auc:
            print(f"✓ Validation ROC-AUC: {val_roc_auc:.4f}")

    print("\nValidation metrics:")
    pprint(training_result["best_model_metrics"])

    if training_result["test_metrics"]:
        print("\nTest metrics:")
        pprint(training_result["test_metrics"])

    if training_result["model_artifact_path"]:
        print(f"\n✓ Model saved to: {training_result['model_artifact_path'].resolve()}")

    print("\nModel training completed successfully.")


if __name__ == "__main__":
    main()
