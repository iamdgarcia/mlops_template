# 🛡️ Fraud Detection API - Model Serving

This directory contains the production-ready serving infrastructure for the fraud detection model, including the FastAPI application, monitoring dashboard, and deployment configurations.

## 📋 Overview

The serving component provides:
- **Real-time API** for fraud detection predictions
- **Comprehensive monitoring** with Streamlit dashboard
- **Docker containerization** for easy deployment
- **Automated testing** and validation
- **Production-ready** logging and error handling

## 🏗️ Architecture

```
src/serving/
├── main.py              # FastAPI application
├── test_api.py          # API testing suite
└── monitoring/
    └── dashboard.py     # Streamlit monitoring dashboard

configs/
└── serving_config.yaml  # Serving configuration

Docker/
├── Dockerfile           # Container definition
├── docker-compose.yml   # Multi-service deployment
└── start_api.sh         # Startup script
```

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Make sure you've trained a model first
cd notebooks/
jupyter notebook 03_model_training.ipynb

# Start the API
./start_api.sh start-local
```

### Option 2: Run with Docker

```bash
# Build and start with Docker
./start_api.sh start-docker

# Or manually
docker-compose up --build
```

### Option 3: Test the API

```bash
# Run comprehensive test suite
./start_api.sh test

# Or manually
python src/serving/test_api.py
```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check endpoint |
| `/predict` | POST | Fraud prediction endpoint |
| `/metrics` | GET | API performance metrics |
| `/docs` | GET | Interactive API documentation |

### Prediction Request Format

```json
{
  "amount": 150.0,
  "merchant_category": "grocery",
  "transaction_type": "purchase", 
  "location": "seattle_wa",
  "device_type": "mobile",
  "hour_of_day": 14,
  "day_of_week": 2,
  "user_transaction_frequency": 5.0,
  "user_avg_amount": 100.0,
  "user_transaction_count": 25
}
```

### Prediction Response Format

```json
{
  "fraud_probability": 0.1234,
  "is_fraud": false,
  "risk_level": "low",
  "prediction_id": "pred_1694123456_1",
  "timestamp": "2025-09-12T10:30:45.123456",
  "model_version": "Random_Forest_v1.0",
  "processing_time_ms": 12.34
}
```

## 🧪 Testing

### Automated Test Suite

The test suite covers:
- ✅ Health checks and connectivity
- ✅ Normal transaction predictions
- ✅ Suspicious transaction detection
- ✅ Input validation and error handling
- ✅ Performance benchmarking

```bash
# Run all tests
python src/serving/test_api.py

# Test specific scenarios
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2500.0,
    "merchant_category": "online",
    "transaction_type": "purchase",
    "location": "unknown_location", 
    "device_type": "mobile",
    "hour_of_day": 3,
    "day_of_week": 6,
    "user_transaction_frequency": 2.0,
    "user_avg_amount": 50.0,
    "user_transaction_count": 5
  }'
```

### Sample Test Scenarios

**Normal Transaction (Low Risk):**
```json
{
  "amount": 45.67,
  "merchant_category": "grocery",
  "transaction_type": "purchase",
  "location": "seattle_wa",
  "device_type": "mobile", 
  "hour_of_day": 10,
  "day_of_week": 2
}
```

**Suspicious Transaction (High Risk):**
```json
{
  "amount": 5000.0,
  "merchant_category": "online",
  "transaction_type": "purchase",
  "location": "unknown_location",
  "device_type": "atm",
  "hour_of_day": 3,
  "day_of_week": 6
}
```

## 📊 Monitoring Dashboard

Access the Streamlit monitoring dashboard:

```bash
# Start the dashboard
streamlit run src/monitoring/dashboard.py --server.port 8501

# Access at: http://localhost:8501
```

### Dashboard Features

- 🔴🟢 **Real-time API health status**
- 📊 **Prediction analytics and trends**
- ⚡ **Performance metrics and latency**
- 🎯 **Fraud detection rates**
- 💰 **Transaction amount analysis**
- 📥 **Data export capabilities**

## ⚙️ Configuration

Edit `configs/serving_config.yaml` to customize:

```yaml
# API Configuration
api:
  host: "0.0.0.0"
  port: 8000
  workers: 1

# Model Configuration  
model:
  fraud_threshold: 0.5
  cache_model: true

# Monitoring
monitoring:
  enable_drift_detection: true
  log_predictions: true
  prediction_log_path: "data/logs/predictions.csv"
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t fraud-detection-api .

# Run container
docker run -p 8000:8000 fraud-detection-api

# Or use docker-compose
docker-compose up --build
```

### Docker Configuration

The Dockerfile includes:
- ✅ Multi-stage build for optimization
- ✅ Health checks for container orchestration  
- ✅ Proper logging configuration
- ✅ Security best practices

## 📈 Performance

### Benchmarks

Based on test runs with Random Forest model:

| Metric | Value |
|--------|-------|
| **Average Latency** | ~15ms |
| **Throughput** | ~50 requests/second |
| **Memory Usage** | ~200MB |
| **Model Load Time** | ~2 seconds |

### Optimization Tips

1. **Model Caching**: Keep model in memory (enabled by default)
2. **Feature Engineering**: Pre-compute user features when possible
3. **Async Processing**: Use background tasks for logging
4. **Load Balancing**: Use multiple workers for high traffic

## 🔒 Security

### Input Validation

- ✅ Pydantic models for request validation
- ✅ Range checks for numerical inputs
- ✅ Enum validation for categorical inputs
- ✅ SQL injection prevention
- ✅ Rate limiting (configurable)

### Production Checklist

- [ ] Enable HTTPS/TLS
- [ ] Configure API keys/authentication
- [ ] Set up rate limiting
- [ ] Enable CORS appropriately
- [ ] Configure logging levels
- [ ] Set up monitoring alerts

## 📝 Logging

### Log Locations

```
logs/
├── serving.log          # API application logs
└── data/logs/
    ├── predictions.csv  # Prediction history
    └── metrics.csv      # Performance metrics
```

### Log Levels

- `INFO`: Normal operation events
- `WARNING`: Performance issues 
- `ERROR`: Prediction failures
- `DEBUG`: Detailed debugging info

## 🚨 Troubleshooting

### Common Issues

**Model Not Found:**
```bash
# Ensure model was trained
ls -la models/Random_Forest_final_model.joblib

# Retrain if necessary
jupyter notebook notebooks/03_model_training.ipynb
```

**API Not Starting:**
```bash
# Check port availability
lsof -i :8000

# Check logs
tail -f logs/serving.log

# Verify dependencies
pip install -r requirements.txt
```

**Prediction Errors:**
```bash
# Validate input format
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "merchant_category": "grocery", ...}'

# Check API documentation
open http://localhost:8000/docs
```

## 🔄 Development

### Adding New Features

1. **New Endpoints**: Add to `src/serving/main.py`
2. **New Tests**: Update `src/serving/test_api.py` 
3. **New Monitoring**: Extend `src/monitoring/dashboard.py`
4. **Configuration**: Update `configs/serving_config.yaml`

### Local Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Start in development mode
uvicorn src.serving.main:app --reload --host 0.0.0.0 --port 8000

# Run tests continuously
pytest src/serving/ --watch
```

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Test with both normal and edge cases
5. Verify Docker deployment works

## 📄 License

This project is part of the MLOps Fraud Detection template.
