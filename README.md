# MLOps Fraud Detection Pipeline

A complete end-to-end machine learning pipeline demonstrating MLOps best practices through a fraud detection use case.

## Overview

This repository contains a comprehensive MLOps implementation that covers the entire machine learning lifecycle, from data preparation to model monitoring in production. The project uses a fraud detection scenario to demonstrate real-world MLOps patterns and best practices.

## Learning Modules

The pipeline is structured as 5 sequential Jupyter notebooks that build upon each other:

### 1. Data Preparation
**File**: `notebooks/01_data_preparation.ipynb`

- Generate synthetic fraud detection dataset
- Perform data validation and quality checks
- Create stratified train/validation/test splits
- Analyze data distributions and patterns

### 2. Feature Engineering  
**File**: `notebooks/02_feature_engineering.ipynb`

- Create behavioral and temporal features
- Implement feature selection techniques
- Analyze feature importance and correlations
- Prepare features for model training

### 3. Model Training
**File**: `notebooks/03_model_training.ipynb`

- Compare multiple machine learning algorithms
- Perform hyperparameter tuning with cross-validation
- Track experiments using MLflow
- Save trained models and evaluation metrics

### 4. Model Inference
**File**: `notebooks/04_model_inference.ipynb`

- Build production-ready inference pipeline
- Implement batch and real-time prediction patterns
- Optimize model loading and performance
- Handle prediction requests efficiently

### 5. Drift Detection & Monitoring
**File**: `notebooks/05_drift_detection.ipynb`

- Implement statistical drift detection methods
- Set up automated monitoring and alerting
- Track model performance over time
- Integrate monitoring with MLflow

## Prerequisites

- Python 3.8 or higher
- Basic knowledge of machine learning concepts
- Familiarity with pandas, scikit-learn, and Jupyter notebooks

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mlops_template
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Run the core notebooks in sequence (fast path):
   - `notebooks/01_data_preparation.ipynb`
   - `notebooks/02_feature_engineering.ipynb`
   - `notebooks/03_model_training.ipynb`
   - `notebooks/04_model_inference.ipynb`
   - `notebooks/05_drift_detection.ipynb`

   This repository focuses on these five modules for the quick demo.

2. **Launch MLflow UI** (optional): 
```bash
mlflow ui --port 5000
```
Access the MLflow interface at http://localhost:5000

3. **Start the inference API** (after completing the notebooks):
```bash
# Full FastAPI app
uvicorn src.serving.main:app --reload --port 8000

# Or use the minimal demo server
uvicorn scripts.minimal_serve:app --reload --port 8000
```

## Project Structure

```
mlops_template/
├── notebooks/              # Educational Jupyter notebooks (execute in order 01-05)
│   ├── 01_data_preparation.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_inference.ipynb
│   └── 05_drift_detection.ipynb
├── src/                     # Reusable Python modules
│   ├── data_generation/     # Data generation utilities
│   ├── feature_engineering/ # Feature creation functions
│   ├── models/             # Model training and evaluation
│   ├── inference/          # Prediction pipeline
│   ├── serving/            # FastAPI application
│   └── pipelines/          # High-level pipeline orchestration
├── scripts/                # Automation scripts
│   ├── run_full_pipeline.py  # End-to-end pipeline execution
│   └── minimal_serve.py      # Minimal API demo
├── configs/                # YAML configuration files
├── data/                   # Generated datasets (created during execution)
├── models/                 # Saved model artifacts
├── tests/                  # Unit and integration tests
└── requirements.txt        # Python dependencies
```

## Key Technologies

- **Data Processing**: pandas, numpy
- **Machine Learning**: scikit-learn, xgboost
- **Experiment Tracking**: MLflow
- **API Framework**: FastAPI
- **Testing**: pytest
- **Visualization**: matplotlib, seaborn

## Learning Outcomes

After completing this project, you will understand:

- How to structure an end-to-end ML pipeline
- MLOps best practices for experiment tracking and model versioning
- Production patterns for model serving and monitoring
- How to implement data drift detection
- Integration of MLflow for ML lifecycle management

## Use Case: Fraud Detection

The project simulates a banking system that needs to detect fraudulent transactions in real-time. The pipeline includes:

- **Synthetic Data**: Realistic transaction data with fraud/legitimate labels
- **Feature Engineering**: Transaction patterns, user behavior, temporal features
- **Model Comparison**: Multiple algorithms with hyperparameter optimization
- **Production Serving**: REST API for real-time predictions
- **Monitoring**: Data drift detection and model performance tracking

## Educational Focus

