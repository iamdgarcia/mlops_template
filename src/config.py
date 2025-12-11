"""
Configuration management utilities for the fraud detection system.

This module provides utilities for loading and validating configuration
files used throughout the MLOps pipeline.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Configuration manager for loading and validating YAML configurations."""

    def __init__(self, config_dir: str = "configs"):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        base_dir = Path(__file__).resolve().parents[1]
        cfg_path = Path(config_dir)
        if not cfg_path.is_absolute():
            cfg_path = base_dir / cfg_path

        self.config_dir = cfg_path
        self._configs = {}

    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file.

        Args:
            config_name: Name of the configuration file (without .yaml extension)

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        if config_name in self._configs:
            return self._configs[config_name]

        config_path = self.config_dir / f"{config_name}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

            # Validate configuration
            self._validate_config(config_name, config)

            # Cache configuration
            self._configs[config_name] = config

            logger.info(f"Loaded configuration: {config_name}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration {config_name}: {e}")
            raise

    def get_training_config(self) -> Dict[str, Any]:
        """Load training configuration."""
        return self.load_config("training_config")

    def get_serving_config(self) -> Dict[str, Any]:
        """Load serving configuration."""
        return self.load_config("serving_config")

    def _validate_config(self, config_name: str, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure and values.

        Args:
            config_name: Name of the configuration
            config: Configuration dictionary to validate

        Raises:
            ValueError: If validation fails
        """
        if config_name == "training_config":
            self._validate_training_config(config)
        elif config_name == "serving_config":
            self._validate_serving_config(config)

    def _validate_training_config(self, config: Dict[str, Any]) -> None:
        """Validate training configuration."""
        required_sections = ["data", "features", "models", "mlflow"]

        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section in training config: {section}")

        # Validate data section
        data_config = config["data"]
        if "test_size" in data_config:
            test_size = data_config["test_size"]
            if not 0 < test_size < 1:
                raise ValueError(f"test_size must be between 0 and 1, got: {test_size}")

        # Validate models section
        models_config = config["models"]
        if not any(
            isinstance(model, dict) and model.get("enabled", False)
            for model in models_config.values()
        ):
            raise ValueError("At least one model must be enabled in training config")

    def _validate_serving_config(self, config: Dict[str, Any]) -> None:
        """Validate serving configuration."""
        required_sections = ["api", "model", "prediction"]

        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section in serving config: {section}")

        # Validate API configuration
        api_config = config["api"]
        if "port" in api_config:
            port = api_config["port"]
            if not 1024 <= port <= 65535:
                raise ValueError(f"API port must be between 1024 and 65535, got: {port}")

        # Validate prediction thresholds
        prediction_config = config["prediction"]
        if "fraud_threshold" in prediction_config:
            threshold = prediction_config["fraud_threshold"]
            if not 0 <= threshold <= 1:
                raise ValueError(f"fraud_threshold must be between 0 and 1, got: {threshold}")

    def update_config(self, config_name: str, updates: Dict[str, Any]) -> None:
        """
        Update configuration values.

        Args:
            config_name: Name of the configuration to update
            updates: Dictionary of updates to apply
        """
        config = self.load_config(config_name)
        config.update(updates)
        self._configs[config_name] = config
        logger.info(f"Updated configuration: {config_name}")

    def save_config(self, config_name: str, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config_name: Name of the configuration file
            config: Configuration dictionary to save
        """
        config_path = self.config_dir / f"{config_name}.yaml"

        try:
            with open(config_path, "w", encoding="utf-8") as file:
                yaml.safe_dump(config, file, default_flow_style=False, indent=2)

            logger.info(f"Saved configuration: {config_name}")

        except Exception as e:
            logger.error(f"Error saving configuration {config_name}: {e}")
            raise


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging based on configuration.

    Args:
        config: Configuration dictionary containing logging settings
    """
    logging_config = config.get("logging", {})

    level = logging_config.get("level", "INFO")
    format_str = logging_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_file = logging_config.get("file")

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_str))
    handlers.append(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_str))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()), format=format_str, handlers=handlers, force=True
    )


def get_config_manager() -> ConfigManager:
    """Get a global configuration manager instance."""
    return ConfigManager()


# Global configuration manager instance
config_manager = get_config_manager()
