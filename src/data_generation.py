"""
Simplified synthetic data generation for fraud detection training.

This module creates realistic synthetic transaction data with configurable
fraud patterns for training and testing fraud detection models.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TransactionDataGenerator:
    """Generator for synthetic financial transaction data with fraud patterns."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the data generator.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Merchant categories based on real payment data
        self.merchant_categories = [
            "grocery", "gas_station", "restaurant", "retail", "online",
            "pharmacy", "entertainment", "travel", "utilities", "healthcare"
        ]
        
        # Transaction types
        self.transaction_types = [
            "purchase", "withdrawal", "transfer", "payment", "refund"
        ]
        
        # Device types
        self.device_types = [
            "mobile", "desktop", "tablet", "pos_terminal", "atm"
        ]
        
        # Geographic locations (simplified)
        self.locations = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix"
        ]
    
    def generate_dataset(
        self,
        n_samples: int = 100000,
        fraud_rate: float = 0.02,
        n_days: int = 90
    ) -> pd.DataFrame:
        """
        Generate complete synthetic dataset.
        
        Args:
            n_samples: Number of transactions to generate
            fraud_rate: Fraction of fraudulent transactions
            n_days: Number of days of transaction history
            
        Returns:
            Complete dataset with transactions and features
        """
        logger.info(f"Generating {n_samples} synthetic transactions with {fraud_rate:.1%} fraud rate")
        
        # Generate base transaction data
        transactions = []
        start_date = datetime.now() - timedelta(days=n_days)
        
        # Estimate number of users (average 10 transactions per user)
        n_users = max(1000, n_samples // 10)
        
        for i in range(n_samples):
            # Generate timestamp within the date range
            days_offset = np.random.randint(0, n_days)
            hour = np.random.randint(6, 23)  # Active hours
            minute = np.random.randint(0, 60)
            timestamp = start_date + timedelta(days=days_offset, hours=hour, minutes=minute)
            
            # Generate user ID
            user_id = f"user_{np.random.randint(1, n_users + 1):06d}"
            
            # Generate transaction amount (log-normal distribution)
            amount = np.random.lognormal(mean=3.5, sigma=1.2)
            amount = max(1.0, min(amount, 10000.0))  # Clamp between $1 and $10,000
            
            # Select merchant category
            merchant_category = np.random.choice(self.merchant_categories)
            
            # Select transaction type
            transaction_type = np.random.choice(
                self.transaction_types, 
                p=[0.7, 0.1, 0.1, 0.08, 0.02]  # Most are purchases
            )
            
            # Generate device ID (users tend to use same devices)
            device_num = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
            device_id = f"device_{user_id}_{device_num}"
            
            # Select device type
            device_type = np.random.choice(
                self.device_types,
                p=[0.4, 0.3, 0.1, 0.15, 0.05]  # Mobile and desktop most common
            )
            
            # Select location
            location = np.random.choice(self.locations)
            
            transaction = {
                "transaction_id": f"txn_{i+1:08d}",
                "user_id": user_id,
                "timestamp": timestamp,
                "amount": round(amount, 2),
                "merchant_category": merchant_category,
                "transaction_type": transaction_type,
                "device_id": device_id,
                "device_type": device_type,
                "location": location,
                "hour_of_day": hour,
                "day_of_week": timestamp.weekday(),
                "is_weekend": timestamp.weekday() >= 5
            }
            
            transactions.append(transaction)
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Generate fraud labels
        df = self._assign_fraud_labels(df, fraud_rate)
        
        # Add user behavior features
        df = self._add_user_features(df)
        
        logger.info(f"Generated dataset with {len(df)} transactions")
        logger.info(f"Actual fraud rate: {df['is_fraud'].mean():.3f}")
        
        return df.sort_values("timestamp").reset_index(drop=True)
    
    def _assign_fraud_labels(self, df: pd.DataFrame, fraud_rate: float) -> pd.DataFrame:
        """Assign fraud labels to transactions."""
        n_fraud = int(len(df) * fraud_rate)
        
        # Initialize all as non-fraud
        df["is_fraud"] = False
        
        # Select random transactions to be fraudulent
        fraud_indices = np.random.choice(len(df), n_fraud, replace=False)
        
        # Mark selected transactions as fraud using boolean indexing
        df["is_fraud"] = df.index.isin(fraud_indices)
        
        # Modify fraudulent transactions to have suspicious patterns
        fraud_mask = df["is_fraud"] == True
        
        if fraud_mask.any():
            # Fraudulent transactions tend to be higher amounts
            df.loc[fraud_mask, "amount"] *= np.random.uniform(1.5, 3.0, size=fraud_mask.sum())
            
            # Fraudulent transactions more likely at odd hours
            odd_hours = np.random.choice([1, 2, 3, 4, 5, 23], size=fraud_mask.sum())
            df.loc[fraud_mask, "hour_of_day"] = odd_hours
        
        return df
    
    def _add_user_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add user behavior features."""
        # Calculate user statistics
        user_stats = df.groupby("user_id").agg({
            "amount": ["count", "mean", "std"],
            "merchant_category": "nunique",
            "device_id": "nunique",
            "location": "nunique"
        })
        
        # Flatten column names
        user_stats.columns = [
            "user_transaction_count", "user_avg_amount", "user_std_amount",
            "user_unique_categories", "user_unique_devices", "user_unique_locations"
        ]
        
        # Fill NaN with 0
        user_stats = user_stats.fillna(0)
        
        # Merge back to main dataframe
        df = df.merge(user_stats, left_on="user_id", right_index=True, how="left")
        
        # Calculate amount z-score relative to user's pattern
        df["amount_zscore"] = (
            (df["amount"] - df["user_avg_amount"]) / 
            (df["user_std_amount"] + 1.0)  # Add 1 to avoid division by zero
        )
        
        return df


def generate_sample_data(config: Dict) -> pd.DataFrame:
    """
    Generate sample data based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Generated dataset
    """
    data_config = config["data"]
    
    generator = TransactionDataGenerator(
        random_state=data_config.get("random_state", 42)
    )
    
    dataset = generator.generate_dataset(
        n_samples=data_config.get("n_samples", 100000),
        fraud_rate=data_config.get("fraud_rate", 0.02),
        n_days=90
    )
    
    # Save to file if path specified
    raw_data_path = data_config.get("raw_data_path")
    if raw_data_path:
        output_dir = Path(raw_data_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        dataset.to_csv(raw_data_path, index=False)
        logger.info(f"Saved dataset to {raw_data_path}")
    
    return dataset


if __name__ == "__main__":
    # Simple test
    generator = TransactionDataGenerator()
    test_data = generator.generate_dataset(n_samples=1000, fraud_rate=0.05)
    print(f"Generated {len(test_data)} transactions")
    print(f"Fraud rate: {test_data['is_fraud'].mean():.3f}")
    print(test_data.head())
