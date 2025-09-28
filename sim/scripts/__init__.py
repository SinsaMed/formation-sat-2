"""Simulation scripting package for formation flight workflows.

This package groups the scaffolded modules that will host the
formation-flying simulation logic. The modules are intentionally kept as
lightweight placeholders so that subsequent tasks can introduce concrete
implementations without disrupting interoperability with Systems Tool Kit
(STK) 11.2 exports.

Modules
=======
1. :mod:`scenario_execution` orchestrates the loading and execution of
   STK scenarios once the helper functions are implemented.
2. :mod:`baseline_generation` prepares reference trajectories or
   parameters that will serve as baselines for comparative studies.
3. :mod:`metric_extraction` will collate simulation outputs into mission
   design metrics ready for validation against ``tools/stk_export.py``.

Usage
======
1. Import the desired functions from the respective modules once they are
   implemented.
2. Maintain STK 11.2 data compatibility by cross-checking any new data
   products with ``tools/stk_export.py`` during development.
"""

from .scenario_execution import execute_scenario, prepare_scenario_context
from .baseline_generation import generate_baseline_conditions
from .metric_extraction import extract_metrics

__all__ = [
    "execute_scenario",
    "prepare_scenario_context",
    "generate_baseline_conditions",
    "extract_metrics",
]
