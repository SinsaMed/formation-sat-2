"""Unit tests for the relative orbital element toolkit."""

from __future__ import annotations

import math

from constellation import roe


def test_orbital_elements_mean_motion_matches_kepler() -> None:
    """The computed mean motion should satisfy Kepler's third law."""

    elements = roe.OrbitalElements(7_000_000.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    expected = math.sqrt(roe.MU_EARTH / elements.semi_major_axis**3)
    assert math.isclose(elements.mean_motion(), expected)


def test_roe_from_absolute_handles_equatorial_case() -> None:
    """For equatorial chiefs the node offset should map directly to ``delta_iy``."""

    chief = roe.OrbitalElements(7_000_000.0, 0.0, 0.0, 0.1, 0.2, 0.3)
    deputy = roe.OrbitalElements(7_003_500.0, 0.0008, 0.0, 0.15, 0.22, 0.4)
    rel = roe.roe_from_absolute(chief, deputy)
    assert math.isclose(rel.delta_a_over_a, (deputy.semi_major_axis - chief.semi_major_axis) / chief.semi_major_axis)
    assert math.isclose(rel.delta_iy, deputy.raan - chief.raan)


def test_absolute_from_roe_recovers_deputy_elements() -> None:
    """The inverse mapping should reconstruct the deputy state."""

    chief = roe.OrbitalElements(7_000_000.0, 0.001, 0.01, 0.2, 0.4, 0.6)
    desired = roe.RelativeOrbitalElements(2e-3, 0.015, 1e-4, -2e-4, 3e-4, -1.5e-4)
    deputy = roe.absolute_from_roe(chief, desired)
    reconstructed = roe.roe_from_absolute(chief, deputy)
    assert all(
        math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
        for a, b in zip(desired.as_tuple(), reconstructed.as_tuple())
    )


def test_propagate_roe_applies_linear_drift() -> None:
    """Propagation should apply the expected along-track drift rate."""

    chief = roe.OrbitalElements(7_000_000.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    initial = roe.RelativeOrbitalElements(5e-4, 0.01, 0.0, 0.0, 0.0, 0.0)
    dt = 3600.0
    propagated = roe.propagate_roe(initial, mean_motion=chief.mean_motion(), dt=dt)
    expected_delta_lambda = initial.delta_lambda - 1.5 * chief.mean_motion() * initial.delta_a_over_a * dt
    assert math.isclose(propagated.delta_lambda, expected_delta_lambda)
    assert math.isclose(propagated.delta_ex, initial.delta_ex)
    assert math.isclose(propagated.delta_ix, initial.delta_ix)


def test_absolute_from_roe_handles_polar_inclination() -> None:
    """High-inclination chiefs should scale the node offset by ``sin(i)``."""

    chief = roe.OrbitalElements(7_000_000.0, 0.001, math.radians(87.0), 0.1, 0.2, 0.3)
    desired = roe.RelativeOrbitalElements(0.0, 0.005, 0.0, 0.0, 0.0, 0.002)
    deputy = roe.absolute_from_roe(chief, desired)
    difference = deputy.raan - chief.raan
    assert math.isclose(difference * math.sin(chief.inclination), desired.delta_iy, rel_tol=1e-12)
