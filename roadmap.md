# Project Roadmap (English)

This roadmap prioritizes work to prepare the repository for public release and outlines the next features and improvements for the MLOps Fraud Detection Pipeline.

## Release Readiness (Next 2 weeks)
- Finalize documentation cleanup
  - Remove deprecated `REQUIREMENTS.md` and ensure `requirements.txt` is canonical
  - Update `README.md` to reference `design.md`, `tasks.md`, and `docs_review_plan.md`
- Validate quick start on a clean environment
  - Confirm virtualenv creation, dependency installation, and API startup
- Add community files
  - `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, PR template
- Add basic CI
  - GitHub Actions: run pytest, flake8, black check

## Short Term (1-3 months)
- Improve developer experience
  - Add pre-commit hooks (black, isort, flake8)
  - Add Makefile or CLI scripts for common tasks
- Enhance API testing and examples
  - Add integration tests for endpoints and sample curl examples
- Archive unused/demo scripts
  - Move to `scripts/archived/` with clear explanations

## Medium Term (3-6 months)
- CI/CD and release automation
  - Build release artifacts, test matrix for Python versions
- MLflow remote registry example
  - Document and provide configuration for remote MLflow server
- Add notebooks for deployment patterns
  - Kubernetes example, Docker-only deployment guide

## Long Term (6-12 months)
- Add more advanced monitoring
  - Real-time alerting examples, dashboards
- Extend to multimodal models and advanced feature stores
- Community contributions and examples
  - Invite community PRs for additional models and datasets

## Metrics for success
- All core tests passing in CI
- Docs validated by an external reviewer
- At least one community contribution (PR) within 3 months

*This roadmap is a living document and will be updated in `tasks.md` and via monthly documentation reviews.*
