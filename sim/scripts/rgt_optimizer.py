"""Repeat-ground-track orbit optimisation utilities and command-line entry point."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

from . import configuration


MU_EARTH_KM3_S2 = 398_600.4418
EARTH_RADIUS_KM = 6_378.1363
J2_COEFFICIENT = 1.082_626_68e-3
SIDEREAL_DAY_S = 86_164.0905
EARTH_ROTATION_RATE_RAD_S = 2.0 * math.pi / SIDEREAL_DAY_S

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = PROJECT_ROOT / "config" / "scenarios" / "tehran_daily_pass.json"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "artefacts" / "rgt"


@dataclass
class RepeatGroundTrackSolution:
    """Container describing the outcome of the repeat-ground-track solver."""

    semi_major_axis_km: float
    nodal_period_s: float
    repeat_cycle_days: float
    orbits_per_cycle: float
    repeat_ratio: float
    residual_tau: float
    mean_motion_rev_per_day: float
    raan_rate_deg_per_day: float
    argument_of_perigee_rate_deg_per_day: float
    mean_anomaly_rate_deg_per_day: float
    perigee_altitude_km: float
    apogee_altitude_km: float
    converged: bool
    iterations: int
    initial_guess_km: float

    def as_mapping(self) -> MutableMapping[str, float | int | bool]:
        """Return a JSON-serialisable mapping of the solution attributes."""

        return {
            "semi_major_axis_km": float(self.semi_major_axis_km),
            "perigee_altitude_km": float(self.perigee_altitude_km),
            "apogee_altitude_km": float(self.apogee_altitude_km),
            "nodal_period_s": float(self.nodal_period_s),
            "repeat_cycle_days": float(self.repeat_cycle_days),
            "orbits_per_cycle": float(self.orbits_per_cycle),
            "repeat_ratio": float(self.repeat_ratio),
            "residual_tau": float(self.residual_tau),
            "mean_motion_rev_per_day": float(self.mean_motion_rev_per_day),
            "raan_rate_deg_per_day": float(self.raan_rate_deg_per_day),
            "argument_of_perigee_rate_deg_per_day": float(
                self.argument_of_perigee_rate_deg_per_day
            ),
            "mean_anomaly_rate_deg_per_day": float(
                self.mean_anomaly_rate_deg_per_day
            ),
            "converged": bool(self.converged),
            "iterations": int(self.iterations),
            "initial_guess_semi_major_axis_km": float(self.initial_guess_km),
        }


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario",
        nargs="?",
        default=DEFAULT_SCENARIO,
        help="Scenario identifier or configuration path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to store optimisation artefacts.",
    )
    parser.add_argument(
        "--repeat-cycle-days",
        type=int,
        help="Override the repeat cycle length in sidereal days.",
    )
    parser.add_argument(
        "--orbits-per-cycle",
        type=int,
        help="Override the number of revolutions completed during the repeat cycle.",
    )
    parser.add_argument(
        "--time-step-s",
        type=float,
        default=1.0,
        help="Sampling interval, in seconds, for visibility estimation.",
    )
    parser.add_argument(
        "--min-elevation-deg",
        type=float,
        default=20.0,
        help="Minimum elevation, in degrees, defining a valid access segment.",
    )
    return parser.parse_args(args)


def compute_repeat_ground_track_solution(
    scenario: Mapping[str, object],
    *,
    repeat_cycle_days: Optional[float] = None,
    orbits_per_cycle: Optional[float] = None,
    tolerance: float = 1e-10,
    max_iterations: int = 80,
) -> RepeatGroundTrackSolution | None:
    """Solve for the semi-major axis delivering the requested repeat ground track."""

    orbital = scenario.get("orbital_elements")
    if not isinstance(orbital, Mapping):
        return None
    classical = orbital.get("classical")
    if not isinstance(classical, Mapping):
        return None

    repeat = orbital.get("repeat_ground_track", {})
    if not isinstance(repeat, Mapping):
        repeat = {}

    repeat_cycle = (
        float(repeat_cycle_days)
        if repeat_cycle_days is not None
        else float(repeat.get("repeat_cycle_days", 1.0))
    )
    orbits_cycle = (
        float(orbits_per_cycle)
        if orbits_per_cycle is not None
        else float(repeat.get("orbits_per_cycle", 15.0))
    )

    if repeat_cycle <= 0.0 or orbits_cycle <= 0.0:
        return None

    repeat_ratio = repeat_cycle / orbits_cycle

    eccentricity = float(classical.get("eccentricity", 0.0))
    inclination = math.radians(float(classical.get("inclination_deg", 0.0)))

    nodal_period_target = repeat_cycle * SIDEREAL_DAY_S / orbits_cycle
    initial_semi_major_axis = (
        MU_EARTH_KM3_S2 * (nodal_period_target / (2.0 * math.pi)) ** 2
    ) ** (1.0 / 3.0)

    def error_function(a_km: float) -> float:
        rates = _j2_secular_rates(a_km, eccentricity, inclination)
        n_rad_s = rates["mean_motion_rad_s"]
        nodal_rate = n_rad_s + rates["mean_anomaly_rate_rad_s"] + rates["argument_of_perigee_rate_rad_s"]
        numerator = EARTH_ROTATION_RATE_RAD_S - rates["raan_rate_rad_s"]
        denominator = nodal_rate
        if denominator == 0.0:
            return math.inf
        return repeat_ratio - numerator / denominator

    lower = max(initial_semi_major_axis * 0.9, EARTH_RADIUS_KM + 100.0)
    upper = initial_semi_major_axis * 1.1
    f_lower = error_function(lower)
    f_upper = error_function(upper)

    expansion = 0
    while f_lower * f_upper > 0.0 and expansion < 40:
        expansion += 1
        span = 50.0 * expansion
        lower = max(lower - span, EARTH_RADIUS_KM + 100.0)
        upper = upper + span
        f_lower = error_function(lower)
        f_upper = error_function(upper)

    converged = False
    iterations = 0
    solution = initial_semi_major_axis

    if f_lower * f_upper <= 0.0 and math.isfinite(f_lower) and math.isfinite(f_upper):
        for iterations in range(1, max_iterations + 1):
            midpoint = 0.5 * (lower + upper)
            f_mid = error_function(midpoint)
            if abs(f_mid) < tolerance or abs(upper - lower) < 1e-9:
                solution = midpoint
                converged = True
                break
            if f_lower * f_mid <= 0.0:
                upper = midpoint
                f_upper = f_mid
            else:
                lower = midpoint
                f_lower = f_mid
        else:
            solution = midpoint
    else:
        iterations = 0

    rates = _j2_secular_rates(solution, eccentricity, inclination)
    n_rad_s = rates["mean_motion_rad_s"]
    nodal_rate = n_rad_s + rates["mean_anomaly_rate_rad_s"] + rates["argument_of_perigee_rate_rad_s"]
    nodal_period = 2.0 * math.pi / nodal_rate if nodal_rate else math.inf
    residual = error_function(solution)

    perigee_altitude = solution * (1.0 - eccentricity) - EARTH_RADIUS_KM
    apogee_altitude = solution * (1.0 + eccentricity) - EARTH_RADIUS_KM

    mean_motion_rev_per_day = (n_rad_s * 86_400.0) / (2.0 * math.pi)

    return RepeatGroundTrackSolution(
        semi_major_axis_km=solution,
        nodal_period_s=nodal_period,
        repeat_cycle_days=repeat_cycle,
        orbits_per_cycle=orbits_cycle,
        repeat_ratio=repeat_ratio,
        residual_tau=residual,
        mean_motion_rev_per_day=mean_motion_rev_per_day,
        raan_rate_deg_per_day=math.degrees(rates["raan_rate_rad_s"]) * 86_400.0,
        argument_of_perigee_rate_deg_per_day=math.degrees(
            rates["argument_of_perigee_rate_rad_s"]
        )
        * 86_400.0,
        mean_anomaly_rate_deg_per_day=math.degrees(
            rates["mean_anomaly_rate_rad_s"]
        )
        * 86_400.0,
        perigee_altitude_km=perigee_altitude,
        apogee_altitude_km=apogee_altitude,
        converged=converged,
        iterations=iterations,
        initial_guess_km=initial_semi_major_axis,
    )


def estimate_visibility(
    scenario: Mapping[str, object],
    semi_major_axis_km: float,
    *,
    time_step_s: float = 1.0,
    elevation_threshold_deg: float = 20.0,
) -> MutableMapping[str, object]:
    """Estimate target visibility based on a two-body propagation."""

    target_lat, target_lon = _target_coordinates(scenario)
    if target_lat is None or target_lon is None:
        return {}

    timing = scenario.get("timing") if isinstance(scenario.get("timing"), Mapping) else {}
    propagation = timing.get("propagation") if isinstance(timing, Mapping) else {}

    start_time = _parse_time(propagation.get("start_utc")) if propagation else None
    stop_time = _parse_time(propagation.get("end_utc")) if propagation else None
    midpoint = _scenario_midpoint(scenario)

    if midpoint is None:
        return {}

    if start_time is None:
        start_time = midpoint - timedelta(minutes=8)
    if stop_time is None:
        stop_time = midpoint + timedelta(minutes=8)

    orbital = scenario.get("orbital_elements")
    if not isinstance(orbital, Mapping):
        return {}
    classical = orbital.get("classical")
    if not isinstance(classical, Mapping):
        return {}

    epoch = _parse_time(orbital.get("epoch_utc"))
    if epoch is None:
        epoch = midpoint - timedelta(minutes=30)

    inclination = math.radians(float(classical.get("inclination_deg", 0.0)))
    eccentricity = float(classical.get("eccentricity", 0.0))
    raan = math.radians(float(classical.get("raan_deg", 0.0)))
    argument_of_perigee = math.radians(float(classical.get("argument_of_perigee_deg", 0.0)))
    mean_anomaly = math.radians(float(classical.get("mean_anomaly_deg", 0.0)))

    rates = _j2_secular_rates(semi_major_axis_km, eccentricity, inclination)
    mean_motion = rates["mean_motion_rad_s"]

    dt_midpoint = (midpoint - epoch).total_seconds()
    r_mid = _position_eci(
        semi_major_axis_km,
        eccentricity,
        inclination,
        raan,
        argument_of_perigee,
        mean_anomaly + mean_motion * dt_midpoint,
    )
    phi_mid = math.atan2(r_mid[1], r_mid[0])
    theta_mid = _wrap_angle(phi_mid - target_lon)
    theta0 = theta_mid - EARTH_ROTATION_RATE_RAD_S * dt_midpoint

    samples: list[tuple[datetime, float]] = []
    step = max(time_step_s, 0.5)
    current = start_time
    while current <= stop_time:
        dt_seconds = (current - epoch).total_seconds()
        mean_anomaly_t = mean_anomaly + mean_motion * dt_seconds
        position_eci = _position_eci(
            semi_major_axis_km,
            eccentricity,
            inclination,
            raan,
            argument_of_perigee,
            mean_anomaly_t,
        )
        theta = theta0 + EARTH_ROTATION_RATE_RAD_S * dt_seconds
        position_ecef = _eci_to_ecef(position_eci, theta)
        elevation = _elevation_angle(position_ecef, target_lat, target_lon)
        samples.append((current, elevation))
        current += timedelta(seconds=step)

    segments = _visibility_segments(samples, elevation_threshold_deg)
    durations = [
        (end - start).total_seconds()
        for start, end in segments
        if end > start
    ]
    longest = max(durations) if durations else 0.0
    max_elevation = max((elevation for _, elevation in samples), default=float("nan"))

    return {
        "threshold_elevation_deg": float(elevation_threshold_deg),
        "time_step_s": float(step),
        "longest_duration_s": float(longest),
        "segments": [
            {
                "start_utc": start.isoformat().replace("+00:00", "Z"),
                "end_utc": end.isoformat().replace("+00:00", "Z"),
                "duration_s": float((end - start).total_seconds()),
            }
            for start, end in segments
        ],
        "max_elevation_deg": float(max_elevation),
        "sample_count": len(samples),
    }


def main(args: Optional[Iterable[str]] = None) -> int:
    namespace = parse_args(args)

    scenario_path = configuration.resolve_scenario_path(namespace.scenario)
    scenario = configuration.load_scenario(scenario_path)

    solution = compute_repeat_ground_track_solution(
        scenario,
        repeat_cycle_days=namespace.repeat_cycle_days,
        orbits_per_cycle=namespace.orbits_per_cycle,
    )

    if solution is None:
        print("Repeat-ground-track solution could not be derived from the scenario.")
        return 1

    visibility = estimate_visibility(
        scenario,
        solution.semi_major_axis_km,
        time_step_s=namespace.time_step_s,
        elevation_threshold_deg=namespace.min_elevation_deg,
    )

    output_dir = _resolve_output_directory(namespace.output_dir)

    summary: MutableMapping[str, object] = {
        "scenario_source": str(scenario_path),
        "repeat_ground_track": solution.as_mapping(),
        "visibility": visibility,
    }

    summary_path = output_dir / "repeat_ground_track_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    updated = _updated_scenario_mapping(scenario, solution)
    updated_path = output_dir / "updated_scenario.json"
    updated_path.write_text(json.dumps(updated, indent=2), encoding="utf-8")

    print(
        "Resolved repeat-ground-track semi-major axis: {:.3f} km (residual {:.3e}).".format(
            solution.semi_major_axis_km, solution.residual_tau
        )
    )
    if visibility:
        print(
            "Longest elevation-above-{:.1f}° segment lasts {:.1f} s.".format(
                namespace.min_elevation_deg, visibility.get("longest_duration_s", 0.0)
            )
        )
    print(f"Artefacts written to {output_dir}")

    return 0


def _resolve_output_directory(candidate: Optional[Path]) -> Path:
    if candidate is None:
        timestamp = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%MZ")
        directory = DEFAULT_OUTPUT_ROOT / timestamp
    else:
        directory = candidate if candidate.is_absolute() else (PROJECT_ROOT / candidate)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _j2_secular_rates(
    semi_major_axis_km: float,
    eccentricity: float,
    inclination_rad: float,
) -> MutableMapping[str, float]:
    semi_major_axis = max(semi_major_axis_km, EARTH_RADIUS_KM + 100.0)
    mean_motion = math.sqrt(MU_EARTH_KM3_S2 / (semi_major_axis**3))
    semi_latus_rectum = semi_major_axis * (1.0 - eccentricity**2)
    sqrt_term = math.sqrt(max(1.0 - eccentricity**2, 1e-12))

    factor = 0.75 * J2_COEFFICIENT * (EARTH_RADIUS_KM**2) * mean_motion / (semi_latus_rectum**2)
    sin_i = math.sin(inclination_rad)
    cos_i = math.cos(inclination_rad)

    argument_rate = factor * (4.0 - 5.0 * sin_i**2)
    raan_rate = -2.0 * factor * cos_i
    mean_anomaly_rate = -factor * sqrt_term * (3.0 * sin_i**2 - 2.0)

    return {
        "mean_motion_rad_s": mean_motion,
        "argument_of_perigee_rate_rad_s": argument_rate,
        "raan_rate_rad_s": raan_rate,
        "mean_anomaly_rate_rad_s": mean_anomaly_rate,
    }


def _parse_time(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        text = value
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            timestamp = datetime.fromisoformat(text)
        except ValueError:
            return None
        return timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
    return None


def _scenario_midpoint(scenario: Mapping[str, object]) -> datetime | None:
    access_window = scenario.get("access_window")
    if isinstance(access_window, Mapping):
        midpoint = _parse_time(access_window.get("midpoint_utc"))
        if midpoint is not None:
            return midpoint
    timing = scenario.get("timing") if isinstance(scenario.get("timing"), Mapping) else {}
    windows = timing.get("daily_access_windows") if isinstance(timing, Mapping) else []
    if isinstance(windows, Sequence) and windows:
        candidate = windows[0] if isinstance(windows[0], Mapping) else {}
        midpoint = _parse_time(candidate.get("midpoint_utc"))
        if midpoint is not None:
            return midpoint
        start = _parse_time(candidate.get("start_utc"))
        end = _parse_time(candidate.get("end_utc"))
        if start and end:
            return start + (end - start) / 2
    return None


def _target_coordinates(
    scenario: Mapping[str, object],
) -> tuple[float | None, float | None]:
    metadata = scenario.get("metadata") if isinstance(scenario.get("metadata"), Mapping) else {}
    region = metadata.get("region") if isinstance(metadata, Mapping) else {}
    if isinstance(region, Mapping):
        try:
            latitude = math.radians(float(region.get("latitude_deg")))
            longitude = math.radians(float(region.get("longitude_deg")))
            return latitude, longitude
        except (TypeError, ValueError):
            return None, None
    return None, None


def _position_eci(
    semi_major_axis_km: float,
    eccentricity: float,
    inclination_rad: float,
    raan_rad: float,
    argument_of_perigee_rad: float,
    mean_anomaly_rad: float,
) -> tuple[float, float, float]:
    E = _solve_kepler(mean_anomaly_rad, eccentricity)
    cos_E = math.cos(E)
    radius = semi_major_axis_km * (1.0 - eccentricity * cos_E)

    sin_half_E = math.sin(E / 2.0)
    cos_half_E = math.cos(E / 2.0)
    true_anomaly = 2.0 * math.atan2(
        math.sqrt(1.0 + eccentricity) * sin_half_E,
        math.sqrt(1.0 - eccentricity) * cos_half_E,
    )

    argument_of_latitude = argument_of_perigee_rad + true_anomaly
    cos_u = math.cos(argument_of_latitude)
    sin_u = math.sin(argument_of_latitude)
    cos_raan = math.cos(raan_rad)
    sin_raan = math.sin(raan_rad)
    cos_inc = math.cos(inclination_rad)
    sin_inc = math.sin(inclination_rad)

    x = radius * (cos_raan * cos_u - sin_raan * sin_u * cos_inc)
    y = radius * (sin_raan * cos_u + cos_raan * sin_u * cos_inc)
    z = radius * (sin_u * sin_inc)
    return x, y, z


def _solve_kepler(mean_anomaly_rad: float, eccentricity: float) -> float:
    M = _wrap_angle(mean_anomaly_rad)
    if abs(eccentricity) < 1e-12:
        return M
    E = M
    for _ in range(60):
        f = E - eccentricity * math.sin(E) - M
        f_prime = 1.0 - eccentricity * math.cos(E)
        if abs(f_prime) < 1e-12:
            break
        delta = f / f_prime
        E -= delta
        if abs(delta) < 1e-12:
            break
    return E


def _wrap_angle(angle_rad: float) -> float:
    wrapped = math.fmod(angle_rad, 2.0 * math.pi)
    if wrapped <= -math.pi:
        wrapped += 2.0 * math.pi
    elif wrapped > math.pi:
        wrapped -= 2.0 * math.pi
    return wrapped


def _eci_to_ecef(vector: tuple[float, float, float], theta_rad: float) -> tuple[float, float, float]:
    cos_t = math.cos(theta_rad)
    sin_t = math.sin(theta_rad)
    x, y, z = vector
    x_ecef = cos_t * x + sin_t * y
    y_ecef = -sin_t * x + cos_t * y
    return x_ecef, y_ecef, z


def _elevation_angle(
    position_ecef: tuple[float, float, float],
    target_lat_rad: float,
    target_lon_rad: float,
) -> float:
    cos_lat = math.cos(target_lat_rad)
    sin_lat = math.sin(target_lat_rad)
    cos_lon = math.cos(target_lon_rad)
    sin_lon = math.sin(target_lon_rad)

    ground = (
        EARTH_RADIUS_KM * cos_lat * cos_lon,
        EARTH_RADIUS_KM * cos_lat * sin_lon,
        EARTH_RADIUS_KM * sin_lat,
    )

    relative = (
        position_ecef[0] - ground[0],
        position_ecef[1] - ground[1],
        position_ecef[2] - ground[2],
    )

    up = (cos_lat * cos_lon, cos_lat * sin_lon, sin_lat)
    dot = sum(rel * u for rel, u in zip(relative, up))
    norm_rel = math.sqrt(sum(component * component for component in relative))
    if norm_rel == 0.0:
        return -90.0
    elevation = math.degrees(math.asin(max(min(dot / norm_rel, 1.0), -1.0)))
    return elevation


def _visibility_segments(
    samples: Sequence[tuple[datetime, float]],
    threshold_deg: float,
) -> list[tuple[datetime, datetime]]:
    if not samples:
        return []

    segments: list[tuple[datetime, datetime]] = []
    prev_time, prev_elev = samples[0]
    current_start: datetime | None = prev_time if prev_elev >= threshold_deg else None

    for index in range(1, len(samples)):
        time, elev = samples[index]
        if prev_elev < threshold_deg <= elev:
            fraction = 0.0
            if elev != prev_elev:
                fraction = (threshold_deg - prev_elev) / (elev - prev_elev)
            delta = (time - prev_time).total_seconds()
            current_start = prev_time + timedelta(seconds=delta * fraction)
        elif prev_elev >= threshold_deg > elev and current_start is not None:
            fraction = 0.0
            if prev_elev != elev:
                fraction = (prev_elev - threshold_deg) / (prev_elev - elev)
            delta = (time - prev_time).total_seconds()
            end_time = prev_time + timedelta(seconds=delta * fraction)
            segments.append((current_start, end_time))
            current_start = None
        prev_time, prev_elev = time, elev

    if current_start is not None:
        segments.append((current_start, samples[-1][0]))

    return segments


def _updated_scenario_mapping(
    scenario: Mapping[str, object],
    solution: RepeatGroundTrackSolution,
) -> MutableMapping[str, object]:
    updated = json.loads(json.dumps(scenario))
    orbital = updated.setdefault("orbital_elements", {})
    if isinstance(orbital, Mapping):
        classical = orbital.setdefault("classical", {})
        if isinstance(classical, Mapping):
            classical["semi_major_axis_km"] = solution.semi_major_axis_km
            classical.setdefault("eccentricity", 0.0)
        repeat = orbital.setdefault("repeat_ground_track", {})
        if isinstance(repeat, Mapping):
            repeat["repeat_cycle_days"] = solution.repeat_cycle_days
            repeat["orbits_per_cycle"] = solution.orbits_per_cycle
            repeat["residual_tau"] = solution.residual_tau
    return updated


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
