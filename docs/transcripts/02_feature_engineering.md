# Module 2 — Feature Engineering (Recording Script)

Audience: ML newcomers learning practical feature pipelines
Goal: Engineer predictive features consistently for training and inference

## Opening (00:00)
- Say: “We’ll build features once and reuse them everywhere. The `FeatureEngineer` in `src/features.py` guarantees parity between training and serving.”

## Create Features with FeatureEngineer (00:30)
- Run: instantiate `FeatureEngineer(config)` and call `create_all_features(df)` on the cleaned dataset.
- Explain each transformation exactly (from `src/features.py`):

1) Temporal features (`create_temporal_features`)
- Input: `timestamp`
- Columns created:
  - `hour_of_day = dt.hour`
  - `day_of_week = dt.dayofweek`
  - `day_of_month = dt.day`
  - `month = dt.month`
  - `is_weekend = (day_of_week >= 5)`
  - `time_category = cut(hour_of_day, bins=[-1,6,12,18,24], labels=[night,morning,afternoon,evening])`
  - `is_business_hours = 9 ≤ hour_of_day ≤ 17 and weekday`
  - `is_late_night = hour_of_day ≥ 23 or ≤ 6`

2) Amount features (`create_amount_features`)
- Input: `amount`
- Columns created:
  - `amount_log = log1p(amount)`
  - `amount_category = quartile binning of amount` with labels {low, medium, high, very_high}
  - Roundness indicators: `is_round_amount`, `is_round_10`, `is_round_100`

3) User behavior (`create_user_behavior_features`)
- If missing, compute per‑user stats (groupby `user_id`):
  - `user_transaction_count`, `user_avg_amount`, `user_std_amount`, `user_min_amount`, `user_max_amount`, `user_total_amount`
  - `user_unique_categories`, `user_unique_devices`, `user_unique_locations`
- Row‑level derived features:
  - `amount_zscore = (amount - user_avg_amount)/(user_std_amount + 1.0)`
  - `amount_ratio_to_user_avg = amount/(user_avg_amount + 1.0)`
  - `amount_ratio_to_user_max = amount/(user_max_amount + 1.0)`
  - `is_amount_outlier = |amount_zscore| > 3`

4) Frequency features (`create_frequency_features`)
- Requires sorted by `user_id, timestamp`
- Columns created:
  - `time_since_last_transaction = groupby(user_id).timestamp.diff().seconds`
  - `hours_since_last_transaction = time_since_last_transaction / 3600`
  - `transactions_per_day = user_transaction_count / 30.0`
  - `is_quick_transaction = hours_since_last_transaction ≤ 1`
  - `is_very_quick_transaction = time_since_last_transaction ≤ 300`

5) Location features (`create_location_features`)
- Most frequent location per user:
  - `user_frequent_location`
  - `is_usual_location = (location == user_frequent_location)`

6) Device features (`create_device_features`)
- User‑device consistency:
  - `user_frequent_device`
  - `is_usual_device = (device_id == user_frequent_device)`

7) Merchant features (`create_merchant_features`)
- User‑merchant consistency:
  - `user_frequent_merchant`
  - `is_usual_merchant_category = (merchant_category == user_frequent_merchant)`

8) Final encoding & cleanup (`_encode_categorical_features`)
- Drop high‑cardinality/non‑predictive identifiers to keep runtime small:
  - Drop: `transaction_id`, `user_id`, `device_id`, `timestamp`, `user_frequent_location`, `user_frequent_device`, `user_frequent_merchant`
- For remaining `object` or `category` columns:
  - Convert to categorical codes (`astype('category').cat.codes`), replace `-1` with `NaN`, cast to `float`
- Result: a fully numeric feature table appropriate for training and XGBoost/Sklearn

## Select & Persist (04:00)
- For the demo path, we keep a compact feature set. Persist:
  - `data/selected_features.json` (list of feature names)
  - `data/transactions_final.csv` (features + `is_fraud`)
- Say: “This feature list is what the inference pipeline will load to ensure parity.”

## Close (04:30)
- Summarize: temporal + behavior + consistency checks + safe numeric encoding; next: training.

*** End of Module 2 ***

