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
- `GET /health` - Health check
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions
- `GET /model/info` - Model metadata

### Example API Usage
```python
import requests

# Single prediction
response = requests.post('http://localhost:8000/predict', 
                        json={'amount': 150.0, 'hour_of_day': 14, ...})
print(response.json())
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
- `feature_engineering/` - Feature creation functions
- `models/` - Training and evaluation utilities
- `inference/` - Prediction pipeline
- `serving/` - FastAPI application

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
   ```bash
   # Clear MLflow cache
   rm -rf mlruns/
   mlflow ui --port 5000
   ```

3. **Data Not Found**
   ```bash
   # Run notebooks in sequence
   # Each notebook generates data for the next
   ```

4. **API Connection Issues**
  ```bash
  # Check if port is available
  lsof -i :8000
  # Use different port if needed
  uvicorn src.serving.main:app --port 8001
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
