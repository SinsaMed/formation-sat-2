"""Simulation of a three-satellite triangular formation over Tehran."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Sequence

import numpy as np

from constellation.geometry import triangle_area, triangle_aspect_ratio, triangle_side_lengths
from constellation.orbit import (
    cartesian_to_classical,
    geodetic_coordinates,
    haversine_distance,
    inertial_to_ecef,
    propagate_kepler,
)
from constellation.roe import OrbitalElements
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

    target = formation.get("target", {})
    target_lat = math.radians(float(target.get("latitude_deg", 0.0)))
    target_lon = math.radians(float(target.get("longitude_deg", 0.0)))

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
        for sat_id in satellite_ids:
            distance = haversine_distance(
                latitudes[sat_id][index],
                longitudes[sat_id][index],
                target_lat,
                target_lon,
            )
            max_distance = max(max_distance, distance)
        max_ground_distance[index] = max_distance / 1_000.0

    velocities: dict[str, np.ndarray] = {
        sat_id: _differentiate(positions[sat_id], time_step_s) for sat_id in satellite_ids
    }

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
    }

    artefacts: MutableMapping[str, Optional[str]] = {"summary_path": None, "stk_directory": None}

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
        metrics=metrics,
        artefacts=artefacts,
    )

    if output_directory is not None:
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        summary_path = output_path / "triangle_summary.json"
        summary_path.write_text(json.dumps(result.to_summary(), indent=2), encoding="utf-8")
        artefacts["summary_path"] = str(summary_path)

        stk_dir = output_path / "stk"
        _export_to_stk(
            result,
            stk_dir,
            scenario_name=str(metadata.get("scenario_name", "Tehran Triangle Formation")),
        )
        artefacts["stk_directory"] = str(stk_dir)

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

