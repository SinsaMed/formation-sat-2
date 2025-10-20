r"""High-fidelity constellation propagation with \(J_2\) and drag perturbations.

The helper functions defined here extend the lightweight scenario pipeline by
introducing a deterministic force model and a Monte Carlo dispersion analysis
tailored to the Tehran daily pass configuration.  The propagated states capture
cross-track offsets for every spacecraft in the formation, enabling direct
verification of the ±30 km primary alignment tolerance (and the ±70 km waiver
ceiling) that governs MR-2 and SRD-P-001.  Outputs are serialisable to JSON and
comma-separated value (CSV) formats so they remain compatible with Systems Tool
Kit (STK 11.2) validation workflows as required by the repository guidelines.
"""

from __future__ import annotations

import json
import math
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping, MutableMapping, Sequence

import os

import numpy as np
from statistics import fmean

from constellation.frames import rotation_matrix_rtn_to_eci
from constellation.orbit import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_ROTATION_RATE,
    geodetic_coordinates,
    haversine_distance,
    inertial_to_ecef,
)
from constellation.roe import MU_EARTH, OrbitalElements


J2_COEFFICIENT = 1.08262668e-3
SOLAR_FLUX_BASE = 150.0
OMEGA_EARTH_VECTOR = np.array([0.0, 0.0, EARTH_ROTATION_RATE], dtype=float)
OMEGA_EARTH_VECTOR = np.array([0.0, 0.0, EARTH_ROTATION_RATE], dtype=float)

DEFAULT_FORMATION = (
    {
        "identifier": "FSAT-LDR",
        "role": "leader",
        "radial_offset_km": 0.0,
        "along_track_offset_km": 0.0,
        "cross_track_offset_km": 0.0,
    },
    {
        "identifier": "FSAT-DP1",
        "role": "deputy",
        "radial_offset_km": -0.05,
        "along_track_offset_km": 20.0,
        "cross_track_offset_km": 0.2,
    },
    {
        "identifier": "FSAT-DP2",
        "role": "deputy",
        "radial_offset_km": 0.05,
        "along_track_offset_km": -20.0,
        "cross_track_offset_km": -0.2,
    },
)

PLANE_ASSIGNMENTS = {
    "FSAT-LDR": "Plane A",
    "FSAT-DP1": "Plane A",
    "FSAT-DP2": "Plane B",
}

LOGGER = logging.getLogger(__name__)


DEFAULT_MONTE_CARLO = {
    "enabled": True,
    "runs": 500,
    "seed": 42,
    "dispersions": {
        "semi_major_axis_sigma_m": 5.0,
        "inclination_sigma_deg": 0.01,
        "drag_coefficient_sigma": 0.05,
    },
}


@dataclass
class PropagatorSettings:
    """Container describing the deterministic propagation configuration."""

    start_time: datetime
    epoch_time: datetime
    stop_time: datetime
    time_step_s: float
    drag_coefficient: float
    ballistic_coefficient_m2_per_kg: float
    solar_flux_index: float
    evaluation_time: datetime | None = None
    primary_cross_track_limit_km: float = 30.0
    waiver_cross_track_limit_km: float = 70.0
    plane_intersection_limit_km: float | None = None


@dataclass
class SpacecraftState:
    """Cartesian state and drag properties for a spacecraft."""

    identifier: str
    position_m: np.ndarray
    velocity_mps: np.ndarray
    drag_coefficient: float
    area_m2: float
    mass_kg: float


def propagate_constellation(
    scenario: Mapping[str, object],
    *,
    output_directory: Path | None = None,
    formation: Sequence[Mapping[str, float | str]] = DEFAULT_FORMATION,
    settings: PropagatorSettings | None = None,
    monte_carlo: Mapping[str, object] | None = None,
) -> tuple[
    MutableMapping[str, object],
    MutableMapping[str, str],
]:
    r"""Propagate the constellation including \(J_2\) and atmospheric drag."""

    resolved_settings = settings or _default_settings(scenario)
    monte_carlo_config = _normalise_monte_carlo(monte_carlo)

    target_lat, target_lon = _target_coordinates(scenario)
    leader_elements = _scenario_orbital_elements(scenario)

    deterministic_series, deterministic_metrics = _propagate_deterministic(
        leader_elements,
        formation,
        resolved_settings,
        target_lat,
        target_lon,
    )

    monte_carlo_metrics = _run_monte_carlo(
        leader_elements,
        formation,
        resolved_settings,
        target_lat,
        target_lon,
        monte_carlo_config,
    )

    artefact_paths: MutableMapping[str, str] = {}
    if output_directory:
        artefact_paths = _write_outputs(
            Path(output_directory),
            deterministic_series,
            deterministic_metrics,
            monte_carlo_metrics,
            resolved_settings,
            monte_carlo_config,
        )

    summary = _build_summary(
        deterministic_metrics,
        monte_carlo_metrics,
        resolved_settings,
        monte_carlo_config,
    )

    return summary, artefact_paths


def scenario_cross_track_limits(
    scenario: Mapping[str, object]
) -> tuple[float, float, float | None]:
    """Return the primary, waiver, and optional plane-intersection limits."""

    primary_limit = float(os.getenv("FSAT_PRIMARY_CROSS_TRACK_LIMIT_KM", "30.0"))
    waiver_limit = float(os.getenv("FSAT_WAIVER_CROSS_TRACK_LIMIT_KM", "70.0"))
    plane_limit_env = os.getenv("FSAT_PLANE_INTERSECTION_LIMIT_KM")
    plane_limit: float | None = (
        float(plane_limit_env) if plane_limit_env is not None else None
    )

    limits = scenario.get("cross_track_limits")
    if isinstance(limits, Mapping):
        if "primary_km" in limits:
            try:
                primary_limit = float(limits["primary_km"])
            except (TypeError, ValueError):
                pass
        if "waiver_km" in limits:
            try:
                waiver_limit = float(limits["waiver_km"])
            except (TypeError, ValueError):
                pass
        plane_candidate = limits.get("plane_intersection_limit_km")
        if plane_candidate is not None:
            try:
                plane_limit = float(plane_candidate)
            except (TypeError, ValueError):
                pass
    else:
        requirements = scenario.get("alignment_requirements")
        if isinstance(requirements, Mapping):
            primary_limit = float(
                requirements.get("primary_cross_track_limit_km", primary_limit)
            )
            waiver_limit = float(
                requirements.get("waiver_cross_track_limit_km", waiver_limit)
            )
            plane_candidate = requirements.get("plane_intersection_limit_km", plane_limit)
            if plane_candidate is not None:
                plane_limit = float(plane_candidate)

    return primary_limit, waiver_limit, plane_limit


def scenario_access_window(
    scenario: Mapping[str, object]
) -> tuple[datetime | None, datetime | None, datetime | None]:
    """Return start, end, and midpoint timestamps for the primary access window."""

    window = scenario.get("access_window")
    start = _parse_time(window.get("start_utc")) if isinstance(window, Mapping) else None
    end = _parse_time(window.get("end_utc")) if isinstance(window, Mapping) else None
    midpoint = (
        _parse_time(window.get("midpoint_utc")) if isinstance(window, Mapping) else None
    )

    timing = (
        scenario.get("timing", {}) if isinstance(scenario.get("timing"), Mapping) else {}
    )
    windows = timing.get("daily_access_windows")
    if start is None or end is None:
        if isinstance(windows, Sequence) and windows:
            primary = windows[0] if isinstance(windows[0], Mapping) else {}
            if start is None:
                start = _parse_time(primary.get("start_utc"))
            if end is None:
                end = _parse_time(primary.get("end_utc"))
            if midpoint is None:
                midpoint = _parse_time(primary.get("midpoint_utc"))

    if midpoint is None and start and end:
        midpoint = start + (end - start) / 2
    elif midpoint is None and start:
        midpoint = start + timedelta(seconds=45.0)

    return start, end, midpoint


