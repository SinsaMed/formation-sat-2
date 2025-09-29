"""Simulation scripts package providing scaffolding for scenario workflows."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
for candidate in (SRC_DIR, PROJECT_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from .scenario_execution import run_scenario
from .baseline_generation import generate_baseline
from .metric_extraction import extract_metrics as extract_metrics_summary
from . import extract_metrics as extract_metrics  # type: ignore[F401]  # Re-export module
from .configuration import load_scenario, resolve_scenario_path

__all__ = [
    "run_scenario",
    "generate_baseline",
    "extract_metrics",
    "extract_metrics_summary",
    "load_scenario",
    "resolve_scenario_path",
]
