# Module 5 — Drift Detection (Recording Script)

Audience: ML newcomers learning lightweight monitoring patterns
Goal: Detect data drift statistically; optionally assess performance drift; export simple alerts

## Opening (00:00)
- Say: “We’ll detect drift using statistical tests; MLflow and seaborn are optional. The notebook falls back gracefully if they’re not installed.”

## Inputs (00:30)
- Load config from `configs/training_config.yaml`.
- Load training summary `data/training_summary.json` (keys used: `best_model`, `test_metrics.test_roc_auc` when available).
- Load reference data:
  - Prefer `data/transactions_final.csv`.
- Load `data/selected_features.json` for the monitored feature list.

## DataDriftDetector (01:00)
- Implementation: `src/drift_detection.py::DataDriftDetector`
- For each feature:
  - If numeric:
    - Kolmogorov‑Smirnov: `ks_2samp(ref, cur)` → p‑value
    - Wasserstein distance (EMD) for scale shift
    - Jensen‑Shannon divergence via binned entropies
  - If categorical:
    - Chi‑square on contingency table of value counts
    - PSI (Population Stability Index)
- Dataset‑level summary:
  - `features_with_drift` and `drift_percentage = 100 * count / total`
  - `overall_drift_detected = drift_percentage > 25` (teachable threshold)

## Drift datasets (02:00)
- Create 3 synthetic snapshots: `No Drift`, `Moderate Drift`, `Severe Drift` using `create_drifted_data`:
  - Moderate: `amount *= N(1.2, 0.1)`, increase evening hours frequency
  - Severe: `amount *= N(2.0, 0.3)`, hours moved to {0..5}
- Run the detector on each snapshot; print summary lines explicitly:
  - Overall drift (Yes/No); counts and percentage
  - Top features by `(1 - p_value)`

## Alerts (03:30)
- Use `DriftAlertSystem` to map drift percentage to severity:
  - OK (< 25%), WARNING (≥ 25% and < 50%), CRITICAL (≥ 50%)
- Export alert JSON to `data/drift_alerts/drift_alert_<label>_<ts>.json` with:
  - `overall_severity`, `features_affected`, `total_features`, `drift_percentage`
  - Recommendations as ASCII strings (e.g., “Continue normal operations”, “Trigger emergency model retraining”).

## (Optional) Performance drift (04:15)
- `ModelPerformanceDriftDetector` computes on a snapshot:
  - `roc_auc` on probabilities
  - `precision, recall, f1` on predictions
  - flags drift if relative change > 5%
- The notebook attempts to load a local model `models/random_forest_final_model.joblib` and skips gracefully if unavailable.

## Visual Dashboard (04:45)
- A compact 2×2 dashboard:
  - Bar of drift percentage per snapshot
  - Top features impacted (barh)
  - Heatmap of drifted features across snapshots
    - Uses seaborn if available; otherwise matplotlib `imshow` fallback
  - Histogram of `(1 - p_value)` scores with a vertical 0.95 guideline

## Close (05:30)
- “We can now observe statistical drift snapshots, produce actionable alerts, and (optionally) check model performance shifts.”

*** End of Module 5 ***

