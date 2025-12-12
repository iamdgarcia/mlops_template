# Fraud Detection API - Usage Guide

Complete guide for interacting with the deployed fraud detection API, running inference, and understanding the data requirements.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Running Inference](#running-inference)
4. [Data Requirements](#data-requirements)
5. [Response Format](#response-format)
6. [Error Handling](#error-handling)
7. [Examples](#examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Accessing the API

**Production URL**: `https://fraud-detection-api-[your-app-id].ondigitalocean.app`

**Local Development**: `http://localhost:8000`

**Interactive Documentation**: Visit `/docs` for Swagger UI or `/redoc` for ReDoc

```bash
# Check API health
curl https://your-app-url.ondigitalocean.app/health

# Get interactive documentation
open https://your-app-url.ondigitalocean.app/docs
```

---

## API Endpoints

### 1. Root Endpoint

**GET** `/`

Returns basic API information.

```bash
curl https://your-app-url.ondigitalocean.app/
```

**Response:**
```json
{
  "message": "Fraud Detection API",
  "version": "1.1.0",
  "docs": "/docs"
}
```

---

### 2. Health Check

**GET** `/health`

Check the API status and model availability.

```bash
curl https://your-app-url.ondigitalocean.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-12T10:00:00.000000",
  "model_loaded": true,
  "version": "1.1.0",
  "uptime_seconds": 3600.5
}
```

**Status Values:**
- `healthy` - API is operational and model is loaded
- `unhealthy` - API is running but model failed to load

---

### 3. Sample Transaction

**GET** `/sample-transaction`

Get a sample transaction with all required fields populated.

```bash
curl https://your-app-url.ondigitalocean.app/sample-transaction
```

**Response:**
```json
{
  "transaction_id": "txn_159662",
  "user_id": "user_03471",
  "device_id": "device_01026",
  "amount": 29.07,
  "merchant_category": "online",
  "transaction_type": "transfer",
  "location": "denver_co",
  "device_type": "mobile",
  "hour_of_day": 6,
  "day_of_week": 2,
  "user_transaction_frequency": 18.40,
  "user_avg_amount": 169.94,
  "user_transaction_count": 60,
  "timestamp": "2025-11-16T04:46:25.359813"
}
```

**Use Case:** Use this endpoint to understand the expected data structure and test the API.

---

### 4. Fraud Prediction

**POST** `/predict`

Submit a transaction for fraud detection.

```bash
curl -X POST https://your-app-url.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d @transaction.json
```

**Response:**
```json
{
  "fraud_probability": 0.0234,
  "is_fraud": false,
  "risk_level": "low",
  "prediction_id": "pred_a1b2c3d4e5f6",
  "timestamp": "2025-12-12T10:00:00.000000",
  "model_version": "models/random_forest_final_model.joblib",
  "processing_time_ms": 45.2
}
```

---

## Running Inference

### Required Fields

Every prediction request **must** include these fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `amount` | float | Transaction amount (must be > 0) | `150.50` |
| `merchant_category` | string | Category of merchant | `"grocery"`, `"online"`, `"retail"` |
| `transaction_type` | string | Type of transaction | `"purchase"`, `"transfer"`, `"withdrawal"` |
| `location` | string | Transaction location | `"new_york_ny"`, `"denver_co"` |
| `device_type` | string | Device used for transaction | `"mobile"`, `"desktop"`, `"atm"` |
| `hour_of_day` | integer | Hour (0-23) | `14` |
| `day_of_week` | integer | Day of week (0-6, Monday=0) | `2` |

### Optional Fields (Recommended)

These fields improve prediction accuracy by providing user context:

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `user_id` | string | User identifier | `"anonymous_user"` |
| `transaction_id` | string | Transaction identifier | Auto-generated |
| `timestamp` | string | ISO timestamp | Current UTC time |
| `device_id` | string | Device identifier | `"device_{user_id}"` |
| `user_transaction_frequency` | float | Transactions per day | `0.0` |
| `user_avg_amount` | float | Average transaction amount | Same as `amount` |
| `user_transaction_count` | integer | Total user transactions | `1` |

### Complete Example

```json
{
  "amount": 250.75,
  "merchant_category": "electronics",
  "transaction_type": "purchase",
  "location": "san_francisco_ca",
  "device_type": "desktop",
  "hour_of_day": 14,
  "day_of_week": 3,
  "user_id": "user_12345",
  "transaction_id": "txn_abc123",
  "timestamp": "2025-12-12T14:30:00Z",
  "device_id": "device_xyz789",
  "user_transaction_frequency": 5.2,
  "user_avg_amount": 125.50,
  "user_transaction_count": 47
}
```

### Minimal Example

```json
{
  "amount": 250.75,
  "merchant_category": "electronics",
  "transaction_type": "purchase",
  "location": "san_francisco_ca",
  "device_type": "desktop",
  "hour_of_day": 14,
  "day_of_week": 3
}
```

**Note:** Minimal examples work but may produce less accurate predictions due to missing user context.

---

## Data Requirements

### Field Constraints

#### Amount
- Must be greater than 0
- Type: `float`
- Example: `150.50`, `1000.00`, `25.99`

#### Merchant Category
- Non-empty string
- Common values: `"grocery"`, `"online"`, `"retail"`, `"restaurant"`, `"gas_station"`, `"electronics"`, `"entertainment"`, `"travel"`, `"healthcare"`, `"utilities"`
- The model accepts any string but was trained on these categories

#### Transaction Type
- Non-empty string
- Common values: `"purchase"`, `"transfer"`, `"withdrawal"`, `"deposit"`, `"payment"`
- The model accepts any string but was trained on these types

#### Location
- Non-empty string
- Format: `"city_state"` (lowercase, underscores)
- Examples: `"new_york_ny"`, `"los_angeles_ca"`, `"chicago_il"`, `"houston_tx"`, `"denver_co"`

#### Device Type
- Non-empty string
- Valid values: `"mobile"`, `"desktop"`, `"atm"`

#### Hour of Day
- Integer between 0 and 23
- 0 = midnight, 12 = noon, 23 = 11 PM

#### Day of Week
- Integer between 0 and 6
- 0 = Monday, 1 = Tuesday, ..., 6 = Sunday

---

## Response Format

### Success Response

```json
{
  "fraud_probability": 0.0234,
  "is_fraud": false,
  "risk_level": "low",
  "prediction_id": "pred_a1b2c3d4e5f6",
  "timestamp": "2025-12-12T10:00:00.000000",
  "model_version": "models/random_forest_final_model.joblib",
  "processing_time_ms": 45.2
}
```

**Field Descriptions:**

- `fraud_probability` (float): Probability of fraud (0.0 to 1.0)
- `is_fraud` (boolean): Binary fraud classification
  - `true` if `fraud_probability >= 0.5`
  - `false` if `fraud_probability < 0.5`
- `risk_level` (string): Risk assessment
  - `"low"` - probability < 0.3
  - `"medium"` - probability 0.3 to 0.7
  - `"high"` - probability > 0.7
- `prediction_id` (string): Unique identifier for this prediction
- `timestamp` (string): When the prediction was made
- `model_version` (string): Model identifier
- `processing_time_ms` (float): Inference latency in milliseconds

---

## Error Handling

### Validation Errors (422)

When required fields are missing or invalid:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "amount"],
      "msg": "Field required",
      "input": {...},
      "url": "https://errors.pydantic.dev/2.0.3/v/missing"
    }
  ]
}
```

**Common Validation Errors:**
- Missing required fields
- Invalid data types (e.g., string instead of number)
- Out of range values (e.g., `hour_of_day = 25`)
- Negative amounts

### Server Errors (500)

```json
{
  "detail": "Internal server error"
}
```

**Common Causes:**
- Model not loaded properly
- Feature engineering failure
- Unexpected data format

---

## Examples

### Example 1: Python with requests

```python
import requests
import json

# API endpoint
url = "https://your-app-url.ondigitalocean.app/predict"

# Transaction data
transaction = {
    "amount": 500.00,
    "merchant_category": "electronics",
    "transaction_type": "purchase",
    "location": "new_york_ny",
    "device_type": "mobile",
    "hour_of_day": 18,
    "day_of_week": 4,
    "user_id": "user_42",
    "user_transaction_frequency": 8.5,
    "user_avg_amount": 200.00,
    "user_transaction_count": 120
}

# Make prediction request
response = requests.post(url, json=transaction)

# Check response
if response.status_code == 200:
    result = response.json()
    print(f"Fraud Probability: {result['fraud_probability']:.2%}")
    print(f"Is Fraud: {result['is_fraud']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Example 2: cURL

```bash
curl -X POST https://your-app-url.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "merchant_category": "electronics",
    "transaction_type": "purchase",
    "location": "new_york_ny",
    "device_type": "mobile",
    "hour_of_day": 18,
    "day_of_week": 4,
    "user_id": "user_42",
    "user_transaction_frequency": 8.5,
    "user_avg_amount": 200.00,
    "user_transaction_count": 120
  }'
```

### Example 3: JavaScript/Node.js

```javascript
const axios = require('axios');

const transaction = {
  amount: 500.00,
  merchant_category: "electronics",
  transaction_type: "purchase",
  location: "new_york_ny",
  device_type: "mobile",
  hour_of_day: 18,
  day_of_week: 4,
  user_id: "user_42",
  user_transaction_frequency: 8.5,
  user_avg_amount: 200.00,
  user_transaction_count: 120
};

axios.post('https://your-app-url.ondigitalocean.app/predict', transaction)
  .then(response => {
    const result = response.data;
    console.log(`Fraud Probability: ${(result.fraud_probability * 100).toFixed(2)}%`);
    console.log(`Is Fraud: ${result.is_fraud}`);
    console.log(`Risk Level: ${result.risk_level}`);
  })
  .catch(error => {
    console.error('Error:', error.response.data);
  });
```

### Example 4: Batch Processing

```python
import requests
import pandas as pd

# Load transactions from CSV
transactions = pd.read_csv('transactions.csv')

# API endpoint
url = "https://your-app-url.ondigitalocean.app/predict"

# Process each transaction
results = []
for _, row in transactions.iterrows():
    transaction = row.to_dict()
    response = requests.post(url, json=transaction)
    
    if response.status_code == 200:
        result = response.json()
        results.append({
            'transaction_id': transaction.get('transaction_id', 'N/A'),
            'fraud_probability': result['fraud_probability'],
            'is_fraud': result['is_fraud'],
            'risk_level': result['risk_level']
        })

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('fraud_predictions.csv', index=False)
print(f"Processed {len(results)} transactions")
```

---

## Best Practices

### 1. Always Include User Context

For best prediction accuracy, always include user statistics:
- `user_transaction_frequency`
- `user_avg_amount`
- `user_transaction_count`

These fields help the model detect unusual behavior patterns.

### 2. Use Consistent Data Formats

- **Locations**: Use lowercase with underscores (e.g., `"los_angeles_ca"`)
- **Categories**: Use lowercase, consistent naming
- **Timestamps**: Use ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`)

### 3. Handle Errors Gracefully

```python
try:
    response = requests.post(url, json=transaction, timeout=5)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    print("Request timeout - API may be overloaded")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(e.response.json())
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Monitor Response Times

Track `processing_time_ms` to detect performance issues:

```python
if result['processing_time_ms'] > 1000:
    print("Warning: Slow prediction detected")
```

### 5. Implement Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def predict_with_retry(transaction):
    response = requests.post(url, json=transaction)
    response.raise_for_status()
    return response.json()
```

### 6. Cache Predictions

For the same transaction, cache predictions to reduce API calls:

```python
import hashlib
import json

def get_cache_key(transaction):
    return hashlib.md5(json.dumps(transaction, sort_keys=True).encode()).hexdigest()

cache = {}

def predict_with_cache(transaction):
    key = get_cache_key(transaction)
    if key in cache:
        return cache[key]
    
    result = requests.post(url, json=transaction).json()
    cache[key] = result
    return result
```

---

## Troubleshooting

### Issue: "Field required" errors

**Cause:** Missing required fields in the request

**Solution:** Ensure all required fields are present:
```python
required_fields = [
    'amount', 'merchant_category', 'transaction_type',
    'location', 'device_type', 'hour_of_day', 'day_of_week'
]

for field in required_fields:
    if field not in transaction:
        print(f"Missing required field: {field}")
```

### Issue: "Internal Server Error"

**Cause:** Feature engineering failure or model error

**Solution:** 
1. Check that all required fields have valid values
2. Use `/sample-transaction` to get a known-good example
3. Verify data types match expected types

### Issue: Predictions seem inaccurate

**Cause:** Missing user context fields

**Solution:** Include user statistics:
```python
# Calculate user statistics from historical data
user_stats = calculate_user_stats(user_id)

transaction.update({
    'user_transaction_frequency': user_stats['frequency'],
    'user_avg_amount': user_stats['avg_amount'],
    'user_transaction_count': user_stats['count']
})
```

### Issue: Slow response times

**Cause:** Cold start or high load

**Solution:**
1. Implement request timeout (5-10 seconds)
2. Use async/parallel requests for batch processing
3. Monitor `/health` endpoint for API status

### Issue: Connection errors

**Cause:** Network issues or API downtime

**Solution:**
```python
# Check health endpoint first
try:
    health = requests.get(f"{base_url}/health", timeout=5)
    if health.json()['status'] != 'healthy':
        print("API is unhealthy")
except:
    print("Cannot reach API")
```

---

## Testing Locally

### 1. Run the Docker Container

```bash
# Build the image
docker build -t fraud-detection-api:test .

# Run the container
docker run -d --name fraud-test -p 8000:8000 fraud-detection-api:test

# Check logs
docker logs -f fraud-test

# Test health endpoint
curl http://localhost:8000/health
```

### 2. Get a Sample Transaction

```bash
# Get sample data
curl http://localhost:8000/sample-transaction > sample.json

# Use it for prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @sample.json
```

### 3. Stop the Container

```bash
docker stop fraud-test
docker rm fraud-test
```

---

## Integration Checklist

- [ ] Understand required vs optional fields
- [ ] Test with sample transaction from `/sample-transaction`
- [ ] Implement error handling for validation errors
- [ ] Add retry logic for network failures
- [ ] Monitor response times and API health
- [ ] Include user context for better predictions
- [ ] Use consistent data formats
- [ ] Set appropriate request timeouts
- [ ] Log predictions for auditing
- [ ] Handle edge cases (new users, unusual amounts, etc.)

---

## Support and Resources

- **API Documentation**: `https://your-app-url.ondigitalocean.app/docs`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **GitHub Repository**: `https://github.com/iamdgarcia/mlops_template`
- **Health Check**: `https://your-app-url.ondigitalocean.app/health`

For issues or questions, please open an issue on GitHub or contact the development team.

---

## Model Information

**Algorithm**: Random Forest Classifier

**Features**: The model uses 40+ engineered features including:
- Transaction amount and statistics
- User behavioral patterns
- Temporal features (hour, day, weekend)
- Categorical encodings
- Amount ratios and z-scores

**Performance Metrics** (Test Set):
- Accuracy: 81.9%
- ROC AUC: 67.3%
- Precision: 4.4%
- Recall: 38.8%
- F1 Score: 7.9%

**Note**: The model is optimized for recall (catching fraud) at the expense of precision (false positives). Use the `risk_level` field to implement tiered response strategies.

---

**Last Updated**: December 12, 2025  
**API Version**: 1.1.0
