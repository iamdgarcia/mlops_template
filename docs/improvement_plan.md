# MLOps Template Improvement Plan

## Current Assessment

### Project Structure
- `src/` mixes pipelines, utilities, serving code, and scripts without a clear layering strategy.
- Configuration access is inconsistent — notebooks load YAML directly instead of reusing the shared `ConfigManager` utilities.
- There is no orchestrated training or data-prep entry point; multiple scripts duplicate the same logic.

### Core Modules
- `src/inference.py` contains duplicated class definitions and non-package-safe imports (`from features import ...`).
- The FastAPI app in `src/serving/main.py` re-implements feature engineering logic and relies on global state, diverging from the reusable pipeline in `src/features.py`.
- Drift detection utilities embed non-ASCII emojis and lack clear severity mapping useful for automation.
- Logging setup is scattered; reusable helpers are missing.

### Notebooks
- Each notebook performs configuration, data prep, and feature engineering ad hoc; very little reuse from `src/`.
- Narrative is strong but code cells are long and hard to follow for students; repeated imports and manual parameter setting hide best practices such as config-driven runs.
- Outputs (dataset exports, metrics) are written to ad hoc paths rather than orchestrated via the pipeline utilities.

### Testing & Automation
- `tests/` is empty — there is no automated verification of critical components (data validation, feature engineering, inference service).
- No linting or static checks run as part of the repository to ensure teaching-quality code.

## Improvement Objectives
1. **Establish a clean pipeline boundary** between data prep, feature engineering, training, and inference so notebooks teach orchestration rather than raw scripting.
2. **Unify configuration and logging** access across notebooks and modules by relying on `ConfigManager` and shared helpers.
3. **Refactor inference and serving code** to reuse the same FeatureEngineering path as training, eliminate duplication, and provide deterministic interfaces for demos.
4. **Strengthen monitoring utilities** by removing non-ASCII characters and surfacing actionable recommendation strings.
5. **Add a focused automated test suite** covering data validation, feature engineering, and inference contract.
6. **Refresh notebooks** so they import reusable components, surface key learning goals, and become easier to narrate on video.

## Implementation Roadmap
1. Create shared pipeline helpers (`src/pipelines/data_pipeline.py`, `src/pipelines/training_pipeline.py`) that orchestrate generation, validation, feature engineering, and persistence.
2. Refactor `src/inference.py` and `src/serving/main.py` to consume the new pipeline utilities, remove duplication, and align imports with package structure.
3. Update drift detection utilities to use ASCII-only messaging and structured severity enums.
4. Add regression tests under `tests/` covering data processor validation, feature engineering invariants, and inference pipeline predictions.
5. Simplify notebooks to:
   - Load configuration via `ConfigManager`
   - Call the new pipeline helpers for each stage
   - Provide concise, student-friendly markdown narration describing objectives and expected outputs.
6. Update README / docs with guidance on running the new pipelines and tests.

This plan balances hands-on learning with maintainable code, ensuring students see best practices without overwhelming implementation details.