def _build_summary(
    deterministic_metrics: MutableMapping[str, object],
    monte_carlo_metrics: MutableMapping[str, object],
    settings: PropagatorSettings,
    monte_carlo_config: Mapping[str, object],
) -> MutableMapping[str, object]:
    """Combine deterministic and Monte Carlo outputs into a summary map."""

    orbital_period = deterministic_metrics.get("orbital_period_s", 0.0)
    two_body_period = deterministic_metrics.get("two_body_period_s", orbital_period)
    period_delta = float(orbital_period) - float(two_body_period)

    return {
        "model": "high_fidelity_j2_drag",
        "orbital_period_s": float(orbital_period),
        "period_delta_s": float(period_delta),
        "settings": {
            "start_time_utc": settings.start_time.isoformat().replace("+00:00", "Z"),
            "epoch_time_utc": settings.epoch_time.isoformat().replace("+00:00", "Z"),
            "stop_time_utc": settings.stop_time.isoformat().replace("+00:00", "Z"),
            "time_step_s": float(settings.time_step_s),
            "drag_coefficient": float(settings.drag_coefficient),
            "ballistic_coefficient_m2_per_kg": float(settings.ballistic_coefficient_m2_per_kg),
            "solar_flux_index": float(settings.solar_flux_index),
            "monte_carlo_runs": int(monte_carlo_config.get("runs", 0)),
        },
        "cross_track": deterministic_metrics.get("cross_track", {}),
        "altitude_range_m": deterministic_metrics.get("altitude_range_m", {}),
        "plane_intersection": deterministic_metrics.get("plane_intersection", {}),
        "monte_carlo": monte_carlo_metrics,
    }


def _default_settings(scenario: Mapping[str, object]) -> PropagatorSettings:
    """Return baseline propagation settings derived from the scenario."""

    timing = scenario.get("timing", {}) if isinstance(scenario.get("timing"), Mapping) else {}
    window_start, window_end, window_midpoint = scenario_access_window(scenario)
    orbital_elements = scenario.get("orbital_elements", {})
    reference_start = window_start or window_midpoint
    if reference_start is None:
        reference_start = _parse_time(
            orbital_elements.get("epoch_utc") if isinstance(orbital_elements, Mapping) else None
        )
    if reference_start is None:
        reference_start = datetime(2026, 3, 21, 0, 0, 0, tzinfo=timezone.utc)

    epoch_time = _parse_time(
        orbital_elements.get("epoch_utc") if isinstance(orbital_elements, Mapping) else None
    ) or reference_start

    planning = timing.get("planning_horizon", {}) if isinstance(timing.get("planning_horizon"), Mapping) else {}
    planning_stop = _parse_time(planning.get("stop_utc"))

    propagation = timing.get("propagation") if isinstance(timing.get("propagation"), Mapping) else {}
    margin_s = 300.0
    try:
        margin_candidate = float(propagation.get("margin_s", margin_s))
        margin_s = max(margin_candidate, 120.0)
    except (TypeError, ValueError):
        margin_s = max(margin_s, 120.0)
    margin = timedelta(seconds=margin_s)

    start_override = _parse_time(propagation.get("start_utc")) if propagation else None
    end_override = _parse_time(propagation.get("end_utc")) if propagation else None
    time_step = 10.0
    try:
        time_step = float(propagation.get("time_step_s", time_step))
    except (TypeError, ValueError):
        time_step = 10.0

    analysis_start = start_override or (reference_start - margin)
    if window_start and analysis_start > window_start - margin:
        analysis_start = window_start - margin

    candidate_stop = end_override
    if candidate_stop is None:
        if window_end:
            candidate_stop = window_end + margin
        elif window_midpoint:
            candidate_stop = window_midpoint + margin
        else:
            candidate_stop = analysis_start + timedelta(minutes=10)

    if planning_stop:
        candidate_stop = min(candidate_stop, planning_stop)

    if candidate_stop <= analysis_start:
        candidate_stop = analysis_start + timedelta(minutes=10)

    evaluation_time = window_midpoint or reference_start

    primary_limit, waiver_limit, plane_limit = scenario_cross_track_limits(scenario)

    return PropagatorSettings(
        start_time=analysis_start,
        epoch_time=epoch_time,
        stop_time=candidate_stop,
        time_step_s=time_step,
        drag_coefficient=2.2,
        ballistic_coefficient_m2_per_kg=0.025,
        solar_flux_index=SOLAR_FLUX_BASE,
        evaluation_time=evaluation_time,
        primary_cross_track_limit_km=primary_limit,
        waiver_cross_track_limit_km=waiver_limit,
        plane_intersection_limit_km=plane_limit,
    )


def _normalise_monte_carlo(monte_carlo: Mapping[str, object] | None) -> MutableMapping[str, object]:
    """Return a mutable Monte Carlo configuration with defaults applied."""

    if monte_carlo is None:
        config = dict(DEFAULT_MONTE_CARLO)
    else:
        config = dict(DEFAULT_MONTE_CARLO)
        config.update({key: monte_carlo.get(key, value) for key, value in DEFAULT_MONTE_CARLO.items()})
        for key, value in monte_carlo.items():
            if key == "dispersions" and isinstance(value, Mapping):
                default_disp = dict(DEFAULT_MONTE_CARLO.get("dispersions", {}))
                default_disp.update({k: float(v) for k, v in value.items()})
                config["dispersions"] = default_disp
            else:
                config[key] = value

    dispersions = config.get("dispersions", {})
    if not isinstance(dispersions, Mapping):
        dispersions = DEFAULT_MONTE_CARLO["dispersions"]
    config["dispersions"] = dict(dispersions)

    try:
        runs = int(config.get("runs", DEFAULT_MONTE_CARLO["runs"]))
    except (TypeError, ValueError):
        runs = DEFAULT_MONTE_CARLO["runs"]
    config["runs"] = max(runs, 500)

    return config


def _resolve_evaluation_time(settings: PropagatorSettings) -> datetime:
    """Return a clamped evaluation time within the propagation span."""

    evaluation = settings.evaluation_time or settings.start_time
    if evaluation < settings.start_time:
        evaluation = settings.start_time
    if evaluation > settings.stop_time:
        evaluation = settings.stop_time
    return evaluation


def _scenario_orbital_elements(scenario: Mapping[str, object]) -> OrbitalElements:
    """Extract classical elements from the scenario mapping."""

    orbital = scenario.get("orbital_elements")
    if not isinstance(orbital, Mapping):
        fallback = _fallback_orbital_elements(scenario)
        if fallback is None:
            raise ValueError("Scenario is missing the 'orbital_elements' section.")
        return fallback

    classical = orbital.get("classical")
    if not isinstance(classical, Mapping):
        raise ValueError("Scenario orbital elements must include the 'classical' block.")

    semi_major_axis_m = float(classical.get("semi_major_axis_km", 0.0)) * 1_000.0
    eccentricity = float(classical.get("eccentricity", 0.0))
    inclination = math.radians(float(classical.get("inclination_deg", 0.0)))
    raan = math.radians(float(classical.get("raan_deg", 0.0)))
    arg_perigee = math.radians(float(classical.get("argument_of_perigee_deg", 0.0)))
    mean_anomaly = math.radians(float(classical.get("mean_anomaly_deg", 0.0)))

    return OrbitalElements(
        semi_major_axis=semi_major_axis_m,
        eccentricity=eccentricity,
        inclination=inclination,
        raan=raan,
        arg_perigee=arg_perigee,
        mean_anomaly=mean_anomaly,
    )


def _fallback_orbital_elements(
    scenario: Mapping[str, object]
) -> OrbitalElements | None:
    spacecraft = scenario.get("spacecraft")
    if not isinstance(spacecraft, Sequence) or not spacecraft:
        return None
    leader = spacecraft[0]
    if not isinstance(leader, Mapping):
        return None
    initial_state = leader.get("initial_state")
    if not isinstance(initial_state, Mapping):
        return None

    semi_major_axis = float(initial_state.get("semi_major_axis_m", 0.0))
    if semi_major_axis <= 0.0:
        return None
    eccentricity = float(initial_state.get("eccentricity", 0.0))
    inclination = float(initial_state.get("inclination_rad", 0.0))
    raan = math.radians(float(initial_state.get("raan_deg", 0.0)))
    arg_perigee = math.radians(float(initial_state.get("argument_of_perigee_deg", 0.0)))
    mean_anomaly = math.radians(float(initial_state.get("mean_anomaly_deg", 0.0)))

    return OrbitalElements(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=inclination,
        raan=raan,
        arg_perigee=arg_perigee,
        mean_anomaly=mean_anomaly,
    )


