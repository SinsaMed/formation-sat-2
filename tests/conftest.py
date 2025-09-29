"""Shared fixtures and path configuration for the pytest suite."""

from __future__ import annotations

import pathlib
import sys
from typing import Dict, Mapping

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def scenario_configuration() -> Mapping[str, object]:
    """Return a representative mission configuration dictionary."""

    return {
        "mission_name": "Aquila-Pathfinder",
        "duration_hours": 6,
        "spacecraft": [
            {
                "identifier": "AP-LEAD",
                "role": "chief",
                "initial_state": {
                    "semi_major_axis_m": 6_971_000.0,
                    "eccentricity": 0.0007,
                    "inclination_rad": 0.122,
                },
            },
            {
                "identifier": "AP-TRAIL",
                "role": "deputy",
                "initial_state": {
                    "semi_major_axis_m": 6_971_000.0,
                    "eccentricity": 0.0009,
                    "inclination_rad": 0.122,
                },
            },
        ],
        "contact_plan": {
            "ground_sites": [
                {
                    "name": "Kiruna",
                    "latitude_deg": 67.8558,
                    "longitude_deg": 20.2253,
                }
            ]
        },
    }


@pytest.fixture(scope="session")
def reference_outputs() -> Dict[str, object]:
    """Provide placeholder reference artefacts for integration checks."""

    return {
        "ephemeris_stub": {
            "format": "STK-v11",
            "sample_count": 0,
        },
        "metric_expectations": {
            "along_track_drift_m": 0.0,
            "contact_coverage_pct": 0.0,
        },
    }
