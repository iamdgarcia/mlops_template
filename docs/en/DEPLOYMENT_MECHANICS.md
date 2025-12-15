# Deployment Mechanics - Technical Documentation

This document explains the technical architecture and mechanics of deploying the fraud detection API to DigitalOcean App Platform.

## Overview

**Deployment Method**: Automatic deployment via git push (DigitalOcean webhook)

**Why auto-deploy?**
-  Simpler setup - no API tokens or secrets to manage
-  DigitalOcean handles the entire deployment lifecycle
-  Git-based workflow aligns with standard practices
-  Automatic deployments on every push to tracked branches
-  No GitHub Actions secrets required after initial setup
-  Easier to maintain and audit

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Workflow                          │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                  │
             │ git push (code)                  │ Manual: Retrain Model
             ▼                                  ▼
┌─────────────────────────────┐  ┌──────────────────────────────────┐
│   GitHub Actions - CI       │  │  GitHub Actions - Model Retrain  │
│                             │  │                                  │
│  1. Security scan           │  │  1. Select environment (manual)  │
│  2. Code quality checks     │  │  2. Run data pipeline            │
│  3. Unit tests              │  │  3. Train model                  │
│  4.  Pass/Fail feedback   │  │  4. Commit model to git [skip ci]│
│                             │  │  5. Push to repository           │
│  NO model training          │  │  6. Optional: Create release     │
│  NO deployment              │  │                                  │
└─────────────────────────────┘  └──────────────┬───────────────────┘
                                                 │
                                                 │ Git Push (model commit)
                                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              DigitalOcean App Platform                           │
│                                                                  │
│  1. Detects git push via GitHub webhook                         │
│  2. Verifies branch matches app configuration                   │
│  3. Clones repository (includes committed model)                │
│  4. Reads .do/app.yaml specification                            │
│  5. Builds Docker image from Dockerfile                         │
│  6. Runs container health checks                                │
│  7. Deploys to cloud infrastructure (blue-green)                │
│  8. Updates routing (zero-downtime)                             │
│  9. Configures HTTPS and domain                                 │
│ 10. App is live and serving requests                            │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
               Public HTTPS Endpoint
         https://fraud-detection-api.ondigitalocean.app