def _target_coordinates(scenario: Mapping[str, object]) -> tuple[float, float]:
    """Return the target latitude and longitude in radians."""

    metadata = scenario.get("metadata")
    region = metadata.get("region") if isinstance(metadata, Mapping) else None
    if isinstance(region, Mapping):
        latitude = math.radians(float(region.get("latitude_deg", 0.0)))
        longitude = math.radians(float(region.get("longitude_deg", 0.0)))
        return latitude, longitude

    return math.radians(35.6892), math.radians(51.3890)


def _initial_states(
    leader_elements: OrbitalElements,
    formation: Sequence[Mapping[str, float | str]],
    drag_coefficient: float,
    *,
    epoch_offset_s: float = 0.0,
) -> list[SpacecraftState]:
    """Construct initial Cartesian states for the formation."""

    elements_at_start = leader_elements
    if epoch_offset_s:
        mean_motion = leader_elements.mean_motion()
        propagated_mean_anomaly = _wrap_angle(
            leader_elements.mean_anomaly + mean_motion * epoch_offset_s
        )
        elements_at_start = OrbitalElements(
            semi_major_axis=leader_elements.semi_major_axis,
            eccentricity=leader_elements.eccentricity,
            inclination=leader_elements.inclination,
            raan=leader_elements.raan,
            arg_perigee=leader_elements.arg_perigee,
            mean_anomaly=propagated_mean_anomaly,
        )

    position, velocity = _classical_to_cartesian(elements_at_start)
    rotation = rotation_matrix_rtn_to_eci(position, velocity)
    states: list[SpacecraftState] = []

    for entry in formation:
        identifier = str(entry.get("identifier", "spacecraft"))
        radial_offset = float(entry.get("radial_offset_km", 0.0)) * 1_000.0
        along_track_offset = float(entry.get("along_track_offset_km", 0.0)) * 1_000.0
        cross_track_offset = float(entry.get("cross_track_offset_km", 0.0)) * 1_000.0

        offset_rtn = np.array([radial_offset, along_track_offset, cross_track_offset], dtype=float)
        position_shift = rotation @ offset_rtn

        adjusted_position = position + position_shift
        adjusted_velocity = velocity.copy()

        states.append(
            SpacecraftState(
                identifier=identifier,
                position_m=adjusted_position.astype(float),
                velocity_mps=adjusted_velocity.astype(float),
                drag_coefficient=float(entry.get("drag_coefficient", drag_coefficient)),
                area_m2=4.0,
                mass_kg=120.0,
            )
        )

    return states


def _classical_to_cartesian(elements: OrbitalElements) -> tuple[np.ndarray, np.ndarray]:
    """Return Cartesian state vectors for *elements* without SciPy dependency."""

    # This inline implementation mirrors :func:`constellation.orbit.classical_to_cartesian`
    # but operates fully in metres to avoid repeated conversions.
    a = elements.semi_major_axis
    e = elements.eccentricity
    i = elements.inclination
    raan = elements.raan
    argp = elements.arg_perigee
    m_anomaly = elements.mean_anomaly

    true_anomaly = _mean_to_true(m_anomaly, e)
    semi_latus = a * (1.0 - e * e)
    radius = semi_latus / (1.0 + e * math.cos(true_anomaly))

    position_pf = np.array(
        [radius * math.cos(true_anomaly), radius * math.sin(true_anomaly), 0.0],
        dtype=float,
    )
    velocity_pf = np.array(
        [
            -math.sqrt(MU_EARTH / semi_latus) * math.sin(true_anomaly),
            math.sqrt(MU_EARTH / semi_latus) * (e + math.cos(true_anomaly)),
            0.0,
        ],
        dtype=float,
    )

    cos_raan = math.cos(raan)
    sin_raan = math.sin(raan)
    cos_argp = math.cos(argp)
    sin_argp = math.sin(argp)
    cos_i = math.cos(i)
    sin_i = math.sin(i)

    rotation = np.array(
        [
            [
                cos_raan * cos_argp - sin_raan * sin_argp * cos_i,
                -cos_raan * sin_argp - sin_raan * cos_argp * cos_i,
                sin_raan * sin_i,
            ],
            [
                sin_raan * cos_argp + cos_raan * sin_argp * cos_i,
                -sin_raan * sin_argp + cos_raan * cos_argp * cos_i,
                -cos_raan * sin_i,
            ],
            [sin_argp * sin_i, cos_argp * sin_i, cos_i],
        ],
        dtype=float,
    )

    position = rotation @ position_pf
    velocity = rotation @ velocity_pf
    return position, velocity


def _mean_to_true(mean_anomaly: float, eccentricity: float) -> float:
    """Convert mean anomaly to true anomaly using Newton iterations."""

    if eccentricity < 1.0e-12:
        return _wrap_angle(mean_anomaly)

    eccentric = mean_anomaly
    for _ in range(30):
        residual = eccentric - eccentricity * math.sin(eccentric) - mean_anomaly
        derivative = 1.0 - eccentricity * math.cos(eccentric)
        step = -residual / derivative
        eccentric += step
        if abs(step) < 1.0e-12:
            break

    sine_half = math.sqrt(1.0 + eccentricity) * math.sin(0.5 * eccentric)
    cosine_half = math.sqrt(1.0 - eccentricity) * math.cos(0.5 * eccentric)
    return _wrap_angle(2.0 * math.atan2(sine_half, cosine_half))


def _wrap_angle(angle: float) -> float:
    """Normalise *angle* to the ``[0, 2π)`` interval."""

    wrapped = math.fmod(angle, 2.0 * math.pi)
    return wrapped + 2.0 * math.pi if wrapped < 0.0 else wrapped


