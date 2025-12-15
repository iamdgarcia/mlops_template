# MLOps Fraud Detection Pipeline - User Guide

Welcome to the comprehensive MLOps fraud detection pipeline. This guide will walk you through the entire project structure, execution sequence, and key learning concepts.

## Quick Start Guide

### Prerequisites
- Python 3.8+ installed
- Basic knowledge of machine learning concepts
- Familiarity with Jupyter notebooks

### Installation
1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd mlops_template
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   ```bash
   python -c "import mlflow; import pandas; import sklearn; print('Setup complete')"
   ```

## Learning Path - Execute in Order

### Module 1: Data Preparation
**File**: `notebooks/01_data_preparation.ipynb`
**Duration**: 30-45 minutes
**Concepts Learned**:
- Synthetic data generation for ML projects
- Data quality assessment and validation
- Exploratory data analysis (EDA) techniques
- Statistical analysis of fraud patterns
- Data export and pipeline preparation

**Key Outputs**:
- `data/transactions_raw.csv` - Generated transaction dataset
- Data quality report and visualizations
- Understanding of fraud vs normal transaction patterns

### Module 2: Feature Engineering
**File**: `notebooks/02_feature_engineering.ipynb`
**Duration**: 45-60 minutes
**Concepts Learned**:
- Advanced feature creation techniques
- Temporal and behavioral feature engineering
- Feature selection methods (statistical and ML-based)
- Feature validation and correlation analysis
- Pipeline preparation for model training

**Key Outputs**:
- `data/transactions_final.csv` - Feature-engineered dataset
- `data/selected_features.json` - Feature metadata
- Feature importance rankings and correlation analysis

### Module 3: Model Training & MLflow Tracking
**File**: `notebooks/03_model_training.ipynb`
**Duration**: 60-90 minutes
**Concepts Learned**:
- Multiple algorithm comparison
- Hyperparameter optimization with GridSearchCV
- MLflow experiment tracking and logging
- Model evaluation metrics for fraud detection
- Cross-validation and model selection

**Key Outputs**:
- Trained models logged in MLflow
- Performance comparison reports
- Best model selection and registration
- `models/` directory with saved models

### Module 4: Model Inference & Serving
**File**: `notebooks/04_model_inference.ipynb`
**Duration**: 45-60 minutes
**Concepts Learned**:
- Production inference pipeline design
- Batch and real-time prediction patterns
- Model loading and optimization
- API development with FastAPI
- Performance monitoring and logging

**Key Outputs**:
- Production-ready inference pipeline
- FastAPI server implementation
- Prediction performance benchmarks

### Module 5: Drift Detection & Monitoring
**File**: `notebooks/05_drift_detection.ipynb`
**Duration**: 45-60 minutes
**Concepts Learned**:
- Data drift detection techniques
- Statistical methods for distribution comparison
- Model performance monitoring
- Alerting systems and thresholds
- Integration with MLflow for tracking

**Key Outputs**:
- Drift detection framework
- Monitoring dashboards and alerts
- Historical performance tracking

## MLflow Integration

### Starting MLflow UI
```bash
mlflow ui --port 5000
```
Access at: http://localhost:5000

### Key MLflow Features Used
- **Experiment Tracking**: All model training runs
- **Model Registry**: Best model versioning
- **Metrics Logging**: Performance metrics over time
- **Artifact Storage**: Models, plots, and data

## API Deployment

### Starting the Inference API
```bash
# Using the startup script
./start_api.sh

# Or directly with uvicorn
uvicorn src.serving.main:app --reload --port 8000

# Minimal demo server (optional)
uvicorn scripts.minimal_serve:app --reload --port 8000
```

### API Endpoints
- `GET /` - API information and documentation link
- `GET /health` - Health check with model status
- `POST /predict` - Single transaction fraud prediction
- `GET /sample-transaction` - Get a sample transaction for testing
- `GET /metrics` - API performance metrics
- `POST /save-logs` - Manually save prediction logs

**Note**: The `/model/info` endpoint mentioned in earlier documentation has been replaced with `/metrics` which includes model version information.

