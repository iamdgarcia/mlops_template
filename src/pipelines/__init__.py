"""Pipeline utilities for orchestrating the MLOps fraud detection workflow."""

from .data_pipeline import run_data_preparation


def run_training_pipeline(*args, **kwargs):
    from .training_pipeline import run_training_pipeline as _run_training_pipeline

    return _run_training_pipeline(*args, **kwargs)


__all__ = [
    "run_data_preparation",
    "run_training_pipeline",
]
