# MLOps Template Documentation

Complete documentation for the Fraud Detection MLOps Pipeline project.

##  Documentation Guide

Follow this reading order for a complete understanding of the project:

### 1 Getting Started (Start Here!)

**New to the project? Start here:**

1. **[Requirements](getting-started/requirements.md)** - System requirements and prerequisites
2. **[Quick Start Guide](getting-started/quick-start.md)** - Get up and running in 15 minutes
3. **[User Guide](getting-started/user-guide.md)** - Comprehensive guide for users

**Recommended path**: Requirements → Quick Start → User Guide

---

### 2 Deployment

**Setting up production deployment:**

1. **[Deployment Overview](deployment/overview.md)** - High-level deployment architecture
2. **[Setup Guide](deployment/setup-guide.md)** - Step-by-step DigitalOcean deployment
3. **[Deployment Mechanics](DEPLOYMENT_MECHANICS.md)** - Technical deep dive into workflows
4. **[Workflow Changes](deployment/workflow-changes.md)** - Understanding the CI/CD pipelines
5. **[Artifacts Strategy](deployment/artifacts-strategy.md)** - How models are versioned
6. **[Troubleshooting](deployment/troubleshooting.md)** - Common issues and solutions

**Recommended path**: Overview → Setup Guide → Deployment Mechanics

---

### 3 API Usage

**Working with the deployed API:**

1. **[API Guide](api/guide.md)** - Complete API reference and examples

---

### 4 Development

**For contributors and developers:**

1. **[Architecture](architecture.md)** - System architecture and design decisions
2. **[Changelog](CHANGELOG.md)** - Version history and changes

---

##  Quick Links

### For First-Time Users
- **I want to understand what this project does** → [README](overview.md)
- **I want to run the project locally** → [Quick Start](getting-started/quick-start.md)
- **I want to deploy to production** → [Setup Guide](deployment/setup-guide.md)

### For Developers
- **I want to understand the architecture** → [Architecture](architecture.md)
- **I want to contribute** → [README](overview.md#contributing)
- **I need to troubleshoot** → [Troubleshooting](deployment/troubleshooting.md)

### For Operations
- **I need to retrain the model** → [Deployment Mechanics](DEPLOYMENT_MECHANICS.md#workflow-2-model-retraining--deployment)
- **I need to monitor drift** → [Deployment Mechanics](DEPLOYMENT_MECHANICS.md#workflow-3-drift-monitoring)
- **I need to check deployment status** → [Troubleshooting](deployment/troubleshooting.md)

---

##  Documentation Structure

```
docs/
├── README.md                          # This file - documentation index
├── architecture.md                    # System architecture
├── DEPLOYMENT_MECHANICS.md            # Technical deployment guide
│
├── getting-started/
│   ├── requirements.md                # Prerequisites and system requirements
│   ├── quick-start.md                 # 15-minute setup guide
│   └── user-guide.md                  # Comprehensive user manual
│
├── deployment/
│   ├── overview.md                    # Deployment architecture overview
│   ├── setup-guide.md                 # DigitalOcean deployment setup
│   ├── workflow-changes.md            # CI/CD workflow documentation
│   ├── artifacts-strategy.md          # Model versioning approach
│   ├── troubleshooting.md             # Common issues and fixes
│   └── legacy-guide.md                # Old deployment guide (deprecated)
│
├── api/
│   └── guide.md                       # API reference and examples
│
└── development/
    └── (future: contributing guide, coding standards, etc.)
```

---

##  Learning Paths

### Path 1: User Journey (Just want to use the API)
1. [README](overview.md) - Overview
2. [Quick Start](getting-started/quick-start.md) - Setup
3. [API Guide](api/guide.md) - Usage

**Time**: ~30 minutes

---

### Path 2: Deployment Journey (Want to deploy your own)
1. [README](overview.md) - Overview
2. [Requirements](getting-started/requirements.md) - Prerequisites
3. [Deployment Overview](deployment/overview.md) - Architecture
4. [Setup Guide](deployment/setup-guide.md) - Step-by-step setup
5. [Deployment Mechanics](DEPLOYMENT_MECHANICS.md) - Technical details

**Time**: ~2 hours

---

### Path 3: Developer Journey (Want to contribute or customize)
1. [README](overview.md) - Overview
2. [Architecture](architecture.md) - System design
3. [User Guide](getting-started/user-guide.md) - Features and usage
4. [Deployment Mechanics](DEPLOYMENT_MECHANICS.md) - CI/CD workflows
5. [Quick Start](getting-started/quick-start.md) - Local development

**Time**: ~3 hours

---

##  Workflow Overview

### Continuous Integration (CI)
Every code push triggers automated testing:
- Security scans
- Code quality checks
- Unit tests

**No model training, no deployment** - just fast feedback (~2-3 minutes)

### Model Retraining (Manual)
Train and deploy models on-demand:
1. Go to GitHub Actions
2. Select "Model Retraining & Deployment"
3. Choose environment (dev/staging/prod)
4. Trigger workflow

**Complete flow**: Data pipeline → Training → Git commit → Auto-deploy

### Drift Monitoring (Daily)
Automatic drift detection:
- Runs daily at 2 AM UTC
- Creates GitHub issues on drift
- Includes retraining instructions

---

##  External Resources

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **GitHub Actions**: https://docs.github.com/en/actions
- **FastAPI**: https://fastapi.tiangolo.com/
- **MLflow**: https://mlflow.org/docs/latest/index.html

---

##  Need Help?

1. **Check the docs** - Most questions are answered here
2. **Search issues** - Someone may have had the same problem
3. **Troubleshooting guide** - [deployment/troubleshooting.md](deployment/troubleshooting.md)
4. **Create an issue** - If all else fails

---

##  Quick Reference Card

| Task | Documentation |
|------|---------------|
| First-time setup | [Quick Start](getting-started/quick-start.md) |
| Deploy to production | [Setup Guide](deployment/setup-guide.md) |
| Use the API | [API Guide](api/guide.md) |
| Retrain model | [Deployment Mechanics](DEPLOYMENT_MECHANICS.md#workflow-2-model-retraining--deployment) |
| Check deployment | [Troubleshooting](deployment/troubleshooting.md) |
| Understand architecture | [Architecture](architecture.md) |
| Fix common issues | [Troubleshooting](deployment/troubleshooting.md) |

---

**Last Updated**: December 12, 2025  
**Documentation Version**: 2.0
