# Module 3 — Model Training (Recording Script)

Audience: ML newcomers learning model training + tracking in an MLOps layout
Goal: Train a compact set of models, choose the best, persist artefacts

## Opening (00:00)
- Say: “We’ll train a couple of baseline models with a tiny grid for speed, then save the winner and a machine‑readable summary.”
- Note: MLflow is wired but optional for this quick demo.

## Data Splits (00:30)
- From the pipeline/notebook: we obtain `X_train, y_train, X_val, y_val, X_test, y_test` consistent with the selected feature list.
- Stratification is by `is_fraud` to maintain class proportions.

## Models & Hyperparameters (01:00)
- Code lives in `src/train.py::ModelTrainer.prepare_model_configs` (edited for fast runs):
  - Logistic Regression (enabled):
    - Base params: `class_weight='balanced'`, `max_iter=500`, `solver='liblinear'`, `random_state=42`
    - Grid: `C ∈ {0.1, 1.0}`
  - Random Forest (fallback and/or explicit):
    - Base params: `class_weight='balanced'`, `random_state=42`
    - Grid (from `configs/training_config.yaml`):
      - `n_estimators ∈ {100}`
      - `max_depth ∈ {5, None}`
      - `min_samples_split ∈ {2}`
      - `min_samples_leaf ∈ {1}`
  - XGBoost: disabled in the quick path; can be enabled later.
- Cross‑validation: `cv_folds=3`, scoring=`roc_auc`.

## Training & Metrics (02:30)
- For each model:
  - Fit with GridSearchCV (where applicable).
  - Compute and log (train & val where available):
    - `accuracy, precision, recall, f1, roc_auc, average_precision`.
- Best model selection: max validation ROC‑AUC (fallback to train ROC‑AUC if no val).

## Persisting the Winner (03:30)
- Save artefact to `models/<best_model>_final_model.joblib`.
- Write `data/training_summary.json` with:
  - `timestamp, dataset_size, features_used, fraud_rate, best_model`
  - `test_metrics` keys: `test_accuracy, test_precision, test_recall, test_f1, test_roc_auc, test_avg_precision`
  - `model_file`: relative path to artefact
- Mention: These are the exact keys that the inference/drift notebooks read.

## Quick sanity check (04:00)
- Print metrics and path to artefact.
- If MLflow is used, note experiment name; otherwise continue.

## Close (04:30)
- “We have a production‑style artefact and a summary. Next we’ll use the same feature pipeline to serve predictions.”

*** End of Module 3 ***

