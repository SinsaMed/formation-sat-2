from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

from sim.formation import simulate_triangle_formation


def test_triangle_formation_meets_requirements() -> None:
    """The Tehran triangular formation should satisfy duration and geometry limits."""

    config_path = Path("config/scenarios/tehran_triangle.json")
    
    # Load and modify the configuration
    with open(config_path, "r") as f:
        config_data = json.load(f)
    
    # Modify station_keeping_interval_s for testing active station-keeping
    config_data["formation"]["station_keeping_interval_s"] = 60.0
    config_data["formation"]["prediction_horizon_s"] = 60.0
    config_data["formation"]["station_keeping_tolerance_m"] = 60.0
    
    result = simulate_triangle_formation(config_data) # Pass the modified dictionary

    metrics = result.metrics
    window = metrics["formation_window"]
    assert window["duration_s"] >= 90.0

    windows = metrics["formation_windows"]
    assert isinstance(windows, list)
    assert windows
    assert any(
        window["start"] == entry.get("start") and window["end"] == entry.get("end")
        for entry in windows
    )
    for entry in windows:
        assert "duration_s" in entry
        assert "sample_count" in entry

    recurrence = metrics["formation_recurrence"]
    assert recurrence["window_count"] == len(windows)
    assert recurrence["max_duration_s"] >= window["duration_s"]

    triangle_metrics = metrics["triangle"]
    assert triangle_metrics["aspect_ratio_max"] <= 1.02

    ground_metrics = metrics["ground_track"]
    tolerance = ground_metrics["ground_distance_tolerance_km"]

    window_start = datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
    window_end = datetime.fromisoformat(window["end"].replace("Z", "+00:00"))
    distances_within_window = [
        result.max_ground_distance_km[idx]
        for idx, epoch in enumerate(result.times)
        if window_start <= epoch <= window_end
    ]
    assert distances_within_window
    assert max(distances_within_window) <= tolerance

    orbital = metrics["orbital_elements"]
    per_satellite = orbital["per_satellite"]
    assert set(per_satellite) == {"SAT-1", "SAT-2", "SAT-3"}
    plane_counts = Counter(entry["assigned_plane"] for entry in per_satellite.values())
    assert plane_counts["Plane A"] == 2
    assert plane_counts["Plane B"] == 1

    time_series = orbital["time_series"]
    assert set(time_series["fields"]) == {
        "semi_major_axis_km",
        "eccentricity",
        "inclination_deg",
        "raan_deg",
        "argument_of_perigee_deg",
        "mean_anomaly_deg",
    }
    assert time_series["artefact_key"] == "orbital_elements_csv"

    classical = result.classical_elements
    assert set(classical) == {"SAT-1", "SAT-2", "SAT-3"}
    sample_count = len(result.times)
    for series in classical.values():
        for values in series.values():
            assert len(values) == sample_count

    maintenance = metrics["maintenance"]
    budget = maintenance["assumptions"]["delta_v_budget_mps"]
    assert maintenance["annual_delta_v_mps"]["max"] <= budget
    for entry in maintenance["per_spacecraft"].values():
        assert entry["annual_delta_v_mps"] <= budget

    station_keeping = metrics["station_keeping"]
    assert station_keeping["status"] == "nominal"
    assert station_keeping["violation_fraction"] == 0.0
    assert not station_keeping["events"]
    assert station_keeping["total_delta_v_consumed_mps"] >= 0.0

    command_latency = metrics["command_latency"]
    assert command_latency["max_latency_hours"] <= 12.0
    assert command_latency["latency_margin_hours"] >= 0.0
    assert command_latency["contact_probability"] > 0.0

    injection = metrics["injection_recovery"]
    assert injection["sample_count"] == 300
    assert injection["success_rate"] >= 0.95
    for entry in injection["per_spacecraft"].values():
        assert entry["success_rate"] >= 0.95
        assert entry["max_delta_v_mps"] <= injection["assumptions"]["delta_v_budget_mps"]

    drag_dispersion = metrics["drag_dispersion"]
    assert drag_dispersion["sample_count"] >= 50
    assert 0.0 <= drag_dispersion["success_rate"] <= 1.0
    aggregate = drag_dispersion["aggregate"]
    assert aggregate["max_ground_distance_delta_km"] >= 0.0


def test_passive_stability_without_station_keeping() -> None:
    """Long-duration propagation without control should preserve the geometry."""

    config_path = Path("config/scenarios/tehran_triangle.json")
    with open(config_path, "r", encoding="utf-8") as handle:
        configuration = json.load(handle)

    formation = configuration["formation"]
    formation["duration_s"] = 21_600.0  # Six-hour window spanning multiple orbits
    formation["time_step_s"] = 30.0
    formation["station_keeping_interval_s"] = 10.0 * 86_400.0
    formation["prediction_horizon_s"] = 3_600.0
    formation["station_keeping_tolerance_m"] = 1_000.0

    result = simulate_triangle_formation(configuration)

    sides = np.asarray(result.triangle_sides_m, dtype=float)
    baseline_sides = sides[0]
    side_drift = float(np.max(np.abs(sides - baseline_sides)))
    assert side_drift <= 2_000.0

    areas = np.asarray(result.triangle_area_m2, dtype=float)
    area_drift = float(np.max(np.abs(areas - areas[0])))
    assert area_drift <= 1.2e7
