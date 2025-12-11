import pandas as pd
import numpy as np

from src.data_generation import TransactionDataGenerator
from src.features import FeatureEngineer


def test_feature_engineering_produces_numeric_columns():
    gen = TransactionDataGenerator(random_state=123)
    df = gen.generate_dataset(n_samples=200, fraud_rate=0.05, n_days=10)

    fe = FeatureEngineer()
    engineered = fe.create_all_features(df)

    # All non-target columns should be numeric/bool after encoding step
    non_numeric = [
        col
        for col, dtype in engineered.dtypes.items()
        if col != "is_fraud" and dtype.kind not in ("b", "i", "u", "f")
    ]
    assert not non_numeric, f"Found non-numeric engineered columns: {non_numeric}"