def _propagate_deterministic(
    leader_elements: OrbitalElements,
    formation: Sequence[Mapping[str, float | str]],
    settings: PropagatorSettings,
    target_lat: float,
    target_lon: float,
) -> tuple[
    MutableMapping[str, list[tuple[datetime, dict[str, float]]]],
    MutableMapping[str, object],
]:
    """Propagate the deterministic trajectory and capture time histories."""

    epoch_offset = (settings.start_time - settings.epoch_time).total_seconds()
    states = _initial_states(
        leader_elements,
        formation,
        settings.drag_coefficient,
        epoch_offset_s=epoch_offset,
    )
    epoch = settings.start_time
    dt = settings.time_step_s

    times: list[datetime] = []
    cross_track_series: dict[str, list[float]] = {state.identifier: [] for state in states}
    altitude_series: dict[str, list[float]] = {state.identifier: [] for state in states}
    metrics = _initial_metric_structure(states, target_lat, target_lon)
    plane_metrics = _plane_intersection_metrics(states, target_lat, target_lon)
    relative_stats = {"max_abs": 0.0, "min_abs": math.inf, "time_of_min": None, "series": []}

    mean_motion = leader_elements.mean_motion()
    orbital_period = 2.0 * math.pi / mean_motion if mean_motion else 0.0

    while epoch <= settings.stop_time + timedelta(seconds=1e-6):
        times.append(epoch)
        _record_metrics(
            states,
            epoch,
            target_lat,
            target_lon,
            metrics,
            cross_track_series,
            altitude_series,
            relative_stats,
        )

        if epoch >= settings.stop_time:
            break

        states = _rk4_step(states, dt, settings)
        epoch += timedelta(seconds=dt)

    overall_min_abs = 0.0
    for entry in metrics["vehicles"]:
        min_abs = float(entry.get("min_abs_cross_track_km", math.inf))
        if math.isfinite(min_abs):
            overall_min_abs = max(overall_min_abs, min_abs)
    metrics["overall_min_abs_cross_track_km"] = float(overall_min_abs)

    evaluation_time = _resolve_evaluation_time(settings)
    evaluation_timestamp = evaluation_time
    evaluation_index = 0
    if times:
        evaluation_index = min(
            range(len(times)),
            key=lambda idx: abs((times[idx] - evaluation_time).total_seconds()),
        )
        evaluation_timestamp = times[evaluation_index]

    evaluation_values: dict[str, float] = {}
    evaluation_abs: dict[str, float] = {}
    for identifier, series_values in cross_track_series.items():
        value = float("nan")
        if evaluation_index < len(series_values):
            value = float(series_values[evaluation_index])
        elif series_values:
            value = float(series_values[-1])
        evaluation_values[identifier] = value
        evaluation_abs[identifier] = abs(value) if math.isfinite(value) else math.inf

    centroid_value = fmean(evaluation_values.values()) if evaluation_values else math.nan
    centroid_abs = abs(centroid_value) if math.isfinite(centroid_value) else math.inf
    worst_abs = max(evaluation_abs.values()) if evaluation_abs else math.inf

    primary_limit = float(settings.primary_cross_track_limit_km)
    waiver_limit = float(settings.waiver_cross_track_limit_km)

    primary_compliant = (
        math.isfinite(centroid_abs)
        and centroid_abs <= primary_limit
        and math.isfinite(worst_abs)
        and worst_abs <= waiver_limit
    )
    waiver_compliant = math.isfinite(worst_abs) and worst_abs <= waiver_limit
    finite_vehicle_abs = [
        value for value in evaluation_abs.values() if math.isfinite(value)
    ]
    waiver_pass_fraction = (
        sum(1 for value in finite_vehicle_abs if value <= waiver_limit) / len(finite_vehicle_abs)
        if finite_vehicle_abs
        else 0.0
    )
    primary_pass_fraction = 1.0 if primary_compliant else 0.0

    for entry in metrics["vehicles"]:
        identifier = str(entry.get("identifier", ""))
        value = evaluation_values.get(identifier, float("nan"))
        abs_value = evaluation_abs.get(identifier, math.inf)
        entry["cross_track_at_evaluation_km"] = (
            float(value) if math.isfinite(value) else None
        )
        entry["abs_cross_track_at_evaluation_km"] = (
            float(abs_value) if math.isfinite(abs_value) else None
        )
        entry["compliant"] = bool(
            math.isfinite(abs_value) and abs_value <= waiver_limit
        )

    evaluation_timestamp_iso = evaluation_timestamp.isoformat().replace("+00:00", "Z")
    centroid_value_out = float(centroid_value) if math.isfinite(centroid_value) else None
    centroid_abs_out = float(centroid_abs) if math.isfinite(centroid_abs) else None
    worst_abs_out = float(worst_abs) if math.isfinite(worst_abs) else None

    metrics["evaluation"] = {
        "time_utc": evaluation_timestamp_iso,
        "vehicles": {
            identifier: (float(value) if math.isfinite(value) else None)
            for identifier, value in evaluation_values.items()
        },
        "vehicle_abs": {
            identifier: (float(value) if math.isfinite(value) else None)
            for identifier, value in evaluation_abs.items()
        },
        "centroid_cross_track_km": centroid_value_out,
        "centroid_abs_cross_track_km": centroid_abs_out,
        "worst_vehicle_abs_cross_track_km": worst_abs_out,
        "primary_compliant": bool(primary_compliant),
        "waiver_compliant": bool(waiver_compliant),
        "primary_limit_km": float(primary_limit),
        "waiver_limit_km": float(waiver_limit),
        "primary_pass_fraction": float(primary_pass_fraction),
        "waiver_pass_fraction": float(waiver_pass_fraction),
    }
    metrics["centroid_cross_track_km_at_evaluation"] = centroid_value_out
    metrics["centroid_abs_cross_track_km_at_evaluation"] = centroid_abs_out
    metrics["overall_abs_cross_track_km_at_evaluation"] = worst_abs_out
    metrics["primary_compliant"] = bool(primary_compliant)
    metrics["waiver_compliant"] = bool(waiver_compliant)
    metrics["primary_limit_km"] = float(primary_limit)
    metrics["waiver_limit_km"] = float(waiver_limit)
    metrics["primary_pass_fraction"] = float(primary_pass_fraction)
    metrics["waiver_pass_fraction"] = float(waiver_pass_fraction)

    relative_summary = {
        "max_abs_km": float(relative_stats["max_abs"]),
        "min_abs_km": float(relative_stats["min_abs"] if math.isfinite(relative_stats["min_abs"]) else 0.0),
        "time_of_min": relative_stats["time_of_min"],
        "series": list(relative_stats["series"]),
    }

    altitude_min = min(min(series) for series in altitude_series.values()) if altitude_series else 0.0
    altitude_max = max(max(series) for series in altitude_series.values()) if altitude_series else 0.0

    deterministic_metrics: MutableMapping[str, object] = {
        "orbital_period_s": float(orbital_period),
        "two_body_period_s": float(orbital_period),
        "cross_track": metrics,
        "altitude_range_m": {
            "min": float(altitude_min),
            "max": float(altitude_max),
        },
    }
    centroid_summary = metrics.get("centroid", {})
    if isinstance(centroid_summary, Mapping):
        deterministic_metrics["centroid_cross_track"] = {
            "min_cross_track_km": float(centroid_summary.get("min_cross_track_km", math.inf)),
            "min_abs_cross_track_km": float(
                centroid_summary.get("min_abs_cross_track_km", math.inf)
            ),
            "time_of_min_abs_cross_track": centroid_summary.get(
                "time_of_min_abs_cross_track"
            ),
            "vehicle_cross_track_km": centroid_summary.get(
                "vehicle_cross_track_km_at_min", {}
            ),
            "vehicle_abs_cross_track_km": centroid_summary.get(
                "vehicle_abs_cross_track_km_at_min", {}
            ),
            "worst_vehicle_abs_cross_track_km": float(
                centroid_summary.get("worst_vehicle_abs_cross_track_km", math.inf)
            ),
            "evaluation_cross_track_km": centroid_value_out,
            "evaluation_abs_cross_track_km": centroid_abs_out,
            "worst_vehicle_abs_cross_track_km_at_evaluation": worst_abs_out,
            "evaluation_time_utc": evaluation_timestamp_iso,
            "primary_limit_km": float(primary_limit),
            "waiver_limit_km": float(waiver_limit),
            "primary_compliant": bool(primary_compliant),
            "waiver_compliant": bool(waiver_compliant),
        }
    plane_distance = float(plane_metrics.get("target_distance_km", math.inf))
    plane_limit = settings.plane_intersection_limit_km
    if plane_limit is not None:
        plane_metrics["limit_km"] = float(plane_limit)
        if math.isfinite(plane_distance):
            plane_metrics["compliant"] = bool(plane_distance <= plane_limit)
        else:
            plane_metrics["compliant"] = False
    else:
        plane_metrics["compliant"] = None
    deterministic_metrics["plane_intersection"] = plane_metrics
    deterministic_metrics["relative_cross_track"] = relative_summary
    deterministic_metrics["cross_track_limits_km"] = {
        "primary": float(primary_limit),
        "waiver": float(waiver_limit),
    }
    deterministic_metrics["cross_track_evaluation"] = metrics["evaluation"]

    series = {
        "samples": [
            (
                timestamp,
                {identifier: cross_track_series[identifier][index] for identifier in cross_track_series},
            )
            for index, timestamp in enumerate(times)
        ],
        "altitudes": {
            identifier: altitude_series[identifier] for identifier in altitude_series
        },
    }

    return series, deterministic_metrics


