#!/usr/bin/env python3
"""Run only the data preparation pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipelines import run_data_preparation


def main() -> None:
    """Run the data preparation pipeline."""
    print("Starting data preparation pipeline...\n")

    data_outputs = run_data_preparation(regenerate_data=True, persist=True)

    print(f"✓ Raw samples: {len(data_outputs['raw']):,}")
    print(f"✓ Clean samples: {len(data_outputs['clean']):,}")
    print(f"✓ Engineered features: {len(data_outputs['feature_names'])}")
    print(f"✓ Data files saved to: data/")

    print("\nData pipeline completed successfully.")


if __name__ == "__main__":
    main()
