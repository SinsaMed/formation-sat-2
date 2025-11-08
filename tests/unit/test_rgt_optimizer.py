"""Unit tests for the repeat-ground-track optimisation utilities."""

from __future__ import annotations

import math

from sim.scripts import configuration
from sim.scripts.rgt_optimizer import (
    compute_repeat_ground_track_solution,
    estimate_visibility,
)


def test_repeat_ground_track_solution_converges_for_tehran() -> None:
    scenario = configuration.load_scenario("tehran_daily_pass")
    solution = compute_repeat_ground_track_solution(scenario)

    assert solution is not None
    assert solution.converged is True
    assert abs(solution.residual_tau) < 1e-8
    assert 6900.0 < solution.semi_major_axis_km < 6980.0
    assert 500.0 < solution.perigee_altitude_km < 620.0
    assert math.isfinite(solution.nodal_period_s)
    assert solution.nodal_period_s > 5600.0


def test_visibility_estimation_exceeds_minimum_duration() -> None:
    scenario = configuration.load_scenario("tehran_daily_pass")
    solution = compute_repeat_ground_track_solution(scenario)
    assert solution is not None

    visibility = estimate_visibility(
        scenario,
        solution.semi_major_axis_km,
        time_step_s=2.0,
        elevation_threshold_deg=20.0,
    )

    assert visibility
    assert visibility.get("segments")
    longest = float(visibility.get("longest_duration_s", 0.0))
    assert longest >= 96.0
    max_elevation = float(visibility.get("max_elevation_deg", 0.0))
    assert max_elevation > 60.0
