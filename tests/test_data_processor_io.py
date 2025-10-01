from pathlib import Path

import pandas as pd

from src.config import ConfigManager
from src.data_generation import TransactionDataGenerator
from src.data_processing import DataProcessor


def test_data_processor_split_and_io(tmp_path: Path):
    cfg = {
        "data": {
            "raw_data_path": str(tmp_path / "raw.csv"),
            "processed_data_path": str(tmp_path / "processed"),
            "test_size": 0.2,
            "validation_size": 0.2,
            "random_state": 42,
        },
        "features": {"target_column": "is_fraud"},
    }

    gen = TransactionDataGenerator(random_state=42)
    df = gen.generate_dataset(n_samples=300, fraud_rate=0.05, n_days=7)
    df.to_csv(cfg["data"]["raw_data_path"], index=False)

    proc = DataProcessor(cfg)
    clean = proc.clean_data(df)
    train, val, test = proc.split_data(clean)

    paths = proc.save_processed_data(train, test, val_df=val, output_dir=cfg["data"]["processed_data_path"])
    assert Path(paths["train"]).exists()
    assert Path(paths["test"]).exists()
    assert Path(paths["validation"]).exists()

    loaded = proc.load_processed_data(cfg["data"]["processed_data_path"])
    assert set(loaded.keys()) >= {"train", "test", "validation"}
    assert len(loaded["train"]) + len(loaded["validation"]) + len(loaded["test"]) == len(clean)

