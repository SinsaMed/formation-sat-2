from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from sim.formation import simulate_triangle_formation


def test_triangle_formation_meets_requirements() -> None:
    """The Tehran triangular formation should satisfy duration and geometry limits."""

    config = Path("config/scenarios/tehran_triangle.json")
    result = simulate_triangle_formation(config)

    metrics = result.metrics
    window = metrics["formation_window"]
    assert window["duration_s"] >= 90.0

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
    assert set(orbital) == {"SAT-1", "SAT-2", "SAT-3"}
    plane_counts = Counter(entry["assigned_plane"] for entry in orbital.values())
    assert plane_counts["Plane A"] == 2
    assert plane_counts["Plane B"] == 1

    maintenance = metrics["maintenance"]
    budget = maintenance["assumptions"]["delta_v_budget_mps"]
    assert maintenance["annual_delta_v_mps"]["max"] <= budget
    for entry in maintenance["per_spacecraft"].values():
        assert entry["annual_delta_v_mps"] <= budget

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
