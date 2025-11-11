"""Simulation of a three-satellite triangular formation over Tehran."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

import numpy as np
import pandas as pd

SECONDS_PER_DAY = 86_400.0
SECONDS_PER_YEAR = SECONDS_PER_DAY * 365.25

CLASSICAL_ELEMENT_FIELDS = (
    "semi_major_axis_km",
    "eccentricity",
    "inclination_deg",
    "raan_deg",
    "argument_of_perigee_deg",
    "mean_anomaly_deg",
)

from src.constellation.geometry import (
    triangle_area,
    triangle_aspect_ratio,
    triangle_side_lengths,
)
from src.constellation.orbit import (
    EARTH_EQUATORIAL_RADIUS_M,
    cartesian_to_classical,
    geodetic_coordinates,
    haversine_distance,
    inertial_to_ecef,
    propagate_kepler,
    propagate_perturbed,
    classical_to_cartesian,
)
from src.constellation.roe import MU_EARTH, OrbitalElements
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
    classical_elements: Mapping[str, Mapping[str, np.ndarray]]
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
            "classical_element_fields": list(CLASSICAL_ELEMENT_FIELDS),
            "classical_element_units": {
                "semi_major_axis_km": "km",
                "eccentricity": "",
                "inclination_deg": "deg",
                "raan_deg": "deg",
                "argument_of_perigee_deg": "deg",
                "mean_anomaly_deg": "deg",
            },
            "classical_elements": {
                sat_id: {
                    element: self.classical_elements[sat_id][element].tolist()
                    for element in self.classical_elements[sat_id]
                }
                for sat_id in satellite_ids
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
    formation = configuration["formation"]
    metadata = configuration.get("metadata", {})

    satellite_elements: dict[str, OrbitalElements] = {}
    if "satellites" in configuration:
        satellite_ids = [sat["id"] for sat in configuration["satellites"]]
        plane_allocations = {
            sat["id"]: sat["plane"] for sat in configuration["satellites"]
        }
        epoch = _parse_time(
            configuration["satellites"][0]["orbital_elements"]["epoch_utc"]
        )
        semi_major_axis_m = (
            float(
                configuration["satellites"][0]["orbital_elements"]["semi_major_axis_km"]
            )
            * 1_000.0
        )
        inclination = math.radians(
            float(
                configuration["satellites"][0]["orbital_elements"].get(
                    "inclination_deg", 0.0
                )
            )
        )

        for sat_config in configuration["satellites"]:
            elements = sat_config["orbital_elements"]
            satellite_elements[sat_config["id"]] = OrbitalElements(
                semi_major_axis=float(elements["semi_major_axis_km"]) * 1_000.0,
                eccentricity=float(elements.get("eccentricity", 0.0)),
                inclination=math.radians(float(elements.get("inclination_deg", 0.0))),
                raan=math.radians(float(elements.get("raan_deg", 0.0))),
                arg_perigee=math.radians(
                    float(elements.get("argument_of_perigee_deg", 0.0))
                ),
                mean_anomaly=math.radians(float(elements.get("mean_anomaly_deg", 0.0))),
            )
    else:
        reference = configuration["reference_orbit"]
        epoch = _parse_time(reference["epoch_utc"])
        semi_major_axis_m = float(reference["semi_major_axis_km"]) * 1_000.0
        eccentricity = float(reference.get("eccentricity", 0.0))
        inclination = math.radians(float(reference.get("inclination_deg", 0.0)))
        raan = math.radians(float(reference.get("raan_deg", 0.0)))
        arg_perigee = math.radians(
            float(reference.get("argument_of_perigee_deg", 0.0))
        )
        mean_anomaly = math.radians(float(reference.get("mean_anomaly_deg", 0.0)))

        reference_elements = OrbitalElements(
            semi_major_axis=semi_major_axis_m,
            eccentricity=eccentricity,
            inclination=inclination,
            raan=raan,
            arg_perigee=arg_perigee,
            mean_anomaly=mean_anomaly,
        )
        offsets_m = _formation_offsets(float(formation["side_length_m"]))
        satellite_ids = tuple(sorted(offsets_m))

        plane_allocations = formation.get("plane_allocations", {})
        if not plane_allocations:
            plane_allocations = {
                satellite_ids[0]: "Plane A",
                satellite_ids[1]: "Plane A",
                satellite_ids[2]: "Plane B",
            }

        # Get initial state of the reference orbit
        ref_pos_at_epoch, ref_vel_at_epoch = propagate_kepler(reference_elements, 0)

        # Get initial LVLH frame
        frame_at_epoch = _lvlh_frame(ref_pos_at_epoch, ref_vel_at_epoch)

        # Calculate initial orbital elements for each satellite
        for sat_id in satellite_ids:
            offset_vec = frame_at_epoch @ offsets_m[sat_id]
            # For a stable formation with zero radial offset, the initial relative velocity in the LVLH frame should be zero.
            offset_vel = np.array([0.0, 0.0, 0.0])

            sat_pos = ref_pos_at_epoch + offset_vec
            sat_vel = ref_vel_at_epoch + offset_vel
            satellite_elements[sat_id] = cartesian_to_classical(sat_pos, sat_vel)

    duration_s = float(formation.get("duration_s", 180.0))
    time_step_s = float(formation.get("time_step_s", 1.0))
    half_duration = 0.5 * duration_s
    sample_count = int(round(duration_s / time_step_s)) + 1

    offsets = np.arange(sample_count, dtype=float) * time_step_s - half_duration
    times = [epoch + timedelta(seconds=float(offset)) for offset in offsets]

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

    # Propagate each satellite independently
    velocities_temp: dict[str, list[np.ndarray]] = {sat_id: [] for sat_id in satellite_ids}

    perturbations = formation.get("perturbations", {})
    position_noise_sigma_m = float(perturbations.get("position_noise_sigma_m", 0.0))

    # Seed the random number generator for reproducibility
    seed = perturbations.get("seed")
    rng = np.random.default_rng(seed)

    # Initialize current_elements for step-by-step propagation
    current_elements = {sat_id: satellite_elements[sat_id] for sat_id in satellite_ids}

    for index in range(sample_count):
        inertial_positions = {}
        for sat_id in satellite_ids:
            elements = current_elements[sat_id]
            sat_config = next(
                (s for s in configuration.get("satellites", []) if s["id"] == sat_id),
                None,
            )
            C_R = 1.5
            A_srp = 1.0
            m = 150.0
            ballistic_coefficient = 0.025  # Default value
            if sat_config and "physical_properties" in sat_config:
                phys_props = sat_config["physical_properties"]
                C_D = float(phys_props.get("drag_coefficient", 2.2))
                A_drag = float(phys_props.get("area_m2", 1.0))
                m = float(phys_props.get("mass_kg", 150.0))
                ballistic_coefficient = C_D * A_drag / m
                C_R = float(phys_props.get("reflectivity_coefficient", 1.5))
                A_srp = float(phys_props.get("srp_area_m2", 1.0))

            # Propagate for one time_step_s from the current elements
            propagated_elements = propagate_perturbed(
                elements,
                time_step_s,  # Propagate for a single time step
                ballistic_coefficient,
                C_R=C_R,
                A_srp=A_srp,
                m=m,
            )
            current_elements[sat_id] = propagated_elements # Update current elements for next iteration

            pos, vel = classical_to_cartesian(propagated_elements)

            # if position_noise_sigma_m > 0.0:
            #     noise = rng.normal(0.0, position_noise_sigma_m, size=3)
            #     pos += noise

            positions[sat_id][index] = pos
            velocities_temp[sat_id].append(vel)
            inertial_positions[sat_id] = pos

            ecef = inertial_to_ecef(pos, times[index])
            lat, lon, alt = geodetic_coordinates(ecef)
            latitudes[sat_id][index] = lat
            longitudes[sat_id][index] = lon
            altitudes[sat_id][index] = alt

        # Now, compute triangle geometry based on the actual positions
        # The order of vertices matters for side length calculations, so sort by sat_id
        vertices = [inertial_positions[sat_id] for sat_id in satellite_ids]

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
        sat_id: np.array(velocities_temp[sat_id]) for sat_id in satellite_ids
    }

    triangle_area_series, triangle_aspect_series, triangle_sides_series = (
        _compute_triangle_geometry_from_positions(positions)
    )

    classical_series = _compute_classical_elements_series(positions, velocities)

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
            "inclination_deg": _normalise_degrees(elements.inclination),
            "raan_deg": _normalise_degrees(elements.raan),
            "argument_of_perigee_deg": _normalise_degrees(elements.arg_perigee),
            "mean_anomaly_deg": _normalise_degrees(elements.mean_anomaly),
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

    window, window_series = _formation_window(
        triangle_aspect_series,
        max_ground_distance,
        time_step_s,
        formation,
        times,
    )

    recurrence = _summarise_window_recurrence(
        window_series,
        semi_major_axis_m,
    )

    station_keeping = _assess_station_keeping(
        times,
        triangle_sides_series,
        formation,
        maintenance,
        time_step_s,
    )

    metrics: MutableMapping[str, object] = {
        "triangle": triangle_stats,
        "ground_track": ground_stats,
        "formation_window": window,
        "formation_windows": window_series,
        "formation_recurrence": recurrence,
        "orbital_elements": {
            "per_satellite": orbital_elements,
            "plane_assignments": plane_allocations,
            "time_series": {
                "fields": CLASSICAL_ELEMENT_FIELDS,
                "units": {
                    "semi_major_axis_km": "km",
                    "eccentricity": "",
                    "inclination_deg": "deg",
                    "raan_deg": "deg",
                    "argument_of_perigee_deg": "deg",
                    "mean_anomaly_deg": "deg",
                },
                "artefact_key": "orbital_elements_csv",
                "per_satellite_directory_key": "orbital_elements_directory",
            },
        },
        "maintenance": maintenance,
        "station_keeping": station_keeping,
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
        "formation_windows_csv": None,
        "station_keeping_csv": None,
        "orbital_elements_csv": None,
        "orbital_elements_directory": None,
    }

    result = TriangleFormationResult(
        times=times,
        positions_m=positions,
        velocities_mps=velocities,
        classical_elements=classical_series,
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

        windows_path = output_path / "formation_windows.csv"
        _write_formation_windows_csv(windows_path, window_series)
        artefacts["formation_windows_csv"] = str(windows_path)

        station_path = output_path / "station_keeping_events.csv"
        _write_station_keeping_csv(station_path, station_keeping)
        artefacts["station_keeping_csv"] = str(station_path)

        plot_path = output_path / "injection_recovery_cdf.svg"
        _write_injection_recovery_plot(injection_samples, plot_path)
        if plot_path.exists():
            artefacts["injection_recovery_plot"] = str(plot_path)

        orbital_path = output_path / "orbital_elements.csv"
        _write_orbital_elements_csv(orbital_path, times, classical_series)
        artefacts["orbital_elements_csv"] = str(orbital_path)
        metrics["orbital_elements"]["time_series"]["artefact"] = str(orbital_path)
        orbital_sat_dir = output_path / "orbital_elements"
        orbital_sat_dir.mkdir(parents=True, exist_ok=True)
        per_sat_paths = _write_orbital_elements_per_spacecraft(
            orbital_sat_dir, times, classical_series
        )
        if per_sat_paths:
            artefacts["orbital_elements_directory"] = str(orbital_sat_dir)
            metrics["orbital_elements"]["time_series"]["per_satellite_files"] = {
                sat_id: str(path)
                for sat_id, path in sorted(per_sat_paths.items(), key=lambda item: item[0])
            }

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
    if "satellites" not in payload and "reference_orbit" not in payload:
        raise ValueError(
            "Configuration missing required section: satellites or reference_orbit"
        )
    if "formation" not in payload:
        raise ValueError("Configuration missing required section: formation")
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
    """Return equilateral offsets constrained to the local horizontal plane."""

    sqrt_three = math.sqrt(3.0)
    return {
        "SAT-1": np.array(
            [0.0, -0.5 * side_length_m, -sqrt_three / 6.0 * side_length_m]
        ),
        "SAT-2": np.array(
            [0.0, 0.5 * side_length_m, -sqrt_three / 6.0 * side_length_m]
        ),
        "SAT-3": np.array([0.0, 0.0, sqrt_three / 3.0 * side_length_m]),
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


def _compute_triangle_geometry_from_positions(
    positions: Mapping[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Derive triangle diagnostics directly from the propagated positions."""

    if not positions:
        return (
            np.zeros(0, dtype=float),
            np.zeros(0, dtype=float),
            np.zeros((0, 3), dtype=float),
        )

    satellite_ids = sorted(positions)
    sample_count = next(iter(positions.values())).shape[0]
    areas = np.zeros(sample_count, dtype=float)
    aspects = np.zeros(sample_count, dtype=float)
    sides = np.zeros((sample_count, 3), dtype=float)

    for index in range(sample_count):
        vertices = [positions[sat_id][index] for sat_id in satellite_ids]
        areas[index] = triangle_area(vertices)
        aspects[index] = triangle_aspect_ratio(vertices)
        sides[index] = triangle_side_lengths(vertices)

    return areas, aspects, sides


