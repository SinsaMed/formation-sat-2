"""Shared fixtures and path configuration for the pytest suite."""

from __future__ import annotations

import pathlib
import sys
import csv
import json
from datetime import datetime, timedelta
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


@pytest.fixture()
def synthetic_metric_inputs(tmp_path):
    """Create synthetic simulation artefacts for metric extraction tests."""

    from constellation.geometry import (
        triangle_area,
        triangle_aspect_ratio,
        triangle_side_lengths,
    )

    window_file = tmp_path / "windows.csv"
    window_start = datetime(2024, 1, 1, 0, 0, 0)
    durations = [60, 90, 120]
    with window_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["start", "end"])
        for offset, duration in enumerate(durations):
            start = window_start + timedelta(hours=offset)
            end = start + timedelta(seconds=duration)
            writer.writerow([start.isoformat(), end.isoformat()])

    baseline_vertices = [
        [0.0, 0.0, 0.0],
        [10.0, 0.0, 0.0],
        [5.0, 8.660254037844386, 0.0],
    ]
    variant_vertices = [
        [0.05, -0.02, 0.01],
        [10.1, 0.05, -0.02],
        [5.1, 8.60, 0.03],
    ]
    triangle_series = [
        {"time": (window_start).isoformat(), "vertices": baseline_vertices},
        {"time": (window_start + timedelta(seconds=10)).isoformat(), "vertices": variant_vertices},
    ]
    triangle_file = tmp_path / "triangles.json"
    triangle_file.write_text(json.dumps(triangle_series, indent=2), encoding="utf-8")

    delta_v_file = tmp_path / "delta_v.csv"
    delta_v_rows = [
        ("SatA", 0.10),
        ("SatB", 0.20),
        ("SatA", 0.05),
        ("SatC", 0.15),
    ]
    with delta_v_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["spacecraft", "delta_v_mps"])
        for name, value in delta_v_rows:
            writer.writerow([name, value])

    baseline_area = triangle_area(baseline_vertices)
    baseline_aspect = triangle_aspect_ratio(baseline_vertices)
    baseline_sides = triangle_side_lengths(baseline_vertices)

    baseline_file = tmp_path / "baseline.json"
    baseline_payload = {
        "triangle_geometry": {
            "area": baseline_area,
            "aspect_ratio": baseline_aspect,
            "side_lengths": baseline_sides,
        }
    }
    baseline_file.write_text(json.dumps(baseline_payload, indent=2), encoding="utf-8")

    triangle_areas = [triangle_area(item["vertices"]) for item in triangle_series]
    triangle_aspects = [triangle_aspect_ratio(item["vertices"]) for item in triangle_series]
    triangle_sides = [triangle_side_lengths(item["vertices"]) for item in triangle_series]

    area_errors = [area - baseline_area for area in triangle_areas]
    side_errors = [
        [side - ref for side, ref in zip(lengths, baseline_sides)]
        for lengths in triangle_sides
    ]

    data_bundle = {
        "window_file": window_file,
        "triangle_file": triangle_file,
        "delta_v_file": delta_v_file,
        "baseline_file": baseline_file,
        "output_dir": tmp_path / "metrics_output",
    }

    expected = {
        "durations": durations,
        "triangle_areas": triangle_areas,
        "triangle_aspects": triangle_aspects,
        "triangle_sides": triangle_sides,
        "area_errors": area_errors,
        "side_errors": side_errors,
        "baseline": {
            "area": baseline_area,
            "aspect_ratio": baseline_aspect,
            "side_lengths": baseline_sides,
        },
        "delta_v_totals": {
            "SatA": 0.15,
            "SatB": 0.20,
            "SatC": 0.15,
        },
    }

    return {
        "data_bundle": data_bundle,
        "expected": expected,
        "paths": {
            "baseline": baseline_file,
            "window": window_file,
            "triangle": triangle_file,
            "delta_v": delta_v_file,
            "output": data_bundle["output_dir"],
        },
    }
