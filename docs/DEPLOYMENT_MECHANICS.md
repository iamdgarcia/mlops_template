# Deployment Mechanics - Technical Documentation

This document explains the technical architecture and mechanics of deploying the fraud detection API to DigitalOcean App Platform.

## Overview

**Deployment Method**: Explicit deployment triggered by GitHub Actions using `digitalocean/app_action/deploy@v2`

**Why explicit deployment?**
- ✅ More control over deployment timing
- ✅ Immediate deployment after model training
- ✅ Clear deployment status in GitHub Actions logs
- ✅ No waiting for webhook detection delays
- ✅ Easier troubleshooting with detailed action logs
- ✅ Predictable deployment timing (no race conditions)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Workflow                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ git push origin master/staging/develop
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions CI/CD                         │
│                                                                  │
│  1. Trigger on push to master/staging/develop                   │
│  2. Run data processing pipeline                                │
│  3. Train model with latest data                                │
│  4. Package model + code as artifact                            │
│  5. Download deployment artifact                                │
│  6. Verify model files exist                                    │
│  7. Commit model to git [skip ci]                               │
│  8. Push to repository                                           │
│  9. EXPLICITLY DEPLOY using digitalocean/app_action/deploy@v2   │
│     └─> Triggers immediate deployment to DigitalOcean           │
│ 10. Wait for deployment to complete                             │
│ 11. Verify health check                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Deploy API call (with token authentication)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              DigitalOcean App Platform                           │
│                                                                  │
│  1. Receives deployment trigger from GitHub Actions             │
│  2. Authenticates using DIGITALOCEAN_ACCESS_TOKEN               │
│  3. Clones repository (includes committed model)                │
│  4. Reads .do/app.yaml specification                            │
│  5. Builds Docker image from Dockerfile                         │
│  6. Runs container health checks                                │
│  7. Deploys to cloud infrastructure (blue-green)                │
│  8. Updates routing (zero-downtime)                             │
│  9. Configures HTTPS and domain                                 │
│ 10. Returns deployment status to GitHub Actions                 │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
               Public HTTPS Endpoint
         https://fraud-detection-api.ondigitalocean.app
