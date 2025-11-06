"""Regression tests for geodetic utilities in :mod:`sim.scripts.run_scenario`."""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

import importlib

run_scenario = importlib.import_module("sim.scripts.run_scenario")


def test_greenwich_sidereal_angle_matches_reference_value() -> None:
    """Ensure the sidereal rotation matches the IAU 2006 expression to high precision."""

    epoch = datetime(2026, 3, 21, 7, 40, tzinfo=timezone.utc)
    angle = run_scenario._greenwich_sidereal_angle(epoch)
    assert angle == pytest.approx(5.128507946572053, rel=1e-12, abs=0.0)


def test_eci_to_geodetic_recovers_tehran_coordinates() -> None:
    """The ECI-to-geodetic conversion should map Tehran's sub-satellite point correctly."""

    epoch = datetime(2026, 3, 21, 7, 40, tzinfo=timezone.utc)

    latitude = math.radians(35.6892)
    longitude = math.radians(51.3890)
    altitude_km = 1.2

    a = run_scenario.EARTH_RADIUS_KM
    e2 = run_scenario.EARTH_ECCENTRICITY_SQUARED

    sin_lat = math.sin(latitude)
    cos_lat = math.cos(latitude)
    sin_lon = math.sin(longitude)
    cos_lon = math.cos(longitude)

    normal = a / math.sqrt(1.0 - e2 * sin_lat**2)
    x_ecef = (normal + altitude_km) * cos_lat * cos_lon
    y_ecef = (normal + altitude_km) * cos_lat * sin_lon
    z_ecef = (normal * (1.0 - e2) + altitude_km) * sin_lat

    greenwich_angle = 5.128507946572053
    cos_angle = math.cos(greenwich_angle)
    sin_angle = math.sin(greenwich_angle)
    x_eci = cos_angle * x_ecef - sin_angle * y_ecef
    y_eci = sin_angle * x_ecef + cos_angle * y_ecef
    z_eci = z_ecef

    lat_deg, lon_deg, alt_km = run_scenario._eci_to_geodetic((x_eci, y_eci, z_eci), epoch, epoch)

    assert lat_deg == pytest.approx(35.6892, abs=1e-4)
    assert lon_deg == pytest.approx(51.3890, abs=1e-4)
    assert alt_km == pytest.approx(altitude_km, rel=5e-4)
