# GitHub Actions Workflow Changes

## Summary

The MLOps pipeline has been refactored into three separate, focused workflows for better separation of concerns and control.

## New Workflow Structure

### 1. CI Workflow (`ci.yml`)
**Trigger**: Every push or pull request to main branches
**Purpose**: Fast feedback on code quality
**Jobs**:
- Security vulnerability scanning
- Code quality checks (black, isort, flake8)
- Unit tests with coverage

**Duration**: ~2-3 minutes
**No model training or deployment**

### 2. Model Retraining Workflow (`model-retrain.yml`)
**Trigger**: Manual only (workflow_dispatch)
**Purpose**: Train and deploy models on-demand
**Options**:
- Select environment (development/staging/production)
- Choose whether to create GitHub release

**Jobs**:
1. Determine environment and map to branch
2. Run data pipeline
3. Train model
4. Commit model to git
5. Auto-deploy via DigitalOcean webhook
6. (Optional) Create GitHub release

**Duration**: ~8-12 minutes

### 3. Drift Monitoring Workflow (`drift-monitoring.yml`)
**Trigger**: Daily at 2 AM UTC (or manual)
**Purpose**: Detect data drift and alert
**Actions**:
- Run drift detection tests
- Create GitHub issue if drift detected
- Issue includes instructions for manual retraining

**Duration**: ~1-2 minutes

## Key Benefits

✅ **Faster CI**: Code changes get test feedback in 2-3 minutes
✅ **Controlled Model Updates**: Retrain only when needed, manually triggered
✅ **Environment Selection**: Deploy to dev/staging/prod as needed
✅ **No Secrets Required**: Auto-deploy via git webhook
✅ **Proactive Monitoring**: Daily drift detection with alerts
✅ **Model Versioning**: Optional GitHub releases with artifacts

## How to Use

### Running CI (Automatic)
```bash
# Just push code - CI runs automatically
git push origin develop
```

### Retraining a Model (Manual)
1. Go to GitHub Actions tab
2. Select "Model Retraining & Deployment"
3. Click "Run workflow"
4. Choose environment and options
5. Click "Run workflow" button

### Checking Drift (Automatic Daily)
- Runs automatically at 2 AM UTC
- Check Issues tab for drift alerts
- Follow issue instructions to retrain

## Migration Notes

**Removed**:
- `.github/workflows/mlops_pipeline.yml` (monolithic workflow)

**Added**:
- `.github/workflows/ci.yml`
- `.github/workflows/model-retrain.yml`
- `.github/workflows/drift-monitoring.yml`

**Updated**:
- `docs/DEPLOYMENT_MECHANICS.md` - Reflects new workflow structure
- `SETUP_SUMMARY.md` - Updated setup instructions
- `DEPLOYMENT_GUIDE.md` - Auto-deploy approach
- `README.md` - Simplified deployment section

## Deployment Flow

```
Developer Push → CI (tests) ✓
                 ↓
            (code is good)
                 ↓
Manual Trigger → Model Retrain
                 ↓
            Train Model
                 ↓
         Commit to Git [skip ci]
                 ↓
            Git Push
                 ↓
        DO Webhook Detects
                 ↓
         Auto-Deploy ✓
```

## Example Workflow Run

**Scenario**: Retrain production model

1. **Trigger**: Go to Actions → Model Retraining & Deployment → Run workflow
2. **Select**: Environment: production, Create release: true
3. **Run**: Click "Run workflow"
4. **Monitor**: Watch progress in Actions tab
5. **Result**: Model trained, committed to master, deployed to production
6. **Release**: GitHub release created with model artifacts
7. **Verify**: Check app at https://fraud-detection-api.ondigitalocean.app/health

**Timeline**:
- 0:00 - Workflow starts
- 2:00 - Data pipeline complete
- 8:00 - Model training complete
- 9:00 - Model committed to git
- 9:30 - DigitalOcean deployment starts
- 11:00 - Deployment complete, app healthy
- 12:00 - GitHub release created

## Troubleshooting

**CI fails on push**:
- Check security scan, code quality, or test failures
- Fix issues and push again

**Model retrain fails**:
- Check workflow logs in Actions tab
- Verify data pipeline ran successfully
- Ensure model training completed

**Deployment not happening**:
- Verify `deploy_on_push: true` in `.do/app.yaml`
- Check DigitalOcean dashboard for deployment status
- Ensure model was committed to git

**Drift alerts too noisy**:
- Adjust drift detection thresholds in `drift-monitoring.yml`
- Consider weekly instead of daily runs
