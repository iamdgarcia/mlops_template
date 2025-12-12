# MLOps Course: Deployment Guide

## Overview
This guide explains how to deploy the complete MLOps pipeline, including model serving, containerization, and CI/CD automation.

## Prerequisites
- Docker installed
- Python 3.8+
- GitHub account (for CI/CD)

## Steps

### 1. Build and Run Docker Container
```
docker build -t fraud-detection:latest .
docker run -p 8000:8000 fraud-detection:latest
```

### 2. Deploy Model API
- The FastAPI app is served at `http://localhost:8000`
- Health check endpoint: `/health`
- Prediction endpoint: `/predict`

### 3. Enable CI/CD
- Push code to GitHub
- GitHub Actions workflow (`.github/workflows/mlops_pipeline.yml`) will run tests and deploy automatically

### 4. Monitoring
- Monitor logs and metrics via the dashboard notebook
- Alerts and reports are generated automatically

## Troubleshooting
- See `troubleshooting.md` for common issues

---
This guide ensures a smooth deployment from development to production for your ML system.
