"""Efficient multi-day validation of the Tehran triangular formation."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

import numpy as np

from . import configuration
from .rgt_optimizer import (
    EARTH_RADIUS_KM,
    _ecef_to_geodetic,
    _eci_to_ecef,
    _greenwich_sidereal_angle,
    _haversine_distance,
    _j2_secular_rates,
    _state_vectors_eci,
    _target_coordinates,
    _wrap_angle,
    compute_repeat_ground_track_solution,
)
from sim.formation.triangle import _lvlh_frame, triangle_aspect_ratio, triangle_side_lengths


SECONDS_PER_DAY = 86_400.0


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path("config/scenarios/tehran_triangle.json"),
        help="Path to the formation configuration file.",
    )
    parser.add_argument(
        "--rgt-scenario",
        type=Path,
        default=Path("config/scenarios/tehran_daily_pass.json"),
        help="Scenario used to derive the repeat-ground-track solution.",
    )
    parser.add_argument(
        "--extended-days",
        type=float,
        default=1.0,
        help="Propagation horizon in days.",
    )
    parser.add_argument(
        "--time-step-s",
        type=float,
        default=5.0,
        help="Sampling interval in seconds for the validation propagation.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artefacts/formation_validation.json"),
        help="Path of the JSON report to produce.",
    )
    return parser.parse_args(args)


@dataclass
class FormationSample:
    epoch: datetime
    centroid_ground_distance_km: float
    centroid_cross_track_km: float
    centroid_lat_deg: float
    centroid_lon_deg: float
    aspect_ratio: float
    side_lengths_km: Sequence[float]


def main(args: Optional[Iterable[str]] = None) -> int:
    namespace = parse_args(args)

    formation_scenario = configuration.load_scenario(namespace.scenario)
    rgt_scenario = configuration.load_scenario(namespace.rgt_scenario)

    rgt_solution = compute_repeat_ground_track_solution(rgt_scenario)
    if rgt_solution is None or not rgt_solution.converged:
        raise RuntimeError("Repeat-ground-track solution could not be derived.")

    formation = formation_scenario["formation"]
    reference = formation_scenario["reference_orbit"]

    side_length_m = float(formation.get("side_length_m", 6_000.0))
    tolerance_km = float(formation.get("ground_tolerance_km", 30.0))
    aspect_limit = float(formation.get("aspect_ratio_tolerance", 1.02))

    offsets_rtn_km = _equilateral_offsets(side_length_m / 1_000.0)
    satellite_ids = tuple(sorted(offsets_rtn_km))

    step_s = max(float(namespace.time_step_s), 1.0)
    duration_days = max(float(namespace.extended_days), 1.0)
    sample_count = int(math.floor(duration_days * SECONDS_PER_DAY / step_s)) + 1

    start_epoch = _planning_start(rgt_scenario)
    rates = _prepare_rates(reference, rgt_solution)

    target_lat, target_lon = _target_coordinates(rgt_scenario)
    if target_lat is None or target_lon is None:
        raise RuntimeError("Scenario does not define target coordinates.")
    target_lat_deg = math.degrees(target_lat)
    target_lon_deg = math.degrees(target_lon)
    latitude_band_deg = float(formation.get("latitude_window_deg", 5.0))

    samples: list[FormationSample] = []
    day_windows: MutableMapping[int, list[tuple[int, int]]] = {}

    for index in range(sample_count):
        epoch = start_epoch + timedelta(seconds=index * step_s)
        state = _reference_state(reference, rates, epoch)
        positions = _apply_offsets(state, offsets_rtn_km, satellite_ids)

        centroid = np.mean(positions, axis=0)
        centroid_ecef = _eci_to_ecef(centroid, _greenwich_sidereal_angle(epoch))
        latitude_deg, longitude_deg, _ = _ecef_to_geodetic(centroid_ecef)
        distance_km = _haversine_distance(
            math.radians(latitude_deg),
            math.radians(longitude_deg),
            target_lat,
            target_lon,
        )
        delta_lon = _wrap_angle(math.radians(longitude_deg) - target_lon)
        cross_track_km = abs(math.cos(target_lat) * delta_lon) * EARTH_RADIUS_KM

        sides_km = np.asarray(triangle_side_lengths(positions), dtype=float)
        aspect = triangle_aspect_ratio(positions)

        samples.append(
            FormationSample(
                epoch=epoch,
                centroid_ground_distance_km=float(distance_km),
                centroid_cross_track_km=float(cross_track_km),
                centroid_lat_deg=float(latitude_deg),
                centroid_lon_deg=float(longitude_deg),
                aspect_ratio=float(aspect),
                side_lengths_km=[float(side) for side in sides_km],
            )
        )

        day_index = (epoch.date() - start_epoch.date()).days
        if day_index not in day_windows:
            day_windows[day_index] = []
        in_latitude_band = abs(samples[-1].centroid_lat_deg - target_lat_deg) <= latitude_band_deg
        if (
            in_latitude_band
            and samples[-1].centroid_cross_track_km <= tolerance_km
            and samples[-1].aspect_ratio <= aspect_limit
        ):
            if day_windows[day_index] and day_windows[day_index][-1][1] == index - 1:
                start_idx, _ = day_windows[day_index][-1]
                day_windows[day_index][-1] = (start_idx, index)
            else:
                day_windows[day_index].append((index, index))

    summaries = _summarise_days(samples, day_windows, step_s, tolerance_km)

    cross_track_series = [sample.centroid_cross_track_km for sample in samples]
    ground_series = [sample.centroid_ground_distance_km for sample in samples]
    aspect_series = [sample.aspect_ratio for sample in samples]
    side_lengths_series = [sample.side_lengths_km for sample in samples]
    latitude_series = [sample.centroid_lat_deg for sample in samples]
    longitude_series = [sample.centroid_lon_deg for sample in samples]
    max_side = max((max(lengths) for lengths in side_lengths_series), default=0.0)
    min_side = min((min(lengths) for lengths in side_lengths_series), default=0.0)
    metrics = {
        "min_cross_track_km": float(min(cross_track_series)) if cross_track_series else float("nan"),
        "max_cross_track_km": float(max(cross_track_series)) if cross_track_series else float("nan"),
        "min_ground_distance_km": float(min(ground_series)) if ground_series else float("nan"),
        "max_ground_distance_km": float(max(ground_series)) if ground_series else float("nan"),
        "max_aspect_ratio": float(max(aspect_series)) if aspect_series else float("nan"),
        "min_aspect_ratio": float(min(aspect_series)) if aspect_series else float("nan"),
        "max_side_length_km": float(max_side),
        "min_side_length_km": float(min_side),
        "min_latitude_deg": float(min(latitude_series)) if latitude_series else float("nan"),
        "max_latitude_deg": float(max(latitude_series)) if latitude_series else float("nan"),
        "min_longitude_deg": float(min(longitude_series)) if longitude_series else float("nan"),
        "max_longitude_deg": float(max(longitude_series)) if longitude_series else float("nan"),
    }

    report: MutableMapping[str, object] = {
        "scenario": str(namespace.scenario),
        "rgt_scenario": str(namespace.rgt_scenario),
        "start_utc": start_epoch.isoformat().replace("+00:00", "Z"),
        "duration_days": duration_days,
        "time_step_s": step_s,
        "side_length_km": side_length_m / 1_000.0,
        "tolerance_km": tolerance_km,
        "aspect_limit": aspect_limit,
        "target_latitude_deg": target_lat_deg,
        "target_longitude_deg": target_lon_deg,
        "latitude_band_deg": latitude_band_deg,
        "repeat_ground_track": rgt_solution.as_mapping(),
        "metrics": metrics,
        "daily_windows": summaries,
    }

    output_path = namespace.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Validation report written to {output_path}")
    return 0


def _equilateral_offsets(side_length_km: float) -> Mapping[str, Sequence[float]]:
    radius = side_length_km / math.sqrt(3.0)
    return {
        "SAT-1": (0.0, radius, 0.0),
        "SAT-2": (-0.5 * side_length_km, -0.5 * radius, 0.0),
        "SAT-3": (0.5 * side_length_km, -0.5 * radius, 0.0),
    }


def _planning_start(scenario: Mapping[str, object]) -> datetime:
    timing = scenario.get("timing") if isinstance(scenario.get("timing"), Mapping) else {}
    planning = timing.get("planning_horizon") if isinstance(timing, Mapping) else {}
    start = None
    if isinstance(planning, Mapping):
        start = _parse_time(planning.get("start_utc"))
    if start is None:
        start = _parse_time(scenario.get("epoch_utc"))
    if start is None:
        start = _parse_time(scenario.get("start_utc"))
    if start is None:
        start = datetime.now(timezone.utc)
    return start


def _parse_time(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        text = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            stamp = datetime.fromisoformat(text)
        except ValueError:
            return None
        return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
    return None


def _prepare_rates(
    reference: Mapping[str, object], rgt_solution
) -> Mapping[str, float]:
    semi_major_axis_km = float(reference.get("semi_major_axis_km", rgt_solution.semi_major_axis_km))
    inclination = math.radians(float(reference.get("inclination_deg", 0.0)))
    eccentricity = float(reference.get("eccentricity", 0.0))
    rates = _j2_secular_rates(semi_major_axis_km, eccentricity, inclination)
    rates["semi_major_axis_km"] = semi_major_axis_km
    rates["eccentricity"] = eccentricity
    rates["inclination_rad"] = inclination
    rates["raan_rad"] = math.radians(float(reference.get("raan_deg", 0.0)))
    rates["argument_of_perigee_rad"] = math.radians(float(reference.get("argument_of_perigee_deg", 0.0)))
    rates["mean_anomaly_rad"] = math.radians(float(reference.get("mean_anomaly_deg", 0.0)))
    return rates


def _reference_state(
    reference: Mapping[str, object],
    rates: Mapping[str, float],
    epoch: datetime,
) -> tuple[np.ndarray, np.ndarray]:
    epoch_ref = _parse_time(reference.get("epoch_utc")) or epoch
    dt_seconds = (epoch - epoch_ref).total_seconds()

    raan = _wrap_angle(rates["raan_rad"] + rates["raan_rate_rad_s"] * dt_seconds)
    argument = _wrap_angle(rates["argument_of_perigee_rad"] + rates["argument_of_perigee_rate_rad_s"] * dt_seconds)
    mean_anomaly = _wrap_angle(rates["mean_anomaly_rad"] + (rates["mean_motion_rad_s"] + rates["mean_anomaly_rate_rad_s"]) * dt_seconds)

    position, velocity = _state_vectors_eci(
        rates["semi_major_axis_km"],
        rates["eccentricity"],
        rates["inclination_rad"],
        raan,
        argument,
        mean_anomaly,
    )
    return np.asarray(position), np.asarray(velocity)


def _apply_offsets(
    state: tuple[np.ndarray, np.ndarray],
    offsets_rtn_km: Mapping[str, Sequence[float]],
    satellite_ids: Sequence[str],
) -> np.ndarray:
    position, velocity = state
    frame = _lvlh_frame(position, velocity)
    positions = []
    for sat_id in satellite_ids:
        offset = np.asarray(offsets_rtn_km[sat_id], dtype=float)
        transformed = position + frame @ offset
        positions.append(transformed)
    return np.asarray(positions)


def _summarise_days(
    samples: Sequence[FormationSample],
    day_windows: Mapping[int, Sequence[tuple[int, int]]],
    step_s: float,
    tolerance_km: float,
) -> Sequence[Mapping[str, object]]:
    summaries: list[Mapping[str, object]] = []
    for day_index, windows in sorted(day_windows.items()):
        if not windows:
            continue
        best_window = max(windows, key=lambda pair: pair[1] - pair[0])
        start_idx, end_idx = best_window
        start_epoch = samples[start_idx].epoch
        end_epoch = samples[end_idx].epoch
        duration = (end_epoch - start_epoch).total_seconds() + step_s
        cross_track_slice = [
            samples[i].centroid_cross_track_km for i in range(start_idx, end_idx + 1)
        ]
        ground_slice = [
            samples[i].centroid_ground_distance_km for i in range(start_idx, end_idx + 1)
        ]
        aspect_slice = [samples[i].aspect_ratio for i in range(start_idx, end_idx + 1)]
        latitude_slice = [samples[i].centroid_lat_deg for i in range(start_idx, end_idx + 1)]
        longitude_slice = [samples[i].centroid_lon_deg for i in range(start_idx, end_idx + 1)]
        summaries.append(
            {
                "day_index": int(day_index),
                "start": start_epoch.isoformat().replace("+00:00", "Z"),
                "end": end_epoch.isoformat().replace("+00:00", "Z"),
                "duration_s": float(duration),
                "max_cross_track_km": float(max(cross_track_slice)),
                "min_cross_track_km": float(min(cross_track_slice)),
                "max_ground_distance_km": float(max(ground_slice)),
                "min_ground_distance_km": float(min(ground_slice)),
                "max_aspect_ratio": float(max(aspect_slice)),
                "min_latitude_deg": float(min(latitude_slice)),
                "max_latitude_deg": float(max(latitude_slice)),
                "min_longitude_deg": float(min(longitude_slice)),
                "max_longitude_deg": float(max(longitude_slice)),
                "samples": int(end_idx - start_idx + 1),
            }
        )
    return summaries


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
