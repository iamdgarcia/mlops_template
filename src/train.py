"""
Model training utilities for fraud detection.

This module provides functions for training, evaluating, and tracking
machine learning models with MLflow integration.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import seaborn as sns
from mlflow.models.signature import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV

# Try to import xgboost, fall back gracefully if not available
try:
    import xgboost as xgb

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available, will use RandomForest instead")

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Model training and evaluation class with MLflow integration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize model trainer.

        Args:
            config: Configuration dictionary containing training parameters
        """
        self.config = config
        self.mlflow_config = config.get("mlflow", {})
        self.models_config = config.get("models", {})
        self.cv_config = config.get("cross_validation", {})

        # Set up MLflow
        self._setup_mlflow()

        # Initialize models
        self.models = {}
        self.best_models = {}
        self.model_metrics = {}
        self.model_run_ids = {}

    def _setup_mlflow(self) -> None:
        """Set up MLflow tracking."""
        tracking_uri = self.mlflow_config.get("tracking_uri", "file:./mlruns")
        experiment_name = self.mlflow_config.get("experiment_name", "fraud-detection")

        mlflow.set_tracking_uri(tracking_uri)

        # Create or get experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created MLflow experiment: {experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing MLflow experiment: {experiment_name}")

            mlflow.set_experiment(experiment_name)

        except Exception as e:
            logger.error(f"Error setting up MLflow: {e}")
            raise

    def prepare_model_configs(self) -> Dict[str, Any]:
        """Prepare model configurations."""
        model_configs = {}

        # Logistic Regression
        if self.models_config.get("logistic_regression", {}).get("enabled", True):
            model_configs["logistic_regression"] = {
                "model_class": LogisticRegression,
                "params": {"random_state": 42, "max_iter": 1000, "class_weight": "balanced"},
                "param_grid": self.models_config.get("logistic_regression", {}).get(
                    "hyperparameters", {"C": [0.1, 1.0, 10.0], "solver": ["liblinear", "lbfgs"]}
                ),
            }

        # XGBoost (or RandomForest as fallback)
        if XGBOOST_AVAILABLE and self.models_config.get("xgboost", {}).get("enabled", True):
            model_configs["xgboost"] = {
                "model_class": xgb.XGBClassifier if XGBOOST_AVAILABLE else None,
                "params": {
                    "random_state": 42,
                    "eval_metric": "logloss",
                    "use_label_encoder": False,
                },
                "param_grid": self.models_config.get("xgboost", {}).get(
                    "hyperparameters",
                    {
                        "n_estimators": [100, 200],
                        "max_depth": [3, 5],
                        "learning_rate": [0.1, 0.2],
                        "scale_pos_weight": [1, 10],
                    },
                ),
            }
        else:
            # Fallback to RandomForest; allow overriding the grid via config if provided
            rf_cfg = self.models_config.get("random_forest", {})
            rf_param_grid = rf_cfg.get(
                "hyperparameters",
                {
                    "n_estimators": [100],
                    "max_depth": [5, None],
                    "min_samples_split": [2],
                    "min_samples_leaf": [1],
                },
            )

            model_configs["random_forest"] = {
                "model_class": RandomForestClassifier,
                "params": {"random_state": 42, "class_weight": "balanced"},
                "param_grid": rf_param_grid,
            }

        return model_configs

    def train_model(
        self,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        use_grid_search: bool = True,
    ) -> Any:
        """
        Train a single model with hyperparameter tuning.

        Args:
            model_name: Name of the model to train
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            use_grid_search: Whether to use grid search for hyperparameter tuning

        Returns:
            Trained model
        """
        logger.info(f"Training {model_name} model")

        model_configs = self.prepare_model_configs()

        if model_name not in model_configs:
            raise ValueError(f"Model {model_name} not configured")

        config = model_configs[model_name]
        param_grid = config.get("param_grid", {})
        tuned_param_keys = set(param_grid.keys()) if param_grid else set()
        # Log only non-tuned parameters before training
        non_tuned_params = {k: v for k, v in config["params"].items() if k not in tuned_param_keys}
        with mlflow.start_run(run_name=f"{model_name}_training") as run:
            if non_tuned_params:
                mlflow.log_params(non_tuned_params)

            if use_grid_search and config.get("param_grid"):
                model = self._train_with_grid_search(config, X_train, y_train)
                # Log only tuned parameters (best_params_) that were not already logged
                best_params_to_log = {
                    k: v for k, v in model.best_params_.items() if k not in non_tuned_params
                }
                if best_params_to_log:
                    mlflow.log_params(best_params_to_log)
                mlflow.log_metric("best_cv_score", model.best_score_)
                best_model = model.best_estimator_
            else:
                model_class = config["model_class"]
                model = model_class(**config["params"])
                model.fit(X_train, y_train)
                best_model = model

            metrics = self._evaluate_model(best_model, X_train, y_train, X_val, y_val)

            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            try:
                mlflow.sklearn.log_model(
                    best_model,
                    model_name,
                    input_example=X_train.head(3),
                    signature=infer_signature(X_train, y_train),
                )
            except Exception as e:
                logger.warning(f"Error logging model to MLflow: {e}")

            self.models[model_name] = model if use_grid_search else best_model
            self.best_models[model_name] = best_model
            self.model_metrics[model_name] = metrics
            self.model_run_ids[model_name] = run.info.run_id

            val_auc = metrics.get("val_roc_auc")
            if val_auc is not None:
                logger.info(f"Validation ROC AUC: {val_auc:.4f}")
            else:
                logger.info("Validation ROC AUC not available (no validation split)")

            logger.info(f"Completed training {model_name}")

            return best_model

    def _train_with_grid_search(
        self, config: Dict[str, Any], X_train: pd.DataFrame, y_train: pd.Series
    ) -> GridSearchCV:
        """Train model with grid search."""
        model_class = config["model_class"]
        base_model = model_class(**config["params"])

        cv_folds = self.cv_config.get("cv_folds", 5)
        scoring = self.cv_config.get("scoring", "roc_auc")
        n_jobs = self.cv_config.get("n_jobs", -1)

        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=config["param_grid"],
            cv=cv_folds,
            scoring=scoring,
            n_jobs=n_jobs,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)

        logger.info(f"Grid search completed. Best score: {grid_search.best_score_:.4f}")
        logger.info(f"Best parameters: {grid_search.best_params_}")

        return grid_search

    def _evaluate_model(
        self,
        model: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Dict[str, float]:
        """Evaluate model and return metrics."""
        metrics = {}

        # Training metrics
        y_train_pred = model.predict(X_train)
        y_train_proba = model.predict_proba(X_train)[:, 1]

        metrics["train_accuracy"] = accuracy_score(y_train, y_train_pred)
        metrics["train_precision"] = precision_score(y_train, y_train_pred)
        metrics["train_recall"] = recall_score(y_train, y_train_pred)
        metrics["train_f1"] = f1_score(y_train, y_train_pred)
        metrics["train_roc_auc"] = roc_auc_score(y_train, y_train_proba)
        metrics["train_avg_precision"] = average_precision_score(y_train, y_train_proba)

        # Validation metrics
        if X_val is not None and y_val is not None:
            y_val_pred = model.predict(X_val)
            y_val_proba = model.predict_proba(X_val)[:, 1]

            metrics["val_accuracy"] = accuracy_score(y_val, y_val_pred)
            metrics["val_precision"] = precision_score(y_val, y_val_pred)
            metrics["val_recall"] = recall_score(y_val, y_val_pred)
            metrics["val_f1"] = f1_score(y_val, y_val_pred)
            metrics["val_roc_auc"] = roc_auc_score(y_val, y_val_proba)
            metrics["val_avg_precision"] = average_precision_score(y_val, y_val_proba)

        return metrics

    def train_all_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Dict[str, Any]:
        """
        Train all configured models.

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)

        Returns:
            Dictionary of trained models
        """
        logger.info("Training all configured models")

        model_configs = self.prepare_model_configs()
        trained_models = {}

        for model_name in model_configs.keys():
            try:
                model = self.train_model(model_name, X_train, y_train, X_val, y_val)
                trained_models[model_name] = model
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                continue

        # Select best model based on validation ROC AUC (fallback to train ROC AUC)
        if self.model_metrics:

            def _score(model_key: str) -> float:
                metrics = self.model_metrics[model_key]
                val_auc = metrics.get("val_roc_auc")
                return val_auc if val_auc is not None else metrics.get("train_roc_auc", 0.0)

            best_model_name = max(self.model_metrics.keys(), key=_score)
            logger.info(f"Best model: {best_model_name}")

            run_id = self.model_run_ids.get(best_model_name)
            if run_id:
                self._register_best_model(best_model_name, run_id)
            else:
                logger.warning("Best model run identifier not available; skipping registry sync")

        return trained_models

    def _register_best_model(self, model_name: str, run_id: Optional[str]) -> None:
        """Register best model in MLflow Model Registry."""
        if not run_id:
            logger.warning("Run id missing; cannot register model in MLflow")
            return

        try:
            registry_model_name = self.mlflow_config.get("model_name", "fraud-detector")
            model_uri = f"runs:/{run_id}/{model_name}"

            mlflow.register_model(
                model_uri=model_uri,
                name=registry_model_name,
                tags={"model_type": model_name, "stage": "development"},
            )

            logger.info(
                f"Registered {model_name} as {registry_model_name} in MLflow Model Registry"
            )

        except Exception as e:
            logger.error(f"Error registering model: {e}")

    def evaluate_on_test(
        self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, model_name: str = "model"
    ) -> Dict[str, float]:
        """
        Evaluate model on test set.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test targets
            model_name: Name of the model for logging

        Returns:
            Dictionary of test metrics
        """
        logger.info(f"Evaluating {model_name} on test set")

        with mlflow.start_run(run_name=f"{model_name}_test_evaluation"):
            # Make predictions
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            test_metrics = {
                "test_accuracy": accuracy_score(y_test, y_pred),
                "test_precision": precision_score(y_test, y_pred),
                "test_recall": recall_score(y_test, y_pred),
                "test_f1": f1_score(y_test, y_pred),
                "test_roc_auc": roc_auc_score(y_test, y_proba),
                "test_avg_precision": average_precision_score(y_test, y_proba),
            }

            # Log metrics
            for metric_name, metric_value in test_metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Generate and log plots
            self._create_evaluation_plots(y_test, y_pred, y_proba, model_name)

            logger.info(f"Test evaluation completed for {model_name}")
            logger.info(f"Test ROC AUC: {test_metrics['test_roc_auc']:.4f}")

            return test_metrics

    def _create_evaluation_plots(
        self, y_true: pd.Series, y_pred: pd.Series, y_proba: np.ndarray, model_name: str
    ) -> None:
        """Create and log evaluation plots."""
        try:
            # Confusion Matrix
            plt.figure(figsize=(8, 6))
            cm = confusion_matrix(y_true, y_pred)
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
            plt.title(f"Confusion Matrix - {model_name}")
            plt.ylabel("True Label")
            plt.xlabel("Predicted Label")
            plt.tight_layout()
            mlflow.log_figure(plt.gcf(), f"{model_name}_confusion_matrix.png")
            plt.close()

            # ROC Curve
            plt.figure(figsize=(8, 6))
            fpr, tpr, _ = roc_curve(y_true, y_proba)
            auc_score = roc_auc_score(y_true, y_proba)
            plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {auc_score:.3f})")
            plt.plot([0, 1], [0, 1], "k--", label="Random")
            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.title(f"ROC Curve - {model_name}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            mlflow.log_figure(plt.gcf(), f"{model_name}_roc_curve.png")
            plt.close()

            # Precision-Recall Curve
            plt.figure(figsize=(8, 6))
            precision, recall, _ = precision_recall_curve(y_true, y_proba)
            avg_precision = average_precision_score(y_true, y_proba)
            plt.plot(recall, precision, label=f"PR Curve (AP = {avg_precision:.3f})")
            plt.xlabel("Recall")
            plt.ylabel("Precision")
            plt.title(f"Precision-Recall Curve - {model_name}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            mlflow.log_figure(plt.gcf(), f"{model_name}_pr_curve.png")
            plt.close()

        except Exception as e:
            logger.warning(f"Error creating plots: {e}")

    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """
        Evaluate a trained model.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test targets

        Returns:
            Dictionary of evaluation metrics
        """
        # Make predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "avg_precision": average_precision_score(y_test, y_proba),
            "confusion_matrix": confusion_matrix(y_test, y_pred),
        }

        return metrics

    def save_model(
        self,
        model: Any,
        model_path: str,
        model_name: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        """
        Save model to disk.

        Args:
            model: Trained model
            model_path: Path to save the model (can be string or Path)
            model_name: Name of the model (optional, for backward compatibility)
            output_dir: Output directory (optional, for backward compatibility)
        """
        # Handle both old (model, model_name, output_dir) and new (model, model_path) signatures
        if output_dir is not None:
            # Old signature: save_model(model, model_name, output_dir)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            final_path = output_path / f"{model_path}.joblib"
        else:
            # New signature: save_model(model, model_path)
            final_path = Path(model_path)
            final_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(model, final_path)
        logger.info(f"Saved model to {final_path}")


def train_fraud_detection_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convenience function to train fraud detection models.

    Args:
        X_train: Training features
        y_train: Training targets
        X_val: Validation features
        y_val: Validation targets
        config: Configuration dictionary

    Returns:
        Dictionary of trained models
    """
    trainer = ModelTrainer(config)
    return trainer.train_all_models(X_train, y_train, X_val, y_val)