def _initial_metric_structure(
    states: Sequence[SpacecraftState],
    target_lat: float,
    target_lon: float,
) -> MutableMapping[str, object]:
    """Construct the dictionary used to record cross-track statistics."""

    vehicle_metrics: list[MutableMapping[str, object]] = []
    for state in states:
        vehicle_metrics.append(
            {
                "identifier": state.identifier,
                "target_latitude_deg": math.degrees(target_lat),
                "target_longitude_deg": math.degrees(target_lon),
                "max_cross_track_km": -math.inf,
                "min_cross_track_km": math.inf,
                "max_abs_cross_track_km": -math.inf,
                "min_abs_cross_track_km": math.inf,
                "time_of_max_abs_cross_track": None,
                "time_of_min_abs_cross_track": None,
                "pass_count": 0,
                "compliant": False,
            }
        )

    return {
        "vehicles": vehicle_metrics,
        "overall_max_abs_cross_track_km": -math.inf,
        "overall_min_abs_cross_track_km": math.inf,
        "centroid": {
            "min_cross_track_km": math.inf,
            "min_abs_cross_track_km": math.inf,
            "time_of_min_abs_cross_track": None,
            "vehicle_cross_track_km_at_min": {},
            "vehicle_abs_cross_track_km_at_min": {},
            "worst_vehicle_abs_cross_track_km": math.inf,
        },
    }


def _plane_intersection_metrics(
    states: Sequence[SpacecraftState],
    target_lat: float,
    target_lon: float,
) -> MutableMapping[str, object]:
    """Compute the plane intersection proximity to the target."""

    plane_normals: dict[str, list[np.ndarray]] = {}
    for state in states:
        plane = PLANE_ASSIGNMENTS.get(state.identifier, "Plane A")
        h_vec = np.cross(state.position_m, state.velocity_mps)
        norm = np.linalg.norm(h_vec)
        if norm == 0.0:
            continue
        plane_normals.setdefault(plane, []).append(h_vec / norm)

    averaged_normals: dict[str, np.ndarray] = {}
    for plane, vectors in plane_normals.items():
        if not vectors:
            continue
        stacked = np.vstack(vectors)
        mean_vec = np.mean(stacked, axis=0)
        norm = np.linalg.norm(mean_vec)
        if norm == 0.0:
            continue
        averaged_normals[plane] = mean_vec / norm

    plane_a = averaged_normals.get("Plane A")
    plane_b = averaged_normals.get("Plane B")
    if plane_a is None or plane_b is None:
        return {
            "planes": {plane: vec.tolist() for plane, vec in averaged_normals.items()},
            "intersection_candidates": [],
            "target_distance_km": math.inf,
        }

    line_direction = np.cross(plane_a, plane_b)
    norm_line = np.linalg.norm(line_direction)
    if norm_line == 0.0:
        return {
            "planes": {plane: vec.tolist() for plane, vec in averaged_normals.items()},
            "intersection_candidates": [],
            "target_distance_km": math.inf,
        }

    unit_direction = line_direction / norm_line
    candidates = [unit_direction, -unit_direction]
    candidate_metrics: list[MutableMapping[str, float]] = []
    min_distance = math.inf

    for candidate in candidates:
        surface_point = candidate * EARTH_EQUATORIAL_RADIUS_M
        lat, lon, _ = geodetic_coordinates(surface_point)
        distance = haversine_distance(lat, lon, target_lat, target_lon)
        min_distance = min(min_distance, distance)
        candidate_metrics.append(
            {
                "latitude_deg": math.degrees(lat),
                "longitude_deg": math.degrees(lon),
                "distance_to_target_km": distance / 1_000.0,
            }
        )

    return {
        "planes": {plane: vec.tolist() for plane, vec in averaged_normals.items()},
        "intersection_candidates": candidate_metrics,
        "target_distance_km": min_distance / 1_000.0,
    }


def _record_metrics(
    states: Sequence[SpacecraftState],
    epoch: datetime,
    target_lat: float,
    target_lon: float,
    metrics: MutableMapping[str, object],
    cross_track_series: MutableMapping[str, list[float]],
    altitude_series: MutableMapping[str, list[float]],
    relative_stats: MutableMapping[str, object],
) -> None:
    """Update cross-track statistics for the current epoch."""

    vehicle_entries = metrics["vehicles"]
    centroid_metrics = metrics.get("centroid", {})
    epoch_values: dict[str, float] = {}

    for index, state in enumerate(states):
        position_ecef = inertial_to_ecef(state.position_m, epoch)
        latitude, longitude, altitude = geodetic_coordinates(position_ecef)
        cross_track_distance_m = haversine_distance(latitude, longitude, target_lat, target_lon)
        sign = 1.0 if latitude >= target_lat else -1.0
        cross_track_km = sign * (cross_track_distance_m / 1_000.0)

        cross_track_series[state.identifier].append(float(cross_track_km))
        altitude_series[state.identifier].append(float(altitude))
        epoch_values[state.identifier] = float(cross_track_km)

        entry = vehicle_entries[index]
        entry["max_cross_track_km"] = max(entry["max_cross_track_km"], cross_track_km)
        entry["min_cross_track_km"] = min(entry["min_cross_track_km"], cross_track_km)

        abs_value = abs(cross_track_km)
        if abs_value > entry["max_abs_cross_track_km"]:
            entry["max_abs_cross_track_km"] = abs_value
            entry["time_of_max_abs_cross_track"] = epoch.isoformat().replace("+00:00", "Z")
        if abs_value < entry["min_abs_cross_track_km"]:
            entry["min_abs_cross_track_km"] = abs_value
            entry["time_of_min_abs_cross_track"] = epoch.isoformat().replace("+00:00", "Z")

        previous_series = cross_track_series[state.identifier]
        if len(previous_series) >= 2 and previous_series[-2] == 0.0:
            entry["pass_count"] += 1
        elif len(previous_series) >= 2 and previous_series[-2] * cross_track_km < 0.0:
            entry["pass_count"] += 1

        metrics["overall_max_abs_cross_track_km"] = max(
            metrics["overall_max_abs_cross_track_km"], abs_value
        )
        metrics["overall_min_abs_cross_track_km"] = min(
            metrics["overall_min_abs_cross_track_km"], abs_value
        )

    if epoch_values and isinstance(centroid_metrics, MutableMapping):
        centroid_value = fmean(epoch_values.values())
        abs_centroid = abs(centroid_value)
        if abs_centroid < centroid_metrics.get("min_abs_cross_track_km", math.inf):
            centroid_metrics["min_cross_track_km"] = float(centroid_value)
            centroid_metrics["min_abs_cross_track_km"] = float(abs_centroid)
            centroid_metrics["time_of_min_abs_cross_track"] = (
                epoch.isoformat().replace("+00:00", "Z")
            )
            centroid_metrics["vehicle_cross_track_km_at_min"] = {
                identifier: float(value) for identifier, value in epoch_values.items()
            }
            centroid_metrics["vehicle_abs_cross_track_km_at_min"] = {
                identifier: float(abs(value))
                for identifier, value in epoch_values.items()
            }
            centroid_metrics["worst_vehicle_abs_cross_track_km"] = float(
                max(abs(value) for value in epoch_values.values())
            )

    leader_state = next((state for state in states if state.identifier == "FSAT-LDR"), None)
    plane_b_state = next(
        (state for state in states if PLANE_ASSIGNMENTS.get(state.identifier) == "Plane B"),
        None,
    )
    if leader_state is not None and plane_b_state is not None:
        normal_vec = np.cross(leader_state.position_m, leader_state.velocity_mps)
        norm_normal = np.linalg.norm(normal_vec)
        if norm_normal > 0.0:
            normal_unit = normal_vec / norm_normal
            relative_vec = plane_b_state.position_m - leader_state.position_m
            cross_track_km = float(np.dot(relative_vec, normal_unit) / 1_000.0)
            abs_val = abs(cross_track_km)
            if abs_val > relative_stats["max_abs"]:
                relative_stats["max_abs"] = abs_val
            if abs_val < relative_stats["min_abs"]:
                relative_stats["min_abs"] = abs_val
                relative_stats["time_of_min"] = epoch.isoformat().replace("+00:00", "Z")
            relative_stats["series"].append(
                (epoch.isoformat().replace("+00:00", "Z"), cross_track_km)
            )