```

---

## Deployment Workflow Breakdown

### Workflow 1: Continuous Integration (CI)

**Trigger**: Every push or pull request to `master`, `staging`, or `develop` branches

**Workflow file**: `.github/workflows/ci.yml`

**Purpose**: Validate code quality and ensure tests pass - NO model training or deployment

**Jobs:**
1. **Security Scan**: Safety checks and Bandit security linting
2. **Code Quality**: Black formatting, isort imports, flake8 linting
3. **Unit Tests**: pytest with coverage reporting

**Result**: Fast feedback on code quality (typically completes in 2-3 minutes)

---

### Workflow 2: Model Retraining & Deployment

**Trigger**: **Manual only** via GitHub Actions UI

**Workflow file**: `.github/workflows/model-retrain.yml`

**Purpose**: Train a new model and deploy it to a specific environment

**How to trigger:**
1. Go to GitHub Actions tab
2. Select "Model Retraining & Deployment" workflow
3. Click "Run workflow"
4. Choose:
   - **Environment**: development, staging, or production
   - **Create release**: true/false (optional GitHub release with artifacts)
5. Click "Run workflow" button

**Jobs:**

#### 1. Determine Environment
Maps the selected environment to the appropriate branch:
- `production` → `master` branch
- `staging` → `staging` branch  
- `development` → `develop` branch

#### 2. Data Pipeline
- Checks out the target branch
- Runs data generation and processing
- Creates training dataset
- Uploads artifacts for next job

#### 3. Model Training
- Downloads data artifacts
- Trains model with latest data
- Validates model performance
- Uploads trained model artifacts

#### 4. Deploy to Git
- Downloads trained model
- Commits model to the target branch with `[skip ci]`
- Pushes to repository
- Triggers DigitalOcean auto-deploy via webhook

#### 5. Create Release (Optional)
- Creates GitHub release with model artifacts
- Includes training metadata and metrics
- Tags release with timestamp and environment

**Deployment flow:**
```
Manual Trigger → Train Model → Commit to Git → Push → DO Webhook → Auto-Deploy
```

---

### Workflow 3: Drift Monitoring

**Trigger**: Daily at 2 AM UTC (or manual)

**Workflow file**: `.github/workflows/drift-monitoring.yml`

**Purpose**: Monitor for data drift and alert when detected

**Jobs:**
1. **Drift Detection**: Runs statistical tests on production data
2. **Create Issue**: Automatically creates GitHub issue if drift detected

**Issue includes**:
- Drift detection results
- Timestamp and workflow run link
- Instructions for manual model retraining

---

### Step 1: Code Changes (CI Pipeline)

When you push code to any branch:

```bash
git push origin develop  # Triggers CI workflow only
```

GitHub Actions runs CI workflow (`.github/workflows/ci.yml`):
-  Security scans
-  Code quality checks  
-  Unit tests
-  NO model training
-  NO deployment

**Fast feedback** - completes in 2-3 minutes

---

### Step 2: Manual Model Retraining

When you need to retrain the model:

1. **Navigate to Actions**: Go to repository → Actions tab
2. **Select workflow**: Click "Model Retraining & Deployment"
3. **Run workflow**: Click "Run workflow" button
4. **Configure**:
   - Select environment (dev/staging/prod)
   - Choose whether to create release
5. **Execute**: Click "Run workflow"

**What happens:**

**What happens:**

1. **Data Processing**: Load and prepare training data
2. **Feature Engineering**: Create features using `selected_features.json`
3. **Model Training**: Train model(s) and select the best one
4. **Artifact Creation**: Package model and configuration files
5. **Git Commit**: Commit model to target branch with detailed message
6. **Git Push**: Push triggers DigitalOcean webhook
7. **Auto-deploy**: DigitalOcean detects push and deploys automatically

**Artifacts created:**
- `trained-models/` - Model files (*.joblib)
- `data/selected_features.json` - Feature configuration
- `data/training_summary.json` - Training metrics

---

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
- `[skip ci]` in commit message prevents infinite CI loop (won't trigger CI workflow)
- Model files are committed to git for version control
- Push updates the repository with latest trained model
- Detailed commit message includes environment, timestamp, and workflow run link

---

### Step 4: Automatic Deployment via Webhook

After the model is committed and pushed, DigitalOcean automatically detects the push via GitHub webhook.

**Configuration in `.do/app.yaml`:**
```yaml
services:
- name: api
  github:
    repo: iamdgarcia/mlops_template
    branch: master
    deploy_on_push: true  # Enables automatic deployment
```

**This triggers:**
1. DigitalOcean detects push to configured branch (`master`, `staging`, or `develop`)
2. Clones the repository (including the newly committed model)
3. Reads `.do/app.yaml` for build configuration
4. Builds Docker image from `Dockerfile`
5. Deploys using blue-green deployment (zero-downtime)
6. Runs health checks on `/health` endpoint
7. Routes traffic to new deployment once healthy

**Deployment typically completes in 60-90 seconds.**

### Step 5: Monitor Deployment

**DigitalOcean Dashboard:**
- View deployment progress: https://cloud.digitalocean.com/apps
- Check build logs for errors
- Monitor runtime logs
- View deployment history

**Verify deployment:**
```bash
# Health check
curl https://your-app.ondigitalocean.app/health

# Check app info with doctl
doctl apps list
doctl apps get <APP_ID>
```

---

## Initial Setup via doctl CLI

### Required One-Time Setup

Before deploying, you need to create the DigitalOcean apps and authorize GitHub access.

**Using the automated script:**

```bash
# Install and authenticate doctl
doctl auth init

