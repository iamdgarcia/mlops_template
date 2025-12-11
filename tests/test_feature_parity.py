"""
Test feature engineering parity across training, notebooks, and serving contexts.

This test suite ensures that the FeatureEngineer class in src/features.py
produces consistent results regardless of where it's called from.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ConfigManager
from src.features import FeatureEngineer, create_features
from src.inference import InferencePipeline, create_sample_transaction


class TestFeatureParity:
    """Test that feature engineering is consistent across all contexts."""

    @pytest.fixture
    def sample_raw_data(self):
        """Create a small sample dataset for testing."""
        np.random.seed(42)
        n_samples = 100

        data = {
            "transaction_id": [f"txn_{i:06d}" for i in range(n_samples)],
            "user_id": [f"user_{i % 20:05d}" for i in range(n_samples)],
            "device_id": [f"device_{i % 30:05d}" for i in range(n_samples)],
            "amount": np.random.lognormal(4, 0.9, n_samples),
            "merchant_category": np.random.choice(
                ["grocery", "gas_station", "restaurant", "retail"], n_samples
            ),
            "transaction_type": np.random.choice(["purchase", "withdrawal", "transfer"], n_samples),
            "location": np.random.choice(
                ["seattle_wa", "portland_or", "san_francisco_ca"], n_samples
            ),
            "device_type": np.random.choice(["mobile", "desktop", "atm"], n_samples),
            "timestamp": pd.date_range("2024-01-01", periods=n_samples, freq="1H"),
            "user_transaction_count": np.random.randint(1, 100, n_samples),
            "user_avg_amount": np.random.uniform(50, 300, n_samples),
            "user_std_amount": np.random.uniform(10, 100, n_samples),
            "user_unique_categories": np.random.randint(1, 5, n_samples),
            "user_unique_devices": np.random.randint(1, 3, n_samples),
            "user_unique_locations": np.random.randint(1, 4, n_samples),
        }

        return pd.DataFrame(data)

    @pytest.fixture
    def feature_engineer(self):
        """Create a FeatureEngineer instance with default config."""
        config_manager = ConfigManager()
        config = config_manager.get_training_config()
        return FeatureEngineer(config)

    def test_feature_engineer_creates_all_features(self, feature_engineer, sample_raw_data):
        """Test that FeatureEngineer.create_all_features produces expected features."""
        result = feature_engineer.create_all_features(sample_raw_data)

        # Should have more columns than input due to feature engineering
        assert result.shape[0] == sample_raw_data.shape[0], "Row count should be preserved"
        assert result.shape[1] > sample_raw_data.shape[1], "Should create additional features"

        # Check for expected feature categories
        expected_temporal_features = [
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "is_business_hours",
        ]
        for feature in expected_temporal_features:
            assert feature in result.columns, f"Missing temporal feature: {feature}"

        expected_amount_features = ["amount_log", "is_round_amount"]
        for feature in expected_amount_features:
            assert feature in result.columns, f"Missing amount feature: {feature}"

        # Check no NaN values in critical features
        assert not result["hour_of_day"].isna().any(), "hour_of_day should not have NaN"
        assert not result["amount_log"].isna().any(), "amount_log should not have NaN"

    def test_convenience_function_matches_class(self, sample_raw_data):
        """Test that create_features() function matches FeatureEngineer class."""
        config_manager = ConfigManager()
        config = config_manager.get_training_config()

        # Use class method
        engineer = FeatureEngineer(config)
        result_class = engineer.create_all_features(sample_raw_data)

        # Use convenience function
        result_function = create_features(sample_raw_data, config)

        # Should produce identical results
        assert result_class.shape == result_function.shape, "Shape should match"
        assert list(result_class.columns) == list(result_function.columns), "Columns should match"

        # Check numerical features are equal (allowing for floating point tolerance)
        numeric_cols = result_class.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            pd.testing.assert_series_equal(
                result_class[col], result_function[col], check_names=True, rtol=1e-5, atol=1e-8
            )

    def test_inference_pipeline_uses_feature_engineer(self, sample_raw_data, tmp_path):
        """Test that InferencePipeline.preprocess_data uses FeatureEngineer."""
        # Create a simple mock model
        from sklearn.ensemble import RandomForestClassifier

        mock_model = RandomForestClassifier(n_estimators=10, random_state=42)

        # Train on some dummy data
        engineer = FeatureEngineer()
        features_df = engineer.create_all_features(sample_raw_data)
        feature_cols = [
            col
            for col in features_df.columns
            if col not in ["transaction_id", "user_id", "timestamp"]
        ]

        X = features_df[feature_cols].fillna(0)
        y = np.random.randint(0, 2, len(X))
        mock_model.fit(X, y)

        # Save model
        import joblib

        model_path = tmp_path / "test_model.joblib"
        joblib.dump(mock_model, model_path)

        # Create inference pipeline
        pipeline = InferencePipeline(model_path=str(model_path))

        # Preprocess should use FeatureEngineer
        preprocessed = pipeline.preprocess_data(sample_raw_data)

        # Should create the same features as direct FeatureEngineer call
        direct_features = engineer.create_all_features(sample_raw_data)

        # The preprocessed output should be a subset of direct features
        assert preprocessed.shape[0] == sample_raw_data.shape[0]
        assert all(col in direct_features.columns for col in preprocessed.columns)

    def test_feature_names_consistency(self, feature_engineer, sample_raw_data):
        """Test that get_feature_names returns consistent results."""
        features_df = feature_engineer.create_all_features(sample_raw_data)
        feature_names = feature_engineer.get_feature_names(features_df)

        # Should exclude identifier columns
        excluded = ["transaction_id", "user_id", "timestamp", "is_fraud"]
        for col in excluded:
            if col in features_df.columns:
                assert col not in feature_names, f"{col} should be excluded from feature names"

        # All returned features should exist in the dataframe
        for feature in feature_names:
            assert feature in features_df.columns, f"Feature {feature} not in dataframe"

    def test_temporal_features_are_deterministic(self, feature_engineer):
        """Test that temporal features are computed consistently."""
        # Create two identical dataframes
        data = pd.DataFrame(
            {
                "transaction_id": ["txn_001", "txn_002"],
                "timestamp": pd.to_datetime(["2024-01-15 14:30:00", "2024-01-16 09:15:00"]),
                "amount": [100.0, 50.0],
                "user_id": ["user_001", "user_002"],
                "device_id": ["device_001", "device_002"],
                "merchant_category": ["grocery", "gas_station"],
                "transaction_type": ["purchase", "purchase"],
                "location": ["seattle_wa", "portland_or"],
                "device_type": ["mobile", "desktop"],
            }
        )

        result1 = feature_engineer.create_temporal_features(data.copy())
        result2 = feature_engineer.create_temporal_features(data.copy())

        # Should produce identical results
        temporal_cols = ["hour_of_day", "day_of_week", "is_weekend", "is_business_hours"]
        for col in temporal_cols:
            pd.testing.assert_series_equal(result1[col], result2[col])

    def test_amount_features_handle_edge_cases(self, feature_engineer):
        """Test that amount features handle edge cases correctly."""
        # Test with edge case amounts
        data = pd.DataFrame(
            {
                "amount": [0.01, 10.00, 100.00, 1000.00, 0.99],
                "transaction_id": [f"txn_{i}" for i in range(5)],
                "user_id": ["user_001"] * 5,
            }
        )

        result = feature_engineer.create_amount_features(data)

        # Check round amount detection
        assert result["is_round_amount"].iloc[1] == 1, "10.00 should be round"
        assert result["is_round_10"].iloc[1] == 1, "10.00 should be round to 10"
        assert result["is_round_100"].iloc[2] == 1, "100.00 should be round to 100"

        # Check log transformation doesn't produce inf
        assert not np.isinf(result["amount_log"]).any(), "amount_log should not have inf"

    def test_user_behavior_features_aggregate_correctly(self, feature_engineer):
        """Test that user behavior features compute correct aggregations."""
        # Create data with known user patterns
        data = pd.DataFrame(
            {
                "user_id": ["user_001", "user_001", "user_002", "user_002"],
                "amount": [100.0, 200.0, 50.0, 50.0],
                "transaction_id": [f"txn_{i}" for i in range(4)],
                "device_id": [f"device_{i}" for i in range(4)],
                "merchant_category": ["grocery", "grocery", "gas_station", "retail"],
                "location": ["seattle_wa", "seattle_wa", "portland_or", "portland_or"],
            }
        )

        result = feature_engineer.create_user_behavior_features(data)

        # Check user_001 statistics
        user_001_rows = result[result["user_id"] == "user_001"]
        if "user_avg_amount" in user_001_rows.columns:
            # If user stats were created (not pre-existing)
            avg_amount = user_001_rows["user_avg_amount"].iloc[0]
            assert abs(avg_amount - 150.0) < 0.01, f"user_001 avg should be 150, got {avg_amount}"

    def test_categorical_encoding_is_consistent(self, feature_engineer, sample_raw_data):
        """Test that categorical encoding produces consistent results."""
        result1 = feature_engineer.create_all_features(sample_raw_data.copy())
        result2 = feature_engineer.create_all_features(sample_raw_data.copy())

        # Encoded categorical columns should be identical
        cat_cols = sample_raw_data.select_dtypes(include=["object"]).columns
        for col in cat_cols:
            if col in result1.columns and col in result2.columns:
                pd.testing.assert_series_equal(result1[col], result2[col], check_names=True)

    def test_feature_store_compatibility(self, feature_engineer, sample_raw_data, tmp_path):
        """Test that features are compatible with saved feature store."""
        # Create features
        features_df = feature_engineer.create_all_features(sample_raw_data)
        feature_names = feature_engineer.get_feature_names(features_df)

        # Save feature metadata (simulating what notebooks do)
        feature_metadata = {
            "features": feature_names,
            "feature_count": len(feature_names),
            "timestamp": "2024-01-01T00:00:00",
        }

        feature_store_path = tmp_path / "selected_features.json"
        with open(feature_store_path, "w") as f:
            json.dump(feature_metadata, f)

        # Load with InferencePipeline (which reads feature store)
        from src.inference import _load_feature_store

        loaded_features = _load_feature_store(feature_store_path)

        # Should load the same features
        assert len(loaded_features) == len(feature_names)
        assert set(loaded_features) == set(feature_names)

    def test_serving_api_sample_transaction(self):
        """Test that create_sample_transaction works with feature engineering."""
        sample = create_sample_transaction()

        # Should have required fields
        required_fields = [
            "amount",
            "merchant_category",
            "transaction_type",
            "location",
            "device_type",
            "hour_of_day",
            "day_of_week",
        ]
        for field in required_fields:
            assert field in sample, f"Missing required field: {field}"

        # Convert to DataFrame and apply feature engineering
        df = pd.DataFrame([sample])
        engineer = FeatureEngineer()
        result = engineer.create_all_features(df)

        # Should successfully create features
        assert len(result) == 1
        assert result.shape[1] > len(sample)


class TestFeatureEngineeringEdgeCases:
    """Test edge cases and error handling in feature engineering."""

    def test_empty_dataframe_handling(self):
        """Test that feature engineering handles empty dataframes gracefully."""
        engineer = FeatureEngineer()
        empty_df = pd.DataFrame()

        # Should handle empty dataframe without crashing
        result = engineer.create_temporal_features(empty_df)
        assert len(result) == 0

    def test_missing_columns_handling(self):
        """Test that feature engineering handles missing columns gracefully."""
        engineer = FeatureEngineer()

        # Dataframe without timestamp
        df = pd.DataFrame({"amount": [100.0, 200.0], "user_id": ["user_001", "user_002"]})

        # Should not crash, just skip temporal features
        result = engineer.create_temporal_features(df)
        assert "hour_of_day" not in result.columns

    def test_single_row_dataframe(self):
        """Test that feature engineering works with single-row dataframes."""
        engineer = FeatureEngineer()

        single_row = pd.DataFrame(
            {
                "transaction_id": ["txn_001"],
                "user_id": ["user_001"],
                "device_id": ["device_001"],
                "amount": [100.0],
                "timestamp": pd.to_datetime(["2024-01-15 14:30:00"]),
                "merchant_category": ["grocery"],
                "transaction_type": ["purchase"],
                "location": ["seattle_wa"],
                "device_type": ["mobile"],
            }
        )

        result = engineer.create_all_features(single_row)

        # Should successfully process single row
        assert len(result) == 1
        assert result.shape[1] > single_row.shape[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
