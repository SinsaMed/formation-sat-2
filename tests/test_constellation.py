"""Tests for the constellation utilities module.

The scenarios mirror typical configuration checks run before exchanging state
vectors with Systems Tool Kit during mission analysis cycles.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.testing import assert_allclose

from constellation import frames, geometry, roe


def test_rotation_matrix_aligns_with_equatorial_case() -> None:
    """Verify RTN alignment for an equatorial circular orbit."""

    position = np.array([7000e3, 0.0, 0.0])
    velocity = np.array([0.0, 7.5e3, 0.0])
    matrix = frames.rotation_matrix_eci_to_rtn(position, velocity)
    assert_allclose(matrix, np.eye(3), atol=1e-12)


def test_lvlh_points_towards_earth() -> None:
    """Ensure LVLH x-axis is anti-radial (towards nadir)."""

    position = np.array([7078137.0, 0.0, 0.0])
    velocity = np.array([0.0, 7.0e3, 0.0])
    c_eci_lvlh = frames.rotation_matrix_eci_to_lvlh(position, velocity)
    # x-axis must point towards Earth, hence opposite of the radial unit vector.
    r_hat = position / np.linalg.norm(position)
    assert_allclose(c_eci_lvlh[0], -r_hat, atol=1e-12)


def test_geometry_metrics_match_equilateral_triangle() -> None:
    """Check triangle utilities for an equilateral in-plane configuration."""

    side = 50.0
    vertices = (
        np.array([0.0, 0.0, 0.0]),
        np.array([side, 0.0, 0.0]),
        np.array([0.5 * side, math.sqrt(3) / 2 * side, 0.0]),
    )
    area = geometry.triangle_area(vertices)
    aspect = geometry.triangle_aspect_ratio(vertices)
    assert math.isclose(area, math.sqrt(3) / 4 * side**2)
    assert math.isclose(aspect, 1.0)


def test_visibility_reflects_minimum_elevation() -> None:
    """Visibility should fail when the target is below the horizon."""

    earth_radius = 6_378_137.0
    altitude = 500e3
    observer = np.array([earth_radius + altitude, 0.0, 0.0])
    target_below = np.array([
        -(earth_radius + altitude) * math.sin(math.radians(100.0)),
        (earth_radius + altitude) * math.cos(math.radians(100.0)),
        0.0,
    ])
    assert not geometry.is_visible(observer, target_below)

    target_visible = np.array([
        (earth_radius + altitude) * math.cos(math.radians(20.0)),
        (earth_radius + altitude) * math.sin(math.radians(20.0)),
        0.0,
    ])
    assert geometry.is_visible(observer, target_visible, minimum_elevation_deg=0.0)


def test_roe_round_trip() -> None:
    """ROE forward and inverse mappings should be consistent."""

    chief = roe.OrbitalElements(7000e3, 0.001, 0.01, 0.1, 0.2, 0.3)
    deputy = roe.OrbitalElements(7007e3, 0.0012, 0.0105, 0.12, 0.25, 0.35)
    elements = roe.roe_from_absolute(chief, deputy)
    reconstructed = roe.absolute_from_roe(chief, elements)
    assert math.isclose(reconstructed.semi_major_axis, deputy.semi_major_axis, rel_tol=1e-8)
    assert math.isclose(reconstructed.eccentricity, deputy.eccentricity, rel_tol=1e-8)
    assert math.isclose(reconstructed.inclination, deputy.inclination, rel_tol=1e-8)
    assert math.isclose(reconstructed.raan, deputy.raan, rel_tol=1e-8)
    assert math.isclose(reconstructed.arg_perigee, deputy.arg_perigee, rel_tol=1e-8)
    assert math.isclose(reconstructed.mean_anomaly, deputy.mean_anomaly, rel_tol=1e-8)


def test_roe_propagation_matches_linearised_drift() -> None:
    """Validate the closed-form drift equation for along-track separation."""

    chief = roe.OrbitalElements(7000e3, 0.0, 0.0, 0.0, 0.0, 0.0)
    initial = roe.RelativeOrbitalElements(5e-4, 0.0, 0.0, 0.0, 0.0, 0.0)
    dt = 1800.0
    propagated = roe.propagate_roe(initial, mean_motion=chief.mean_motion(), dt=dt)
    expected_delta_lambda = -1.5 * chief.mean_motion() * initial.delta_a_over_a * dt
    assert math.isclose(propagated.delta_lambda, expected_delta_lambda)