def _rk4_step(states: Sequence[SpacecraftState], dt: float, settings: PropagatorSettings) -> list[SpacecraftState]:
    """Advance the spacecraft states by *dt* seconds using RK4 integration."""

    next_states: list[SpacecraftState] = []
    for state in states:
        x0 = state.position_m
        v0 = state.velocity_mps

        a1 = _acceleration(x0, v0, state, settings)
        k1_pos = v0
        k1_vel = a1

        a2 = _acceleration(x0 + 0.5 * dt * k1_pos, v0 + 0.5 * dt * k1_vel, state, settings)
        k2_pos = v0 + 0.5 * dt * k1_vel
        k2_vel = a2

        a3 = _acceleration(x0 + 0.5 * dt * k2_pos, v0 + 0.5 * dt * k2_vel, state, settings)
        k3_pos = v0 + 0.5 * dt * k2_vel
        k3_vel = a3

        a4 = _acceleration(x0 + dt * k3_pos, v0 + dt * k3_vel, state, settings)
        k4_pos = v0 + dt * k3_vel
        k4_vel = a4

        new_position = x0 + (dt / 6.0) * (k1_pos + 2.0 * k2_pos + 2.0 * k3_pos + k4_pos)
        new_velocity = v0 + (dt / 6.0) * (k1_vel + 2.0 * k2_vel + 2.0 * k3_vel + k4_vel)

        state.position_m = new_position
        state.velocity_mps = new_velocity
        next_states.append(state)

    return next_states


def _acceleration(
    position: np.ndarray,
    velocity: np.ndarray,
    state: SpacecraftState,
    settings: PropagatorSettings,
) -> np.ndarray:
    r"""Return acceleration including central gravity, \(J_2\), and drag."""

    r_vec = position
    v_vec = velocity
    r_norm = np.linalg.norm(r_vec)

    if r_norm == 0.0:
        raise ValueError("State vector has zero magnitude; cannot propagate.")

    mu = MU_EARTH
    central = -mu * r_vec / (r_norm**3)

    z2 = r_vec[2] ** 2
    r2 = r_norm**2
    factor = 1.5 * J2_COEFFICIENT * mu * (EARTH_EQUATORIAL_RADIUS_M**2) / (r_norm**5)
    coef_xy = factor * (5.0 * z2 / r2 - 1.0)
    coef_z = factor * (5.0 * z2 / r2 - 3.0)
    accel_j2 = np.array([coef_xy * r_vec[0], coef_xy * r_vec[1], coef_z * r_vec[2]], dtype=float)

    v_rel = v_vec - np.cross(OMEGA_EARTH_VECTOR, r_vec)
    speed_rel = np.linalg.norm(v_rel)
    altitude = r_norm - EARTH_EQUATORIAL_RADIUS_M
    density = _atmospheric_density(altitude, settings.solar_flux_index)
    drag = np.zeros(3, dtype=float)

    if speed_rel > 0.0 and density > 0.0:
        ballistic = state.area_m2 / state.mass_kg
        drag = (
            -0.5
            * density
            * state.drag_coefficient
            * ballistic
            * speed_rel
            * v_rel
        )

    return central + accel_j2 + drag


def _atmospheric_density(altitude_m: float, solar_index: float) -> float:
    """Return a simple exponential atmospheric density profile."""

    base_density = 3.614e-11  # kg/m^3 at 400 km reference
    scale_height = 55_000.0 * math.sqrt(max(solar_index, 1.0) / SOLAR_FLUX_BASE)
    density = base_density * math.exp(-(altitude_m - 400_000.0) / scale_height)
    return max(density, 0.0)


