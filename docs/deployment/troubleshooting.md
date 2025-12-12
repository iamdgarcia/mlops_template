# MLOps Course: Troubleshooting Guide

## Common Issues & Solutions

### 1. Docker Build Fails
- **Solution:** Check Dockerfile syntax and ensure all dependencies are listed in `requirements.txt`.

### 2. API Not Responding
- **Solution:** Ensure the container is running and port 8000 is open. Check logs for errors.

### 3. CI/CD Pipeline Fails
- **Solution:** Review GitHub Actions logs. Ensure all test files and scripts are present and pass locally.

### 4. Model Not Found
- **Solution:** Confirm a model artefact exists under `models/` and that the server points to it.
  - Default paths:
    - Full app: `configs/serving_config.yaml -> model.local_model_path` (defaults to `models/random_forest_final_model.joblib`)
    - Minimal server: same default path
  - If missing, rerun notebooks 03 (training) and 04 (inference).

### 5. Import Path for API
- **Symptom:** `uvicorn` fails with `ModuleNotFoundError: src.serving.api`.
- **Solution:** Use the correct app path:
  - Full app: `uvicorn src.serving.main:app --reload --port 8000`
  - Minimal demo: `uvicorn scripts.minimal_serve:app --reload --port 8000`

### 6. Feature Mismatch at Inference
- **Symptom:** Notebook prints “Missing features relative to model”.
- **Solution:** Ensure `data/selected_features.json` matches the trained model.
  - Rerun 02 (feature engineering) and 03 (training); then 04 (inference).
  - Avoid hand-editing `selected_features.json`.

### 7. Monitoring Alerts Triggered
- **Solution:** Review alert details in the dashboard. Investigate data drift, performance drops, or system health issues.

## Getting Help
- Review course notebooks for implementation details
- Consult official docs for MLflow, FastAPI, Docker, and GitHub Actions

---
This guide helps you quickly resolve common issues in your MLOps pipeline.
