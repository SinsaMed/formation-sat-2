from __future__ import annotations

import math

import pytest

from constellation.orbit import cartesian_to_classical, classical_to_cartesian
from constellation.roe import OrbitalElements


def _angle_close(a: float, b: float, tol: float = 1.0e-8) -> bool:
    diff = abs((a - b + math.pi) % (2.0 * math.pi) - math.pi)
    return diff <= tol


def test_cartesian_conversion_round_trip() -> None:
    """Converting to Cartesian and back should preserve the orbital elements."""

    elements = OrbitalElements(
        semi_major_axis=6_950_000.0,
        eccentricity=0.012,
        inclination=math.radians(97.6),
        raan=math.radians(15.0),
        arg_perigee=math.radians(45.0),
        mean_anomaly=math.radians(120.0),
    )

    position, velocity = classical_to_cartesian(elements)
    recovered = cartesian_to_classical(position, velocity)

    assert recovered.semi_major_axis == pytest.approx(elements.semi_major_axis, rel=1e-9)
    assert recovered.eccentricity == pytest.approx(elements.eccentricity, rel=1e-9)
    assert recovered.inclination == pytest.approx(elements.inclination, rel=1e-9)
    assert _angle_close(recovered.raan, elements.raan)
    assert _angle_close(recovered.arg_perigee, elements.arg_perigee)
    assert _angle_close(recovered.mean_anomaly, elements.mean_anomaly)


def test_cartesian_conversion_handles_near_circular_case() -> None:
    """Near-circular orbits should still yield sensible angular parameters."""

    elements = OrbitalElements(
        semi_major_axis=6_898_137.0,
        eccentricity=1.0e-6,
        inclination=math.radians(0.25),
        raan=math.radians(10.0),
        arg_perigee=math.radians(5.0),
        mean_anomaly=math.radians(250.0),
    )

    position, velocity = classical_to_cartesian(elements)
    recovered = cartesian_to_classical(position, velocity)

    assert recovered.semi_major_axis == pytest.approx(elements.semi_major_axis, rel=1e-9)
    assert recovered.eccentricity == pytest.approx(elements.eccentricity, rel=1e-6, abs=1e-12)
    assert recovered.inclination == pytest.approx(elements.inclination, rel=1e-9)
    assert _angle_close(recovered.raan, elements.raan, tol=1e-6)
    assert _angle_close(recovered.mean_anomaly, elements.mean_anomaly, tol=1e-6)