def _run_monte_carlo(
    leader_elements: OrbitalElements,
    formation: Sequence[Mapping[str, float | str]],
    settings: PropagatorSettings,
    target_lat: float,
    target_lon: float,
    monte_carlo: Mapping[str, object],
) -> MutableMapping[str, object]:
    """Execute Monte Carlo dispersions and aggregate cross-track statistics."""

    if not monte_carlo.get("enabled", True):
        return {
            "runs": 0,
            "max_abs_cross_track_km": {},
            "fleet_compliance_probability": 1.0,
        }

    runs = int(monte_carlo.get("runs", 0))
    if runs <= 0:
        return {
            "runs": 0,
            "max_abs_cross_track_km": {},
            "fleet_compliance_probability": 1.0,
        }
    runs = max(runs, 500)

    dispersions = monte_carlo.get("dispersions", {})
    sigma_a = float(dispersions.get("semi_major_axis_sigma_m", 0.0))
    sigma_i = math.radians(float(dispersions.get("inclination_sigma_deg", 0.0)))
    sigma_cd = float(dispersions.get("drag_coefficient_sigma", 0.0))

    seed = int(monte_carlo.get("seed", 42))
    rng = np.random.default_rng(seed)

    vehicle_ids = [entry.get("identifier", "spacecraft") for entry in formation]
    run_metrics_max: dict[str, list[float]] = {str(identifier): [] for identifier in vehicle_ids}
    run_metrics_min: dict[str, list[float]] = {str(identifier): [] for identifier in vehicle_ids}
    run_metrics_eval: dict[str, list[float]] = {str(identifier): [] for identifier in vehicle_ids}
    intersection_distances: list[float] = []
    relative_max_list: list[float] = []
    relative_min_list: list[float] = []
    centroid_abs_list: list[float] = []
    worst_abs_list: list[float] = []

    primary_success_count = 0
    waiver_success_count = 0
    relative_success_count = 0
    plane_success_count = 0

    evaluation_time = _resolve_evaluation_time(settings)
    primary_limit = float(settings.primary_cross_track_limit_km)
    waiver_limit = float(settings.waiver_cross_track_limit_km)
    plane_limit = settings.plane_intersection_limit_km

    epoch_offset = (settings.start_time - settings.epoch_time).total_seconds()

    evaluation_iso = evaluation_time.isoformat().replace("+00:00", "Z")
    LOGGER.info(
        "Monte Carlo dispersion: seed=%d, runs=%d, evaluation_utc=%s",
        seed,
        runs,
        evaluation_iso,
    )

    for _ in range(runs):
        dispersed_elements = OrbitalElements(
            semi_major_axis=leader_elements.semi_major_axis + rng.normal(0.0, sigma_a),
            eccentricity=leader_elements.eccentricity,
            inclination=leader_elements.inclination + rng.normal(0.0, sigma_i),
            raan=leader_elements.raan,
            arg_perigee=leader_elements.arg_perigee,
            mean_anomaly=leader_elements.mean_anomaly,
        )

        drag_scale = 1.0 + rng.normal(0.0, sigma_cd)
        states = _initial_states(
            dispersed_elements,
            formation,
            settings.drag_coefficient * drag_scale,
            epoch_offset_s=epoch_offset,
        )
        plane_metrics = _plane_intersection_metrics(states, target_lat, target_lon)
        plane_distance = float(plane_metrics.get("target_distance_km", math.inf))

        epoch = settings.start_time
        dt = settings.time_step_s
        vehicle_metrics = _initial_metric_structure(states, target_lat, target_lon)
        previous_signs = {state.identifier: 0.0 for state in states}
        relative_run_stats = {"max": 0.0, "min": math.inf}
        evaluation_snapshot: dict[str, float] = {}
        evaluation_best = math.inf

        while epoch <= settings.stop_time + timedelta(seconds=1e-6):
            current_values: dict[str, float] = {}
            for idx, state in enumerate(states):
                position_ecef = inertial_to_ecef(state.position_m, epoch)
                latitude, longitude, _ = geodetic_coordinates(position_ecef)
                distance = haversine_distance(latitude, longitude, target_lat, target_lon)
                sign = 1.0 if latitude >= target_lat else -1.0
                cross_track_km = sign * (distance / 1_000.0)

                vehicle_entry = vehicle_metrics["vehicles"][idx]
                vehicle_entry["max_cross_track_km"] = max(
                    vehicle_entry["max_cross_track_km"], cross_track_km
                )
                vehicle_entry["min_cross_track_km"] = min(
                    vehicle_entry["min_cross_track_km"], cross_track_km
                )
                abs_value = abs(cross_track_km)
                if abs_value > vehicle_entry["max_abs_cross_track_km"]:
                    vehicle_entry["max_abs_cross_track_km"] = abs_value
                if abs_value < vehicle_entry["min_abs_cross_track_km"]:
                    vehicle_entry["min_abs_cross_track_km"] = abs_value

                current_values[str(state.identifier)] = float(cross_track_km)

                identifier = str(state.identifier)
                previous_sign = previous_signs[identifier]
                if previous_sign != 0.0 and previous_sign * cross_track_km < 0.0:
                    vehicle_entry["pass_count"] += 1
                previous_signs[identifier] = cross_track_km

            diff = abs((epoch - evaluation_time).total_seconds())
            if diff < evaluation_best:
                evaluation_best = diff
                evaluation_snapshot = dict(current_values)

            if epoch >= settings.stop_time:
                break

            states = _rk4_step(states, dt, settings)
            epoch += timedelta(seconds=dt)

            leader_state = next((state for state in states if state.identifier == "FSAT-LDR"), None)
            plane_b_state = next(
                (state for state in states if PLANE_ASSIGNMENTS.get(state.identifier) == "Plane B"),
                None,
            )
            if leader_state is not None and plane_b_state is not None:
                normal_vec = np.cross(leader_state.position_m, leader_state.velocity_mps)
                norm_normal = np.linalg.norm(normal_vec)
                if norm_normal > 0.0:
                    normal_unit = normal_vec / norm_normal
                    relative_vec = plane_b_state.position_m - leader_state.position_m
                    cross_track_km = float(np.dot(relative_vec, normal_unit) / 1_000.0)
                    abs_val = abs(cross_track_km)
                    if abs_val > relative_run_stats["max"]:
                        relative_run_stats["max"] = abs_val
                    if abs_val < relative_run_stats["min"]:
                        relative_run_stats["min"] = abs_val

        evaluation_abs = {
            identifier: abs(value) if math.isfinite(value) else math.inf
            for identifier, value in evaluation_snapshot.items()
        }
        centroid_value = (
            fmean(evaluation_snapshot.values()) if evaluation_snapshot else math.nan
        )
        centroid_abs = abs(centroid_value) if math.isfinite(centroid_value) else math.inf
        worst_abs = max(evaluation_abs.values()) if evaluation_abs else math.inf

        primary_compliant = (
            math.isfinite(centroid_abs)
            and centroid_abs <= primary_limit
            and math.isfinite(worst_abs)
            and worst_abs <= waiver_limit
        )
        waiver_compliant = math.isfinite(worst_abs) and worst_abs <= waiver_limit

        if math.isfinite(centroid_abs):
            centroid_abs_list.append(centroid_abs)
        if math.isfinite(worst_abs):
            worst_abs_list.append(worst_abs)

        for entry in vehicle_metrics["vehicles"]:
            identifier = str(entry["identifier"])
            max_abs = float(entry["max_abs_cross_track_km"])
            min_abs = float(entry.get("min_abs_cross_track_km", math.inf))
            value = evaluation_snapshot.get(identifier, float("nan"))
            abs_value = evaluation_abs.get(identifier, math.inf)
            entry["cross_track_at_evaluation_km"] = (
                float(value) if math.isfinite(value) else None
            )
            entry["abs_cross_track_at_evaluation_km"] = (
                float(abs_value) if math.isfinite(abs_value) else None
            )
            entry["compliant"] = bool(
                math.isfinite(abs_value) and abs_value <= waiver_limit
            )
            run_metrics_max[identifier].append(max_abs)
            if math.isfinite(min_abs):
                run_metrics_min[identifier].append(min_abs)
            if math.isfinite(abs_value):
                run_metrics_eval[identifier].append(abs_value)

        plane_success = True
        if math.isfinite(plane_distance):
            intersection_distances.append(plane_distance)
            if plane_limit is not None:
                plane_success = plane_distance <= plane_limit
        elif plane_limit is not None:
            plane_success = False

        if plane_success:
            plane_success_count += 1

        if math.isfinite(relative_run_stats["max"]):
            relative_max_list.append(relative_run_stats["max"])
        if math.isfinite(relative_run_stats["min"]):
            relative_min_list.append(relative_run_stats["min"])

        if primary_compliant:
            primary_success_count += 1
        if waiver_compliant:
            waiver_success_count += 1
        if relative_run_stats["max"] <= waiver_limit:
            relative_success_count += 1

    aggregated: MutableMapping[str, object] = {
        "runs": runs,
        "seed": seed,
        "max_abs_cross_track_km": {},
        "min_abs_cross_track_km": {},
        "evaluation_abs_cross_track_km": {},
        "plane_intersection_distance_km": {},
        "relative_cross_track_km": {},
        "compliance": {
            "primary_fraction": float(primary_success_count / runs) if runs else 0.0,
            "waiver_fraction": float(waiver_success_count / runs) if runs else 0.0,
            "relative_fraction": float(relative_success_count / runs) if runs else 0.0,
        },
        "fleet_compliance_probability": float(primary_success_count / runs)
        if runs
        else 0.0,
        "absolute_cross_track_compliance_probability": float(
            waiver_success_count / runs
        )
        if runs
        else 0.0,
        "evaluation_time_utc": evaluation_time.isoformat().replace("+00:00", "Z"),
        "cross_track_limits_km": {
            "primary": float(primary_limit),
            "waiver": float(waiver_limit),
        },
    }

    if plane_limit is not None:
        aggregated["compliance"]["plane_fraction"] = float(
            plane_success_count / runs
        ) if runs else 0.0

    for identifier, values in run_metrics_max.items():
        if not values:
            continue
        array = np.asarray(values, dtype=float)
        aggregated["max_abs_cross_track_km"][identifier] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }

    for identifier, values in run_metrics_min.items():
        if not values:
            continue
        array = np.asarray(values, dtype=float)
        aggregated["min_abs_cross_track_km"][identifier] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }

    for identifier, values in run_metrics_eval.items():
        if not values:
            continue
        array = np.asarray(values, dtype=float)
        aggregated["evaluation_abs_cross_track_km"][identifier] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }

    if intersection_distances:
        array = np.asarray(intersection_distances, dtype=float)
        aggregated["plane_intersection_distance_km"]["fleet"] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }

    if relative_max_list:
        array = np.asarray(relative_max_list, dtype=float)
        aggregated["relative_cross_track_km"]["fleet_relative_max"] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }
    if relative_min_list:
        array = np.asarray(relative_min_list, dtype=float)
        aggregated["relative_cross_track_km"]["fleet_relative_min"] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }

    if centroid_abs_list:
        array = np.asarray(centroid_abs_list, dtype=float)
        aggregated["centroid_abs_cross_track_km"] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }
    if worst_abs_list:
        array = np.asarray(worst_abs_list, dtype=float)
        aggregated["worst_vehicle_abs_cross_track_km"] = {
            "mean": float(np.mean(array)),
            "std": float(np.std(array)),
            "p95": float(np.percentile(array, 95.0)),
            "min": float(np.min(array)),
            "max": float(np.max(array)),
        }

    return aggregated