### Example API Usage
```python
import requests

# Get a sample transaction to test with
sample = requests.get('http://localhost:8000/sample-transaction').json()
print("Sample transaction:", sample)

# Single prediction
response = requests.post('http://localhost:8000/predict', json=sample)
result = response.json()
print(f"Fraud probability: {result['fraud_probability']}")
print(f"Risk level: {result['risk_level']}")

# Check API health
health = requests.get('http://localhost:8000/health').json()
print(f"Model loaded: {health['model_loaded']}")
```

## Docker Deployment

### Building and Running with Docker
```bash
# Build image
docker build -t fraud-detection-api .

# Run container
docker run -p 8000:8000 fraud-detection-api

# Or use Docker Compose
docker-compose up
```

## Project Structure Deep Dive

### `/notebooks/` - Educational Sequence
Sequential Jupyter notebooks that build upon each other. Each notebook is self-contained but designed to be executed in order.

### `/src/` - Production Code
Modularized, reusable Python code extracted from notebooks:
- `data_generation/` - Synthetic data creation
- `features.py` - **Single source of truth for feature engineering** (used by training, inference, and serving)
- `inference.py` - Prediction pipeline that uses `FeatureEngineer`
- `serving/` - FastAPI application
- `pipelines/` - High-level orchestration for data preparation and training

**Key Design Pattern**: All feature engineering flows through `src/features.py`'s `FeatureEngineer` class to ensure training/serving parity.

### `/configs/` - Configuration Management
YAML configuration files for different environments and components.

### `/data/` - Data Storage
Generated during notebook execution:
- `raw/` - Original generated data
- `processed/` - Cleaned and transformed data
- Feature metadata and pipeline artifacts

### `/models/` - Model Artifacts
Trained models, scalers, and metadata saved for production use.

## Key Learning Concepts

### MLOps Best Practices Demonstrated
1. **Reproducibility**: Seed management and configuration
2. **Experiment Tracking**: Comprehensive MLflow integration
3. **Code Organization**: Modular structure with notebooks + src/
4. **Version Control**: Git-friendly project structure
5. **Documentation**: Comprehensive inline documentation
6. **Testing**: Framework for unit and integration tests
7. **Deployment**: Docker and API serving patterns
8. **Monitoring**: Data drift and model performance tracking

### Fraud Detection Domain Knowledge
1. **Imbalanced Classification**: Techniques for rare event detection
2. **Feature Engineering**: Domain-specific feature creation
3. **Evaluation Metrics**: Precision, recall, F1 for fraud detection
4. **Temporal Patterns**: Time-based fraud analysis
5. **Behavioral Analysis**: User pattern recognition

## Feature Engineering: Single Source of Truth

### Architecture Pattern
This project implements a critical MLOps best practice: **feature engineering parity** between training and serving.

**How it works**:
1. **Canonical Implementation**: All feature engineering logic lives in `src/features.py` in the `FeatureEngineer` class
2. **Training Path**: Notebooks and training scripts import and use `FeatureEngineer.create_all_features()`
3. **Inference Path**: `InferencePipeline` in `src/inference.py` uses `FeatureEngineer` for preprocessing
4. **Serving Path**: FastAPI application delegates to `InferencePipeline`, which uses `FeatureEngineer`

### Why This Matters
**Training/Serving Skew** is a common MLOps failure mode where features computed differently in training vs. production cause model performance degradation. By using the same code path, we eliminate this risk.

### Example Usage

**In Training** (notebooks/03_model_training.ipynb):
```python
from src.features import FeatureEngineer

engineer = FeatureEngineer(config)
features_df = engineer.create_all_features(raw_data)
# Use features_df for training...
```

**In Inference** (src/inference.py):
```python
from src.features import FeatureEngineer

class InferencePipeline:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
    
    def preprocess_data(self, raw_data):
        return self.feature_engineer.create_all_features(raw_data)
```

**In Serving** (src/serving/main.py):
```python
# FastAPI endpoint
@app.post("/predict")
async def predict_fraud(transaction: TransactionRequest):
    # InferencePipeline handles feature engineering internally
    predictions = inference_pipeline.predict_batch(transaction_df)
    return predictions
```

### Validation
The test suite `tests/test_feature_parity.py` validates that:
- Feature engineering produces consistent results across all contexts
- No features are computed differently in training vs. serving
- Edge cases are handled correctly
- Feature schemas remain compatible

## Video Tutorial Integration

