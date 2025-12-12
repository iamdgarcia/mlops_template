#!/usr/bin/env python3
"""Validate deployment package before deploying to production."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def check_file_exists(path: Path, description: str) -> bool:
    """Check if a file exists and report the result."""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {path}")
        return False


def validate_deployment_package() -> Tuple[bool, List[str]]:
    """Validate that all required files for deployment are present."""
    print("=" * 60)
    print("Validating Deployment Package")
    print("=" * 60)

    errors = []
    all_checks_passed = True

    # Check for model file
    models_dir = project_root / "models"
    model_files = list(models_dir.glob("*_final_model.joblib"))

    if model_files:
        for model_file in model_files:
            if not check_file_exists(model_file, "Model file"):
                all_checks_passed = False
                errors.append(f"Model file missing: {model_file}")
    else:
        print("✗ No trained model found in models/")
        all_checks_passed = False
        errors.append("No model files found")

    # Check for feature metadata
    feature_store = project_root / "data" / "selected_features.json"
    if check_file_exists(feature_store, "Feature metadata"):
        try:
            with open(feature_store) as f:
                metadata = json.load(f)
                # Support both "features" and "selected_features" keys
                features = metadata.get("features", metadata.get("selected_features", []))
                print(f"  → {len(features)} features defined")
        except Exception as e:
            print(f"  ⚠ Warning: Could not parse feature metadata: {e}")
            errors.append(f"Invalid feature metadata: {e}")
    else:
        all_checks_passed = False
        errors.append("Feature metadata missing")

    # Check for training summary
    training_summary = project_root / "data" / "training_summary.json"
    if check_file_exists(training_summary, "Training summary"):
        try:
            with open(training_summary) as f:
                summary = json.load(f)
                print(f"  → Best model: {summary.get('best_model', 'unknown')}")
                metrics = summary.get("best_model_metrics", {})
                if "val_roc_auc" in metrics:
                    print(f"  → Validation ROC-AUC: {metrics['val_roc_auc']:.4f}")
        except Exception as e:
            print(f"  ⚠ Warning: Could not parse training summary: {e}")

    # Check for serving script
    serve_script = project_root / "scripts" / "serve_model.py"
    if not check_file_exists(serve_script, "Serving script"):
        all_checks_passed = False
        errors.append("Serving script missing")

    # Check for source code
    src_dir = project_root / "src"
    if not check_file_exists(src_dir, "Source code directory"):
        all_checks_passed = False
        errors.append("Source code missing")

    # Check for config files
    config_dir = project_root / "configs"
    if not check_file_exists(config_dir, "Configuration directory"):
        all_checks_passed = False
        errors.append("Configuration missing")

    # Check for requirements
    requirements = project_root / "requirements.txt"
    if not check_file_exists(requirements, "Requirements file"):
        all_checks_passed = False
        errors.append("Requirements file missing")

    print("=" * 60)

    if all_checks_passed:
        print("✓ All deployment artifacts validated successfully!")
        print("=" * 60)
        return True, []
    else:
        print("\n✗ Validation FAILED - Missing required artifacts:")
        for error in errors:
            print(f"  - {error}")
        print("=" * 60)
        return False, errors


def main() -> None:
    """Run deployment validation."""
    success, errors = validate_deployment_package()

    if not success:
        print("\nDeployment package is incomplete. Fix the errors above before deploying.")
        sys.exit(1)
    else:
        print("\nDeployment package is ready for production!")
        sys.exit(0)


if __name__ == "__main__":
    main()
