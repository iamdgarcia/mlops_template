#!/usr/bin/env python3
"""End-to-end pipeline runner for the fraud detection project."""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipelines import run_data_preparation, run_training_pipeline


def run_pipeline() -> None:
    print("Starting full fraud detection pipeline...\n")

    print("Step 1/2: Preparing data")
    data_outputs = run_data_preparation(regenerate_data=False, persist=True)
    print(f"  Raw samples: {len(data_outputs['raw']):,}")
    print(f"  Clean samples: {len(data_outputs['clean']):,}")
    print(f"  Engineered feature count: {len(data_outputs['feature_names'])}")

    print("\nStep 2/2: Training models")
    training_result = run_training_pipeline(save_model=True)

    print("  Best model:", training_result["best_model_name"])
    print("  Validation metrics:")
    pprint(training_result["best_model_metrics"])

    if training_result["test_metrics"]:
        print("  Test metrics:")
        pprint(training_result["test_metrics"])

    if training_result["model_artifact_path"]:
        print("  Model artefact saved at:", training_result["model_artifact_path"].resolve())

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
