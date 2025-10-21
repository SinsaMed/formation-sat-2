"""Simulation of a three-satellite triangular formation over Tehran."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Sequence

import numpy as np
import pandas as pd

SECONDS_PER_DAY = 86_400.0
SECONDS_PER_YEAR = SECONDS_PER_DAY * 365.25

from constellation.geometry import triangle_area, triangle_aspect_ratio, triangle_side_lengths
from constellation.orbit import (
    EARTH_EQUATORIAL_RADIUS_M,
    cartesian_to_classical,
    geodetic_coordinates,
    haversine_distance,
    inertial_to_ecef,
    propagate_kepler,
)
from constellation.roe import MU_EARTH, OrbitalElements
from tools.stk_export import (
    FacilityDefinition,
    GroundContactInterval,
    GroundTrack,
    GroundTrackPoint,
    PropagatedStateHistory,
    ScenarioMetadata,
    SimulationResults,
    StateSample,
    sanitize_stk_identifier,
    unique_stk_names,
    export_simulation_to_stk,
)


@dataclass
class TriangleFormationResult:
    """Container collecting the outputs of the triangle simulation."""

    times: Sequence[datetime]
    positions_m: Mapping[str, np.ndarray]
    velocities_mps: Mapping[str, np.ndarray]
    latitudes_rad: Mapping[str, np.ndarray]
    longitudes_rad: Mapping[str, np.ndarray]
    altitudes_m: Mapping[str, np.ndarray]
    triangle_area_m2: np.ndarray
    triangle_aspect_ratio: np.ndarray
    triangle_sides_m: np.ndarray
    centroid_lat_rad: np.ndarray
    centroid_lon_rad: np.ndarray
    centroid_alt_m: np.ndarray
    max_ground_distance_km: np.ndarray
    min_command_distance_km: np.ndarray
    metrics: Mapping[str, object]
    artefacts: Mapping[str, Optional[str]]

    def to_summary(self) -> MutableMapping[str, object]:
        """Convert the simulation result into a JSON-serialisable mapping."""

        samples: list[MutableMapping[str, object]] = []
        satellite_ids = sorted(self.positions_m)
        geometry: MutableMapping[str, object] = {
            "times": [epoch.isoformat().replace("+00:00", "Z") for epoch in self.times],
            "satellite_ids": satellite_ids,
            "positions_m": {
                sat_id: self.positions_m[sat_id].tolist() for sat_id in satellite_ids
            },
            "latitudes_rad": {
                sat_id: self.latitudes_rad[sat_id].tolist() for sat_id in satellite_ids
            },
            "longitudes_rad": {
                sat_id: self.longitudes_rad[sat_id].tolist() for sat_id in satellite_ids
            },
            "altitudes_m": {
                sat_id: self.altitudes_m[sat_id].tolist() for sat_id in satellite_ids
            },
        }
        geometry["max_ground_distance_km"] = [
            float(value) for value in self.max_ground_distance_km
        ]
        geometry["min_command_distance_km"] = [
            float(value) for value in self.min_command_distance_km
        ]
        for index, epoch in enumerate(self.times):
            samples.append(
                {
                    "time": epoch.isoformat().replace("+00:00", "Z"),
                    "triangle_area_m2": float(self.triangle_area_m2[index]),
                    "triangle_aspect_ratio": float(self.triangle_aspect_ratio[index]),
                    "triangle_side_lengths_m": [
                        float(val) for val in self.triangle_sides_m[index]
                    ],
                    "centroid": {
                        "latitude_deg": math.degrees(self.centroid_lat_rad[index]),
                        "longitude_deg": math.degrees(self.centroid_lon_rad[index]),
                        "altitude_m": float(self.centroid_alt_m[index]),
                    },
                    "max_ground_distance_km": float(self.max_ground_distance_km[index]),
                }
            )

        return {
            "metrics": self.metrics,
            "samples": samples,
            "artefacts": dict(self.artefacts),
            "geometry": geometry,
        }


def simulate_triangle_formation(
    config_source: Mapping[str, object] | Path | str,
    output_directory: Optional[Path | str] = None,
) -> TriangleFormationResult:
    """Simulate the triangular formation described by *config_source*."""

    configuration = _load_configuration(config_source)
    reference = configuration["reference_orbit"]
    formation = configuration["formation"]
    metadata = configuration.get("metadata", {})

    epoch = _parse_time(reference["epoch_utc"])
    semi_major_axis_m = float(reference["semi_major_axis_km"]) * 1_000.0
    eccentricity = float(reference.get("eccentricity", 0.0))
    inclination = math.radians(float(reference.get("inclination_deg", 0.0)))
    raan = math.radians(float(reference.get("raan_deg", 0.0)))
    arg_perigee = math.radians(float(reference.get("argument_of_perigee_deg", 0.0)))
    mean_anomaly = math.radians(float(reference.get("mean_anomaly_deg", 0.0)))

    elements = OrbitalElements(
        semi_major_axis=semi_major_axis_m,
        eccentricity=eccentricity,
        inclination=inclination,
        raan=raan,
        arg_perigee=arg_perigee,
        mean_anomaly=mean_anomaly,
    )

    duration_s = float(formation.get("duration_s", 180.0))
    time_step_s = float(formation.get("time_step_s", 1.0))
    half_duration = 0.5 * duration_s
    sample_count = int(round(duration_s / time_step_s)) + 1

    offsets_m = _formation_offsets(float(formation["side_length_m"]))
    satellite_ids = tuple(sorted(offsets_m))

    plane_allocations = formation.get("plane_allocations", {})
    if not plane_allocations:
        plane_allocations = {
            satellite_ids[0]: "Plane A",
            satellite_ids[1]: "Plane A",
            satellite_ids[2]: "Plane B",
        }

    offsets = np.arange(sample_count, dtype=float) * time_step_s - half_duration
    times = [epoch + timedelta(seconds=float(offset)) for offset in offsets]

    reference_positions: list[np.ndarray] = []
    orientation_frames: list[np.ndarray] = []

    for delta_t in offsets:
        position, velocity = propagate_kepler(elements, delta_t)
        reference_positions.append(position)
        orientation_frames.append(_lvlh_frame(position, velocity))

    reference_positions = np.asarray(reference_positions)
    orientation_frames = np.asarray(orientation_frames)

    positions: dict[str, np.ndarray] = {
        sat_id: np.zeros((sample_count, 3), dtype=float) for sat_id in satellite_ids
    }
    latitudes: dict[str, np.ndarray] = {
        sat_id: np.zeros(sample_count, dtype=float) for sat_id in satellite_ids
    }
    longitudes: dict[str, np.ndarray] = {
        sat_id: np.zeros(sample_count, dtype=float) for sat_id in satellite_ids
    }
    altitudes: dict[str, np.ndarray] = {
        sat_id: np.zeros(sample_count, dtype=float) for sat_id in satellite_ids
    }

    triangle_area_series = np.zeros(sample_count, dtype=float)
    triangle_aspect_series = np.zeros(sample_count, dtype=float)
    triangle_sides_series = np.zeros((sample_count, 3), dtype=float)
    centroid_positions = np.zeros((sample_count, 3), dtype=float)
    centroid_latitudes = np.zeros(sample_count, dtype=float)
    centroid_longitudes = np.zeros(sample_count, dtype=float)
    centroid_altitudes = np.zeros(sample_count, dtype=float)
    max_ground_distance = np.zeros(sample_count, dtype=float)
    min_command_distance = np.full(sample_count, np.inf, dtype=float)

    target = formation.get("target", {})
    target_lat = math.radians(float(target.get("latitude_deg", 0.0)))
    target_lon = math.radians(float(target.get("longitude_deg", 0.0)))

    command = formation.get("command", {})
    command_station = command.get("station", {})
    default_lat_deg = math.degrees(target_lat)
    default_lon_deg = math.degrees(target_lon)
    command_lat = math.radians(float(command_station.get("latitude_deg", default_lat_deg)))
    command_lon = math.radians(float(command_station.get("longitude_deg", default_lon_deg)))

    for index, (position, frame) in enumerate(zip(reference_positions, orientation_frames)):
        vertices = []
        for sat_id in satellite_ids:
            offset_vec = frame @ offsets_m[sat_id]
            inertial = position + offset_vec
            positions[sat_id][index] = inertial
            vertices.append(inertial)

            ecef = inertial_to_ecef(inertial, times[index])
            lat, lon, alt = geodetic_coordinates(ecef)
            latitudes[sat_id][index] = lat
            longitudes[sat_id][index] = lon
            altitudes[sat_id][index] = alt

        triangle_area_series[index] = triangle_area(vertices)
        triangle_aspect_series[index] = triangle_aspect_ratio(vertices)
        triangle_sides_series[index] = triangle_side_lengths(vertices)

        centroid = sum(vertices) / len(vertices)
        centroid_positions[index] = centroid
        centroid_ecef = inertial_to_ecef(centroid, times[index])
        centroid_lat, centroid_lon, centroid_alt = geodetic_coordinates(centroid_ecef)
        centroid_latitudes[index] = centroid_lat
        centroid_longitudes[index] = centroid_lon
        centroid_altitudes[index] = centroid_alt

        max_distance = 0.0
        min_command = np.inf
        for sat_id in satellite_ids:
            distance = haversine_distance(
                latitudes[sat_id][index],
                longitudes[sat_id][index],
                target_lat,
                target_lon,
            )
            max_distance = max(max_distance, distance)
            command_distance = haversine_distance(
                latitudes[sat_id][index],
                longitudes[sat_id][index],
                command_lat,
                command_lon,
            )
            min_command = min(min_command, command_distance)
        max_ground_distance[index] = max_distance / 1_000.0
        min_command_distance[index] = min_command

    velocities: dict[str, np.ndarray] = {
        sat_id: _differentiate(positions[sat_id], time_step_s) for sat_id in satellite_ids
    }

    finite_mask = np.isfinite(min_command_distance)
    min_command_distance_km = np.where(
        finite_mask, min_command_distance / 1_000.0, np.inf
    )

    centre_index = int(np.argmin(np.abs(offsets)))
    orbital_elements = {}
    for sat_id in satellite_ids:
        elements = cartesian_to_classical(
            positions[sat_id][centre_index], velocities[sat_id][centre_index]
        )
        orbital_elements[sat_id] = {
            "semi_major_axis_km": elements.semi_major_axis / 1_000.0,
            "eccentricity": elements.eccentricity,
            "inclination_deg": math.degrees(elements.inclination),
            "raan_deg": math.degrees(elements.raan),
            "argument_of_perigee_deg": math.degrees(elements.arg_perigee),
            "mean_anomaly_deg": math.degrees(elements.mean_anomaly),
            "assigned_plane": plane_allocations.get(sat_id),
        }

    triangle_stats = _summarise_triangle_metrics(
        triangle_area_series,
        triangle_aspect_series,
        triangle_sides_series,
    )
    ground_stats = _summarise_ground_metrics(max_ground_distance, formation)
    maintenance = _estimate_maintenance_delta_v(
        positions,
        times,
        formation,
        semi_major_axis_m,
    )
    command_latency = _analyse_command_latency(
        min_command_distance_km,
        times,
        formation,
        semi_major_axis_m,
        command_lat,
        command_lon,
    )
    injection_recovery, injection_samples = _run_injection_recovery_monte_carlo(
        satellite_ids,
        formation,
    )
    drag_dispersion, drag_samples = _run_atmospheric_drag_dispersion_monte_carlo(
        formation,
        semi_major_axis_m,
        inclination,
    )

    window = _formation_window(
        triangle_aspect_series,
        max_ground_distance,
        time_step_s,
        formation,
        times,
    )

    metrics: MutableMapping[str, object] = {
        "triangle": triangle_stats,
        "ground_track": ground_stats,
        "formation_window": window,
        "orbital_elements": orbital_elements,
        "maintenance": maintenance,
        "command_latency": command_latency,
        "injection_recovery": injection_recovery,
        "drag_dispersion": drag_dispersion,
    }

    artefacts: MutableMapping[str, Optional[str]] = {
        "summary_path": None,
        "stk_directory": None,
        "maintenance_csv": None,
        "command_windows_csv": None,
        "injection_recovery_csv": None,
        "injection_recovery_plot": None,
        "drag_dispersion_csv": None,
    }

    result = TriangleFormationResult(
        times=times,
        positions_m=positions,
        velocities_mps=velocities,
        latitudes_rad=latitudes,
        longitudes_rad=longitudes,
        altitudes_m=altitudes,
        triangle_area_m2=triangle_area_series,
        triangle_aspect_ratio=triangle_aspect_series,
        triangle_sides_m=triangle_sides_series,
        centroid_lat_rad=centroid_latitudes,
        centroid_lon_rad=centroid_longitudes,
        centroid_alt_m=centroid_altitudes,
        max_ground_distance_km=max_ground_distance,
        min_command_distance_km=min_command_distance_km,
        metrics=metrics,
        artefacts=artefacts,
    )

    if output_directory is not None:
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        summary_path = output_path / "triangle_summary.json"
        artefacts["summary_path"] = str(summary_path)

        maintenance_rows = [
            {
                "satellite_id": sat_id,
                "mean_diff_accel_mps2": data["mean_diff_accel_mps2"],
                "peak_diff_accel_mps2": data["peak_diff_accel_mps2"],
                "delta_v_per_burn_mps": data["delta_v_per_burn_mps"],
                "annual_delta_v_mps": data["annual_delta_v_mps"],
            }
            for sat_id, data in maintenance["per_spacecraft"].items()
        ]
        maintenance_df = pd.DataFrame(
            maintenance_rows,
            columns=[
                "satellite_id",
                "mean_diff_accel_mps2",
                "peak_diff_accel_mps2",
                "delta_v_per_burn_mps",
                "annual_delta_v_mps",
            ],
        )
        maintenance_path = output_path / "maintenance_summary.csv"
        maintenance_df.to_csv(maintenance_path, index=False)
        artefacts["maintenance_csv"] = str(maintenance_path)

        command_rows = [
            {"window_index": index, **window}
            for index, window in enumerate(command_latency["contact_windows"])
        ]
        command_df = pd.DataFrame(
            command_rows, columns=["window_index", "start", "end", "duration_s"]
        )
        command_path = output_path / "command_windows.csv"
        command_df.to_csv(command_path, index=False)
        artefacts["command_windows_csv"] = str(command_path)

        injection_path = output_path / "injection_recovery.csv"
        injection_samples.to_csv(
            injection_path,
            index=False,
            columns=[
                "sample_id",
                "satellite_id",
                "position_error_m",
                "velocity_error_mps",
                "delta_v_mps",
                "success",
            ],
        )
        artefacts["injection_recovery_csv"] = str(injection_path)

        drag_path = output_path / "drag_dispersion.csv"
        drag_samples.to_csv(
            drag_path,
            index=False,
            columns=[
                "sample_id",
                "density_scale",
                "drag_coefficient",
                "ballistic_coefficient_m2_per_kg",
                "semi_major_axis_delta_m",
                "altitude_delta_m",
                "along_track_shift_km",
                "ground_distance_delta_km",
                "command_distance_delta_km",
                "within_tolerance",
            ],
        )
        artefacts["drag_dispersion_csv"] = str(drag_path)

        plot_path = output_path / "injection_recovery_cdf.svg"
        _write_injection_recovery_plot(injection_samples, plot_path)
        if plot_path.exists():
            artefacts["injection_recovery_plot"] = str(plot_path)

        stk_dir = output_path / "stk"
        _export_to_stk(
            result,
            stk_dir,
            scenario_name=str(metadata.get("scenario_name", "Tehran Triangle Formation")),
        )
        artefacts["stk_directory"] = str(stk_dir)

        summary_payload = result.to_summary()
        summary_path.write_text(
            json.dumps(summary_payload, indent=2), encoding="utf-8"
        )

    return result


def _load_configuration(source: Mapping[str, object] | Path | str) -> Mapping[str, object]:
    if isinstance(source, Mapping):
        return source
    path = Path(source)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise TypeError("Triangle configuration must be a mapping.")
    for key in ("reference_orbit", "formation"):
        if key not in payload:
            raise ValueError(f"Configuration missing required section: {key}")
    return payload


def _parse_time(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    raise TypeError("Configuration epoch must be a datetime or ISO 8601 string.")


def _lvlh_frame(position: Sequence[float], velocity: Sequence[float]) -> np.ndarray:
    r = np.asarray(position, dtype=float)
    v = np.asarray(velocity, dtype=float)
    r_hat = r / np.linalg.norm(r)
    h = np.cross(r, v)
    k_hat = h / np.linalg.norm(h)
    j_hat = np.cross(k_hat, r_hat)
    j_hat /= np.linalg.norm(j_hat)
    return np.column_stack((r_hat, j_hat, k_hat))


def _formation_offsets(side_length_m: float) -> Mapping[str, np.ndarray]:
    sqrt_three = math.sqrt(3.0)
    return {
        "SAT-1": np.array([-sqrt_three / 6.0 * side_length_m, -0.5 * side_length_m, 0.0]),
        "SAT-2": np.array([-sqrt_three / 6.0 * side_length_m, 0.5 * side_length_m, 0.0]),
        "SAT-3": np.array([sqrt_three / 3.0 * side_length_m, 0.0, 0.0]),
    }


def _differentiate(samples: np.ndarray, step: float) -> np.ndarray:
    derivatives = np.zeros_like(samples)
    count = samples.shape[0]
    for index in range(count):
        if 0 < index < count - 1:
            derivatives[index] = (samples[index + 1] - samples[index - 1]) / (2.0 * step)
        elif index == 0:
            derivatives[index] = (samples[index + 1] - samples[index]) / step
        else:
            derivatives[index] = (samples[index] - samples[index - 1]) / step
    return derivatives


def _summarise_triangle_metrics(areas: np.ndarray, aspects: np.ndarray, sides: np.ndarray) -> Mapping[str, float]:
    return {
        "mean_area_m2": float(np.mean(areas)),
        "min_area_m2": float(np.min(areas)),
        "max_area_m2": float(np.max(areas)),
        "mean_aspect_ratio": float(np.mean(aspects)),
        "aspect_ratio_max": float(np.max(aspects)),
        "mean_side_lengths_m": [float(val) for val in np.mean(sides, axis=0)],
    }


def _summarise_ground_metrics(distances_km: np.ndarray, formation: Mapping[str, object]) -> Mapping[str, float]:
    return {
        "max_ground_distance_km": float(np.max(distances_km)),
        "min_ground_distance_km": float(np.min(distances_km)),
        "ground_distance_tolerance_km": float(formation.get("ground_tolerance_km", 350.0)),
    }


def _formation_window(
    aspects: np.ndarray,
    distances_km: np.ndarray,
    step: float,
    formation: Mapping[str, object],
    times: Sequence[datetime],
) -> Mapping[str, object]:
    tolerance = float(formation.get("ground_tolerance_km", 350.0))
    aspect_limit = float(formation.get("aspect_ratio_tolerance", 1.02))
    mask = (distances_km <= tolerance) & (aspects <= aspect_limit)

    longest = 0
    current = 0
    start_index = 0
    window_start = window_end = 0

    for index, valid in enumerate(mask):
        if valid:
            if current == 0:
                start_index = index
            current += 1
            if current > longest:
                longest = current
                window_start = start_index
                window_end = index
        else:
            current = 0

    duration = max(longest - 1, 0) * step
    if longest == 0:
        return {"duration_s": 0.0, "start": None, "end": None}

    return {
        "duration_s": float(duration),
        "start": times[window_start].isoformat().replace("+00:00", "Z"),
        "end": times[window_end].isoformat().replace("+00:00", "Z"),
    }


def _estimate_maintenance_delta_v(
    positions: Mapping[str, np.ndarray],
    times: Sequence[datetime],
    formation: Mapping[str, object],
    semi_major_axis_m: float,
) -> Mapping[str, object]:
    maintenance = formation.get("maintenance", {})
    burn_duration_s = float(maintenance.get("burn_duration_s", 45.0))
    interval_days = float(maintenance.get("interval_days", 7.0))
    delta_v_budget_mps = float(maintenance.get("delta_v_budget_mps", 15.0))
    interval_seconds = max(interval_days * SECONDS_PER_DAY, 1.0)
    burns_per_year = SECONDS_PER_YEAR / interval_seconds

    count = len(times)
    if count > 1:
        step = (times[1] - times[0]).total_seconds()
    else:
        step = 0.0

    centroid = sum(positions[sat_id] for sat_id in positions) / float(len(positions))
    centroid_norm = np.linalg.norm(centroid, axis=1)
    centroid_accel = -MU_EARTH * centroid / centroid_norm[:, None] ** 3

    per_spacecraft: MutableMapping[str, Mapping[str, float]] = {}
    mean_accels = []
    peak_accels = []
    annual_totals = []

    for sat_id, states in positions.items():
        radii = np.linalg.norm(states, axis=1)
        accelerations = -MU_EARTH * states / radii[:, None] ** 3
        differential = np.linalg.norm(accelerations - centroid_accel, axis=1)
        mean_diff = float(np.mean(differential))
        peak_diff = float(np.max(differential))
        dv_per_burn = mean_diff * burn_duration_s
        annual_delta_v = dv_per_burn * burns_per_year

        mean_accels.append(mean_diff)
        peak_accels.append(peak_diff)
        annual_totals.append(annual_delta_v)

        per_spacecraft[sat_id] = {
            "mean_diff_accel_mps2": mean_diff,
            "peak_diff_accel_mps2": peak_diff,
            "delta_v_per_burn_mps": dv_per_burn,
            "annual_delta_v_mps": annual_delta_v,
        }

    annual_array = np.asarray(annual_totals, dtype=float)
    mean_accel = float(np.mean(mean_accels)) if mean_accels else 0.0
    peak_accel = float(np.max(peak_accels)) if peak_accels else 0.0

    orbit_period = 2.0 * math.pi * math.sqrt(semi_major_axis_m**3 / MU_EARTH)

    return {
        "assumptions": {
            "burn_duration_s": burn_duration_s,
            "maintenance_interval_days": interval_days,
            "burns_per_year": float(burns_per_year),
            "analysis_window_s": float(max((count - 1), 0) * step),
            "orbit_period_s": float(orbit_period),
            "delta_v_budget_mps": delta_v_budget_mps,
        },
        "mean_differential_acceleration_mps2": mean_accel,
        "peak_differential_acceleration_mps2": peak_accel,
        "per_spacecraft": per_spacecraft,
        "annual_delta_v_mps": {
            "mean": float(np.mean(annual_array)) if annual_totals else 0.0,
            "max": float(np.max(annual_array)) if annual_totals else 0.0,
            "min": float(np.min(annual_array)) if annual_totals else 0.0,
        },
    }


def _analyse_command_latency(
    min_distances_km: np.ndarray,
    times: Sequence[datetime],
    formation: Mapping[str, object],
    semi_major_axis_m: float,
    command_lat: float,
    command_lon: float,
) -> Mapping[str, object]:
    command_cfg = formation.get("command", {})
    range_km = float(
        command_cfg.get("contact_range_km", formation.get("ground_tolerance_km", 350.0))
    )

    count = len(times)
    if count > 1:
        step = (times[1] - times[0]).total_seconds()
    else:
        step = 0.0

    mask = np.asarray(min_distances_km) <= range_km

    windows: list[Mapping[str, object]] = []
    current_start: Optional[int] = None
    for index, in_contact in enumerate(mask):
        if in_contact and current_start is None:
            current_start = index
        elif not in_contact and current_start is not None:
            end_index = index - 1
            windows.append(
                _format_contact_window(times, current_start, end_index, step)
            )
            current_start = None
    if current_start is not None:
        windows.append(
            _format_contact_window(times, current_start, len(mask) - 1, step)
        )

    contact_duration_s = float(sum(window["duration_s"] for window in windows))
    orbit_period = 2.0 * math.pi * math.sqrt(semi_major_axis_m**3 / MU_EARTH)
    contact_probability = contact_duration_s / orbit_period if orbit_period else 0.0
    gap_s = max(orbit_period - contact_duration_s, 0.0)
    max_latency_hours = gap_s / 3600.0
    mean_latency_hours = max_latency_hours / 2.0

    return {
        "station": {
            "latitude_deg": math.degrees(command_lat),
            "longitude_deg": math.degrees(command_lon),
            "contact_range_km": range_km,
        },
        "contact_probability": contact_probability,
        "contact_duration_s": contact_duration_s,
        "contact_windows": windows,
        "passes_per_day": SECONDS_PER_DAY / orbit_period if orbit_period else 0.0,
        "max_latency_hours": max_latency_hours,
        "mean_latency_hours": mean_latency_hours,
        "latency_margin_hours": 12.0 - max_latency_hours,
        "assumptions": {
            "uniform_request_distribution": True,
            "single_station_operations": True,
        },
    }


def _format_contact_window(
    times: Sequence[datetime], start_index: int, end_index: int, step: float
) -> Mapping[str, object]:
    count = end_index - start_index + 1
    duration = max(count - 1, 0) * step
    return {
        "start": times[start_index].isoformat().replace("+00:00", "Z"),
        "end": times[end_index].isoformat().replace("+00:00", "Z"),
        "duration_s": float(duration),
    }


def _run_injection_recovery_monte_carlo(
    satellite_ids: Sequence[str], formation: Mapping[str, object]
) -> tuple[Mapping[str, object], pd.DataFrame]:
    config = formation.get("monte_carlo", {})
    sample_count = int(config.get("samples", 200))
    position_sigma_m = float(config.get("position_sigma_m", 250.0))
    velocity_sigma_mmps = float(config.get("velocity_sigma_mmps", 5.0))
    velocity_sigma_mps = velocity_sigma_mmps / 1_000.0
    recovery_time_s = float(config.get("recovery_time_s", 12.0 * 3600.0))
    delta_v_budget = float(config.get("delta_v_budget_mps", 15.0))
    seed = config.get("seed")
    rng = np.random.default_rng(seed)

    records: list[Mapping[str, object]] = []
    for sample_index in range(sample_count):
        for sat_id in satellite_ids:
            position_error = rng.normal(0.0, position_sigma_m, size=3)
            velocity_error = rng.normal(0.0, velocity_sigma_mps, size=3)
            position_mag = float(np.linalg.norm(position_error))
            velocity_mag = float(np.linalg.norm(velocity_error))
            delta_v_position = 2.0 * position_mag / recovery_time_s
            delta_v_total = delta_v_position + velocity_mag
            success = delta_v_total <= delta_v_budget
            records.append(
                {
                    "sample_id": sample_index,
                    "satellite_id": sat_id,
                    "position_error_m": position_mag,
                    "velocity_error_mps": velocity_mag,
                    "delta_v_mps": delta_v_total,
                    "success": bool(success),
                }
            )

    dataframe = pd.DataFrame.from_records(records)

    if dataframe.empty:
        aggregate = {
            "success_rate": 1.0,
            "mean_delta_v_mps": 0.0,
            "p95_delta_v_mps": 0.0,
            "max_delta_v_mps": 0.0,
        }
        per_spacecraft = {sat_id: aggregate for sat_id in satellite_ids}
        success_rate = 1.0
    else:
        success_rate = float(dataframe["success"].mean())
        per_spacecraft = {}
        for sat_id, group in dataframe.groupby("satellite_id"):
            per_spacecraft[str(sat_id)] = {
                "mean_delta_v_mps": float(group["delta_v_mps"].mean()),
                "p95_delta_v_mps": float(group["delta_v_mps"].quantile(0.95)),
                "max_delta_v_mps": float(group["delta_v_mps"].max()),
                "success_rate": float(group["success"].mean()),
            }
        aggregate = {
            "mean_delta_v_mps": float(dataframe["delta_v_mps"].mean()),
            "p95_delta_v_mps": float(dataframe["delta_v_mps"].quantile(0.95)),
            "max_delta_v_mps": float(dataframe["delta_v_mps"].max()),
        }

    metrics = {
        "success_rate": success_rate,
        "sample_count": sample_count,
        "per_spacecraft": per_spacecraft,
        "aggregate": aggregate,
        "assumptions": {
            "position_sigma_m": position_sigma_m,
            "velocity_sigma_mmps": velocity_sigma_mmps,
            "recovery_time_s": recovery_time_s,
            "delta_v_budget_mps": delta_v_budget,
        },
    }

    return metrics, dataframe


def _run_atmospheric_drag_dispersion_monte_carlo(
    formation: Mapping[str, object],
    semi_major_axis_m: float,
    inclination_rad: float,
) -> tuple[Mapping[str, object], pd.DataFrame]:
    settings = formation.get("drag_dispersion", {})
    sample_count = int(settings.get("samples", 200))
    density_sigma = float(settings.get("density_sigma", 0.2))
    drag_coefficient_sigma = float(settings.get("drag_coefficient_sigma", 0.05))
    reference_density = float(settings.get("reference_density_kg_m3", 3.5e-12))
    drag_coefficient = float(settings.get("drag_coefficient", 2.2))
    ballistic_area = float(settings.get("reference_area_m2", 1.0))
    spacecraft_mass = float(settings.get("spacecraft_mass_kg", 150.0))
    time_horizon_orbits = float(settings.get("time_horizon_orbits", 15.0))
    integration_step = float(settings.get("integration_step_s", 60.0))
    seed = settings.get("seed")

    if spacecraft_mass <= 0.0:
        raise ValueError("Spacecraft mass must be positive for drag dispersions.")

    rng = np.random.default_rng(seed)
    ballistic_coeff_base = ballistic_area / spacecraft_mass

    mean_motion = math.sqrt(MU_EARTH / semi_major_axis_m**3)
    orbital_period = 2.0 * math.pi / mean_motion
    horizon = max(time_horizon_orbits, 0.0) * orbital_period
    horizon = max(horizon, integration_step)

    records: list[Mapping[str, object]] = []
    tolerance_km = float(formation.get("ground_tolerance_km", 350.0))
    orbital_radius = semi_major_axis_m
    ground_projection_scale = math.cos(inclination_rad)

    time_samples = np.arange(0.0, horizon + 0.5 * integration_step, integration_step)

    for sample_id in range(sample_count):
        density_scale = max(0.0, 1.0 + rng.normal(0.0, density_sigma))
        cd_scale = max(0.0, 1.0 + rng.normal(0.0, drag_coefficient_sigma))

        rho = reference_density * density_scale
        cd = drag_coefficient * cd_scale
        ballistic_coefficient = ballistic_coeff_base

        orbital_velocity = math.sqrt(MU_EARTH / semi_major_axis_m)
        drag_acceleration = 0.5 * rho * cd * ballistic_coefficient * orbital_velocity**2
        da_dt = -2.0 * semi_major_axis_m**2 * drag_acceleration / MU_EARTH

        semi_major_axis_series = semi_major_axis_m + da_dt * time_samples
        semi_major_axis_series = np.maximum(semi_major_axis_series, EARTH_EQUATORIAL_RADIUS_M + 150_000.0)

        altitude_delta = semi_major_axis_series[-1] - semi_major_axis_m
        new_mean_motion = math.sqrt(MU_EARTH / semi_major_axis_series[-1] ** 3)
        delta_theta = (new_mean_motion - mean_motion) * horizon
        along_track_shift = abs(delta_theta) * orbital_radius / 1_000.0

        ground_distance_delta = along_track_shift * abs(ground_projection_scale)
        command_distance_delta = along_track_shift

        within_tolerance = ground_distance_delta <= tolerance_km

        records.append(
            {
                "sample_id": sample_id,
                "density_scale": float(density_scale),
                "drag_coefficient": float(cd),
                "ballistic_coefficient_m2_per_kg": float(ballistic_coefficient),
                "semi_major_axis_delta_m": float(altitude_delta),
                "altitude_delta_m": float(altitude_delta),
                "along_track_shift_km": float(along_track_shift),
                "ground_distance_delta_km": float(ground_distance_delta),
                "command_distance_delta_km": float(command_distance_delta),
                "within_tolerance": bool(within_tolerance),
            }
        )

    dataframe = pd.DataFrame.from_records(records)

    if dataframe.empty:
        aggregate = {
            "p95_ground_distance_delta_km": 0.0,
            "max_ground_distance_delta_km": 0.0,
            "p95_along_track_shift_km": 0.0,
            "max_along_track_shift_km": 0.0,
            "p95_altitude_delta_m": 0.0,
        }
        success_rate = 1.0
    else:
        aggregate = {
            "p95_ground_distance_delta_km": float(
                dataframe["ground_distance_delta_km"].quantile(0.95)
            ),
            "max_ground_distance_delta_km": float(
                dataframe["ground_distance_delta_km"].max()
            ),
            "p95_along_track_shift_km": float(
                dataframe["along_track_shift_km"].quantile(0.95)
            ),
            "max_along_track_shift_km": float(
                dataframe["along_track_shift_km"].max()
            ),
            "p95_altitude_delta_m": float(
                dataframe["altitude_delta_m"].quantile(0.95)
            ),
        }
        success_rate = float(dataframe["within_tolerance"].mean())

    metrics = {
        "sample_count": sample_count,
        "success_rate": success_rate,
        "aggregate": aggregate,
        "assumptions": {
            "density_sigma": density_sigma,
            "drag_coefficient_sigma": drag_coefficient_sigma,
            "reference_density_kg_m3": reference_density,
            "drag_coefficient": drag_coefficient,
            "reference_area_m2": ballistic_area,
            "spacecraft_mass_kg": spacecraft_mass,
            "time_horizon_orbits": time_horizon_orbits,
            "integration_step_s": integration_step,
        },
        "tolerance_km": tolerance_km,
    }

    return metrics, dataframe


def _write_injection_recovery_plot(samples: pd.DataFrame, output_path: Path) -> None:
    if samples.empty:
        return

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: WPS433 - imported for plotting

    values = np.sort(samples["delta_v_mps"].to_numpy(dtype=float))
    cumulative = (np.arange(len(values), dtype=float) + 1.0) / float(len(values))

    figure, axis = plt.subplots(figsize=(6.0, 4.0))
    axis.plot(values, cumulative, color="#1f77b4", linewidth=2.0)
    axis.set_xlabel("Δv per spacecraft (m/s)")
    axis.set_ylabel("Cumulative probability")
    axis.set_title("Injection recovery Δv distribution")
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)

def _export_to_stk(result: TriangleFormationResult, output_dir: Path, scenario_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    state_histories = []
    ground_tracks = []
    contacts = []

    satellite_ids = sorted(result.positions_m)
    safe_satellite_names = unique_stk_names(satellite_ids)
    safe_facility_name = sanitize_stk_identifier("Tehran", default="Facility")
    safe_scenario_name = sanitize_stk_identifier(scenario_name, default="Scenario")

    for sat_id in satellite_ids:
        safe_id = safe_satellite_names[sat_id]
        samples = [
            StateSample(
                epoch=epoch,
                position_eci_km=result.positions_m[sat_id][index] / 1_000.0,
                velocity_eci_kms=result.velocities_mps[sat_id][index] / 1_000.0,
            )
            for index, epoch in enumerate(result.times)
        ]
        state_histories.append(PropagatedStateHistory(satellite_id=safe_id, samples=samples))

        track_points = [
            GroundTrackPoint(
                epoch=epoch,
                latitude_deg=math.degrees(result.latitudes_rad[sat_id][index]),
                longitude_deg=math.degrees(result.longitudes_rad[sat_id][index]),
                altitude_km=result.altitudes_m[sat_id][index] / 1_000.0,
            )
            for index, epoch in enumerate(result.times)
        ]
        ground_tracks.append(GroundTrack(satellite_id=safe_id, points=track_points))

    window = result.metrics["formation_window"]
    if window.get("start") and window.get("end"):
        start = datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(window["end"].replace("Z", "+00:00"))
        for sat_id in satellite_ids:
            safe_id = safe_satellite_names[sat_id]
            contacts.append(
                GroundContactInterval(
                    satellite_id=safe_id,
                    facility_name=safe_facility_name,
                    start=start,
                    end=end,
                )
            )

    facilities = [
        FacilityDefinition(
            name=safe_facility_name,
            latitude_deg=35.6892,
            longitude_deg=51.3890,
            altitude_km=1.5,
        )
    ]

    scenario_metadata = ScenarioMetadata(
        scenario_name=safe_scenario_name,
        start_epoch=result.times[0],
        stop_epoch=result.times[-1],
        central_body="Earth",
        coordinate_frame="TEME",
        ephemeris_step_seconds=(result.times[1] - result.times[0]).total_seconds()
        if len(result.times) > 1
        else None,
    )

    sim_results = SimulationResults(
        state_histories=state_histories,
        ground_tracks=ground_tracks,
        ground_contacts=contacts,
        facilities=facilities,
    )

    export_simulation_to_stk(sim_results, output_dir, scenario_metadata)


__all__ = ["simulate_triangle_formation", "TriangleFormationResult"]

