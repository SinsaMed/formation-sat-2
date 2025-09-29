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