# Run initialization script
./scripts/init_digitalocean_apps.sh
```

**This script:**
1. Creates three apps (production, staging, development)
2. Configures each with correct branch and `deploy_on_push: true`
3. Sets up GitHub repository authorization
4. Generates `.env.digitalocean` with app URLs and IDs

**No GitHub secrets required!** After setup, deployments happen automatically via git push.

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

1.  Validates prerequisites (doctl installed, authenticated, spec file exists)
2.  Creates production app from `.do/app.yaml`
3.  Creates staging app (modified for `staging` branch)
4.  Creates development app (modified for `develop` branch)
5.  Retrieves app IDs and URLs
6.  Generates `.env.digitalocean` with all configuration
7.  Displays setup instructions

**Output:**
```
 Production App
   Name: fraud-detection-api
   ID:   abc123...
   URL:  https://fraud-detection-api-xxxxx.ondigitalocean.app
   Branch: master

 Staging App
   Name: fraud-detection-api-staging
   ID:   def456...
   URL:  https://fraud-detection-api-staging-xxxxx.ondigitalocean.app
   Branch: staging

 Development App
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

### Current Approach: Auto-Deploy (Git-based)

**Advantages:**
-  Simpler setup (no deploy action needed)
-  DigitalOcean handles entire lifecycle
-  No secrets needed in GitHub Actions
-  Standard git-based workflow
-  Easier to maintain and audit

**Trade-offs:**
-  Webhook detection delays (30-90 seconds)
-  Less visibility into deployment status from GitHub Actions
-  Must check DigitalOcean dashboard for deployment progress

### Alternative: Explicit Deployment (GitHub Actions)

**Advantages:**
-  Immediate deployment after model training
-  Clear deployment status in GitHub Actions logs
-  Can run health checks directly in workflow
-  Easier debugging with action logs

**Trade-offs:**
-  Requires DIGITALOCEAN_ACCESS_TOKEN in GitHub
-  Requires APP_URL secrets for health checks
-  More complex workflow
-  Potential for double-deployment if both enabled

---

## Summary

**Three Separate Workflows:**

1. **CI (`ci.yml`)** - Runs on every push/PR
   - Security scans, code quality, unit tests
   - Fast feedback (2-3 minutes)
   - NO model training or deployment

2. **Model Retrain (`model-retrain.yml`)** - Manual trigger only
   - Choose environment (dev/staging/prod)
   - Train model → Commit to git → Auto-deploy
   - Optional: Create GitHub release
   - Controlled, on-demand model updates

3. **Drift Monitoring (`drift-monitoring.yml`)** - Daily at 2 AM UTC
   - Detects data drift
   - Creates GitHub issues with alerts
   - Links to manual retrain workflow

**Deployment Flow:**
1. Push code → Triggers CI (tests only)
2. Manual: Trigger model retrain → Trains model
3. Model committed → Version controlled in git
4. Git push → Triggers DigitalOcean webhook
5. DigitalOcean → Builds and deploys automatically
6. Health check → Validates deployment (via DigitalOcean)
7. API live → Ready for requests

**Key Files:**
- `.github/workflows/ci.yml` - Continuous integration
- `.github/workflows/model-retrain.yml` - Model retraining (manual)
- `.github/workflows/drift-monitoring.yml` - Daily drift checks
- `.do/app.yaml` - App Platform configuration with `deploy_on_push: true`
- `scripts/init_digitalocean_apps.sh` - Setup automation
- `.env.digitalocean` - Generated app URLs and IDs (not committed)

**Next Steps:**
1. Run initialization script: `./scripts/init_digitalocean_apps.sh`
2. Push code to trigger CI and verify tests pass
3. Manually trigger model retrain for initial deployment
4. Monitor deployment in DigitalOcean console: https://cloud.digitalocean.com/apps
5. Verify API health: `curl https://your-app.ondigitalocean.app/health`
