# Appendix — Minimal Serving (Recording Script)

Audience: Same learners; show a tiny real-time path
Goal: Demonstrate a minimal API using the exact same inference pipeline as the notebooks

## Opening (00:00)
- Say: “Let’s serve real-time predictions with a minimal FastAPI app that reuses our `InferencePipeline`.”

## Start the server (00:20)
- Command:
```
uvicorn scripts.minimal_serve:app --reload --port 8000
```
- Health:
```
curl -s localhost:8000/health | jq
```
- Explain: you’ll see `status`, `timestamp`, and `model_info` with `model_type` and `feature_count`.

## Single prediction (01:00)
- POST example:
```
curl -s -X POST localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
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
      }' | jq
```
- Output keys:
  - `fraud_probability`, `fraud_prediction`, `timestamp`

## Notes (01:45)
- The script reads `configs/serving_config.yaml` and default model path `models/random_forest_final_model.joblib`.
- It uses the same `FeatureEngineer` under the hood — no mismatch between training and serving.

*** End of Appendix ***