This project is designed to support video tutorials for key concepts:

### Recommended Video Topics
1. **"MLOps Pipeline Overview"** - Complete walkthrough of the 5-module structure
2. **"MLflow in Practice"** - Deep dive into experiment tracking and model registry
3. **"Feature Engineering for Fraud Detection"** - Domain-specific feature creation techniques
4. **"Production ML Deployment"** - API development and Docker deployment
5. **"Monitoring ML Models"** - Drift detection and performance monitoring

### Video Tutorial Guidelines
- Each video should correspond to 1-2 notebooks
- Include live coding demonstrations
- Explain both the code and the underlying ML concepts
- Show the MLflow UI and API interactions
- Demonstrate troubleshooting common issues

## Troubleshooting Guide

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **MLflow Issues**
## Troubleshooting

### Common Issues and Solutions

1. **Model File Not Found**
   ```bash
   # Error: Model file not found at models/random_forest_final_model.joblib
   # Solution: Run the training notebook first to generate the model
   jupyter notebook notebooks/03_model_training.ipynb
   ```

2. **MLflow Port Conflict**
   ```bash
   # Error: Address already in use
   # Solution: Either kill the existing process or use a different port
   lsof -i :5000  # Find the process using port 5000
   kill -9 <PID>  # Kill the process
   # Or use a different port:
   mlflow ui --port 5001
   ```

3. **Permission Errors on data/ or models/ directories**
   ```bash
   # Error: Permission denied when writing to data/ or models/
   # Solution: Ensure directories exist and have proper permissions
   mkdir -p data/logs data/inference_results data/drift_alerts models logs
   chmod -R u+w data models logs
   ```

4. **Docker HEALTHCHECK Fails**
   ```bash
   # Error: Container marked as unhealthy
   # Cause: curl not installed in container (fixed in latest Dockerfile)
   # Solution: Rebuild the Docker image
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

5. **Missing Dependencies in Notebooks**
   ```bash
   # Error: ModuleNotFoundError
   # Solution: Ensure virtual environment is activated and packages installed
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   # For Jupyter, ensure kernel uses correct environment
   python -m ipykernel install --user --name=mlops_env
   ```

6. **Data Not Found**
   ```bash
   # Error: File not found: data/transactions_raw.csv
   # Solution: Run notebooks in sequence - each generates data for the next
   # Start with 01_data_preparation.ipynb
   ```

7. **API Connection Issues**
  ```bash
  # Check if port is available
  lsof -i :8000
  # Kill process if needed
  kill -9 <PID>
  # Or use different port
  uvicorn src.serving.main:app --port 8001
  ```

8. **MLflow Experiment Tracking Issues**
   ```bash
   # Error: Failed to create experiment
   # Solution: Clear MLflow cache and restart
   rm -rf mlruns/
   # MLflow will recreate experiments when you run training notebook
   ```

### Performance Optimization
- Reduce dataset size in config files for faster execution
- Use multiprocessing for feature engineering
- Consider GPU acceleration for large models

## Next Steps and Extensions

### Potential Enhancements
1. **Advanced Models**: Deep learning approaches (neural networks)
2. **Real-time Streaming**: Integration with Kafka or similar
3. **Advanced Monitoring**: Prometheus and Grafana integration
4. **Cloud Deployment**: AWS/GCP/Azure deployment patterns
5. **A/B Testing**: Champion/challenger model patterns
6. **Advanced Drift Detection**: More sophisticated statistical methods

### Production Considerations
1. **Security**: Authentication and authorization
2. **Scalability**: Load balancing and auto-scaling
3. **Reliability**: Circuit breakers and fallback mechanisms
4. **Compliance**: Audit trails and model explainability
5. **Cost Optimization**: Resource management and monitoring

## Support and Community

### Getting Help
1. Review the notebook documentation and comments
2. Check the MLflow UI for experiment details
3. Consult the API documentation at `/docs` endpoint
4. Review the troubleshooting section above

### Contributing
1. Follow the existing code structure and documentation style
2. Add comprehensive comments for educational value
3. Include tests for new functionality
4. Update this guide with new features

This project serves as a comprehensive foundation for understanding and implementing MLOps practices in a real-world fraud detection scenario. The modular structure allows for easy customization and extension based on specific requirements and learning objectives.
