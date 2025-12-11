"""
Feature engineering utilities for fraud detection.

This module provides functions for creating, transforming, and selecting
features that are relevant for fraud detection models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering class for fraud detection pipeline."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize feature engineer.

        Args:
            config: Configuration dictionary containing feature engineering parameters
        """
        self.config = config or {}
        self.features_config = self.config.get("features", {})

        # Feature engineering parameters
        self.lookback_days = self.features_config.get("lookback_days", 30)
        self.min_user_transactions = self.features_config.get("min_user_transactions", 5)

    def _get_user_frequent_value(
        self, df: pd.DataFrame, group_col: str, value_col: str
    ) -> Dict[str, Any]:
        """
        Helper function to get the most frequent value per group.

        This extracts duplicate logic for finding frequent locations, devices, and merchants.

        Args:
            df: Input dataframe
            group_col: Column to group by (e.g., 'user_id')
            value_col: Column to find mode for (e.g., 'location', 'device_id')

        Returns:
            Dictionary mapping group values to their most frequent value

        Example:
            >>> user_locations = _get_user_frequent_value(df, 'user_id', 'location')
            >>> df['frequent_location'] = df['user_id'].map(user_locations)
        """
        return (
            df.groupby(group_col)[value_col]
            .apply(lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0])
            .to_dict()
        )

    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-based features from timestamp column.

        Args:
            df: Input dataframe with timestamp column

        Returns:
            Dataframe with additional temporal features
        """
        logger.info("Creating temporal features")
        df_temp = df.copy()

        if "timestamp" in df_temp.columns:
            # Ensure timestamp is datetime
            df_temp["timestamp"] = pd.to_datetime(df_temp["timestamp"])

            # Basic time features
            df_temp["hour_of_day"] = df_temp["timestamp"].dt.hour
            df_temp["day_of_week"] = df_temp["timestamp"].dt.dayofweek
            df_temp["day_of_month"] = df_temp["timestamp"].dt.day
            df_temp["month"] = df_temp["timestamp"].dt.month
            df_temp["is_weekend"] = (df_temp["day_of_week"] >= 5).astype(int)

            # Time of day categories
            df_temp["time_category"] = pd.cut(
                df_temp["hour_of_day"],
                bins=[-1, 6, 12, 18, 24],
                labels=["night", "morning", "afternoon", "evening"],
            )

            # Business hours (9 AM to 5 PM, weekdays)
            df_temp["is_business_hours"] = (
                (df_temp["hour_of_day"] >= 9)
                & (df_temp["hour_of_day"] <= 17)
                & (df_temp["day_of_week"] < 5)
            ).astype(int)

            # Late night transactions (11 PM to 6 AM)
            df_temp["is_late_night"] = (
                (df_temp["hour_of_day"] >= 23) | (df_temp["hour_of_day"] <= 6)
            ).astype(int)

            logger.info(
                "Created temporal features: hour_of_day, day_of_week, is_weekend, time_category, is_business_hours, is_late_night"
            )

        return df_temp

    def create_amount_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create amount-based features.

        Args:
            df: Input dataframe with amount column

        Returns:
            Dataframe with additional amount features
        """
        logger.info("Creating amount-based features")
        df_amount = df.copy()

        if "amount" in df_amount.columns:
            # Log transformation (helps with skewed distribution)
            df_amount["amount_log"] = np.log1p(df_amount["amount"])

            # Amount categories (based on quartiles)
            try:
                df_amount["amount_category"] = pd.qcut(
                    df_amount["amount"],
                    4,
                    labels=["low", "medium", "high", "very_high"],
                    duplicates="drop",
                )
            except Exception as e:
                logger.warning(
                    f"Could not create amount categories (likely due to low variance or duplicates): {e}. Setting all to 'unknown'."
                )
                df_amount["amount_category"] = "unknown"

            # Round amount (some fraud patterns involve round numbers)
            df_amount["is_round_amount"] = (df_amount["amount"] % 1 == 0).astype(int)
            df_amount["is_round_10"] = (df_amount["amount"] % 10 == 0).astype(int)
            df_amount["is_round_100"] = (df_amount["amount"] % 100 == 0).astype(int)

            logger.info(
                "Created amount features: amount_log, amount_category, round amount indicators"
            )

        return df_amount

    def create_user_behavior_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create user behavior features based on historical transactions.

        Args:
            df: Input dataframe with user_id and transaction data

        Returns:
            Dataframe with user behavior features
        """
        logger.info("Creating user behavior features")
        df_user = df.copy()

        if "user_id" not in df_user.columns:
            logger.warning("user_id column not found, skipping user behavior features")
            return df_user

        # Sort by user and timestamp for sequential analysis
        if "timestamp" in df_user.columns:
            df_user = df_user.sort_values(["user_id", "timestamp"])

        # Check if user features already exist (from data generation)
        existing_user_features = [col for col in df_user.columns if col.startswith("user_")]

        if not existing_user_features:
            # Create user statistics if they don't exist
            user_stats = (
                df_user.groupby("user_id")
                .agg(
                    {
                        "amount": ["count", "mean", "std", "min", "max", "sum"],
                        "merchant_category": "nunique",
                        "device_id": "nunique",
                        "location": "nunique",
                    }
                )
                .round(3)
            )

            # Flatten column names
            user_stats.columns = [
                "user_transaction_count",
                "user_avg_amount",
                "user_std_amount",
                "user_min_amount",
                "user_max_amount",
                "user_total_amount",
                "user_unique_categories",
                "user_unique_devices",
                "user_unique_locations",
            ]

            # Fill NaN values
            user_stats["user_std_amount"] = user_stats["user_std_amount"].fillna(0)

            # Merge back to main dataframe
            df_user = df_user.merge(user_stats, left_on="user_id", right_index=True, how="left")

            logger.info("Created new user statistics")
        else:
            logger.info(f"Using existing user features: {existing_user_features}")

        # Ensure required columns exist
        if "user_avg_amount" not in df_user.columns:
            df_user["user_avg_amount"] = df_user.groupby("user_id")["amount"].transform("mean")
        if "user_std_amount" not in df_user.columns:
            df_user["user_std_amount"] = (
                df_user.groupby("user_id")["amount"].transform("std").fillna(0)
            )
        if "user_max_amount" not in df_user.columns:
            df_user["user_max_amount"] = df_user.groupby("user_id")["amount"].transform("max")

        # Transaction-level user features
        df_user["amount_zscore"] = (df_user["amount"] - df_user["user_avg_amount"]) / (
            df_user["user_std_amount"] + 1.0
        )

        df_user["amount_ratio_to_user_avg"] = df_user["amount"] / (df_user["user_avg_amount"] + 1.0)
        df_user["amount_ratio_to_user_max"] = df_user["amount"] / (df_user["user_max_amount"] + 1.0)

        # Flag unusual amounts for user
        df_user["is_amount_outlier"] = (np.abs(df_user["amount_zscore"]) > 3).astype(int)

        logger.info(
            "Created user behavior features: transaction counts, amount statistics, z-scores, ratios"
        )

        return df_user

    def create_frequency_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create frequency-based features.

        Args:
            df: Input dataframe with timestamp and user data

        Returns:
            Dataframe with frequency features
        """
        logger.info("Creating frequency features")
        df_freq = df.copy()

        if "user_id" not in df_freq.columns or "timestamp" not in df_freq.columns:
            logger.warning("Required columns missing for frequency features")
            return df_freq

        # Sort by user and timestamp
        df_freq = df_freq.sort_values(["user_id", "timestamp"])

        # Time since last transaction (within same user)
        df_freq["time_since_last_transaction"] = (
            df_freq.groupby("user_id")["timestamp"].diff().dt.total_seconds().fillna(0)
        )

        # Convert to hours
        df_freq["hours_since_last_transaction"] = df_freq["time_since_last_transaction"] / 3600

        # Transaction frequency features (transactions per day)
        df_freq["transactions_per_day"] = (
            df_freq["user_transaction_count"] / 30.0
        )  # Assuming 30-day window

        # Quick successive transactions (within 1 hour)
        df_freq["is_quick_transaction"] = (df_freq["hours_since_last_transaction"] <= 1).astype(int)

        # Very quick transactions (within 5 minutes)
        df_freq["is_very_quick_transaction"] = (
            df_freq["time_since_last_transaction"] <= 300
        ).astype(int)

        logger.info("Created frequency features: time since last transaction, transaction rates")

        return df_freq

    def create_location_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create location-based features.

        Args:
            df: Input dataframe with location data

        Returns:
            Dataframe with location features
        """
        logger.info("Creating location features")
        df_loc = df.copy()

        if "location" not in df_loc.columns:
            logger.warning("location column not found")
            return df_loc

        # Most frequent location per user
        if "user_id" in df_loc.columns:
            user_frequent_location = self._get_user_frequent_value(df_loc, "user_id", "location")

            df_loc["user_frequent_location"] = df_loc["user_id"].map(user_frequent_location)
            df_loc["is_usual_location"] = (
                df_loc["location"] == df_loc["user_frequent_location"]
            ).astype(int)

            logger.info("Created location features: usual location indicators")

        return df_loc

    def create_device_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create device-based features.

        Args:
            df: Input dataframe with device data

        Returns:
            Dataframe with device features
        """
        logger.info("Creating device features")
        df_device = df.copy()

        # Device type features
        if "device_type" in df_device.columns:
            # One-hot encode device types
            device_dummies = pd.get_dummies(df_device["device_type"], prefix="device")
            df_device = pd.concat([df_device, device_dummies], axis=1)

        # Device consistency features
        if "user_id" in df_device.columns and "device_id" in df_device.columns:
            # Most frequent device per user
            user_frequent_device = self._get_user_frequent_value(df_device, "user_id", "device_id")

            df_device["user_frequent_device"] = df_device["user_id"].map(user_frequent_device)
            df_device["is_usual_device"] = (
                df_device["device_id"] == df_device["user_frequent_device"]
            ).astype(int)

            logger.info("Created device features: device type encoding, usual device indicators")

        return df_device

    def create_merchant_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create merchant category features.

        Args:
            df: Input dataframe with merchant data

        Returns:
            Dataframe with merchant features
        """
        logger.info("Creating merchant features")
        df_merchant = df.copy()

        if "merchant_category" not in df_merchant.columns:
            logger.warning("merchant_category column not found")
            return df_merchant

        # One-hot encode merchant categories
        merchant_dummies = pd.get_dummies(df_merchant["merchant_category"], prefix="merchant")
        df_merchant = pd.concat([df_merchant, merchant_dummies], axis=1)

        # User's merchant preferences
        if "user_id" in df_merchant.columns:
            # Most frequent merchant category per user
            user_frequent_merchant = self._get_user_frequent_value(
                df_merchant, "user_id", "merchant_category"
            )

            df_merchant["user_frequent_merchant"] = df_merchant["user_id"].map(
                user_frequent_merchant
            )
            df_merchant["is_usual_merchant_category"] = (
                df_merchant["merchant_category"] == df_merchant["user_frequent_merchant"]
            ).astype(int)

            logger.info("Created merchant features: category encoding, usual merchant indicators")

        return df_merchant

    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all engineered features.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with all engineered features
        """
        logger.info("Creating all engineered features")

        # Create features in sequence
        df_features = self.create_temporal_features(df)
        df_features = self.create_amount_features(df_features)
        df_features = self.create_user_behavior_features(df_features)
        df_features = self.create_frequency_features(df_features)
        df_features = self.create_location_features(df_features)
        df_features = self.create_device_features(df_features)
        df_features = self.create_merchant_features(df_features)
        df_features = self._encode_categorical_features(df_features)

        logger.info(f"Feature engineering completed. Final shape: {df_features.shape}")

        return df_features

    def _encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert remaining categorical columns to numeric codes for modeling."""
        encoded_df = df.copy()

        # Drop identifier columns that do not add predictive value and explode encoding time
        drop_columns = [
            "transaction_id",
            "user_id",
            "device_id",
            "timestamp",
            "user_frequent_location",
            "user_frequent_device",
            "user_frequent_merchant",
        ]
        drop_existing = [col for col in drop_columns if col in encoded_df.columns]
        if drop_existing:
            encoded_df = encoded_df.drop(columns=drop_existing)

        categorical_cols = encoded_df.select_dtypes(include=["object", "category"]).columns.tolist()

        if not categorical_cols:
            return encoded_df

        logger.info(
            "Encoding %d categorical features using categorical codes", len(categorical_cols)
        )
        for col in categorical_cols:
            cat_series = encoded_df[col].astype("category")
            # Replace missing categories with -1 and shift to keep non-negative values
            codes = cat_series.cat.codes.replace(-1, np.nan)
            encoded_df[col] = codes.astype(float)

        return encoded_df

    def get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of all engineered feature names.

        Args:
            df: Dataframe with engineered features

        Returns:
            List of feature column names
        """
        # Base features that should not be used for modeling
        exclude_columns = [
            "transaction_id",
            "user_id",
            "timestamp",
            "is_fraud",
            "user_frequent_location",
            "user_frequent_device",
            "user_frequent_merchant",
        ]

        # Get all columns except excluded ones
        feature_columns = [col for col in df.columns if col not in exclude_columns]

        return feature_columns


def create_features(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Convenience function to create all features.

    Args:
        df: Input dataframe
        config: Configuration dictionary

    Returns:
        Dataframe with engineered features
    """
    engineer = FeatureEngineer(config)
    return engineer.create_all_features(df)
