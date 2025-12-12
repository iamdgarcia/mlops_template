#!/usr/bin/env python3
"""Validate deployment package and enforce quality gates before deploying to production."""

from __future__ import annotations

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

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


def load_training_config() -> Dict[str, Any]:
    """Load training configuration from YAML."""
    config_path = project_root / "configs" / "training_config.yaml"
    if not config_path.exists():
        print(f"⚠ Warning: Training config not found at {config_path}")
        return {}
    
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_production_baseline() -> Optional[Dict[str, Any]]:
    """Load production model baseline metrics if available."""
    config = load_training_config()
    baseline_path = config.get("deployment", {}).get(
        "production_baseline_path", 
        "data/production_model_baseline.json"
    )
    baseline_file = project_root / baseline_path
    
    if not baseline_file.exists():
        print("ℹ No production baseline found (first deployment)")
        return None
    
    try:
        with open(baseline_file) as f:
            baseline = json.load(f)
            print(f"✓ Production baseline loaded: {baseline_file}")
            return baseline
    except Exception as e:
        print(f"⚠ Warning: Could not load production baseline: {e}")
        return None


def validate_minimum_thresholds(
    metrics: Dict[str, float],
    config: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """Validate that model meets minimum quality thresholds."""
    print("\n" + "=" * 60)
    print("Validating Minimum Quality Thresholds")
    print("=" * 60)
    
    errors = []
    min_metrics = config.get("evaluation", {}).get("minimum_metrics", {})
    
    if not min_metrics:
        print("⚠ Warning: No minimum thresholds configured")
        return True, []
    
    for metric_name, threshold in min_metrics.items():
        # Look for validation metric (prefer val_ prefix)
        val_metric = f"val_{metric_name}"
        test_metric = f"test_{metric_name}"
        
        actual_value = metrics.get(val_metric) or metrics.get(test_metric)
        
        if actual_value is None:
            errors.append(f"Metric '{metric_name}' not found in training summary")
            print(f"✗ {metric_name}: NOT FOUND")
            continue
        
        passed = actual_value >= threshold
        status = "✓" if passed else "✗"
        print(f"{status} {metric_name}: {actual_value:.4f} (threshold: {threshold:.4f})")
        
        if not passed:
            errors.append(
                f"{metric_name}: {actual_value:.4f} < minimum {threshold:.4f} "
                f"(deficit: {threshold - actual_value:.4f})"
            )
    
    print("=" * 60)
    return len(errors) == 0, errors


def compare_with_production(
    new_metrics: Dict[str, float],
    production_baseline: Dict[str, Any],
    config: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """Compare new model with production baseline."""
    print("\n" + "=" * 60)
    print("Comparing with Production Model")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    prod_metrics = production_baseline.get("best_model_metrics", {})
    if not prod_metrics:
        print("⚠ Warning: No metrics in production baseline")
        return True, []
    
    # Get degradation tolerance thresholds
    degradation_tolerance = config.get("deployment", {}).get(
        "degradation_tolerance", 
        {"roc_auc": 0.05, "precision": 0.05, "recall": 0.03, "f1_score": 0.05}
    )
    
    critical_metrics = config.get("deployment", {}).get(
        "critical_metrics", 
        ["recall", "roc_auc"]
    )
    
    print(f"Production model: {production_baseline.get('best_model', 'unknown')}")
    print(f"\nMetric Comparison:")
    print("-" * 60)
    
    for metric_base in ["roc_auc", "precision", "recall", "f1_score"]:
        val_metric = f"val_{metric_base}"
        test_metric = f"test_{metric_base}"
        
        # Get new model metric
        new_value = new_metrics.get(val_metric) or new_metrics.get(test_metric)
        if new_value is None:
            continue
        
        # Get production metric
        prod_value = prod_metrics.get(val_metric) or prod_metrics.get(test_metric)
        if prod_value is None:
            continue
        
        # Calculate degradation
        degradation = (prod_value - new_value) / prod_value if prod_value != 0 else 0
        tolerance = degradation_tolerance.get(metric_base, 0.05)
        
        # Determine status
        if new_value >= prod_value:
            status = "✓ IMPROVED"
            change = f"+{((new_value - prod_value) / prod_value * 100):.2f}%"
        elif degradation <= tolerance:
            status = "✓ ACCEPTABLE"
            change = f"-{(degradation * 100):.2f}%"
        else:
            status = "✗ DEGRADED"
            change = f"-{(degradation * 100):.2f}%"
        
        print(f"{status:15} {metric_base:12}: {new_value:.4f} vs {prod_value:.4f} ({change})")
        
        # Check if degradation exceeds tolerance
        if degradation > tolerance:
            is_critical = metric_base in critical_metrics
            msg = (
                f"{metric_base} degraded by {degradation*100:.1f}% "
                f"(new: {new_value:.4f} vs prod: {prod_value:.4f}, "
                f"tolerance: {tolerance*100:.0f}%)"
            )
            
            if is_critical:
                errors.append(f"CRITICAL: {msg}")
            else:
                warnings.append(msg)
    
    print("-" * 60)
    
    # Display warnings
    if warnings:
        print("\n⚠ WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("=" * 60)
    return len(errors) == 0, errors


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
        print("✓ All deployment artifacts present")
        return True, []
    else:
        print("\n✗ Validation FAILED - Missing required artifacts:")
        for error in errors:
            print(f"  - {error}")
        return False, errors


def validate_model_quality() -> Tuple[bool, List[str]]:
    """Validate model quality against thresholds and production baseline."""
    errors = []
    
    # Load training summary
    training_summary_path = project_root / "data" / "training_summary.json"
    if not training_summary_path.exists():
        return False, ["Training summary not found"]
    
    try:
        with open(training_summary_path) as f:
            summary = json.load(f)
    except Exception as e:
        return False, [f"Failed to load training summary: {e}"]
    
    new_metrics = summary.get("best_model_metrics", {})
    if not new_metrics:
        return False, ["No metrics found in training summary"]
    
    # Load configuration
    config = load_training_config()
    
    # Step 1: Validate minimum thresholds
    threshold_ok, threshold_errors = validate_minimum_thresholds(new_metrics, config)
    errors.extend(threshold_errors)
    
    # Step 2: Compare with production baseline
    production_baseline = load_production_baseline()
    if production_baseline:
        comparison_ok, comparison_errors = compare_with_production(
            new_metrics, production_baseline, config
        )
        errors.extend(comparison_errors)
    else:
        print("\nℹ Skipping production comparison (first deployment)")
    
    return len(errors) == 0, errors


def main() -> None:
    """Run deployment validation."""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  DEPLOYMENT VALIDATION & QUALITY GATES".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60 + "\n")
    
    all_errors = []
    
    # Step 1: Validate deployment package
    package_ok, package_errors = validate_deployment_package()
    all_errors.extend(package_errors)
    
    # Step 2: Validate model quality (only if package is complete)
    if package_ok:
        quality_ok, quality_errors = validate_model_quality()
        all_errors.extend(quality_errors)
    else:
        print("\n⚠ Skipping quality validation due to missing artifacts")
        quality_ok = False
    
    # Final summary
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    
    if package_ok and quality_ok:
        print("#" + "  ✓ ALL VALIDATIONS PASSED".center(58) + "#")
        print("#" + " " * 58 + "#")
        print("#" * 60)
        print("\n✅ Deployment package is ready for production!")
        print("🚀 Model meets all quality gates and can be safely deployed.\n")
        sys.exit(0)
    else:
        print("#" + "  ✗ VALIDATION FAILED".center(58) + "#")
        print("#" + " " * 58 + "#")
        print("#" * 60)
        print("\n❌ Deployment BLOCKED - Quality gates not met:")
        print("\nErrors:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print("\n🛑 Fix the errors above before deploying to production.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