```

---

## Deployment Workflow Breakdown

### Step 1: Git Push Triggers CI/CD

When you push code to `master`, `staging`, or `develop` branches:

```bash
git push origin master  # Triggers production deployment
git push origin staging # Triggers staging deployment
git push origin develop # Triggers development deployment
```

GitHub Actions workflow (`.github/workflows/mlops_pipeline.yml`) is triggered based on the branch.

### Step 2: Model Training in CI

GitHub Actions runs the complete ML pipeline:

1. **Data Processing**: Load and prepare training data
2. **Feature Engineering**: Create features using `selected_features.json`
3. **Model Training**: Train model(s) and select the best one
4. **Artifact Creation**: Package model and configuration files

**Artifacts created:**
- `trained-models/` - Model files (*.joblib)
- `deployment-package/` - Model + configs ready for deployment

### Step 3: Commit Model to Repository

```yaml
- name: Commit model to repository
  run: |
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git config user.name "github-actions[bot]"
    git add models/*.joblib data/selected_features.json
    git diff --staged --quiet || git commit -m "chore: update trained model [skip ci]"
    git push
```

**Key points:**
- `[skip ci]` in commit message prevents infinite CI loop
- Model files are committed to git for version control
- Push updates the repository with latest trained model

### Step 4: Explicit Deployment

```yaml
- name: Deploy to DigitalOcean App Platform
  id: deploy
  uses: digitalocean/app_action/deploy@v2
  with:
    token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
    app_name: fraud-detection-api  # or -staging, -dev
```

**This action:**
1. Authenticates with DigitalOcean using the API token
2. Triggers deployment of the specified app
3. Waits for deployment to complete
4. Returns deployment metadata (URL, status, etc.)

### Step 5: Health Check Validation

```yaml
- name: Verify deployment
  run: |
    echo "🏥 Verifying production deployment..."
    sleep 30  # Give app time to start
    curl -f ${{ secrets.PRODUCTION_APP_URL }}/health || exit 1
    echo "✓ Production deployment successful"
```

**Validates:**
- Application is running
- Health endpoint responds with 200 OK
- API is accessible

---

## Configuration via GitHub Secrets

### Required Secrets

All secrets are configured in: **GitHub Repository → Settings → Secrets and variables → Actions**

| Secret Name | Example Value | Purpose |
|-------------|---------------|---------|
| `DIGITALOCEAN_ACCESS_TOKEN` | `dop_v1_abc123...` | Authenticate deployment API calls |
| `PRODUCTION_APP_URL` | `https://fraud-api-xxxxx.ondigitalocean.app` | Production health checks |
| `STAGING_APP_URL` | `https://fraud-api-staging-xxxxx.ondigitalocean.app` | Staging health checks |
| `DEV_APP_URL` | `https://fraud-api-dev-xxxxx.ondigitalocean.app` | Dev health checks |

### How to Set Secrets

**After running `./scripts/init_digitalocean_apps.sh`:**

1. The script creates `.env.digitalocean` with all values
2. Copy each value into GitHub:
   - Go to your repository on GitHub
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DIGITALOCEAN_ACCESS_TOKEN`, Value: your token
   - Repeat for each URL secret

---

## Multi-Environment Setup

### Three Separate Apps

The project uses three independent DigitalOcean apps:

1. **Production** (`fraud-detection-api`)
   - Branch: `master`
   - Environment: production
   - URL: https://fraud-detection-api-xxxxx.ondigitalocean.app

2. **Staging** (`fraud-detection-api-staging`)
   - Branch: `staging`
   - Environment: staging
   - URL: https://fraud-detection-api-staging-xxxxx.ondigitalocean.app

3. **Development** (`fraud-detection-api-dev`)
   - Branch: `develop`
   - Environment: development
   - URL: https://fraud-detection-api-dev-xxxxx.ondigitalocean.app

### Branch Strategy

```
develop     →  Development App   (rapid iteration)
   ↓
staging     →  Staging App       (pre-production testing)
   ↓
master      →  Production App    (stable releases)
```

**Workflow:**
1. Develop features on `develop` branch
2. Test in development environment
3. Merge to `staging` for integration testing
4. Merge to `master` for production release

---

## Initialization Script

### Using `./scripts/init_digitalocean_apps.sh`

This automated script creates all three apps:

```bash
# Authenticate with DigitalOcean
doctl auth init

# Run initialization
./scripts/init_digitalocean_apps.sh
```

**What it does:**

1. ✅ Validates prerequisites (doctl installed, authenticated, spec file exists)
2. ✅ Creates production app from `.do/app.yaml`
3. ✅ Creates staging app (modified for `staging` branch)
4. ✅ Creates development app (modified for `develop` branch)
5. ✅ Retrieves app IDs and URLs
6. ✅ Generates `.env.digitalocean` with all configuration
7. ✅ Displays setup instructions

**Output:**
```
📦 Production App
   Name: fraud-detection-api
   ID:   abc123...
   URL:  https://fraud-detection-api-xxxxx.ondigitalocean.app
   Branch: master

📦 Staging App
   Name: fraud-detection-api-staging
   ID:   def456...
   URL:  https://fraud-detection-api-staging-xxxxx.ondigitalocean.app
   Branch: staging

📦 Development App
   Name: fraud-detection-api-dev
   ID:   ghi789...
   URL:  https://fraud-detection-api-dev-xxxxx.ondigitalocean.app
   Branch: develop
```

---

## App Specification (`.do/app.yaml`)

### Key Configuration

```yaml
name: fraud-detection-api
region: nyc

services:
- name: api
  github:
    repo: iamdgarcia/mlops_template
    branch: master
    deploy_on_push: false  # We use explicit deployment
  
  dockerfile_path: Dockerfile
  
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb  # $5/month
  
  http_port: 8000
  
  health_check:
    http_path: /health
    initial_delay_seconds: 10
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  
  envs:
  - key: MODEL_PATH
    value: models/random_forest_final_model.joblib
    type: GENERAL
  - key: FEATURES_PATH
    value: data/selected_features.json
    type: GENERAL
```

**Important settings:**
- `deploy_on_push: false` - We control deployment via GitHub Actions
- `instance_size_slug` - Controls cost ($5/month for basic tier)
- `health_check` - Ensures app is healthy before routing traffic

---

## Troubleshooting

### Deployment Not Triggering

**Symptoms**: GitHub Actions runs but deployment doesn't happen

**Solutions:**
1. Check `DIGITALOCEAN_ACCESS_TOKEN` is set correctly
2. Verify app name matches in workflow and DigitalOcean
3. Check GitHub Actions logs for error messages
4. Ensure app exists: `doctl apps list`

### Health Check Failing

**Symptoms**: Deployment completes but health check returns non-200

**Solutions:**
1. Check app logs: `doctl apps logs <app-id> --type run`
2. Verify model file exists in repository: `ls models/*.joblib`
3. Check Dockerfile builds successfully: `docker build -t test .`
4. Verify health endpoint locally: `curl http://localhost:8000/health`
5. Check DigitalOcean console for build errors

### Model Not Found Error

**Symptoms**: `FileNotFoundError: models/random_forest_final_model.joblib`

**Solutions:**
1. Verify model was committed: `git log --oneline | grep "update trained model"`
2. Check .gitignore allows model files (should have `# *.joblib` commented out)
3. Verify deployment package includes model: Check GitHub Actions artifacts
4. Re-run training pipeline: Push code change to trigger re-training

### Deployment Takes Too Long

**Symptoms**: Deployment step times out or takes 5+ minutes

**Solutions:**
1. Check DigitalOcean status page: https://status.digitalocean.com
2. Reduce Docker image size (check Dockerfile optimization)
3. Use `.dockerignore` to exclude unnecessary files
4. Consider pre-building base images

---

## Best Practices

### 1. Use `[skip ci]` in Model Commits

Always include `[skip ci]` when committing models to prevent infinite CI loops:

```bash
git commit -m "chore: update trained model [skip ci]"
```

### 2. Monitor Deployment Logs

Check deployment status in GitHub Actions:
- Go to repository → Actions tab
- Select latest workflow run
- Review "Deploy to Production/Staging/Dev" job logs

### 3. Test Before Production

Follow the branch strategy:
1. Test in `develop` environment first
2. Promote to `staging` for integration tests
3. Deploy to `master` only when staging is stable

### 4. Keep Secrets Secure

- Never commit secrets to repository
- Rotate API tokens periodically
- Use GitHub environment protection rules for production

### 5. Version Your Models

Model commits provide automatic versioning:
```bash
git log --oneline models/
# Shows history of model updates
```

To rollback to a previous model:
```bash
git checkout <commit-hash> -- models/
git commit -m "chore: rollback to previous model [skip ci]"
```

---

## Comparison: Explicit Deploy vs Auto-Deploy

### Current Approach: Explicit Deployment

**Advantages:**
- ✅ Immediate deployment after model training
- ✅ Clear deployment status in GitHub Actions
- ✅ No webhook delays or race conditions
- ✅ Easier debugging with action logs
- ✅ Can retry failed deployments easily

**Trade-offs:**
- ⚠️ Requires DIGITALOCEAN_ACCESS_TOKEN in GitHub
- ⚠️ Deployment tied to CI/CD pipeline

### Alternative: Auto-Deploy (Git-based)

**Advantages:**
- ✅ Simpler setup (no deploy action needed)
- ✅ DigitalOcean handles entire lifecycle
- ✅ No secrets needed in GitHub Actions

**Trade-offs:**
- ⚠️ Webhook detection delays (30-90 seconds)
- ⚠️ Less visibility into deployment status
- ⚠️ Harder to troubleshoot issues
- ⚠️ Potential race conditions with multiple pushes

---

## Summary

**Deployment Flow:**
1. Push code → Triggers GitHub Actions
2. GitHub Actions → Trains model
3. Model committed → Version controlled in git
4. Explicit deploy → `digitalocean/app_action/deploy@v2`
5. DigitalOcean → Builds and deploys
6. Health check → Validates deployment
7. API live → Ready for requests

**Key Files:**
- `.github/workflows/mlops_pipeline.yml` - CI/CD pipeline
- `.do/app.yaml` - App Platform configuration
- `scripts/init_digitalocean_apps.sh` - Setup automation
- `.env.digitalocean` - Generated secrets file

**Next Steps:**
1. Run initialization script: `./scripts/init_digitalocean_apps.sh`
2. Configure GitHub Secrets from `.env.digitalocean`
3. Push to master to trigger first deployment
4. Monitor deployment in GitHub Actions and DigitalOcean console
