# MLOps Template - Quick Setup

## What Was Implemented

✅ **App Platform Configuration** (`.do/app.yaml`)
- Fraud detection API service definition
- Basic tier ($5/mo) with 512MB RAM
- Health checks on `/health` endpoint
- Auto-deployment on git push

✅ **GitHub Actions Workflows**
- **CI** (`.github/workflows/ci.yml`):
  - Security scans, code quality, unit tests
  - Runs on every push/PR
  - NO model training or deployment
- **Model Retrain** (`.github/workflows/model-retrain.yml`):
  - Manual trigger only
  - Trains model and deploys to selected environment
  - Optional GitHub release creation
- **Drift Monitoring** (`.github/workflows/drift-monitoring.yml`):
  - Daily drift detection at 2 AM UTC
  - Creates GitHub issues on drift alerts

✅ **Documentation**
- Comprehensive deployment guide (`DEPLOYMENT_GUIDE.md`)
- Technical mechanics documentation (`docs/DEPLOYMENT_MECHANICS.md`)
- Updated README with deployment section
- Troubleshooting tips included

## Next Steps to Deploy

> 💰 **Get $200 Free Credit!** Sign up at https://m.do.co/c/eddc62174250 to receive $200 in free credits for 60 days - run this entire course project for free!

### 1. Install and Authenticate doctl CLI
```bash
# macOS
brew install doctl

# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
tar xf ~/doctl-1.94.0-linux-amd64.tar.gz
sudo mv ~/doctl /usr/local/bin

# Authenticate
doctl auth init
```

### 2. Create DigitalOcean Apps
```bash
# Run the initialization script
./scripts/init_digitalocean_apps.sh

# This creates three apps:
# - fraud-detection-api (production - master branch)
# - fraud-detection-api-staging (staging - staging branch)
# - fraud-detection-api-dev (development - develop branch)
```

### 3. Push Code (Triggers CI)
```bash
# Push code changes - triggers CI workflow only
git add .
git commit -m "Setup DigitalOcean deployment"
git push origin develop

# Watch CI run at:
# https://github.com/iamdgarcia/mlops_template/actions
```

### 4. Train and Deploy Model (Manual)
```bash
# Go to GitHub Actions:
# https://github.com/iamdgarcia/mlops_template/actions/workflows/model-retrain.yml

# Click "Run workflow"
# - Select environment: development
# - Create release: false (optional)
# - Click "Run workflow" button

# This will:
# 1. Train a new model
# 2. Commit model to git
# 3. Trigger DigitalOcean auto-deploy
```

### 5. Access Your API
After deployment completes (60-90 seconds), you'll get a URL like:
```
https://fraud-detection-api-xxxxx.ondigitalocean.app
```

Test it:
```bash
# Health check
curl https://YOUR-APP-URL/health

# View API docs
open https://YOUR-APP-URL/docs

# Make a prediction
curl -X POST https://YOUR-APP-URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.0,
    "merchant_category": "retail",
    "transaction_type": "purchase",
    "location": "US",
    "device_type": "mobile",
    "hour_of_day": 14,
    "day_of_week": 3,
    "user_transaction_frequency": 10.5,
    "user_avg_amount": 250.0,
    "user_transaction_count": 25
  }'
```

## Files Modified/Created

### New Files
- `.do/app.yaml` - DigitalOcean App Platform configuration
- `.github/workflows/ci.yml` - Continuous integration (tests only)
- `.github/workflows/model-retrain.yml` - Manual model retraining
- `.github/workflows/drift-monitoring.yml` - Daily drift detection
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment documentation
- `SETUP_SUMMARY.md` - This quick reference guide
- `docs/DEPLOYMENT_MECHANICS.md` - Technical architecture documentation

### Modified Files
- `README.md` - Added deployment section
- `DEPLOYMENT_SUMMARY.md` - Updated for auto-deploy approach

### Removed Files
- `.github/workflows/mlops_pipeline.yml` - Split into separate workflows

## Deployment Architecture

```
Code Push → CI Workflow (tests only)
    ↓
Manual Trigger → Model Retrain Workflow
    ↓
1. Run data pipeline
2. Train model
3. Commit model to git [skip ci]
4. Push to repository
    ↓
Git Push Webhook → DigitalOcean App Platform
    ↓
1. Clone repository (with model)
2. Build Docker image
3. Run health checks
4. Deploy (zero-downtime)
    ↓
Live API at *.ondigitalocean.app

Daily: Drift Monitoring → Alert if drift detected
```

## Workflow Summary

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| **CI** | Every push/PR | Tests & quality checks | 2-3 min |
| **Model Retrain** | Manual only | Train & deploy model | 8-12 min |
| **Drift Monitoring** | Daily 2 AM UTC | Detect data drift | 1-2 min |

## Cost Breakdown

| Component | Cost |
|-----------|------|
| App Platform (Basic tier) | $5/mo |
| Bandwidth (1TB included) | $0 |
| SSL Certificate | $0 |
| GitHub Actions (2000 min/mo free) | $0 |
| **Total** | **$5/mo** |

**With $200 credit**: 40 months free for 1 environment!

## Features Enabled

✅ Automatic CI on every push (no deployment)
✅ Manual model retraining with environment selection
✅ Auto-deployment on model commit via git webhook
✅ Daily drift monitoring with GitHub issue alerts
✅ HTTPS with free SSL certificate  
✅ Built-in monitoring and logs
✅ Health checks and auto-recovery
✅ Zero-downtime deployments
✅ Optional GitHub releases for model versioning
✅ Environment-specific deployments (prod/staging/dev)

## Troubleshooting

**Deployment fails with "Could not find app"**
- Solution: Authorize GitHub with DigitalOcean (see DEPLOYMENT_GUIDE.md Step 3)

**Health check fails**
- Wait 1-2 minutes for app to fully start
- Check logs in DigitalOcean dashboard
- Verify model files are included in deployment package

**Build timeout or out of memory**
- Upgrade instance size in `app.yaml`:
  ```yaml
  instance_size_slug: apps-s-1vcpu-1gb  # $12/mo
  ```

## Support Resources

- **Full Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **GitHub Actions**: https://github.com/iamdgarcia/mlops_template/actions
- **DigitalOcean Dashboard**: https://cloud.digitalocean.com/apps
- **App Platform Docs**: https://docs.digitalocean.com/products/app-platform/

---

**Ready to deploy?** Follow the 4 steps above! 🚀