def _compute_classical_elements_series(
    positions: Mapping[str, np.ndarray],
    velocities: Mapping[str, np.ndarray],
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Evaluate classical orbital elements for each spacecraft over time."""

    if not positions:
        return {}

    sample_count = next(iter(positions.values())).shape[0]
    series: dict[str, dict[str, np.ndarray]] = {}
    for sat_id, position_history in positions.items():
        per_satellite = {
            name: np.zeros(sample_count, dtype=float) for name in CLASSICAL_ELEMENT_FIELDS
        }
        series[sat_id] = per_satellite
        velocity_history = velocities.get(sat_id)
        if velocity_history is None:
            continue
        for index in range(sample_count):
            elements = cartesian_to_classical(
                position_history[index], velocity_history[index]
            )
            per_satellite["semi_major_axis_km"][index] = elements.semi_major_axis / 1_000.0
            per_satellite["eccentricity"][index] = elements.eccentricity
            per_satellite["inclination_deg"][index] = _normalise_degrees(
                elements.inclination
            )
            per_satellite["raan_deg"][index] = _normalise_degrees(elements.raan)
            per_satellite["argument_of_perigee_deg"][index] = _normalise_degrees(
                elements.arg_perigee
            )
            per_satellite["mean_anomaly_deg"][index] = _normalise_degrees(
                elements.mean_anomaly
            )

    return series


def _normalise_degrees(angle_rad: float) -> float:
    """Convert *angle_rad* to degrees on the [0, 360) interval."""

    value = math.degrees(angle_rad)
    if not math.isfinite(value):
        return float("nan")
    wrapped = math.fmod(value, 360.0)
    if wrapped < 0.0:
        wrapped += 360.0
    return wrapped


def _write_orbital_elements_csv(
    path: Path, times: Sequence[datetime], series: Mapping[str, Mapping[str, np.ndarray]]
) -> None:
    """Write a consolidated orbital-element history to *path*."""

    records: list[dict[str, object]] = []
    satellite_ids = sorted(series)
    for index, epoch in enumerate(times):
        timestamp = epoch.isoformat().replace("+00:00", "Z")
        for sat_id in satellite_ids:
            elements = series.get(sat_id)
            if not elements:
                continue
            record = {"time_utc": timestamp, "satellite_id": sat_id}
            for field in CLASSICAL_ELEMENT_FIELDS:
                values = elements.get(field)
                if values is None or index >= len(values):
                    record[field] = float("nan")
                else:
                    record[field] = float(values[index])
            records.append(record)

    dataframe = pd.DataFrame.from_records(records)
    if dataframe.empty:
        columns = ["time_utc", "satellite_id", *CLASSICAL_ELEMENT_FIELDS]
        dataframe = pd.DataFrame(columns=columns)
    dataframe.to_csv(path, index=False)


def _write_orbital_elements_per_spacecraft(
    directory: Path,
    times: Sequence[datetime],
    series: Mapping[str, Mapping[str, np.ndarray]],
) -> Mapping[str, Path]:
    """Persist individual per-spacecraft orbital-element CSVs."""

    paths: dict[str, Path] = {}
    for sat_id, elements in series.items():
        records: list[dict[str, object]] = []
        for index, epoch in enumerate(times):
            record = {"time_utc": epoch.isoformat().replace("+00:00", "Z")}
            for field in CLASSICAL_ELEMENT_FIELDS:
                values = elements.get(field)
                if values is None or index >= len(values):
                    record[field] = float("nan")
                else:
                    record[field] = float(values[index])
            records.append(record)
        dataframe = pd.DataFrame.from_records(records)
        if dataframe.empty:
            dataframe = pd.DataFrame(columns=["time_utc", *CLASSICAL_ELEMENT_FIELDS])
        filename = f"{sat_id.lower().replace(' ', '_')}_orbital_elements.csv"
        path = directory / filename
        dataframe.to_csv(path, index=False)
        paths[sat_id] = path
    return paths


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
) -> tuple[Mapping[str, object], Sequence[Mapping[str, object]]]:
    """Derive the principal formation window together with the full schedule."""

    windows = list(
        _enumerate_formation_windows(
            aspects,
            distances_km,
            step,
            formation,
            times,
        )
    )
    if not windows:
        primary: Mapping[str, object] = {
            "duration_s": 0.0,
            "start": None,
            "end": None,
            "sample_count": 0,
        }
        return primary, windows

    primary = max(windows, key=lambda item: float(item.get("duration_s", 0.0)))
    return primary, windows


def _enumerate_formation_windows(
    aspects: np.ndarray,
    distances_km: np.ndarray,
    step: float,
    formation: Mapping[str, object],
    times: Sequence[datetime],
) -> Iterable[Mapping[str, object]]:
    """Yield contiguous access windows that satisfy the ground-track criteria."""

    tolerance = float(formation.get("ground_tolerance_km", 350.0))
    aspect_limit = float(formation.get("aspect_ratio_tolerance", 1.02))
    mask = (distances_km <= tolerance) & (aspects <= aspect_limit)

    start_index: Optional[int] = None
    for index, valid in enumerate(mask):
        if valid and start_index is None:
            start_index = index
            continue
        if not valid and start_index is not None:
            yield _describe_window(
                start_index,
                index - 1,
                times,
                distances_km,
                aspects,
                step,
            )
            start_index = None

    if start_index is not None:
        yield _describe_window(
            start_index,
            len(mask) - 1,
            times,
            distances_km,
            aspects,
            step,
        )


def _describe_window(
    start: int,
    end: int,
    times: Sequence[datetime],
    distances_km: np.ndarray,
    aspects: np.ndarray,
    step: float,
) -> Mapping[str, object]:
    """Summarise a valid access window spanning indices ``start`` to ``end``."""

    start_time = times[start]
    end_time = times[end]
    if end > start:
        duration_seconds = max((end_time - start_time).total_seconds(), 0.0)
    else:
        half_step = timedelta(seconds=0.5 * step)
        earlier = start_time - half_step
        later = end_time + half_step
        # Preserve the original timezone information when clamping.
        if earlier < times[0]:
            earlier = times[0]
        if later > times[-1]:
            later = times[-1]
        duration_seconds = float(step)
        start_time = earlier
        end_time = later

    slice_obj = slice(start, end + 1)
    window_distances = distances_km[slice_obj]
    window_aspects = aspects[slice_obj]
    centroid_index = start + (end - start) // 2
    centroid_time = times[centroid_index]

    return {
        "start": start_time.isoformat().replace("+00:00", "Z"),
        "end": end_time.isoformat().replace("+00:00", "Z"),
        "duration_s": float(duration_seconds),
        "sample_count": int(end - start + 1),
        "max_ground_distance_km": float(np.max(window_distances)),
        "min_ground_distance_km": float(np.min(window_distances)),
        "max_aspect_ratio": float(np.max(window_aspects)),
        "centroid_time": centroid_time.isoformat().replace("+00:00", "Z"),
    }


def _summarise_window_recurrence(
    windows: Sequence[Mapping[str, object]],
    semi_major_axis_m: float,
) -> Mapping[str, object]:
    """Quantify the repeatability of access windows over the simulation horizon."""

    if not windows:
        return {
            "window_count": 0,
            "mean_duration_s": 0.0,
            "min_duration_s": 0.0,
            "max_duration_s": 0.0,
            "mean_interval_s": 0.0,
            "min_interval_s": 0.0,
            "max_interval_s": 0.0,
            "std_interval_s": 0.0,
            "expected_orbit_period_s": _orbital_period(semi_major_axis_m),
            "repeatability_score": 0.0,
            "interval_samples": 0,
        }

    durations = np.array([float(window.get("duration_s", 0.0)) for window in windows])
    mean_duration = float(np.mean(durations)) if durations.size else 0.0
    min_duration = float(np.min(durations)) if durations.size else 0.0
    max_duration = float(np.max(durations)) if durations.size else 0.0

    midpoints: list[datetime] = []
    for window in windows:
        start = window.get("start")
        end = window.get("end")
        if not start or not end:
            continue
        start_time = _parse_time(start)
        end_time = _parse_time(end)
        delta = end_time - start_time
        midpoint = start_time + delta / 2 if delta.total_seconds() >= 0.0 else start_time
        midpoints.append(midpoint)

    intervals = []
    for first, second in zip(midpoints, midpoints[1:]):
        delta = (second - first).total_seconds()
        if delta > 0.0:
            intervals.append(delta)

    if intervals:
        interval_array = np.asarray(intervals, dtype=float)
        mean_interval = float(np.mean(interval_array))
        min_interval = float(np.min(interval_array))
        max_interval = float(np.max(interval_array))
        std_interval = float(np.std(interval_array))
        if mean_interval > 0.0:
            repeatability = max(0.0, 1.0 - std_interval / mean_interval)
        else:
            repeatability = 0.0
    else:
        mean_interval = min_interval = max_interval = std_interval = 0.0
        repeatability = 1.0 if len(windows) == 1 else 0.0

    return {
        "window_count": len(windows),
        "mean_duration_s": mean_duration,
        "min_duration_s": min_duration,
        "max_duration_s": max_duration,
        "mean_interval_s": mean_interval,
        "min_interval_s": min_interval,
        "max_interval_s": max_interval,
        "std_interval_s": std_interval,
        "expected_orbit_period_s": _orbital_period(semi_major_axis_m),
        "repeatability_score": repeatability,
        "interval_samples": len(intervals),
    }


def _orbital_period(semi_major_axis_m: float) -> float:
    if semi_major_axis_m <= 0.0:
        return 0.0
    mean_motion = math.sqrt(MU_EARTH / semi_major_axis_m**3)
    return float(2.0 * math.pi / mean_motion)


def _assess_station_keeping(
    times: Sequence[datetime],
    triangle_sides: np.ndarray,
    formation: Mapping[str, object],
    maintenance: Mapping[str, object],
    step: float,
) -> Mapping[str, object]:
    """Detect when the triangular geometry exceeds the maintenance tolerance."""

    if not len(times):
        return {
            "status": "insufficient_data",
            "events": [],
            "tolerance_m": 0.0,
            "violation_fraction": 0.0,
            "recommended_delta_v_mps": 0.0,
            "max_deviation_m": 0.0,
        }

    base_length = float(formation.get("side_length_m", 0.0))
    default_tolerance = base_length * 0.01 if base_length > 0.0 else 10.0
    tolerance = float(
        formation.get(
            "station_keeping_tolerance_m",
            formation.get("repeatability_tolerance_m", default_tolerance),
        )
    )
    if tolerance <= 0.0:
        tolerance = default_tolerance

    deviations = np.abs(triangle_sides - base_length)
    max_deviation_series = np.max(deviations, axis=1)
    violation_mask = max_deviation_series > tolerance

    events: list[Mapping[str, object]] = []
    start_index: Optional[int] = None
    peak_violation = 0.0
    for index, violated in enumerate(violation_mask):
        if violated:
            if start_index is None:
                start_index = index
                peak_violation = float(max_deviation_series[index])
            else:
                peak_violation = max(peak_violation, float(max_deviation_series[index]))
            continue
        if start_index is not None:
            events.append(
                _build_station_event(
                    start_index,
                    index - 1,
                    times,
                    max_deviation_series,
                    peak_violation,
                    step,
                )
            )
            start_index = None
            peak_violation = 0.0

    if start_index is not None:
        events.append(
            _build_station_event(
                start_index,
                len(times) - 1,
                times,
                max_deviation_series,
                peak_violation,
                step,
            )
        )

    recommended_delta_v = _recommended_delta_v(maintenance)
    for event in events:
        event.setdefault("recommended_delta_v_mps", recommended_delta_v)

    violation_fraction = (
        float(np.count_nonzero(violation_mask)) / float(len(max_deviation_series))
        if len(max_deviation_series)
        else 0.0
    )

    max_deviation = float(np.max(max_deviation_series)) if len(max_deviation_series) else 0.0

    status = "nominal" if not events else "correction_required"
    return {
        "status": status,
        "events": events,
        "tolerance_m": tolerance,
        "violation_fraction": violation_fraction,
        "recommended_delta_v_mps": recommended_delta_v,
        "max_deviation_m": max_deviation,
    }


def _build_station_event(
    start_index: int,
    end_index: int,
    times: Sequence[datetime],
    deviations: np.ndarray,
    peak_violation: float,
    step: float,
) -> Mapping[str, object]:
    start_time = times[start_index]
    end_time = times[end_index]
    if end_index > start_index:
        duration_seconds = max((end_time - start_time).total_seconds(), 0.0)
    else:
        half_step = timedelta(seconds=0.5 * step)
        start_time = max(start_time - half_step, times[0])
        end_time = min(end_time + half_step, times[-1])
        duration_seconds = float(step)

    slice_obj = slice(start_index, end_index + 1)
    peak = max(peak_violation, float(np.max(deviations[slice_obj])))

    return {
        "start": start_time.isoformat().replace("+00:00", "Z"),
        "end": end_time.isoformat().replace("+00:00", "Z"),
        "duration_s": float(duration_seconds),
        "violation_samples": int(end_index - start_index + 1),
        "peak_deviation_m": float(peak),
    }


def _recommended_delta_v(maintenance: Mapping[str, object]) -> float:
    per_spacecraft = maintenance.get("per_spacecraft") if isinstance(maintenance, Mapping) else None
    if isinstance(per_spacecraft, Mapping) and per_spacecraft:
        deltas = [
            float(entry.get("delta_v_per_burn_mps", 0.0))
            for entry in per_spacecraft.values()
        ]
        if deltas:
            return float(np.mean(deltas))

    assumptions = maintenance.get("assumptions") if isinstance(maintenance, Mapping) else None
    if isinstance(assumptions, Mapping):
        return float(assumptions.get("delta_v_budget_mps", 0.0))
    return 0.0


def _write_formation_windows_csv(
    path: Path,
    windows: Sequence[Mapping[str, object]],
) -> None:
    """Serialise the detected formation windows to ``path``."""

    records: list[MutableMapping[str, object]] = []
    for index, window in enumerate(windows):
        record: MutableMapping[str, object] = {"window_index": index}
        record["start"] = window.get("start")
        record["end"] = window.get("end")
        record["duration_s"] = float(window.get("duration_s", 0.0))
        record["sample_count"] = int(window.get("sample_count", 0))
        record["max_ground_distance_km"] = float(
            window.get("max_ground_distance_km", float("nan"))
        )
        record["min_ground_distance_km"] = float(
            window.get("min_ground_distance_km", float("nan"))
        )
        record["max_aspect_ratio"] = float(window.get("max_aspect_ratio", float("nan")))
        record["centroid_time"] = window.get("centroid_time")
        records.append(record)

    dataframe = pd.DataFrame.from_records(records)
    if dataframe.empty:
        dataframe = pd.DataFrame(
            columns=[
                "window_index",
                "start",
                "end",
                "duration_s",
                "sample_count",
                "max_ground_distance_km",
                "min_ground_distance_km",
                "max_aspect_ratio",
                "centroid_time",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)


def _write_station_keeping_csv(
    path: Path,
    station_keeping: Mapping[str, object],
) -> None:
    """Write the station-keeping assessment events to ``path``."""

    events = station_keeping.get("events") if isinstance(station_keeping, Mapping) else []
    records: list[MutableMapping[str, object]] = []
    if isinstance(events, Sequence):
        for index, event in enumerate(events):
            record: MutableMapping[str, object] = {"event_index": index}
            record["start"] = event.get("start")
            record["end"] = event.get("end")
            record["duration_s"] = float(event.get("duration_s", 0.0))
            record["violation_samples"] = int(event.get("violation_samples", 0))
            record["peak_deviation_m"] = float(event.get("peak_deviation_m", 0.0))
            record["recommended_delta_v_mps"] = float(
                event.get("recommended_delta_v_mps", station_keeping.get("recommended_delta_v_mps", 0.0))
            )
            records.append(record)

    dataframe = pd.DataFrame.from_records(records)
    if dataframe.empty:
        dataframe = pd.DataFrame(
            columns=[
                "event_index",
                "start",
                "end",
                "duration_s",
                "violation_samples",
                "peak_deviation_m",
                "recommended_delta_v_mps",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)


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
