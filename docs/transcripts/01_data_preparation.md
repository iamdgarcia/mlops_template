# Module 1 — Data Preparation (Recording Script)

Audience: ML newcomers learning MLOps patterns
Goal: Generate, validate, and persist a realistic fraud dataset in a reproducible way

## Opening (00:00)
- Say: “In this first module we’ll generate a synthetic but realistic transactions dataset, validate its quality, and persist it for the rest of the pipeline. Everything is config‑driven so runs are reproducible.”
- Show: `configs/training_config.yaml` and highlight:
  - `data.n_samples` (e.g., 20_000)
  - `data.fraud_rate` (e.g., 0.02)
  - `data.random_state` (e.g., 42)

## Generate Transactions (00:45)
- Run: the cell that creates a `TransactionDataGenerator(random_state=config['data']['random_state'])`.
- Run: `generate_dataset(n_samples, fraud_rate, n_days=90)`
- Explain exact fields created per row:
  - Identifiers and context
    - `transaction_id` (e.g., `txn_00000001`)
    - `user_id` (formatted id)
    - `timestamp` (uniform over last `n_days`)
  - Monetary and categories
    - `amount` ~ LogNormal(mean=3.5, sigma=1.2), clamped to [1.0, 10_000.0]
    - `merchant_category` ∈ {grocery, gas_station, restaurant, retail, online, pharmacy, entertainment, travel, utilities, healthcare}
    - `transaction_type` ∈ {purchase, withdrawal, transfer, payment, refund} with p=[0.7,0.1,0.1,0.08,0.02]
    - `device_type` ∈ {mobile, desktop, tablet, pos_terminal, atm} with p=[0.4,0.3,0.1,0.15,0.05]
    - `location` ∈ {New York, Los Angeles, Chicago, Houston, Phoenix}
  - Time features created at generation
    - `hour_of_day` (0–23)
    - `day_of_week` (0–6)
    - `is_weekend` (bool)

## Fraud Assignment (01:45)
- Explain `_assign_fraud_labels` (in `src/data_generation.py`):
  - `n_fraud = int(len(df) * fraud_rate)`; select random indices; set `is_fraud=True`.
  - For fraudulent rows:
    - `amount *= U(1.5, 3.0)` (higher values)
    - `hour_of_day` set to a random odd hour {1,2,3,4,5,23}.

## User Features at Generation (02:15)
- Explain `_add_user_features`:
  - Group by `user_id` and compute:
    - counts/mean/std for `amount`
    - nunique for `merchant_category`, `device_id`, `location`
  - Flattened columns:
    - `user_transaction_count`, `user_avg_amount`, `user_std_amount`
    - `user_unique_categories`, `user_unique_devices`, `user_unique_locations`
  - Derived per‑row:
    - `amount_zscore = (amount - user_avg_amount)/(user_std_amount + 1.0)`

## Data Validation & Cleaning (03:00)
- Explain `DataProcessor.validate_data(df)` (in `src/data_processing.py`):
  - Checks required columns: `transaction_id,user_id,timestamp,amount,merchant_category,transaction_type,is_fraud`.
  - Type and value checks: `amount` numeric and > 0, `transaction_id` uniqueness, `is_fraud` in {0,1,True,False}, timestamp parseable, missing‑rate warnings.
- Explain `DataProcessor.clean_data(df)` steps exactly:
  - `timestamp` → pandas datetime
  - Missing fills:
    - Categorical: `merchant_category`, `transaction_type`, `device_type`, `location` → fill `'unknown'`
    - Numeric: `amount`, `hour_of_day`, `day_of_week` → fill column median
  - Duplicates: drop by `transaction_id` (keep first)
  - Amount cleanup: remove non‑positive; cap at 99.9th percentile
  - Standardize categories:
    - `merchant_category` and `transaction_type`: lowercase → strip → regex to `[a-z0-9_]`
  - Ensure `is_fraud` is boolean

## Persist Artefacts (04:30)
- Run: the cell that saves datasets from the notebook (or note the pipeline saver).
- Confirm files written:
  - `data/transactions_raw.csv`
  - `data/transactions_processed.csv`
- Say: “We’ll reuse these files in later modules; everything is deterministic from config.”

## Close (05:00)
- Summarize the pipeline boundary and what’s next: feature engineering.

*** End of Module 1 ***

