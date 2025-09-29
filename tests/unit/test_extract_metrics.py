"""Unit tests for the metric extraction workflow."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from sim.scripts import extract_metrics


def test_extract_metrics_computes_expected_statistics(synthetic_metric_inputs) -> None:
    """The extractor should reproduce the analytical expectations."""

    bundle = synthetic_metric_inputs["data_bundle"].copy()
    expected = synthetic_metric_inputs["expected"]

    metrics = extract_metrics.extract_metrics(bundle)

    durations = expected["durations"]
    assert metrics.window_statistics["count"] == pytest.approx(float(len(durations)))
    assert metrics.window_statistics["mean_duration_s"] == pytest.approx(np.mean(durations))
    assert metrics.window_statistics["median_duration_s"] == pytest.approx(np.median(durations))
    assert metrics.window_statistics["min_duration_s"] == pytest.approx(min(durations))
    assert metrics.window_statistics["max_duration_s"] == pytest.approx(max(durations))

    baseline = expected["baseline"]
    triangle_areas = expected["triangle_areas"]
    area_errors = expected["area_errors"]
    area_rms = math.sqrt(np.mean(np.square(area_errors)))
    assert metrics.triangle_geometry["mean_area"] == pytest.approx(np.mean(triangle_areas))
    assert metrics.triangle_geometry["area_error_rms"] == pytest.approx(area_rms)
    assert metrics.triangle_geometry["baseline_area"] == pytest.approx(baseline["area"])

    side_errors = np.asarray(expected["side_errors"], dtype=float)
    side_rms = float(np.sqrt(np.mean(np.square(side_errors))))
    assert metrics.triangle_geometry["side_length_rms_error"] == pytest.approx(side_rms)
    mean_sides = np.mean(np.asarray(expected["triangle_sides"], dtype=float), axis=0)
    for reported, expected_value in zip(
        metrics.triangle_geometry["mean_side_lengths"], mean_sides
    ):
        assert reported == pytest.approx(expected_value)

    per_spacecraft = metrics.delta_v["per_spacecraft"]
    for name, total in expected["delta_v_totals"].items():
        assert per_spacecraft[name] == pytest.approx(total)
    assert metrics.delta_v["total_delta_v_mps"] == pytest.approx(sum(expected["delta_v_totals"].values()))

    output_dir: Path = bundle["output_dir"]
    summary_path = output_dir / "metrics_summary.json"
    assert summary_path.exists()
    window_csv = output_dir / "window_events.csv"
    triangle_csv = output_dir / "triangle_geometry.csv"
    delta_v_csv = output_dir / "delta_v_usage.csv"
    assert window_csv.exists() and triangle_csv.exists() and delta_v_csv.exists()
    assert (output_dir / "window_durations.png").exists()
    assert (output_dir / "triangle_area.png").exists()

    with summary_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["window_statistics"]["count"] == pytest.approx(float(len(durations)))


def test_extract_metrics_updates_baseline(synthetic_metric_inputs) -> None:
    """Baseline files should refresh when requested."""

    bundle = synthetic_metric_inputs["data_bundle"].copy()
    baseline_path: Path = synthetic_metric_inputs["paths"]["baseline"]

    bundle["update_baseline"] = True
    metrics = extract_metrics.extract_metrics(bundle)

    with baseline_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    assert "triangle_geometry" in payload
    assert payload["triangle_geometry"]["area"] == pytest.approx(
        metrics.triangle_geometry["mean_area"]
    )

