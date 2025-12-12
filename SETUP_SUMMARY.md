# DigitalOcean Deployment - Quick Setup

## What Was Implemented

✅ **App Platform Configuration** (`app.yaml`)
- Fraud detection API service definition
- Basic tier ($5/mo) with 512MB RAM
- Health checks on `/health` endpoint
- Auto-deployment on git push

✅ **GitHub Actions Integration** (`.github/workflows/mlops_pipeline.yml`)
- Three deployment jobs updated:
  - `deploy-production` (master branch)
  - `deploy-staging` (staging branch)  
  - `deploy-dev` (develop branch)
- Uses official `digitalocean/app_action/deploy@v2`
- Automated health checks after deployment
- Deployment URL reporting

✅ **Documentation**
- Comprehensive deployment guide (`DEPLOYMENT_GUIDE.md`)
- Updated README with deployment section
- Troubleshooting tips included

## Next Steps to Deploy

> 💰 **Get $200 Free Credit!** Sign up at https://m.do.co/c/eddc62174250 to receive $200 in free credits for 60 days - run this entire course project for free!

### 1. Create DigitalOcean API Token
```
1. Visit: https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: "GitHub Actions MLOps Template"
4. Scopes: Read + Write
5. Copy token (you won't see it again!)
```

### 2. Add Token to GitHub Secrets
```
1. Visit: https://github.com/iamdgarcia/mlops_template/settings/secrets/actions
2. Click "New repository secret"
3. Name: DIGITALOCEAN_ACCESS_TOKEN
4. Value: <paste your token>
5. Click "Add secret"
```

### 3. Deploy!
```bash
# Commit and push the changes
git add .
git commit -m "Add DigitalOcean deployment configuration"
git push origin master

# Watch deployment at:
# https://github.com/iamdgarcia/mlops_template/actions
```

### 4. Access Your API
After deployment completes (5-10 minutes), you'll get a URL like:
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
- `app.yaml` - DigitalOcean App Platform configuration
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment documentation
- `SETUP_SUMMARY.md` - This quick reference guide

### Modified Files
- `.github/workflows/mlops_pipeline.yml` - Updated deployment jobs
- `README.md` - Added deployment section

## Deployment Architecture

```
GitHub Push (master)
    ↓
GitHub Actions Workflow
    ↓
1. Run tests
2. Train model
3. Build Docker image
4. Deploy to DigitalOcean
5. Run health checks
    ↓
Live API at *.ondigitalocean.app
```

## Cost Breakdown

| Component | Cost |
|-----------|------|
| App Platform (Basic tier) | $5/mo |
| Bandwidth (1TB included) | $0 |
| SSL Certificate | $0 |
| **Total** | **$5/mo** |

## Features Enabled

✅ Automatic deployments on git push
✅ HTTPS with free SSL certificate  
✅ Built-in monitoring and logs
✅ Health checks and auto-recovery
✅ Zero-downtime deployments
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
