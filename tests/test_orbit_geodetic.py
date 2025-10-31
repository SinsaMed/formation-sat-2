"""Tests for WGS-84 geodetic conversions."""

from __future__ import annotations

import math

import pytest

from src.constellation import orbit


WGS84_FLATTENING = orbit.WGS84_FLATTENING
WGS84_ECCENTRICITY_SQUARED = orbit.WGS84_ECCENTRICITY_SQUARED


def geodetic_to_ecef(latitude_deg: float, longitude_deg: float, altitude_m: float) -> tuple[float, float, float]:
    """Convert geodetic coordinates to ECEF for validation."""

    a = orbit.EARTH_EQUATORIAL_RADIUS_M
    f = WGS84_FLATTENING
    e2 = WGS84_ECCENTRICITY_SQUARED

    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)

    sin_lat = math.sin(latitude)
    cos_lat = math.cos(latitude)
    sin_lon = math.sin(longitude)
    cos_lon = math.cos(longitude)

    normal = a / math.sqrt(1.0 - e2 * sin_lat**2)

    x = (normal + altitude_m) * cos_lat * cos_lon
    y = (normal + altitude_m) * cos_lat * sin_lon
    z = (normal * (1.0 - e2) + altitude_m) * sin_lat
    return x, y, z


@pytest.mark.parametrize(
    "latitude_deg, longitude_deg, altitude_m",
    [
        (35.6892, 51.3890, 1_200.0),
        (0.0, 0.0, 0.0),
        (89.0, -45.0, 500.0),
    ],
)
def test_geodetic_coordinates_round_trip(latitude_deg: float, longitude_deg: float, altitude_m: float) -> None:
    """ECEF to geodetic conversion should recover the original coordinates."""

    ecef = geodetic_to_ecef(latitude_deg, longitude_deg, altitude_m)
    latitude_rad, longitude_rad, altitude = orbit.geodetic_coordinates(ecef)

    assert math.degrees(latitude_rad) == pytest.approx(latitude_deg, abs=1e-6)
    assert math.degrees(longitude_rad) == pytest.approx(longitude_deg, abs=1e-6)
    assert altitude == pytest.approx(altitude_m, abs=1e-3)


def test_geodetic_coordinates_polar_limit() -> None:
    """Positions above the poles should produce sensible altitudes."""

    polar_radius = orbit.EARTH_EQUATORIAL_RADIUS_M * (1.0 - WGS84_FLATTENING)
    ecef = (0.0, 0.0, polar_radius + 2_000.0)
    latitude_rad, longitude_rad, altitude = orbit.geodetic_coordinates(ecef)

    assert math.degrees(latitude_rad) == pytest.approx(90.0, abs=1e-9)
    assert math.degrees(longitude_rad) == pytest.approx(0.0, abs=1e-9)
    assert altitude == pytest.approx(2_000.0, abs=1e-6)