def _write_outputs(
    output_directory: Path,
    series: Mapping[str, object],
    deterministic_metrics: Mapping[str, object],
    monte_carlo_metrics: Mapping[str, object],
    settings: PropagatorSettings,
    monte_carlo_config: Mapping[str, object],
) -> MutableMapping[str, str]:
    """Persist deterministic and Monte Carlo outputs to the run directory."""

    output_directory.mkdir(parents=True, exist_ok=True)

    deterministic_path = output_directory / "deterministic_cross_track.csv"
    relative_path = output_directory / "relative_cross_track.csv"
    summary_path = output_directory / "deterministic_summary.json"
    monte_carlo_path = output_directory / "monte_carlo_cross_track.csv"
    monte_carlo_summary_path = output_directory / "monte_carlo_summary.json"
    settings_path = output_directory / "solver_settings.json"

    _write_cross_track_csv(deterministic_path, series)

    relative_summary = deterministic_metrics.get("relative_cross_track")
    if isinstance(relative_summary, Mapping):
        _write_relative_cross_track_csv(relative_path, relative_summary)
        relative_summary = dict(relative_summary)
        relative_summary.pop("series", None)
        deterministic_metrics["relative_cross_track"] = relative_summary
    else:
        _write_relative_cross_track_csv(relative_path, {})

    summary_payload = {
        "metrics": deterministic_metrics,
        "settings": {
            "start_time_utc": settings.start_time.isoformat().replace("+00:00", "Z"),
            "epoch_time_utc": settings.epoch_time.isoformat().replace("+00:00", "Z"),
            "stop_time_utc": settings.stop_time.isoformat().replace("+00:00", "Z"),
            "time_step_s": settings.time_step_s,
            "drag_coefficient": settings.drag_coefficient,
            "ballistic_coefficient_m2_per_kg": settings.ballistic_coefficient_m2_per_kg,
            "solar_flux_index": settings.solar_flux_index,
        },
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    _write_monte_carlo_csv(monte_carlo_path, monte_carlo_metrics)
    monte_carlo_summary_path.write_text(json.dumps(monte_carlo_metrics, indent=2), encoding="utf-8")

    settings_payload = {
        "propagator": {
            "integrator": "fixed_step_rk4",
            "time_step_s": settings.time_step_s,
            "force_models": {
                "central_body": True,
                "j2": True,
                "atmospheric_drag": {
                    "model": "exponential",
                    "solar_flux_index": settings.solar_flux_index,
                },
            },
        },
        "monte_carlo": {
            "runs": monte_carlo_config.get("runs", 0),
            "seed": monte_carlo_config.get("seed", 0),
            "dispersions": monte_carlo_config.get("dispersions", {}),
        },
        "epoch_time_utc": settings.epoch_time.isoformat().replace("+00:00", "Z"),
    }
    settings_path.write_text(json.dumps(settings_payload, indent=2), encoding="utf-8")

    return {
        "deterministic_cross_track_csv": str(deterministic_path),
        "deterministic_summary_json": str(summary_path),
        "monte_carlo_cross_track_csv": str(monte_carlo_path),
        "relative_cross_track_csv": str(relative_path),
        "monte_carlo_summary_json": str(monte_carlo_summary_path),
        "solver_settings_json": str(settings_path),
    }


def _write_cross_track_csv(path: Path, series: Mapping[str, object]) -> None:
    """Write deterministic cross-track histories to *path*."""

    samples = series.get("samples", [])
    if not samples:
        path.write_text("time,\n", encoding="utf-8")
        return

    vehicle_ids = sorted(next(iter(samples))[1])
    header = ["time_iso"] + vehicle_ids
    lines = [",".join(header)]

    for timestamp, cross_track in samples:
        row = [timestamp.isoformat().replace("+00:00", "Z")]
        for identifier in vehicle_ids:
            row.append(f"{cross_track.get(identifier, 0.0):.6f}")
        lines.append(",".join(row))

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_monte_carlo_csv(path: Path, metrics: Mapping[str, object]) -> None:
    """Write Monte Carlo aggregate metrics to *path*."""

    vehicle_stats = metrics.get("max_abs_cross_track_km", {})
    min_stats_all = metrics.get("min_abs_cross_track_km", {})
    plane_stats = metrics.get("plane_intersection_distance_km", {})
    relative_stats = metrics.get("relative_cross_track_km", {})
    if (
        not vehicle_stats
        and not min_stats_all
        and not plane_stats
        and not relative_stats
    ):
        path.write_text(
            "vehicle_id,min_abs_cross_track_km_mean,min_abs_cross_track_km_std,min_abs_cross_track_km_p95,"
            "min_abs_cross_track_km_min,min_abs_cross_track_km_max,max_abs_cross_track_km_mean,max_abs_cross_track_km_std,"
            "max_abs_cross_track_km_p95,max_abs_cross_track_km_min,max_abs_cross_track_km_max,"
            "plane_intersection_distance_km_mean,plane_intersection_distance_km_std,plane_intersection_distance_km_p95,"
            "plane_intersection_distance_km_min,plane_intersection_distance_km_max,relative_cross_track_km_mean,"
            "relative_cross_track_km_std,relative_cross_track_km_p95,relative_cross_track_km_min,relative_cross_track_km_max\n",
            encoding="utf-8",
        )
        return

    header = (
        "vehicle_id,min_abs_cross_track_km_mean,min_abs_cross_track_km_std,min_abs_cross_track_km_p95,"
        "min_abs_cross_track_km_min,min_abs_cross_track_km_max,max_abs_cross_track_km_mean,max_abs_cross_track_km_std,"
        "max_abs_cross_track_km_p95,max_abs_cross_track_km_min,max_abs_cross_track_km_max,"
        "plane_intersection_distance_km_mean,plane_intersection_distance_km_std,plane_intersection_distance_km_p95,"
        "plane_intersection_distance_km_min,plane_intersection_distance_km_max,relative_cross_track_km_mean,"
        "relative_cross_track_km_std,relative_cross_track_km_p95,relative_cross_track_km_min,relative_cross_track_km_max"
    )
    lines = [header]

    identifiers = sorted(
        set(
            list(vehicle_stats.keys())
            + list(min_stats_all.keys())
            + list(plane_stats.keys())
            + list(relative_stats.keys())
        )
    )

    for identifier in identifiers:
        stats = vehicle_stats.get(identifier, {})
        min_stats = min_stats_all.get(identifier, {})
        plane_entry = plane_stats.get(identifier, {})
        relative_entry = relative_stats.get(identifier, {})
        line = ",".join(
            [
                str(identifier),
                f"{min_stats.get('mean', 0.0):.6f}",
                f"{min_stats.get('std', 0.0):.6f}",
                f"{min_stats.get('p95', 0.0):.6f}",
                f"{min_stats.get('min', 0.0):.6f}",
                f"{min_stats.get('max', 0.0):.6f}",
                f"{stats.get('mean', 0.0):.6f}",
                f"{stats.get('std', 0.0):.6f}",
                f"{stats.get('p95', 0.0):.6f}",
                f"{stats.get('min', 0.0):.6f}",
                f"{stats.get('max', 0.0):.6f}",
                f"{plane_entry.get('mean', 0.0):.6f}",
                f"{plane_entry.get('std', 0.0):.6f}",
                f"{plane_entry.get('p95', 0.0):.6f}",
                f"{plane_entry.get('min', 0.0):.6f}",
                f"{plane_entry.get('max', 0.0):.6f}",
                f"{relative_entry.get('mean', 0.0):.6f}",
                f"{relative_entry.get('std', 0.0):.6f}",
                f"{relative_entry.get('p95', 0.0):.6f}",
                f"{relative_entry.get('min', 0.0):.6f}",
                f"{relative_entry.get('max', 0.0):.6f}",
            ]
        )
        lines.append(line)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_relative_cross_track_csv(path: Path, summary: Mapping[str, object]) -> None:
    """Write relative cross-track series to *path*."""

    series = summary.get("series") if isinstance(summary, Mapping) else None
    if not series:
        path.write_text("time_iso,relative_cross_track_km\n", encoding="utf-8")
        return

    lines = ["time_iso,relative_cross_track_km"]
    for time_iso, value in series:
        lines.append(f"{time_iso},{float(value):.6f}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_time(value: object) -> datetime | None:
    """Parse an ISO-8601 timestamp into an aware :class:`datetime`."""

    if isinstance(value, str):
        try:
            if value.endswith("Z"):
                return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return None
    return None


__all__ = [
    "PropagatorSettings",
    "propagate_constellation",
    "scenario_cross_track_limits",
    "scenario_access_window",
]