This repository is designed for:
- Data scientists learning MLOps practices
- ML engineers transitioning to production workflows
- Teams implementing their first end-to-end ML pipeline
- Anyone interested in practical MLOps implementation

## Deployment

### DigitalOcean App Platform (Recommended for Course)

This project includes automated deployment to DigitalOcean App Platform with **git-based auto-deploy** - no API tokens or secrets needed!

> 💰 **Get $200 Free Credit!** Sign up using [this link](https://m.do.co/c/eddc62174250) to receive $200 in free credits for 60 days - perfect for running this course project at no cost!

**How it works:** GitHub Actions trains the model and commits it to the repository. DigitalOcean automatically detects the git push and deploys via webhook - simple and secure!

**Quick Setup (Automated):**
```bash
# Install doctl CLI and authenticate
doctl auth init

# Run the initialization script to create all 3 apps
./scripts/init_digitalocean_apps.sh
```

**Manual Setup:**
1. Create a DigitalOcean account at [cloud.digitalocean.com](https://m.do.co/c/eddc62174250) (includes $200 free credit)
2. Install doctl CLI: `brew install doctl` or see [installation guide](https://docs.digitalocean.com/reference/doctl/how-to/install/)
3. Authenticate: `doctl auth init`
4. Run `./scripts/init_digitalocean_apps.sh` to create apps automatically
5. Push to `master` branch to trigger first deployment

**Documentation:**
- **Quick setup script:** `./scripts/init_digitalocean_apps.sh`
- **Step-by-step guide:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **API usage guide:** [API_GUIDE.md](./API_GUIDE.md)

**Cost:** ~$5/month per environment (Basic tier with 512MB RAM)

The deployment automatically:
- ✅ Trains model in GitHub Actions CI
- ✅ **Validates model quality gates** (prevents deploying worse models)
- ✅ Compares against production baseline metrics
- ✅ Commits trained model to repository with `[skip ci]`
- ✅ Triggers DigitalOcean auto-deploy via git webhook
- ✅ Builds Docker container with model
- ✅ Deploys FastAPI application with health checks
- ✅ Provides public HTTPS endpoint
- ✅ Zero-downtime blue-green deployment

**Access your deployed API:**
- Health check: `https://your-app.ondigitalocean.app/health`
- API docs: `https://your-app.ondigitalocean.app/docs`
- Predictions: `POST https://your-app.ondigitalocean.app/predict`

## Testing

Run the test suite to validate the implementation:
```bash
pytest tests/
```

## 📚 Documentation

**Complete documentation is available in the [`docs/`](docs/) directory.**

### Quick Links

- **[Getting Started](docs/getting-started/quick-start.md)** - 15-minute setup guide
- **[Deployment Guide](docs/deployment/setup-guide.md)** - Production deployment
- **[API Reference](docs/api/guide.md)** - API usage and examples
- **[Architecture](docs/architecture.md)** - System design and decisions

### Documentation Structure

```
docs/
├── README.md                      # Documentation index and navigation
├── getting-started/               # Setup and user guides
│   ├── requirements.md            # Prerequisites
│   ├── quick-start.md             # Quick setup guide
│   └── user-guide.md              # Comprehensive manual
├── deployment/                    # Deployment guides
│   ├── overview.md                # Architecture overview
│   ├── setup-guide.md             # DigitalOcean setup
│   ├── workflow-changes.md        # CI/CD workflows
│   └── troubleshooting.md         # Common issues
├── api/                           # API documentation
│   └── guide.md                   # API reference
└── DEPLOYMENT_MECHANICS.md        # Technical deployment details
```

**👉 Start here**: [docs/README.md](docs/README.md) for the complete documentation index.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the educational content or add new features.

## License

This project is open source and available under the MIT License.

## Video Tutorials

For detailed explanations of key concepts, check out the accompanying video tutorials:

- **Module 1-2**: Data Preparation and Feature Engineering Fundamentals
- **Module 3**: MLflow Integration and Experiment Tracking  
- **Module 4-5**: Production Deployment and Monitoring Strategies

*Note: Video tutorial links will be added when available*

## Pipeline Orchestration

The project now exposes high-level helpers that wrap the reusable data and training workflows:

- `src.pipelines.run_data_preparation` generates raw/clean/feature datasets and stratified splits.
- `src.pipelines.run_training_pipeline` trains all configured models, registers the best run with MLflow, and saves the production artefact.

You can execute the full pipeline locally with:

```bash
python scripts/run_full_pipeline.py
```

## Testing

Run the lightweight regression tests to validate the core pipeline behaviour:

```bash
pytest tests/test_pipelines.py
```

(Tests touching the inference pipeline require `mlflow` to be installed; the suite skips them automatically when it is unavailable.)
