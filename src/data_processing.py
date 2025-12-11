"""
Data processing utilities for fraud detection pipeline.

This module provides functions for data validation, cleaning, preprocessing,
and splitting for machine learning workflows.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class DataProcessor:
    """Main data processing class for fraud detection pipeline."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data processor with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_config = config.get("data", {})
        self.features_config = config.get("features", {})

        # Initialize preprocessors
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate input data quality and schema.

        Args:
            df: Input dataframe to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check required columns
        required_columns = [
            "transaction_id",
            "user_id",
            "timestamp",
            "amount",
            "merchant_category",
            "transaction_type",
            "is_fraud",
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")

        # Check data types
        if "amount" in df.columns:
            if not pd.api.types.is_numeric_dtype(df["amount"]):
                issues.append("Amount column should be numeric")
            elif (df["amount"] <= 0).any():
                issues.append("Amount column contains non-positive values")

        # Check for duplicates
        if "transaction_id" in df.columns:
            if df["transaction_id"].duplicated().any():
                issues.append("Duplicate transaction IDs found")

        # Check fraud labels
        if "is_fraud" in df.columns:
            fraud_values = df["is_fraud"].unique()
            if not set(fraud_values).issubset({0, 1, True, False}):
                issues.append("Invalid fraud labels - should be boolean or 0/1")

        # Check for excessive missing values
        missing_threshold = 0.5  # 50%
        high_missing_cols = []
        for col in df.columns:
            missing_rate = df[col].isnull().sum() / len(df)
            if missing_rate > missing_threshold:
                high_missing_cols.append(f"{col} ({missing_rate:.1%})")

        if high_missing_cols:
            issues.append(f"Columns with high missing values: {high_missing_cols}")

        # Check timestamp format
        if "timestamp" in df.columns:
            try:
                pd.to_datetime(df["timestamp"])
            except Exception:
                issues.append("Invalid timestamp format")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.warning(f"Data validation failed with {len(issues)} issues")
            for issue in issues:
                logger.warning(f"  - {issue}")

        return is_valid, issues

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the data.

        Args:
            df: Input dataframe

        Returns:
            Cleaned dataframe
        """
        logger.info("Starting data cleaning")
        df_clean = df.copy()

        # Convert timestamp to datetime
        if "timestamp" in df_clean.columns:
            df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"])

        # Handle missing values
        df_clean = self._handle_missing_values(df_clean)

        # Remove duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=["transaction_id"], keep="first")
        duplicates_removed = initial_len - len(df_clean)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate transactions")

        # Clean amount values
        if "amount" in df_clean.columns:
            # Remove negative amounts
            negative_amounts = (df_clean["amount"] <= 0).sum()
            if negative_amounts > 0:
                logger.info(f"Removing {negative_amounts} transactions with non-positive amounts")
                df_clean = df_clean[df_clean["amount"] > 0]

            # Handle outliers (amounts > 99.9th percentile)
            amount_threshold = df_clean["amount"].quantile(0.999)
            outliers = (df_clean["amount"] > amount_threshold).sum()
            if outliers > 0:
                logger.info(f"Capping {outliers} amount outliers at ${amount_threshold:.2f}")
                df_clean.loc[df_clean["amount"] > amount_threshold, "amount"] = amount_threshold

        # Standardize categorical values
        df_clean = self._standardize_categorical_values(df_clean)

        logger.info(f"Data cleaning completed. Shape: {df_clean.shape}")
        return df_clean

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        df_clean = df.copy()

        # For categorical columns, fill with 'unknown'
        categorical_columns = ["merchant_category", "transaction_type", "device_type", "location"]
        for col in categorical_columns:
            if col in df_clean.columns:
                missing_count = df_clean[col].isnull().sum()
                if missing_count > 0:
                    logger.info(f"Filling {missing_count} missing values in {col} with 'unknown'")
                    df_clean[col] = df_clean[col].fillna("unknown")

        # For numerical columns, fill with median
        numerical_columns = ["amount", "hour_of_day", "day_of_week"]
        for col in numerical_columns:
            if col in df_clean.columns:
                missing_count = df_clean[col].isnull().sum()
                if missing_count > 0:
                    median_val = df_clean[col].median()
                    logger.info(
                        f"Filling {missing_count} missing values in {col} with median: {median_val}"
                    )
                    df_clean[col] = df_clean[col].fillna(median_val)

        return df_clean

    def _standardize_categorical_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize categorical column values."""
        df_clean = df.copy()

        # Standardize merchant categories
        if "merchant_category" in df_clean.columns:
            # Convert to lowercase and strip whitespace
            df_clean["merchant_category"] = (
                df_clean["merchant_category"]
                .astype(str)
                .str.lower()
                .str.strip()
                .str.replace("[^a-z0-9_]", "_", regex=True)
            )

        # Standardize transaction types
        if "transaction_type" in df_clean.columns:
            df_clean["transaction_type"] = (
                df_clean["transaction_type"].astype(str).str.lower().str.strip()
            )

        # Ensure boolean fraud labels
        if "is_fraud" in df_clean.columns:
            df_clean["is_fraud"] = df_clean["is_fraud"].astype(bool)

        return df_clean

    def split_data(
        self,
        df: pd.DataFrame,
        test_size: Optional[float] = None,
        validation_size: Optional[float] = None,
        stratify_column: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, ...]:
        """
        Split data into train/validation/test sets.

        Args:
            df: Input dataframe
            test_size: Proportion for test set
            validation_size: Proportion for validation set
            stratify_column: Column to stratify on

        Returns:
            Tuple of (train_df, val_df, test_df) or (train_df, test_df)
        """
        # Get split parameters from config if not provided
        if test_size is None:
            test_size = self.data_config.get("test_size", 0.2)
        if validation_size is None:
            validation_size = self.data_config.get("validation_size", 0.0)
        if stratify_column is None:
            stratify_column = self.features_config.get("target_column", "is_fraud")

        # Prepare stratification
        stratify_data = df[stratify_column] if stratify_column in df.columns else None

        # First split: separate test set
        if validation_size and validation_size > 0:
            # Three-way split
            train_val_df, test_df = train_test_split(
                df,
                test_size=test_size,
                stratify=stratify_data,
                random_state=self.data_config.get("random_state", 42),
            )

            # Calculate validation size relative to train+val
            val_size_adjusted = validation_size / (1 - test_size)
            stratify_train_val = (
                train_val_df[stratify_column] if stratify_column in train_val_df.columns else None
            )

            train_df, val_df = train_test_split(
                train_val_df,
                test_size=val_size_adjusted,
                stratify=stratify_train_val,
                random_state=self.data_config.get("random_state", 42),
            )

            logger.info(
                f"Data split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}"
            )
            return train_df, val_df, test_df

        else:
            # Two-way split
            train_df, test_df = train_test_split(
                df,
                test_size=test_size,
                stratify=stratify_data,
                random_state=self.data_config.get("random_state", 42),
            )

            logger.info(f"Data split - Train: {len(train_df)}, Test: {len(test_df)}")
            return train_df, test_df

    def get_feature_target_split(
        self, df: pd.DataFrame, target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Split dataframe into features and target.

        Args:
            df: Input dataframe
            target_column: Target column name

        Returns:
            Tuple of (features_df, target_series)
        """
        if target_column is None:
            target_column = self.features_config.get("target_column", "is_fraud")

        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataframe")

        # Get feature columns
        feature_columns = self._get_feature_columns(df, target_column)

        X = df[feature_columns].copy()
        y = df[target_column].copy()

        logger.info(f"Features: {len(feature_columns)} columns, Target: {target_column}")
        return X, y

    def _get_feature_columns(self, df: pd.DataFrame, target_column: str) -> List[str]:
        """Get the list of feature columns."""
        # Exclude non-feature columns
        exclude_columns = {"transaction_id", "user_id", "timestamp", target_column}

        # Add any additional columns to exclude from config
        exclude_columns.update(self.features_config.get("exclude_columns", []))

        feature_columns = [col for col in df.columns if col not in exclude_columns]

        return feature_columns

    def save_processed_data(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Save processed datasets to files.

        Args:
            train_df: Training dataframe
            test_df: Test dataframe
            val_df: Optional validation dataframe
            output_dir: Output directory path

        Returns:
            Dictionary of saved file paths
        """
        if output_dir is None:
            output_dir = self.data_config.get("processed_data_path", "data/processed/")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # Save training data
        train_path = output_path / "train.csv"
        train_df.to_csv(train_path, index=False)
        saved_files["train"] = str(train_path)
        logger.info(f"Saved training data: {train_path}")

        # Save test data
        test_path = output_path / "test.csv"
        test_df.to_csv(test_path, index=False)
        saved_files["test"] = str(test_path)
        logger.info(f"Saved test data: {test_path}")

        # Save validation data if provided
        if val_df is not None:
            val_path = output_path / "validation.csv"
            val_df.to_csv(val_path, index=False)
            saved_files["validation"] = str(val_path)
            logger.info(f"Saved validation data: {val_path}")

        return saved_files

    def load_processed_data(self, input_dir: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Load processed datasets from files.

        Args:
            input_dir: Input directory path

        Returns:
            Dictionary of loaded dataframes
        """
        if input_dir is None:
            input_dir = self.data_config.get("processed_data_path", "data/processed/")

        input_path = Path(input_dir)
        loaded_data = {}

        # Load available datasets
        for dataset_name in ["train", "test", "validation"]:
            file_path = input_path / f"{dataset_name}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path)
                loaded_data[dataset_name] = df
                logger.info(f"Loaded {dataset_name} data: {file_path} ({len(df)} rows)")

        return loaded_data


def process_data(
    config: Dict[str, Any], input_data: Optional[pd.DataFrame] = None
) -> Dict[str, pd.DataFrame]:
    """
    Main data processing function.

    Args:
        config: Configuration dictionary
        input_data: Optional input dataframe (if not provided, will load from config)

    Returns:
        Dictionary of processed datasets
    """
    processor = DataProcessor(config)

    # Load data if not provided
    if input_data is None:
        raw_data_path = config["data"]["raw_data_path"]
        if not Path(raw_data_path).exists():
            raise FileNotFoundError(f"Raw data file not found: {raw_data_path}")
        input_data = pd.read_csv(raw_data_path)
        logger.info(f"Loaded raw data: {raw_data_path} ({len(input_data)} rows)")

    # Validate data
    is_valid, issues = processor.validate_data(input_data)
    if not is_valid:
        logger.error("Data validation failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        raise ValueError("Data validation failed. Please fix the issues and try again.")

    # Clean data
    clean_data = processor.clean_data(input_data)

    # Split data
    validation_size = config["data"].get("validation_size", 0.0)
    if validation_size > 0:
        train_df, val_df, test_df = processor.split_data(clean_data)
        datasets = {"train": train_df, "validation": val_df, "test": test_df}
    else:
        train_df, test_df = processor.split_data(clean_data)
        datasets = {"train": train_df, "test": test_df}

    # Save processed data
    if "validation" in datasets:
        processor.save_processed_data(
            train_df=datasets["train"], test_df=datasets["test"], val_df=datasets["validation"]
        )
    else:
        processor.save_processed_data(train_df=datasets["train"], test_df=datasets["test"])

    logger.info("Data processing completed successfully")
    return datasets
