"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.config import ConfigManager


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory with sample configs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Create sample training config with all required sections
        training_config = {
            "data": {
                "raw_data_path": "data/raw/transactions.csv",
                "processed_data_path": "data/transactions_processed.csv",
                "test_size": 0.2,
            },
            "features": {"selected_features": ["amount", "merchant_id"]},
            "models": {
                "random_forest": {"enabled": True, "n_estimators": 100},
                "logistic_regression": {"enabled": False},
            },
            "mlflow": {"tracking_uri": "sqlite:///mlruns.db", "experiment_name": "test"},
        }

        # Create sample serving config with all required sections
        serving_config = {
            "api": {"host": "0.0.0.0", "port": 8000, "reload": False},
            "model": {"path": "models/random_forest_final_model.joblib"},
            "prediction": {"fraud_threshold": 0.5, "batch_size": 100},
        }

        # Write configs
        with open(config_dir / "training_config.yaml", "w") as f:
            yaml.dump(training_config, f)

        with open(config_dir / "serving_config.yaml", "w") as f:
            yaml.dump(serving_config, f)

        yield config_dir


class TestConfigManager:
    """Test ConfigManager class."""

    def test_initialization(self, temp_config_dir):
        """Test ConfigManager initialization."""
        manager = ConfigManager(config_dir=str(temp_config_dir))
        assert manager.config_dir == temp_config_dir

    def test_load_config(self, temp_config_dir):
        """Test loading a configuration file."""
        manager = ConfigManager(config_dir=str(temp_config_dir))
        config = manager.load_config("training_config")

        assert "data" in config
        assert "features" in config
        assert "models" in config
        assert config["models"]["random_forest"]["enabled"] is True

    def test_load_config_caching(self, temp_config_dir):
        """Test that configs are cached."""
        manager = ConfigManager(config_dir=str(temp_config_dir))

        # Load twice
        config1 = manager.load_config("training_config")
        config2 = manager.load_config("training_config")

        # Should be the same object (cached)
        assert config1 is config2

    def test_load_nonexistent_config(self, temp_config_dir):
        """Test loading a non-existent config raises error."""
        manager = ConfigManager(config_dir=str(temp_config_dir))

        with pytest.raises(FileNotFoundError):
            manager.load_config("nonexistent_config")

    def test_get_training_config(self, temp_config_dir):
        """Test get_training_config helper."""
        manager = ConfigManager(config_dir=str(temp_config_dir))
        config = manager.get_training_config()

        assert "data" in config
        assert "features" in config

    def test_get_serving_config(self, temp_config_dir):
        """Test get_serving_config helper."""
        manager = ConfigManager(config_dir=str(temp_config_dir))
        config = manager.get_serving_config()

        assert "api" in config
        assert "model" in config
        assert "prediction" in config

    def test_get_config_value(self, temp_config_dir):
        """Test retrieving nested config values."""
        manager = ConfigManager(config_dir=str(temp_config_dir))
        config = manager.load_config("training_config")

        # Test nested access
        assert config["models"]["random_forest"]["enabled"] is True
        assert config["data"]["test_size"] == 0.2

    def test_invalid_yaml(self, temp_config_dir):
        """Test handling of invalid YAML."""
        # Create invalid YAML file
        invalid_yaml_path = temp_config_dir / "invalid_config.yaml"
        with open(invalid_yaml_path, "w") as f:
            f.write("invalid: yaml: content: [[[")

        manager = ConfigManager(config_dir=str(temp_config_dir))

        with pytest.raises(yaml.YAMLError):
            manager.load_config("invalid_config")
