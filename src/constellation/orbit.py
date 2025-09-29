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


def cartesian_to_classical(
    position: Sequence[float], velocity: Sequence[float], mu: float = MU_EARTH
) -> OrbitalElements:
    """Return classical orbital elements reconstructed from Cartesian states."""

    r_vec = np.asarray(position, dtype=float)
    v_vec = np.asarray(velocity, dtype=float)
    r_norm = float(np.linalg.norm(r_vec))
    v_norm = float(np.linalg.norm(v_vec))

    if r_norm <= 0.0:
        raise ValueError("Position vector magnitude must be positive.")

    specific_energy = 0.5 * v_norm**2 - mu / r_norm
    if abs(specific_energy) < 1.0e-12:
        raise ValueError("Parabolic trajectories are not supported.")

    semi_major_axis = -mu / (2.0 * specific_energy)

    h_vec = np.cross(r_vec, v_vec)
    h_norm = float(np.linalg.norm(h_vec))
    inclination = math.acos(max(-1.0, min(1.0, h_vec[2] / h_norm)))

    node_vec = np.cross(np.array([0.0, 0.0, 1.0], dtype=float), h_vec)
    node_norm = float(np.linalg.norm(node_vec))

    eccentricity_vec = (
        ((v_norm**2 - mu / r_norm) * r_vec - np.dot(r_vec, v_vec) * v_vec) / mu
    )
    eccentricity = float(np.linalg.norm(eccentricity_vec))

    tolerance = 1.0e-10

    if node_norm > tolerance:
        raan = math.acos(max(-1.0, min(1.0, node_vec[0] / node_norm)))
        if node_vec[1] < 0.0:
            raan = 2.0 * math.pi - raan
    else:
        raan = 0.0

    if eccentricity > tolerance:
        if node_norm > tolerance:
            arg_perigee = math.acos(
                max(-1.0, min(1.0, np.dot(node_vec, eccentricity_vec) / (node_norm * eccentricity)))
            )
            if eccentricity_vec[2] < 0.0:
                arg_perigee = 2.0 * math.pi - arg_perigee
        else:
            arg_perigee = math.atan2(eccentricity_vec[1], eccentricity_vec[0])

        true_anomaly = math.acos(
            max(-1.0, min(1.0, np.dot(eccentricity_vec, r_vec) / (eccentricity * r_norm)))
        )
        if np.dot(r_vec, v_vec) < 0.0:
            true_anomaly = 2.0 * math.pi - true_anomaly
    else:
        arg_perigee = 0.0
        if node_norm > tolerance:
            true_anomaly = math.acos(
                max(-1.0, min(1.0, np.dot(node_vec, r_vec) / (node_norm * r_norm)))
            )
            if np.dot(r_vec, v_vec) < 0.0:
                true_anomaly = 2.0 * math.pi - true_anomaly
        else:
            true_anomaly = math.atan2(r_vec[1], r_vec[0])

    if eccentricity < 1.0:
        if eccentricity > tolerance:
            denominator = 1.0 + eccentricity * math.cos(true_anomaly)
            cos_e = (eccentricity + math.cos(true_anomaly)) / denominator
            sin_e = (
                math.sin(true_anomaly) * math.sqrt(1.0 - eccentricity**2)
            ) / denominator
            eccentric_anomaly = math.atan2(sin_e, cos_e)
            mean_anomaly = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly)
        else:
            mean_anomaly = true_anomaly
    else:
        raise ValueError("Hyperbolic trajectories are not supported.")

    return OrbitalElements(
        semi_major_axis=float(semi_major_axis),
        eccentricity=float(eccentricity),
        inclination=float(inclination),
        raan=float(_wrap_angle(raan)),
        arg_perigee=float(_wrap_angle(arg_perigee)),
        mean_anomaly=float(_wrap_angle(mean_anomaly)),
    )


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
    "cartesian_to_classical",
    "haversine_distance",
    "inertial_to_ecef",
    "julian_date",
    "mean_to_true_anomaly",
    "propagate_kepler",
]

