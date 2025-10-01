# Implementation Roadmap and Tasks

This document lists prioritized tasks to prepare the repository for open-source release and future feature work. Each task follows the Action Documentation Template from the Spec-Driven Workflow.

## High Priority (release readiness)

### [TASK] - Add requirements and docs cleanup - TIMESTAMP
**Objective**: Ensure docs are accurate and dependencies are consistent
**Context**: Users expect a clear quick start and accurate requirements
**Execution**:
- Verify `requirements.txt` matches `REQUIREMENTS.md` and `REQUIREMENTS.md` clarifies optional vs required packages
- Update `README.md` sections to reflect current file locations
**Acceptance Criteria**:
- Documentation builds and quick start works locally following README
- No unresolved mismatches between requirements files

### [TASK] - Remove unused/dead code - TIMESTAMP
**Objective**: Remove or mark unused scripts and modules
**Context**: Reduce confusion for learners and maintainers
**Execution**:
- Search for unused modules referenced nowhere (run static analysis)
- Archive unused demo scripts to `scripts/archived/` with a note
**Acceptance Criteria**:
- No failing imports in main modules
- Tests pass locally

### [TASK] - Add Spec artifacts (`requirements.md`, `design.md`, `tasks.md`) - TIMESTAMP
**Objective**: Include spec-driven workflow artifacts required for handoff
**Execution**: Add `design.md` and `tasks.md` (this task)
**Acceptance Criteria**: Files present in repo and referenced in README

## Medium Priority

### [TASK] - Improve start_api.sh robustness & clarity - TIMESTAMP
**Objective**: Fix duplicated messages and add docker-compose fallback
**Context**: Startup script had duplicated strings and brittle docker handling
**Execution**: Update `start_api.sh` to handle modern `docker compose`, add safer stop logic, and improve messages
**Acceptance Criteria**: Script runs locally and in CI when invoked; no duplicate messages

### [TASK] - Add CONTRIBUTING.md and CODE_OF_CONDUCT.md - TIMESTAMP
**Objective**: Encourage community contributions
**Execution**: Create contributor guidelines and code of conduct
**Acceptance Criteria**: Files present, PR template added

## Low Priority / Future features

### [TASK] - CI pipeline (GitHub Actions)
**Objective**: Add unit test, lint and packaging checks on PRs
**Execution**: Provide workflows for tests, lint, build
**Acceptance Criteria**: Passing checks required on PRs

### [TASK] - Add model registry integration example (remote MLflow)
**Objective**: Teach how to configure MLflow with remote backend
**Acceptance Criteria**: Working example documented

## Maintenance

- Monthly review of notebooks to ensure reproducibility
- Update dependencies annually and run tests


*This task list follows the Spec-Driven Workflow requirement to maintain `tasks.md` as the source of truth for implementation plan.*
