# Deployment Artifacts Strategy

## Overview

This document explains how model artifacts are handled in the CI/CD pipeline for deployment.

## The Challenge

When deploying ML models, we face a key question: **How do we get the trained model into the deployed container?**

### Options Considered

1. **Commit models to Git**  (Current approach)
   - Pros: Simple, works with all CI/CD systems, version controlled
   - Cons: Git isn't optimized for large binary files
   
2. **Use Git LFS**
   - Pros: Better for large files, still version controlled
   - Cons: Additional complexity, costs for storage, requires setup
   
3. **External artifact storage (S3, GCS, etc.)**
   - Pros: Scalable, doesn't bloat repository
   - Cons: More complex, requires cloud credentials, additional cost
   
4. **Container Registry** 
   - Pros: Purpose-built for artifacts
   - Cons: Requires registry setup, more steps in pipeline

## Current Approach: Git Commits

For this template/course project, we use the simplest approach that works:

### How It Works

1. **Training Phase** (GitHub Actions)
   ```yaml
   - Train model using scripts/run_training.py
   - Save model to models/random_forest_final_model.joblib (~10MB)
   - Upload as GitHub Actions artifact
   ```

2. **Deployment Phase** (GitHub Actions)
   ```yaml
   - Download artifact from training job
   - Commit model file to git repository
   - Push to GitHub (triggers DigitalOcean rebuild)
   - DigitalOcean pulls latest code + model
   - Docker builds container with model included
   ```

### Why This Works

- **Model size**: ~10MB (acceptable for Git)
- **Update frequency**: Only on training runs (not every commit)
- **Simplicity**: No external dependencies or complex setup
- **Transparency**: Model version matches git commit
- **Course-friendly**: Easy to understand and replicate

### File Handling

**.gitignore Configuration:**
```gitignore
# By default, ignore joblib files
*.joblib

# But allow models in the models/ directory (commented out)
# This allows CI to commit trained models
# !models/*.joblib
```

**Models Committed:**
- `models/random_forest_final_model.joblib` - Trained classifier
- `data/selected_features.json` - Feature configuration  
- `data/training_summary.json` - Training metrics

### Git Commit Message

The CI uses `[skip ci]` to prevent infinite loops:
```bash
git commit -m "chore: update trained model [skip ci]"
```

This prevents the commit from triggering another CI run.

## Alternative: Artifact Storage (Future Enhancement)

For production systems with larger models or frequent retraining, consider:

### Using S3/GCS

```python
# In serving code
import boto3

def load_model_from_s3():
    s3 = boto3.client('s3')
    s3.download_file(
        'my-models-bucket',
        'fraud-detector/v1.0.0/model.joblib',
        '/tmp/model.joblib'
    )
    return joblib.load('/tmp/model.joblib')
```

### Using MLflow Model Registry

```python
# In serving code  
import mlflow

model_uri = "models:/fraud-detector/production"
model = mlflow.pyfunc.load_model(model_uri)
```

### Using DigitalOcean Spaces

```python
# Similar to S3, using Spaces API
import boto3

spaces = boto3.client('s3',
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id=os.getenv('SPACES_KEY'),
    aws_secret_access_key=os.getenv('SPACES_SECRET')
)
```

## Best Practices

### When to Use Git Commits
- Models < 50MB
- Infrequent retraining (daily/weekly)
- Team size < 10
- Educational/template projects
- Simple deployment pipelines

### When to Use Artifact Storage
- Models > 50MB
- Frequent retraining (hourly)
- Large teams
- Multiple model versions in production
- A/B testing requirements
- Regulatory compliance needs

## Monitoring Artifact Size

Keep an eye on repository size:

```bash
# Check repository size
du -sh .git/

# Check model file sizes
ls -lh models/*.joblib

# See largest files in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort --numeric-sort --key=2 | \
  tail -10
```

If `.git/` exceeds 500MB, consider:
1. Using Git LFS
2. Moving to artifact storage
3. Cleaning git history (careful!)

## Migration Path

To migrate from Git commits to artifact storage:

1. Set up artifact storage (S3/Spaces/MLflow)
2. Update `src/serving/main.py` to download from storage
3. Add credentials to deployment environment
4. Remove model files from repository
5. Update `.gitignore` to ignore models
6. Update CI to push to artifact storage instead of git

## Conclusion

For this MLOps template, **Git commits provide the best balance of simplicity and functionality**. The approach is:

 Easy to understand  
 Easy to replicate  
 Version controlled  
 No external dependencies  
 Works with free tier services  

This makes it ideal for learning, teaching, and small production deployments.

---

**Last Updated**: December 12, 2025  
**Model Size**: ~10MB  
**Repository Size**: <100MB
