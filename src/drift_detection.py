"""
Drift detection utilities for monitoring model and data drift.

This module provides comprehensive drift detection capabilities including:
- Statistical data drift detection
- Model performance drift detection
- Alert generation and retraining triggers
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, ks_2samp, wasserstein_distance
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

logger = logging.getLogger(__name__)


class DataDriftDetector:
    """
    Comprehensive data drift detection using statistical tests.
    """

    def __init__(
        self,
        reference_data: pd.DataFrame,
        selected_features: List[str],
        significance_level: float = 0.05,
    ):
        """
        Initialize drift detector.

        Args:
            reference_data: Reference/baseline dataset
            selected_features: List of features to monitor for drift
            significance_level: Statistical significance threshold
        """
        self.reference_data = reference_data
        self.selected_features = selected_features
        self.significance_level = significance_level
        self.drift_results = {}

    def detect_numerical_drift(
        self, reference_col: pd.Series, current_col: pd.Series, feature_name: str
    ) -> Dict[str, Any]:
        """Detect drift in numerical features using statistical tests."""

        # Remove infinite values and NaNs
        ref_clean = reference_col.replace([np.inf, -np.inf], np.nan).dropna()
        cur_clean = current_col.replace([np.inf, -np.inf], np.nan).dropna()

        if len(ref_clean) == 0 or len(cur_clean) == 0:
            return {
                "drift_detected": False,
                "method": "insufficient_data",
                "p_value": 1.0,
                "test_statistic": 0.0,
                "warning": "Insufficient clean data for testing",
            }

        # Kolmogorov-Smirnov test for distribution comparison
        try:
            ks_test_result = ks_2samp(ref_clean, cur_clean)
            ks_statistic = ks_test_result[0]
            ks_p_value = ks_test_result[1]
        except Exception:
            ks_statistic, ks_p_value = 0.0, 1.0

        # Wasserstein distance (Earth Mover's Distance)
        try:
            wasserstein_dist = wasserstein_distance(ref_clean, cur_clean)
        except Exception:
            wasserstein_dist = 0.0

        # Jensen-Shannon divergence
        js_divergence = self._jensen_shannon_divergence(ref_clean, cur_clean)

        # Determine if drift is detected
        if isinstance(ks_p_value, (int, float)) and isinstance(
            self.significance_level, (int, float)
        ):
            drift_detected = bool(ks_p_value < self.significance_level)
        else:
            drift_detected = False

        return {
            "drift_detected": drift_detected,
            "method": "ks_test",
            "p_value": ks_p_value,
            "test_statistic": ks_statistic,
            "wasserstein_distance": wasserstein_dist,
            "js_divergence": js_divergence,
            "feature_type": "numerical",
        }

    def detect_categorical_drift(
        self, reference_col: pd.Series, current_col: pd.Series, feature_name: str
    ) -> Dict[str, Any]:
        """Detect drift in categorical features using chi-square test."""

        # Get value counts for both datasets
        ref_counts = reference_col.value_counts()
        cur_counts = current_col.value_counts()

        # Get all unique values
        all_values = set(ref_counts.index) | set(cur_counts.index)

        # Create contingency table
        ref_freq = [ref_counts.get(val, 0) for val in all_values]
        cur_freq = [cur_counts.get(val, 0) for val in all_values]

        contingency_table = np.array([ref_freq, cur_freq])

        # Avoid division by zero
        if contingency_table.sum() == 0 or any(contingency_table.sum(axis=0) == 0):
            return {
                "drift_detected": False,
                "method": "insufficient_data",
                "p_value": 1.0,
                "test_statistic": 0.0,
                "warning": "Insufficient data for chi-square test",
            }

        # Chi-square test
        chi2_stat, chi2_p_value, dof, expected = chi2_contingency(contingency_table)

        # PSI (Population Stability Index)
        psi = self._calculate_psi(ref_counts, cur_counts)

        if isinstance(chi2_p_value, (int, float)) and isinstance(
            self.significance_level, (int, float)
        ):
            drift_detected = bool(chi2_p_value < self.significance_level)
        else:
            drift_detected = False

        return {
            "drift_detected": drift_detected,
            "method": "chi2_test",
            "p_value": chi2_p_value,
            "test_statistic": chi2_stat,
            "psi": psi,
            "feature_type": "categorical",
        }

    def _jensen_shannon_divergence(
        self, p_data: pd.Series, q_data: pd.Series, num_bins: int = 50
    ) -> float:
        """Calculate Jensen-Shannon divergence between two distributions."""

        # Create histograms
        min_val = min(p_data.min(), q_data.min())
        max_val = max(p_data.max(), q_data.max())

        if min_val == max_val:
            return 0.0

        bins = np.linspace(min_val, max_val, num_bins + 1)

        p_hist, _ = np.histogram(p_data, bins=bins, density=True)
        q_hist, _ = np.histogram(q_data, bins=bins, density=True)

        # Normalize to probabilities
        p_hist = p_hist / p_hist.sum()
        q_hist = q_hist / q_hist.sum()

        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        p_hist = p_hist + epsilon
        q_hist = q_hist + epsilon

        # Calculate JS divergence
        m = 0.5 * (p_hist + q_hist)
        js_div = 0.5 * stats.entropy(p_hist, m) + 0.5 * stats.entropy(q_hist, m)

        return float(js_div)

    def _calculate_psi(self, reference_counts: pd.Series, current_counts: pd.Series) -> float:
        """Calculate Population Stability Index (PSI)."""

        # Get all categories
        all_categories = set(reference_counts.index) | set(current_counts.index)

        psi = 0
        for category in all_categories:
            ref_pct = reference_counts.get(category, 0) / reference_counts.sum()
            cur_pct = current_counts.get(category, 0) / current_counts.sum()

            # Avoid division by zero
            if ref_pct > 0 and cur_pct > 0:
                psi += (cur_pct - ref_pct) * np.log(cur_pct / ref_pct)
            elif ref_pct == 0 and cur_pct > 0:
                psi += cur_pct * np.log(cur_pct / 0.001)  # Small epsilon
            elif ref_pct > 0 and cur_pct == 0:
                psi += -ref_pct * np.log(ref_pct / 0.001)

        return psi

    def detect_feature_drift(self, current_data: pd.DataFrame, feature_name: str) -> Dict[str, Any]:
        """Detect drift for a single feature."""

        if feature_name not in self.reference_data.columns:
            return {
                "drift_detected": False,
                "error": f"Feature {feature_name} not found in reference data",
            }

        if feature_name not in current_data.columns:
            return {
                "drift_detected": False,
                "error": f"Feature {feature_name} not found in current data",
            }

        ref_col = self.reference_data[feature_name]
        cur_col = current_data[feature_name]

        # Determine if feature is numerical or categorical
        if pd.api.types.is_numeric_dtype(ref_col) and pd.api.types.is_numeric_dtype(cur_col):
            return self.detect_numerical_drift(ref_col, cur_col, feature_name)
        else:
            return self.detect_categorical_drift(ref_col, cur_col, feature_name)

    def detect_dataset_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect drift across all features in the dataset."""

        logger.info("Running comprehensive drift detection...")

        drift_results = {}
        drift_count = 0
        total_features = len(self.selected_features)

        for feature in self.selected_features:
            if feature in current_data.columns:
                result = self.detect_feature_drift(current_data, feature)
                drift_results[feature] = result

                if result.get("drift_detected", False):
                    drift_count += 1

        # Overall drift summary
        drift_percentage = (drift_count / total_features) * 100
        overall_drift = drift_percentage > 25  # Threshold: >25% of features show drift

        summary = {
            "overall_drift_detected": overall_drift,
            "features_with_drift": drift_count,
            "total_features_tested": total_features,
            "drift_percentage": drift_percentage,
            "feature_results": drift_results,
            "timestamp": datetime.now().isoformat(),
        }

        self.drift_results = summary
        return summary


