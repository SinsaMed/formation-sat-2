"""Orbital element utilities supporting the formation simulation workflow.

This module complements :mod:`constellation.roe` by providing forward
propagation and coordinate transformation helpers for near-circular low Earth
orbits.  The routines avoid external dependencies so the simulation tooling can
evaluate candidate formation geometries within the continuous integration
environment while remaining interoperable with the Systems Tool Kit (STK)
exporter.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Sequence, Tuple

import numpy as np

from .roe import MU_EARTH, OrbitalElements

EARTH_ROTATION_RATE = 7.2921150e-5  # [rad s^-1]
EARTH_EQUATORIAL_RADIUS_M = 6_378_137.0  # [m]


def _wrap_angle(angle: float) -> float:
    """Normalise *angle* to the ``[0, 2π)`` interval."""

    wrapped = math.fmod(angle, 2.0 * math.pi)
    return wrapped + 2.0 * math.pi if wrapped < 0.0 else wrapped


def mean_to_true_anomaly(mean_anomaly: float, eccentricity: float) -> float:
    """Convert mean anomaly to true anomaly solving Kepler's equation."""

    if eccentricity < 1.0e-12:
        return _wrap_angle(mean_anomaly)

    eccentric_anomaly = mean_anomaly
    for _ in range(50):
        residual = (
            eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly) - mean_anomaly
        )
        derivative = 1.0 - eccentricity * math.cos(eccentric_anomaly)
        step = -residual / derivative
        eccentric_anomaly += step
        if abs(step) < 1.0e-12:
            break

    sine_half = math.sqrt(1.0 + eccentricity) * math.sin(0.5 * eccentric_anomaly)
    cosine_half = math.sqrt(1.0 - eccentricity) * math.cos(0.5 * eccentric_anomaly)
    return _wrap_angle(2.0 * math.atan2(sine_half, cosine_half))


def classical_to_cartesian(elements: OrbitalElements, mu: float = MU_EARTH) -> Tuple[np.ndarray, np.ndarray]:
    """Return Earth-centred inertial position and velocity from *elements*."""

    a = elements.semi_major_axis
    e = elements.eccentricity
    i = elements.inclination
    raan = elements.raan
    argp = elements.arg_perigee

    true_anomaly = mean_to_true_anomaly(elements.mean_anomaly, e)
    semi_latus_rectum = a * (1.0 - e**2)

    radius = semi_latus_rectum / (1.0 + e * math.cos(true_anomaly))
    position_pf = np.array(
        [radius * math.cos(true_anomaly), radius * math.sin(true_anomaly), 0.0],
        dtype=float,
    )
    velocity_pf = np.array(
        [
            -math.sqrt(mu / semi_latus_rectum) * math.sin(true_anomaly),
            math.sqrt(mu / semi_latus_rectum) * (e + math.cos(true_anomaly)),
            0.0,
        ],
        dtype=float,
    )

    cos_raan = math.cos(raan)
    sin_raan = math.sin(raan)
    cos_argp = math.cos(argp)
    sin_argp = math.sin(argp)
    cos_inc = math.cos(i)
    sin_inc = math.sin(i)

    rotation = np.array(
        [
            [
                cos_raan * cos_argp - sin_raan * sin_argp * cos_inc,
                -cos_raan * sin_argp - sin_raan * cos_argp * cos_inc,
                sin_raan * sin_inc,
            ],
            [
                sin_raan * cos_argp + cos_raan * sin_argp * cos_inc,
                -sin_raan * sin_argp + cos_raan * cos_argp * cos_inc,
                -cos_raan * sin_inc,
            ],
            [sin_argp * sin_inc, cos_argp * sin_inc, cos_inc],
        ],
        dtype=float,
    )

    position = rotation @ position_pf
    velocity = rotation @ velocity_pf
    return position, velocity


def propagate_kepler(elements: OrbitalElements, dt: float, mu: float = MU_EARTH) -> Tuple[np.ndarray, np.ndarray]:
    """Propagate *elements* forward by *dt* seconds using Keplerian motion."""

    mean_motion = elements.mean_motion(mu)
    propagated = OrbitalElements(
        semi_major_axis=elements.semi_major_axis,
        eccentricity=elements.eccentricity,
        inclination=elements.inclination,
        raan=elements.raan,
        arg_perigee=elements.arg_perigee,
        mean_anomaly=_wrap_angle(elements.mean_anomaly + mean_motion * dt),
    )
    return classical_to_cartesian(propagated, mu=mu)


def inertial_to_ecef(position: Sequence[float], epoch: datetime) -> np.ndarray:
    """Rotate an inertial *position* vector into the Earth-fixed frame."""

    theta = greenwich_sidereal_angle(epoch)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    rotation = np.array(
        [[cos_theta, sin_theta, 0.0], [-sin_theta, cos_theta, 0.0], [0.0, 0.0, 1.0]],
        dtype=float,
    )
    return rotation @ np.asarray(position, dtype=float)


def greenwich_sidereal_angle(epoch: datetime) -> float:
    """Return the Greenwich sidereal angle at *epoch* in radians."""

    jd = julian_date(epoch)
    t_centuries = (jd - 2451545.0) / 36_525.0
    gmst_seconds = (
        67_310.54841
        + (876_600.0 * 3_600.0 + 8_640_184.812866) * t_centuries
        + 0.093104 * t_centuries**2
        - 6.2e-6 * t_centuries**3
    )
    gmst_seconds = math.fmod(gmst_seconds, 86_400.0)
    if gmst_seconds < 0.0:
        gmst_seconds += 86_400.0
    return gmst_seconds * (math.pi / 43_200.0)


def julian_date(epoch: datetime) -> float:
    """Return the Julian date corresponding to *epoch*."""

    year = epoch.year
    month = epoch.month
    day = epoch.day + (epoch.hour + (epoch.minute + (epoch.second + epoch.microsecond / 1_000_000.0) / 60.0) / 60.0) / 24.0
    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return float(jd)


def geodetic_coordinates(position_ecef: Sequence[float]) -> Tuple[float, float, float]:
    """Return geodetic latitude, longitude, and altitude from *position_ecef*."""

    x, y, z = position_ecef
    longitude = math.atan2(y, x)
    hyp = math.hypot(x, y)
    latitude = math.atan2(z, hyp)
    altitude = math.sqrt(x * x + y * y + z * z) - EARTH_EQUATORIAL_RADIUS_M
    return latitude, longitude, altitude


def haversine_distance(latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float) -> float:
    """Return the great-circle distance between two geodetic coordinates."""

    delta_lat = latitude_2 - latitude_1
    delta_lon = longitude_2 - longitude_1
    a = (
        math.sin(0.5 * delta_lat) ** 2
        + math.cos(latitude_1) * math.cos(latitude_2) * math.sin(0.5 * delta_lon) ** 2
    )
    return 2.0 * EARTH_EQUATORIAL_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


__all__ = [
    "EARTH_EQUATORIAL_RADIUS_M",
    "EARTH_ROTATION_RATE",
    "classical_to_cartesian",
    "geodetic_coordinates",
    "greenwich_sidereal_angle",
    "haversine_distance",
    "inertial_to_ecef",
    "julian_date",
    "mean_to_true_anomaly",
    "propagate_kepler",
]

