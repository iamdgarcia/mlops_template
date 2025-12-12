# DigitalOcean App Platform Deployment Guide

This guide walks you through deploying the fraud detection API to DigitalOcean App Platform using GitHub Actions.

## Overview

The deployment uses:
- **Platform**: DigitalOcean App Platform (PaaS)
- **CI/CD**: GitHub Actions with `digitalocean/app_action/deploy@v2`
- **Deployment Method**: Explicit deployment triggered by GitHub Actions
- **Cost**: ~$5/month per environment (Basic tier: 512MB RAM, 0.5 vCPU)
  - **FREE for course students!** New signups get $200 credit (40 months free for 1 app)
- **Environments**: Production (master), Staging (staging), Development (develop)

## Prerequisites

1. **GitHub Repository**: Code pushed to GitHub
2. **DigitalOcean Account**: Sign up at [cloud.digitalocean.com](https://m.do.co/c/eddc62174250)
   - 💰 **New users get $200 in free credits for 60 days!**
   - More than enough to run this project for the entire course
3. **doctl CLI**: DigitalOcean command-line tool ([installation guide](https://docs.digitalocean.com/reference/doctl/how-to/install/))
4. **DigitalOcean API Token**: For app creation and deployment

## Quick Setup (Automated)

We provide a script that automatically creates all three app environments:

```bash
# Make sure you're authenticated with doctl first
doctl auth init

# Run the initialization script
./scripts/init_digitalocean_apps.sh
```

This script will:
1. ✅ Create three apps (production, staging, development)
2. ✅ Configure each app with the correct GitHub branch
3. ✅ Generate app URLs and IDs
4. ✅ Create `.env.digitalocean` file with all configuration
5. ✅ Provide instructions for GitHub Secrets setup

**After running the script**, skip to [Step 4: Configure GitHub Secrets](#step-4-configure-github-secrets).

## Manual Setup (Step-by-Step)

If you prefer manual setup or the script doesn't work for your environment:

### Step 1: Create DigitalOcean API Token

1. Log in to DigitalOcean: https://m.do.co/c/eddc62174250
2. Navigate to **API** → **Tokens/Keys** (or visit https://cloud.digitalocean.com/account/api/tokens)
3. Click **Generate New Token**
4. Configure token:
   - **Name**: `GitHub Actions MLOps Template`
   - **Expiration**: 90 days (or No expiry for course)
   - **Scopes**: Check **Read** and **Write**
5. Click **Generate Token**
6. **Copy the token immediately** (you won't see it again!)

### Step 4: Configure GitHub Secrets

1. Go to your GitHub repository settings: **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each of the following:

**Required Secrets:**

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Your API token from Step 1 | Deploy apps via GitHub Actions |
| `PRODUCTION_APP_URL` | `https://fraud-detection-api-xxxxx.ondigitalocean.app` | Health check validation |
| `STAGING_APP_URL` | `https://fraud-detection-api-staging-xxxxx.ondigitalocean.app` | Staging health checks |
| `DEV_APP_URL` | `https://fraud-detection-api-dev-xxxxx.ondigitalocean.app` | Dev health checks |

> ℹ️ **Finding URLs:** 
> - If you used the automated script: Check the `.env.digitalocean` file
> - If manual setup: Go to DigitalOcean dashboard → Apps → Select your app → Copy the URL
> - URLs are also shown when you run: `doctl apps get <app-id> --format LiveURL`

### Step 3: Authenticate GitHub with App Platform

DigitalOcean App Platform needs permission to access your GitHub repository for auto-deploy.

**Option A: Via DigitalOcean Control Panel (Easiest)**

1. Go to https://cloud.digitalocean.com/apps
2. Click **Create App**
3. Select **GitHub** as source
4. Click **Authorize DigitalOcean** and grant permissions
5. You can cancel the app creation after authorization

**Option B: First Deployment (Automatic)**

The first time you push to `master`, the GitHub Action will prompt you to authorize the connection. Check the deployment logs for instructions.

### Step 4: Deploy Your App

Once secrets are configured, deployment happens automatically:

```bash
# Deploy to production (master branch)
git add .
git commit -m "Enable DigitalOcean deployment"
git push origin master
```

**Deployment Flow:**
1. GitHub Actions runs all tests and validations
2. Trains the ML model
3. Builds Docker container
4. Deploys to DigitalOcean App Platform
5. Runs health checks
6. Reports deployment URL

### Step 5: Monitor Deployment

1. **GitHub Actions**: https://github.com/iamdgarcia/mlops_template/actions
   - Watch the `MLOps Pipeline` workflow
   - Check `Deploy to Production` job logs
   - Look for deployment URL in logs

2. **DigitalOcean Dashboard**: https://cloud.digitalocean.com/apps
   - View app status and logs
   - Access deployment history
   - Monitor resource usage

### Step 6: Access Your Deployed API

After successful deployment, you'll get a URL like:
```
https://fraud-detection-api-xxxxx.ondigitalocean.app
```

**Test the API:**

```bash
# Health check
curl https://YOUR-APP-URL.ondigitalocean.app/health

# API documentation (Swagger UI)
open https://YOUR-APP-URL.ondigitalocean.app/docs

# Make a prediction
curl -X POST https://YOUR-APP-URL.ondigitalocean.app/predict \
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

## Multi-Environment Deployment

The pipeline supports three environments:

| Branch | Environment | URL Pattern | Auto-Deploy |
|--------|-------------|-------------|-------------|
| `master` | Production | `fraud-detection-api.ondigitalocean.app` | ✅ Yes |
| `staging` | Staging | `fraud-detection-api-staging.ondigitalocean.app` | ✅ Yes |
| `develop` | Development | `fraud-detection-api-dev.ondigitalocean.app` | ✅ Yes |

**Deploy to staging:**
```bash
git checkout -b staging
git push origin staging
```

**Deploy to development:**
```bash
git checkout -b develop
git push origin develop
```

## Configuration Files

### `.do/app.yaml` - App Platform Specification

Defines the application configuration:
- **Service name**: `fraud-detection-api`
- **Region**: NYC (New York)
- **Instance size**: `apps-s-1vcpu-0.5gb` ($5/mo)
- **Health check**: `/health` endpoint
- **Environment variables**: `PYTHONPATH`, `ENVIRONMENT`, `PYTHONUNBUFFERED`

**Upgrade instance size** (if app needs more resources):

Edit `.do/app.yaml`:
```yaml
instance_size_slug: apps-s-1vcpu-1gb  # $12/mo: 1GB RAM, 1 vCPU
```

Available tiers:
- `apps-s-1vcpu-0.5gb` - $5/mo (512MB RAM)
- `apps-s-1vcpu-1gb` - $12/mo (1GB RAM)
- `apps-s-1vcpu-2gb` - $24/mo (2GB RAM)

### `.github/workflows/mlops_pipeline.yml` - CI/CD Pipeline

Automated workflow:
1. **Security scanning** - Bandit, Safety
2. **Code quality** - Black, isort, flake8
3. **Unit tests** - pytest with coverage
4. **Data pipeline** - Generate and validate data
5. **Model training** - Train and save model
6. **Deployment** - Deploy to DigitalOcean
7. **Health checks** - Verify deployment

## Troubleshooting

### Issue: "Error: Could not find app"

**Solution**: App Platform needs GitHub authorization. Follow Step 3 to authorize.

### Issue: "Error: Authentication failed"

**Solution**: Check that `DIGITALOCEAN_ACCESS_TOKEN` is correctly set in GitHub Secrets.

### Issue: "Health check failed"

**Possible causes:**
1. App is still starting up (wait 1-2 minutes)
2. Insufficient resources (upgrade instance size)
3. Model file missing (check artifact upload)

**Debug steps:**
```bash
# Check logs in DigitalOcean dashboard
# Or use doctl CLI:
doctl apps list
doctl apps logs <APP_ID>
```

### Issue: "Build failed - Out of memory"

**Solution**: Upgrade instance size in `.do/app.yaml`:
```yaml
instance_size_slug: apps-s-1vcpu-1gb
```

### Issue: "Deployment timeout"

**Solution**: Increase health check initial delay in `.do/app.yaml`:
```yaml
health_check:
  initial_delay_seconds: 90  # Increased from 60
```

## Cost Management

### Current Configuration
- **Instance**: $5/mo (Basic tier)
- **Bandwidth**: 1TB included
- **Build minutes**: Unlimited
- **Total**: ~$5/mo

### Cost Optimization Tips

1. **Use smaller instance** for development:
   ```yaml
   # In .do/app.yaml for staging/dev
   instance_size_slug: apps-s-1vcpu-0.5gb
   ```

2. **Pause unused apps**:
   - Go to App Platform dashboard
   - Select app → Settings → Destroy
   - Redeploy anytime from GitHub

3. **Monitor usage**:
   - Check DigitalOcean dashboard for metrics
   - Set up billing alerts

## Advanced Features (Optional)

### Custom Domain

1. Add domain in `.do/app.yaml`:
   ```yaml
   domains:
   - domain: api.yourdomain.com
     type: PRIMARY
   ```

2. Configure DNS:
   - Add CNAME record pointing to App Platform URL

### Environment Variables

Add secrets in DigitalOcean dashboard:
1. Go to App → Settings → App-Level Environment Variables
2. Add variables (e.g., API keys, database URLs)
3. Mark as **Encrypted** for sensitive values

### Scaling

Enable auto-scaling in `.do/app.yaml`:
```yaml
instance_count: 1
autoscaling:
  min_instances: 1
  max_instances: 3
  metrics:
    cpu:
      percent: 75
```

### Monitoring & Alerts

1. **Built-in metrics**: CPU, memory, request rate
2. **Logs**: Real-time in dashboard or via `doctl apps logs`
3. **Alerts**: Configure in App Settings → Alerts

## Additional Resources

- **DigitalOcean App Platform Docs**: https://docs.digitalocean.com/products/app-platform/
- **App Spec Reference**: https://docs.digitalocean.com/products/app-platform/reference/app-spec/
- **GitHub Action Docs**: https://github.com/digitalocean/app_action
- **doctl CLI**: https://docs.digitalocean.com/reference/doctl/

## Support

For course-related questions or deployment issues:
1. Check GitHub Actions logs
2. Review DigitalOcean app logs
3. Consult this guide's troubleshooting section
4. Contact course instructor

---

**Quick Start Checklist:**
- [ ] Created DigitalOcean account
- [ ] Generated API token
- [ ] Added token to GitHub Secrets (`DIGITALOCEAN_ACCESS_TOKEN`)
- [ ] Authorized GitHub with App Platform
- [ ] Pushed to `master` branch
- [ ] Verified deployment in GitHub Actions
- [ ] Tested API health endpoint
- [ ] Accessed Swagger UI documentation

**Deployment successful!** 🚀