class ModelPerformanceDriftDetector:
    """
    Detect concept drift through model performance monitoring.
    """

    def __init__(
        self, model: Any, baseline_metrics: Dict[str, float], performance_threshold: float = 0.05
    ):
        """
        Initialize performance drift detector.

        Args:
            model: Trained model for evaluation
            baseline_metrics: Baseline performance metrics
            performance_threshold: Threshold for performance degradation
        """
        self.model = model
        self.baseline_metrics = baseline_metrics
        self.performance_threshold = performance_threshold

    def evaluate_model_performance(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Optional[Dict[str, float]]:
        """Evaluate model performance on current data."""

        if self.model is None:
            return None

        # Make predictions
        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)[:, 1]

        # Calculate metrics
        current_metrics = {
            "roc_auc": roc_auc_score(y, y_pred_proba),
            "precision": precision_score(y, y_pred),
            "recall": recall_score(y, y_pred),
            "f1_score": f1_score(y, y_pred),
        }

        return current_metrics

    def detect_performance_drift(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Detect concept drift through performance comparison."""

        current_metrics = self.evaluate_model_performance(X, y)

        if current_metrics is None:
            return {
                "performance_drift_detected": False,
                "error": "Model not available for evaluation",
            }

        # Compare with baseline metrics
        drift_detected = False
        metric_changes = {}

        for metric, current_value in current_metrics.items():
            if metric in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric]
                change = abs(current_value - baseline_value) / baseline_value

                metric_changes[metric] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "change_percentage": change * 100,
                    "drift_detected": change > self.performance_threshold,
                }

                if change > self.performance_threshold:
                    drift_detected = True

        return {
            "performance_drift_detected": drift_detected,
            "current_metrics": current_metrics,
            "baseline_metrics": self.baseline_metrics,
            "metric_changes": metric_changes,
            "timestamp": datetime.now().isoformat(),
        }


class DriftAlertSystem:
    """
    Automated alert system for drift detection.
    """

    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None):
        """Initialize alert system with thresholds."""
        self.alert_thresholds = alert_thresholds or {
            "drift_percentage_critical": 50,  # >50% features with drift
            "drift_percentage_warning": 25,  # >25% features with drift
            "performance_degradation_critical": 0.10,  # >10% performance drop
            "performance_degradation_warning": 0.05,  # >5% performance drop
        }

    def evaluate_drift_severity(self, drift_result: Dict[str, Any]) -> str:
        """Evaluate the severity of detected drift."""

        drift_percentage = drift_result["drift_percentage"]

        if drift_percentage >= self.alert_thresholds["drift_percentage_critical"]:
            return "CRITICAL"
        elif drift_percentage >= self.alert_thresholds["drift_percentage_warning"]:
            return "WARNING"
        else:
            return "OK"

    def generate_alert_report(
        self,
        drift_result: Dict[str, Any],
        performance_result: Optional[Dict[str, Any]] = None,
        dataset_name: str = "Current Data",
    ) -> Dict[str, Any]:
        """Generate comprehensive alert report."""

        # Evaluate severity levels
        data_drift_severity = self.evaluate_drift_severity(drift_result)

        # Generate report
        alert_report = {
            "timestamp": datetime.now().isoformat(),
            "dataset_name": dataset_name,
            "overall_severity": data_drift_severity,
            "data_drift": {
                "severity": data_drift_severity,
                "features_affected": drift_result["features_with_drift"],
                "total_features": drift_result["total_features_tested"],
                "drift_percentage": drift_result["drift_percentage"],
            },
        }

        if performance_result:
            alert_report["performance_drift"] = {
                "drift_detected": performance_result.get("performance_drift_detected", False),
                "affected_metrics": [
                    metric
                    for metric, change in performance_result.get("metric_changes", {}).items()
                    if change["drift_detected"]
                ],
            }

        # Recommendations
        recommendations = self._generate_recommendations(data_drift_severity, drift_result)
        alert_report["recommendations"] = recommendations

        return alert_report

    def _generate_recommendations(self, severity: str, drift_result: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on drift severity."""

        recommendations = []

        if severity == "CRITICAL":
            recommendations.extend(
                [
                    "IMMEDIATE ACTION REQUIRED: Severe drift detected",
                    "Trigger emergency model retraining with recent data",
                    "Consider temporarily disabling automated decisions",
                    "Investigate root cause of data distribution changes",
                    "Validate data quality and preprocessing pipeline",
                ]
            )
        elif severity == "WARNING":
            recommendations.extend(
                [
                    "Monitor closely: moderate drift detected",
                    "Schedule model retraining within the next evaluation cycle",
                    "Review recent data collection processes",
                    "Increase monitoring frequency",
                    "Assess whether feature engineering updates are required",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Continue normal operations",
                    "Maintain regular monitoring schedule",
                    "Document baseline performance for future comparisons",
                ]
            )

        return recommendations

    def should_trigger_retraining(self, alert_report: Dict[str, Any]) -> bool:
        """Determine if automatic retraining should be triggered."""

        trigger_conditions = [
            alert_report["overall_severity"] == "CRITICAL",
            alert_report["data_drift"]["drift_percentage"] > 60,
        ]

        return any(trigger_conditions)


def create_drifted_data(
    reference_data: pd.DataFrame, drift_type: str = "moderate", n_samples: int = 500
) -> pd.DataFrame:
    """
    Create synthetic data with intentional drift for demonstration.

    Args:
        reference_data: Original reference dataset
        drift_type: Type of drift ('no_drift', 'moderate', 'severe')
        n_samples: Number of samples to generate

    Returns:
        DataFrame with synthetic drift
    """
    np.random.seed(42)

    # Sample from reference data
    sampled_data = reference_data.sample(n=n_samples, replace=True).copy()

    if drift_type == "no_drift":
        return sampled_data

    elif drift_type == "moderate":
        # Introduce moderate drift
        sampled_data["amount"] = sampled_data["amount"] * np.random.normal(
            1.2, 0.1, len(sampled_data)
        )

        # Change time patterns
        evening_mask = np.random.random(len(sampled_data)) < 0.3
        sampled_data.loc[evening_mask, "hour_of_day"] = np.random.choice(
            [18, 19, 20, 21, 22], size=evening_mask.sum()
        )

    elif drift_type == "severe":
        # Introduce severe drift
        sampled_data["amount"] = sampled_data["amount"] * np.random.normal(
            2.0, 0.3, len(sampled_data)
        )
        sampled_data["hour_of_day"] = np.random.choice([0, 1, 2, 3, 4, 5], size=len(sampled_data))

    # Recalculate derived features
    if "log_amount" in sampled_data.columns:
        sampled_data["log_amount"] = np.log1p(sampled_data["amount"])
    if "hour_sin" in sampled_data.columns:
        sampled_data["hour_sin"] = np.sin(2 * np.pi * sampled_data["hour_of_day"] / 24)
    if "hour_cos" in sampled_data.columns:
        sampled_data["hour_cos"] = np.cos(2 * np.pi * sampled_data["hour_of_day"] / 24)

    return sampled_data
