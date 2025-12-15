# Dependencies Guide

This document explains the dependencies used in this MLOps fraud detection project and their purposes.

## Core Dependencies

### Data Science & Machine Learning
- **pandas (~=1.5.0)**: The foundational library for data manipulation and analysis. Used for loading, cleaning, and transforming transaction data.
- **numpy (~=1.24.0)**: Provides efficient numerical operations and array handling. Used throughout for mathematical computations.
- **scikit-learn (~=1.3.0)**: The main machine learning library containing:
  - Classification algorithms (Logistic Regression, Random Forest)
  - Model evaluation metrics
  - Data preprocessing utilities
  - Cross-validation tools
- **xgboost (~=2.0.0)**: Advanced gradient boosting library. Optional - can be disabled in configuration if not needed.

### MLOps Tools
- **mlflow (~=2.7.0)**: Complete MLOps platform providing:
  - Experiment tracking (log parameters, metrics, artifacts)
  - Model registry (version control for models)
  - Model deployment utilities
  - UI for visualizing experiments

### API & Web Framework
- **fastapi (~=0.100.0)**: Modern, fast web framework for building APIs with:
  - Automatic API documentation (Swagger UI)
  - Data validation via Pydantic
  - Async support for high performance
- **uvicorn (~=0.23.0)**: Lightning-fast ASGI server to run FastAPI applications
- **pydantic (~=2.0.0)**: Data validation and settings management using Python type annotations

### Configuration & Utilities
- **pyyaml (~=6.0)**: Parse YAML configuration files (training_config.yaml, serving_config.yaml)
- **python-multipart (~=0.0.6)**: Handle multipart form data in API requests

## Development Tools

### Testing
- **pytest (~=7.4.0)**: Modern testing framework with:
  - Simple test discovery
  - Powerful fixtures
  - Detailed failure reporting
- **pytest-cov (~=4.1.0)**: Code coverage plugin for pytest to measure test coverage

### Code Quality
- **black (~=23.0.0)**: Opinionated code formatter ensuring consistent style
- **flake8 (~=6.0.0)**: Linting tool to catch common errors and style issues
- **isort (~=5.12.0)**: Automatically organize and sort import statements

## Visualization (Notebook Support)

- **matplotlib (~=3.7.0)**: Basic plotting library for charts and graphs
- **seaborn (~=0.12.0)**: Statistical visualization built on matplotlib with beautiful defaults
- **plotly (~=5.15.0)**: Interactive visualizations and dashboards

## Jupyter Environment

- **jupyter (~=1.0.0)**: Complete Jupyter notebook environment
- **ipykernel (~=6.25.0)**: IPython kernel allowing Python code execution in notebooks

## HTTP Clients

- **requests (~=2.31.0)**: Simple, elegant HTTP library for API testing and interaction
- **httpx (~=0.24.0)**: Modern async-capable HTTP client (used by FastAPI test client)

## Version Pinning Strategy

This project uses **compatible release** pinning (`~=`):
- `pandas~=1.5.0` allows versions `>=1.5.0` and `<1.6.0`
- This permits bug fixes but prevents breaking changes
- For stricter reproducibility in production, consider exact pinning (`==`)

## Optional Dependencies

The following are mentioned in configuration but not installed by default:

### Monitoring (Planned Features)
- **prometheus-client**: Export metrics to Prometheus monitoring system
- **streamlit**: Build interactive dashboards for model monitoring

To install optional dependencies:
```bash
pip install prometheus-client~=0.17.0
pip install streamlit~=1.25.0
```

## Installation

### Standard Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Minimal Installation (API Only)
If you only need to run the API with a pre-trained model:
```bash
pip install pandas numpy scikit-learn mlflow fastapi uvicorn pydantic pyyaml
```

### Development Installation
For contributing to the project:
```bash
pip install -r requirements.txt
# All tools including pytest, black, flake8 are included
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`, ensure:
1. Virtual environment is activated
2. Dependencies are installed: `pip install -r requirements.txt`
3. For Jupyter, the kernel points to your venv: `python -m ipykernel install --user --name=mlops_env`

### Version Conflicts
If pip reports version conflicts:
1. Create a fresh virtual environment
2. Upgrade pip: `pip install --upgrade pip`
3. Install dependencies: `pip install -r requirements.txt`

### XGBoost Installation Issues
XGBoost may require additional system dependencies on some platforms:
- **Linux**: Usually works out of the box
- **macOS**: May need `brew install libomp`
- **Windows**: Use pre-built wheels from PyPI

If XGBoost installation fails, you can disable it:
1. Comment out `xgboost~=2.0.0` in requirements.txt
2. Set `enabled: false` for XGBoost in `configs/training_config.yaml`

## Dependency Updates

To check for outdated packages:
```bash
pip list --outdated
```

To update a specific package:
```bash
pip install --upgrade package-name
```

**Note**: Always test thoroughly after updating dependencies, as new versions may introduce breaking changes.

## Security Considerations

For production deployments:
1. Regularly update dependencies to get security patches
2. Use tools like `pip-audit` or `safety` to check for known vulnerabilities
3. Consider using `pip-tools` or `poetry` for more advanced dependency management

```bash
# Check for security vulnerabilities
pip install pip-audit
pip-audit
```
