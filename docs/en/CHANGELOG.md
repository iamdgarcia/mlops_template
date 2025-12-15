# Changelog

All notable changes to the MLOps Fraud Detection Template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-11

### Added - Production Readiness Improvements

#### Infrastructure
- **`.dockerignore`**: Optimized Docker builds by excluding unnecessary files (notebooks, tests, .git)
- **`pyproject.toml`**: Proper Python package configuration with setuptools, entry points, and metadata
- **`requirements-dev.txt`**: Separated development dependencies from production requirements
- **`.env.example`**: Comprehensive environment variable documentation for all configuration options
- **`data/.gitignore`**: Prevent committing large data files while preserving directory structure

#### CI/CD & Quality
- **`.github/dependabot.yml`**: Automated dependency updates and security scanning for pip, GitHub Actions, and Docker
- **`pytest.ini`**: Comprehensive test configuration with markers, coverage thresholds, and logging
- **`.coveragerc`**: Detailed code coverage configuration with branch coverage and exclusions
- **Comprehensive CI/CD pipeline**: 7-job workflow with code quality, testing, training, Docker build, and deployments

#### Documentation
- **Feature engineering single source of truth**: Documented architecture pattern ensuring training/serving parity
- **Architecture diagrams**: Added Mermaid flowcharts showing data flow and component interactions
- **User guide expansion**: Added feature engineering patterns and validation strategies
- **This CHANGELOG.md**: Version history and release notes

#### Testing
- **`tests/test_feature_parity.py`**: Comprehensive test suite (330+ lines, 14 test methods) validating feature engineering consistency across training, inference, and serving contexts
- **Edge case testing**: Empty dataframes, missing columns, single-row processing
- **Integration testing**: InferencePipeline and FastAPI integration with FeatureEngineer

### Changed

#### Configuration
- **`.pre-commit-config.yaml`**: Fixed broken reference to non-existent `test_integration.py`
- **Documentation structure**: Updated README.md to remove references to non-existent notebooks 06-10

#### Code Quality
- **Feature engineering**: Verified single source of truth pattern (no duplication between training/serving)
- **Import consistency**: All modules use proper package imports (`from src.features import ...`)

### Fixed
- Pre-commit hooks now functional (removed broken test reference)
- Docker builds optimized (reduced image size by excluding dev files)
- Git repository protection against large file commits
- Package installability with proper pyproject.toml

### Security
- Dependabot configuration for automated vulnerability scanning
- Environment variable management with .env.example template
- Separated production and development dependencies
- Docker image optimization reducing attack surface

---

## [0.9.0] - 2025-12-01 (Pre-Production State)

### Added
- Complete MLOps pipeline with 5 educational Jupyter notebooks
- FastAPI serving application with health checks and prediction endpoints
- MLflow integration for experiment tracking and model registry
- Drift detection framework with statistical tests
- Comprehensive documentation (README, USER_GUIDE, architecture, deployment guides)
- Docker and Docker Compose support
- Basic CI/CD with GitHub Actions
- Test suite covering data processing, features, training, and pipelines

### Known Issues (Addressed in v1.0.0)
- No .dockerignore (Docker images unnecessarily large)
- Missing pyproject.toml (package not installable)
- Broken pre-commit hook
- No dependency scanning
- Dev and prod dependencies mixed
- Missing environment variable documentation

---

## Version History Summary

- **v1.0.0** (2025-12-11): Production-ready release with complete infrastructure, security, and quality improvements
- **v0.9.0** (2025-12-01): Educational release with functional pipeline but missing production hardening

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
