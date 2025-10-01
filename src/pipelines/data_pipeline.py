"""Orchestrated data preparation pipeline for the fraud detection project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from ..config import ConfigManager
from ..data_generation import TransactionDataGenerator
from ..data_processing import DataProcessor
from ..features import FeatureEngineer


def _ensure_parent(path: Path) -> None:
    """Create parent directories for a path if they do not yet exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def load_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load training configuration when it is not provided explicitly."""
    if config is not None:
        return config

    manager = ConfigManager()
    return manager.get_training_config()


def generate_raw_data(config: Dict[str, Any], force: bool = False) -> pd.DataFrame:
    """Generate or load the raw transaction dataset."""
    data_cfg = config.get("data", {})
    raw_path = Path(data_cfg.get("raw_data_path", "data/raw/transactions.csv"))
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    if raw_path.exists() and not force:
        df = pd.read_csv(raw_path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    generator = TransactionDataGenerator(random_state=data_cfg.get("random_state", 42))
    dataset = generator.generate_dataset(
        n_samples=data_cfg.get("n_samples", 100_000),
        fraud_rate=data_cfg.get("fraud_rate", 0.02),
        n_days=data_cfg.get("n_days", 90),
    )
    dataset.to_csv(raw_path, index=False)
    return dataset


def run_data_preparation(
    config: Optional[Dict[str, Any]] = None,
    *,
    regenerate_data: bool = False,
    persist: bool = True,
) -> Dict[str, Any]:
    """Execute the full data preparation workflow."""

    cfg = load_config(config)
    data_processor = DataProcessor(cfg)
    feature_engineer = FeatureEngineer(cfg)

    raw_df = generate_raw_data(cfg, force=regenerate_data)

    is_valid, issues = data_processor.validate_data(raw_df)
    if not is_valid:
        issue_list = "\n".join(f"- {issue}" for issue in issues)
        raise ValueError(f"Raw data validation failed:\n{issue_list}")

    cleaned_df = data_processor.clean_data(raw_df)

    features_df = feature_engineer.create_all_features(cleaned_df)
    feature_list = list(feature_engineer.get_feature_names(features_df))
    target_column = cfg.get("features", {}).get("target_column", "is_fraud")

    splits = data_processor.split_data(features_df)

    if len(splits) == 3:
        split_names = ["train", "validation", "test"]
    elif len(splits) == 2:
        split_names = ["train", "test"]
    else:
        raise ValueError("Unexpected number of splits returned from data_processor")

    split_payload: Dict[str, Tuple[pd.DataFrame, pd.Series]] = {}
    for name, split_df in zip(split_names, splits):
        X_split = split_df[feature_list]
        y_split = split_df[target_column]
        split_payload[name] = (X_split, y_split)

    if persist:
        _persist_outputs(cfg, cleaned_df, splits, feature_list)

    return {
        "raw": raw_df,
        "clean": cleaned_df,
        "features": features_df,
        "feature_names": feature_list,
        "splits": split_payload,
    }


def _persist_outputs(
    config: Dict[str, Any],
    cleaned_df: pd.DataFrame,
    splits: Tuple[pd.DataFrame, ...],
    feature_names: Any,
) -> None:
    """Persist intermediate artefacts expected by downstream steps."""
    data_cfg = config.get("data", {})
    processed_dir = Path(data_cfg.get("processed_data_path", "data/processed"))
    processed_dir.mkdir(parents=True, exist_ok=True)

    train_df, *rest = splits
    if len(rest) == 2:
        val_df, test_df = rest
    elif len(rest) == 1:
        val_df = None
        test_df = rest[0]
    else:
        val_df = None
        test_df = None

    data_processor = DataProcessor(config)
    data_processor.save_processed_data(train_df, test_df, val_df, str(processed_dir))

    clean_path = processed_dir / "cleaned_full_dataset.csv"
    cleaned_df.to_csv(clean_path, index=False)

    feature_metadata_path = Path("data/selected_features.json")
    _ensure_parent(feature_metadata_path)
    feature_metadata = {
        "selected_features": list(feature_names),
        "created_at": pd.Timestamp.utcnow().isoformat(),
    }
    feature_metadata_path.write_text(json.dumps(feature_metadata, indent=2))

