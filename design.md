# Design Document

## Overview
This document describes the high-level architecture, components, data flows, interfaces, error handling, testing strategy, and deployment considerations for the MLOps Fraud Detection Pipeline.

## Architecture
- Data generation & ingestion: `scripts/` and `src/data_generation.py`
- Data processing & feature engineering: `src/data_processing.py`, `src/features.py`, `notebooks/02_feature_engineering.ipynb`
- Model training & experiment tracking: `src/train.py`, `notebooks/03_model_training.ipynb`, MLflow (`./mlruns`)
- Inference pipeline & serving: `src/inference.py`, `src/serving/main.py`, `scripts/minimal_serve.py`
- Monitoring & drift detection: `src/drift_detection.py`, `notebooks/05_drift_detection.ipynb`
- CI / tests: `tests/` (pytest)

## Components & Responsibilities
- src.data_generation: create synthetic datasets and sampling utilities
- src.data_processing: validation, cleaning, and saving processed datasets
- src.features: feature engineering, selection, serialization of selected features
- src.train: training orchestration, hyperparameter search, MLflow logging, model export
- src.inference: model loader, preprocessing pipeline, single-row and batch prediction helpers
- src.serving: FastAPI app and endpoints (health, predict, metadata)
- src.drift_detection: drift metrics computation and alert generation

## Data Flow
1. Synthetic data generation -> raw CSV in `data/raw/`
2. Processing & validation -> cleaned datasets in `data/` and features in `data/features/`
3. Training -> models and metrics persisted to `models/` and MLflow tracking
4. Serving -> model artifact loaded into API for real-time inference
5. Monitoring -> periodic jobs evaluate drift and write alerts to `data/drift_alerts/`

## Interfaces / API Contracts
- Health endpoint
  - GET /health
  - Response: 200 with JSON {"status":"ok"}
- Predict endpoint
  - POST /predict
  - Request: JSON with required features (see `data/selected_features.json`)
  - Response: JSON with prediction and probability
- Metadata endpoint
  - GET /metadata
  - Response: model version, training run id, feature list

Define request/response JSON schemas in `src/serving/schemas.py` (if not present, add). Keep schemas backward compatible; add versioning via `model_version` metadata field.

## Data Models
- Use JSON schema for API payloads and Pydantic models in FastAPI
- Persist trained model artifacts using joblib and store metadata in MLflow

## Error Handling
- Fail fast for configuration and missing model files with clear messages
- Return HTTP 4xx for client input errors with structured error body
- Return HTTP 5xx for server errors with generic message and logged stacktrace
- Log all errors to `logs/` with timestamps and structured (JSON) format where possible

## Testing Strategy
- Unit tests for data processing, features, model inference (pytest)
- Integration tests for API endpoints (`tests/test_api` — currently light)
- Coverage target: >= 80% for core modules
- Test data fixtures: small deterministic datasets in `tests/fixtures/`

## Monitoring & Observability
- Health check endpoint used by readiness probes
- Logging to `logs/` and optional forwarding to monitoring stacks
- MLflow for experiment metadata
- Drift detection results saved to `data/drift_alerts/` and summarized in `data/drift_detection_summary.json`

## Deployment
- Local: virtualenv + uvicorn or start_api.sh -> run locally
- Container: Dockerfile + docker-compose.yml for full stack
- CI: run unit tests and linting on PRs

## Security & Privacy
- Uses synthetic data only; no secrets in repo
- Recommend adding simple auth for any deployed demos

## Next Steps (linked to `tasks.md`)
See `tasks.md` for an implementation roadmap, priorities, acceptance criteria, and owners.


*Document created to satisfy Spec-Driven Workflow design artifact requirement.*
