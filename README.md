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

## Testing

Run the test suite to validate the implementation:
```bash
pytest tests/
```

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
