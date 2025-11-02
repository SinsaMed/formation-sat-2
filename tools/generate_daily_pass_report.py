"""Generate analytical figures for the locked Tehran daily pass run."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

from tools import render_debug_plots as rdp

MU_EARTH_KM3_S2 = 398_600.4418
EARTH_RADIUS_KM = 6_378.137


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value).astimezone(timezone.utc)
    except ValueError:
        return None


def _ensure_plot_dir(run_dir: Path) -> Path:
    plot_dir = run_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


@dataclass
class RunInputs:
    run_dir: Path
    config_path: Path
    deterministic: pd.DataFrame
    relative: pd.DataFrame
    deterministic_summary: dict
    monte_carlo_summary: dict
    scenario_summary: dict
    groundtrack: pd.DataFrame | None
    ephemeris: pd.DataFrame | None


def _load_inputs(run_dir: Path, config_path: Path) -> RunInputs:
    deterministic = pd.read_csv(run_dir / "deterministic_cross_track.csv", parse_dates=["time_iso"])
    deterministic = deterministic.rename(columns={"time_iso": "time_utc"})

    relative_path = run_dir / "relative_cross_track.csv"
    if relative_path.exists():
        relative = pd.read_csv(relative_path, parse_dates=["time_iso"])
        relative = relative.rename(columns={"time_iso": "time_utc"})
    else:
        relative = pd.DataFrame(columns=["time_utc", "relative_cross_track_km"])

    deterministic_summary = json.loads((run_dir / "deterministic_summary.json").read_text(encoding="utf-8"))
    monte_carlo_summary = json.loads((run_dir / "monte_carlo_summary.json").read_text(encoding="utf-8"))
    scenario_summary = json.loads((run_dir / "scenario_summary.json").read_text(encoding="utf-8"))

    stk_dir = run_dir / "stk_export"
    groundtracks = rdp._load_stk_groundtracks(stk_dir) if stk_dir.exists() else {}
    ephemerides = rdp._load_stk_ephemerides(stk_dir) if stk_dir.exists() else {}

    groundtrack = None
    if groundtracks:
        groundtrack = next(iter(groundtracks.values()))
    ephemeris = None
    if ephemerides:
        ephemeris = next(iter(ephemerides.values()))

    return RunInputs(
        run_dir=run_dir,
        config_path=config_path,
        deterministic=deterministic,
        relative=relative,
        deterministic_summary=deterministic_summary,
        monte_carlo_summary=monte_carlo_summary,
        scenario_summary=scenario_summary,
        groundtrack=groundtrack,
        ephemeris=ephemeris,
    )


def _extract_satellites(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column != "time_utc"]


def _imaging_window(summary: dict) -> tuple[datetime, datetime]:
    access = summary.get("access_window", {})
    start = _parse_time(access.get("start_utc"))
    end = _parse_time(access.get("end_utc"))
    if start and end:
        return start, end

    nodes = summary.get("nodes", [])
    for node in nodes:
        if node.get("type") == "access_window":
            start = _parse_time(node.get("start"))
            end = _parse_time(node.get("end"))
            if start and end:
                return start, end
    raise ValueError("Unable to determine imaging window from scenario summary.")


def _evaluation_time(summary: dict) -> datetime | None:
    metrics = summary.get("metrics", {})
    cross_track = metrics.get("cross_track", {})
    evaluation = cross_track.get("evaluation") if isinstance(cross_track, Mapping) else {}
    return _parse_time(evaluation.get("time_utc"))


def _target_location(summary: dict) -> tuple[float, float]:
    metadata = summary.get("metadata", {})
    region = metadata.get("region", {}) if isinstance(metadata, Mapping) else {}
    lat = float(region.get("latitude_deg", 35.6892))
    lon = float(region.get("longitude_deg", 51.389))
    return lat, lon


def _orbital_speed_kmps(config: dict) -> float:
    elements = config.get("orbital_elements", {})
    classical = elements.get("classical", {}) if isinstance(elements, Mapping) else {}
    sma = float(classical.get("semi_major_axis_km", 6880.0))
    return math.sqrt(MU_EARTH_KM3_S2 / sma)


def _compute_cross_track_snapshot(
    deterministic: pd.DataFrame,
    evaluation: datetime,
    satellites: list[str],
    orbital_speed: float,
) -> dict[str, tuple[float, float]]:
    data = deterministic.set_index("time_utc").sort_index()
    if evaluation not in data.index:
        data = data.reindex(data.index.union([evaluation])).interpolate().sort_index()
    snapshot = {}
    for sat in satellites:
        cross_track = float(data.loc[evaluation, sat])
        series = data[sat]
        sign_change = series.iloc[(series - 0.0).abs().argsort()[:2]]
        times = sign_change.index.sort_values()
        if len(times) >= 2:
            delta = (evaluation - times[0]).total_seconds()
        else:
            delta = 0.0
        along_track = delta * orbital_speed / 1.0
        snapshot[sat] = (along_track, cross_track)
    return snapshot


def _plot_ground_tracks(inputs: RunInputs, plot_dir: Path) -> None:
    if inputs.groundtrack is None or inputs.groundtrack.empty:
        return
    target_lat, target_lon = _target_location(inputs.scenario_summary)
    window_start, window_end = _imaging_window(inputs.scenario_summary)
    data = inputs.groundtrack.copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(data["longitude_deg"], data["latitude_deg"], color="#377eb8", linewidth=1.2, label="STK ground track")
    window_mask = (data["time_utc"] >= window_start) & (data["time_utc"] <= window_end)
    if window_mask.any():
        ax.plot(
            data.loc[window_mask, "longitude_deg"],
            data.loc[window_mask, "latitude_deg"],
            color="#e41a1c",
            linewidth=2.0,
            label="Imaging window",
        )
    ax.scatter([target_lon], [target_lat], marker="*", color="#4daf4a", s=120, label="Tehran")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Ground track for Tehran daily pass")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks.svg", format="svg")
    plt.close(fig)

    zoom_lat = 5.0
    zoom_lon = 6.0
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(data["longitude_deg"], data["latitude_deg"], color="#377eb8", linewidth=1.2)
    if window_mask.any():
        ax.plot(
            data.loc[window_mask, "longitude_deg"],
            data.loc[window_mask, "latitude_deg"],
            color="#e41a1c",
            linewidth=2.0,
        )
    ax.scatter([target_lon], [target_lat], marker="*", color="#4daf4a", s=140)
    ax.set_xlim(target_lon - zoom_lon, target_lon + zoom_lon)
    ax.set_ylim(target_lat - zoom_lat, target_lat + zoom_lat)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Ground track vicinity of Tehran")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks_tehran.svg", format="svg")
    plt.close(fig)


def _plot_triangle_snapshot(inputs: RunInputs, plot_dir: Path) -> None:
    evaluation = _evaluation_time(inputs.deterministic_summary) or inputs.deterministic["time_utc"].iloc[len(inputs.deterministic) // 2]
    satellites = _extract_satellites(inputs.deterministic)
    config = json.loads(inputs.config_path.read_text(encoding="utf-8"))
    speed = _orbital_speed_kmps(config)
    snapshot = _compute_cross_track_snapshot(inputs.deterministic, evaluation, satellites, speed)
    fig, ax = plt.subplots(figsize=(6.0, 5.5))
    for sat, (along, cross) in snapshot.items():
        ax.scatter(along, cross, s=120, label=sat)
        ax.text(along, cross, f" {sat}", va="bottom", ha="left")
    primary = inputs.deterministic_summary.get("metrics", {}).get("cross_track_limits_km", {}).get("primary")
    waiver = inputs.deterministic_summary.get("metrics", {}).get("cross_track_limits_km", {}).get("waiver")
    if primary is not None:
        ax.axhline(primary, color="#1b9e77", linestyle="--", linewidth=1.0, label="±30 km limit")
        ax.axhline(-primary, color="#1b9e77", linestyle="--", linewidth=1.0)
    if waiver is not None:
        ax.axhline(waiver, color="#d95f02", linestyle=":", linewidth=1.0, label="±70 km waiver")
        ax.axhline(-waiver, color="#d95f02", linestyle=":", linewidth=1.0)
    ax.set_xlabel("Approximate along-track offset [km]")
    ax.set_ylabel("Cross-track offset [km]")
    ax.set_title(f"Formation snapshot at {evaluation:%Y-%m-%d %H:%M:%S}Z")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(plot_dir / "formation_triangle_snapshot.svg", format="svg")
    plt.close(fig)


def _plot_orbital_planes(inputs: RunInputs, plot_dir: Path) -> None:
    if inputs.ephemeris is None or inputs.ephemeris.empty:
        return
    positions = inputs.ephemeris[["x_m", "y_m", "z_m"]].to_numpy() / 1e3
    fig = plt.figure(figsize=(7.5, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], color="#377eb8", label="STK ephemeris")
    radius = EARTH_RADIUS_KM
    u = np.linspace(0, 2 * math.pi, 60)
    v = np.linspace(0, math.pi, 30)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, color="#f0f0f0", alpha=0.35, linewidth=0)

    plane_data = inputs.deterministic_summary.get("metrics", {}).get("plane_intersection", {})
    planes = plane_data.get("planes", {}) if isinstance(plane_data, Mapping) else {}
    colours = ["#4daf4a", "#e41a1c", "#984ea3"]
    for (name, normal), colour in zip(planes.items(), colours):
        normal_vec = np.array(normal, dtype=float)
        normal_vec = normal_vec / np.linalg.norm(normal_vec)
        d = 0.0
        grid = np.linspace(-radius * 1.8, radius * 1.8, 20)
        xx, yy = np.meshgrid(grid, grid)
        zz = (-normal_vec[0] * xx - normal_vec[1] * yy - d) / (normal_vec[2] + 1e-9)
        ax.plot_surface(xx, yy, zz, alpha=0.08, color=colour, linewidth=0, shade=False)
        ax.text(0, 0, radius * 1.9, name, color=colour)

    target_lat, target_lon = _target_location(inputs.scenario_summary)
    lat_rad = math.radians(target_lat)
    lon_rad = math.radians(target_lon)
    target = np.array([
        radius * math.cos(lat_rad) * math.cos(lon_rad),
        radius * math.cos(lat_rad) * math.sin(lon_rad),
        radius * math.sin(lat_rad),
    ])
    ax.scatter(target[0], target[1], target[2], marker="*", color="#ff7f00", s=150, label="Tehran")

    extent = radius * 2.2
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_zlim(-extent, extent)
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.set_zlabel("Z [km]")
    ax.set_title("Orbital planes intersecting above Tehran")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(plot_dir / "orbital_planes_3d.svg", format="svg")
    plt.close(fig)


def _rv_to_elements(position_km: np.ndarray, velocity_km_s: np.ndarray) -> tuple[float, float, float, float]:
    r = np.linalg.norm(position_km)
    v = np.linalg.norm(velocity_km_s)
    h_vec = np.cross(position_km, velocity_km_s)
    h = np.linalg.norm(h_vec)
    inclination = math.degrees(math.acos(h_vec[2] / h))
    n_vec = np.cross([0.0, 0.0, 1.0], h_vec)
    n = np.linalg.norm(n_vec)
    raan = 0.0
    if n > 1e-8:
        raan = math.degrees(math.atan2(n_vec[1], n_vec[0])) % 360
    energy = v**2 / 2 - MU_EARTH_KM3_S2 / r
    sma = -MU_EARTH_KM3_S2 / (2 * energy)
    e_vec = (np.cross(velocity_km_s, h_vec) / MU_EARTH_KM3_S2) - (position_km / r)
    e = np.linalg.norm(e_vec)
    argument = 0.0
    if n > 1e-8 and e > 1e-8:
        argument = math.degrees(math.atan2(np.dot(np.cross(n_vec, e_vec), h_vec) / h, np.dot(n_vec, e_vec) / (n * e))) % 360
    return sma, inclination, raan, argument


def _plot_orbital_elements(inputs: RunInputs, plot_dir: Path) -> None:
    if inputs.ephemeris is None or inputs.ephemeris.empty:
        return
    positions = inputs.ephemeris[["x_m", "y_m", "z_m"]].to_numpy() / 1e3
    time_series = inputs.ephemeris["time_utc"]
    epoch_seconds = (time_series - time_series.iloc[0]).dt.total_seconds().to_numpy()
    velocities = np.gradient(positions, epoch_seconds, axis=0)
    times = time_series
    sma_list, inc_list, raan_list, argp_list = [], [], [], []
    for pos, vel in zip(positions, velocities):
        sma, inc, raan, argp = _rv_to_elements(pos, vel)
        sma_list.append(sma)
        inc_list.append(inc)
        raan_list.append(raan)
        argp_list.append(argp)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    axes = axes.ravel()
    axes[0].plot(times, sma_list, label="Semi-major axis")
    axes[1].plot(times, inc_list, label="Inclination", color="#377eb8")
    axes[2].plot(times, raan_list, label="RAAN", color="#4daf4a")
    axes[3].plot(times, argp_list, label="Argument of perigee", color="#e41a1c")
    axes[0].set_ylabel("Semi-major axis [km]")
    axes[1].set_ylabel("Inclination [deg]")
    axes[2].set_ylabel("RAAN [deg]")
    axes[3].set_ylabel("ω [deg]")
    axes[3].set_xlabel("UTC")
    for ax in axes:
        ax.grid(True, linestyle=":", linewidth=0.5)
        ax.legend(loc="best", fontsize="small")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(plot_dir / "orbital_elements_timeseries.svg", format="svg")
    plt.close(fig)


def _plot_relative_positions(inputs: RunInputs, plot_dir: Path) -> None:
    satellites = _extract_satellites(inputs.deterministic)
    if not satellites:
        return
    times = inputs.deterministic["time_utc"]
    matrix = inputs.deterministic[satellites]
    centroid = matrix.mean(axis=1)
    rel = matrix.subtract(centroid, axis=0)
    snapshots = np.linspace(0, len(times) - 1, 3, dtype=int)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    speed = _orbital_speed_kmps(json.loads(inputs.config_path.read_text(encoding="utf-8")))
    for ax, idx in zip(axes, snapshots):
        epoch = times.iloc[idx]
        for sat in satellites:
            cross = rel.iloc[idx][sat]
            ax.scatter(0.0, cross, s=90, label=sat)
            ax.text(0.0, cross, f" {sat}", va="bottom", ha="left")
        ax.set_title(f"{epoch:%H:%M:%S}Z")
        ax.axhline(0.0, color="#000000", linewidth=0.8)
        ax.set_xlabel("Along-track offset [km]")
        ax.set_ylabel("Cross-track [km]")
        ax.set_xlim(-speed * 10.0, speed * 10.0)
        ax.grid(True, linestyle=":", linewidth=0.5)
    handles, labels = axes[-1].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right")
    fig.tight_layout()
    fig.savefig(plot_dir / "relative_positions.svg", format="svg")
    plt.close(fig)


def _plot_pairwise_distances(inputs: RunInputs, plot_dir: Path) -> None:
    satellites = _extract_satellites(inputs.deterministic)
    if len(satellites) < 2:
        return
    times = inputs.deterministic["time_utc"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for left, right in combinations(satellites, 2):
        separation = (inputs.deterministic[left] - inputs.deterministic[right]).abs()
        ax.plot(times, separation, label=f"|{left} - {right}|")
    window_start, window_end = _imaging_window(inputs.scenario_summary)
    ax.axvspan(window_start, window_end, color="#1b9e77", alpha=0.1, label="Imaging window")
    ax.set_xlabel("UTC")
    ax.set_ylabel("Cross-track separation [km]")
    ax.set_title("Pairwise cross-track separations")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(plot_dir / "pairwise_distances.svg", format="svg")
    plt.close(fig)


def _plot_access_timeline(inputs: RunInputs, plot_dir: Path) -> None:
    times = inputs.deterministic["time_utc"]
    matrix = inputs.deterministic.drop(columns=["time_utc"])
    limits = inputs.deterministic_summary.get("metrics", {}).get("cross_track_limits_km", {})
    primary = float(limits.get("primary", 30.0))
    waiver = float(limits.get("waiver", 70.0))
    within_primary = (matrix.abs() <= primary).sum(axis=1)
    within_waiver = (matrix.abs() <= waiver).sum(axis=1)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.step(times, within_primary, where="mid", label="Within ±30 km", linewidth=2.0)
    ax.step(times, within_waiver, where="mid", label="Within ±70 km", linestyle="--")
    ax.set_ylim(0, matrix.shape[1] + 0.5)
    ax.set_ylabel("Spacecraft count")
    ax.set_xlabel("UTC")
    ax.set_title("Access timeline versus cross-track limits")
    ax.set_yticks(range(0, matrix.shape[1] + 1))
    ax.grid(True, linestyle=":", linewidth=0.5)
    window_start, window_end = _imaging_window(inputs.scenario_summary)
    ax.axvspan(window_start, window_end, color="#fee090", alpha=0.3)
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(plot_dir / "access_timeline.svg", format="svg")
    plt.close(fig)


def _plot_perturbations(inputs: RunInputs, plot_dir: Path) -> None:
    config = json.loads(inputs.config_path.read_text(encoding="utf-8"))
    speed = _orbital_speed_kmps(config)
    sma = config.get("orbital_elements", {}).get("classical", {}).get("semi_major_axis_km", 6880.0)
    inclination = config.get("orbital_elements", {}).get("classical", {}).get("inclination_deg", 97.7)
    eccentricity = config.get("orbital_elements", {}).get("classical", {}).get("eccentricity", 0.0)
    mean_motion = math.sqrt(MU_EARTH_KM3_S2 / sma**3)
    inclination_rad = math.radians(inclination)
    j2 = 1.08262668e-3
    raan_rate = (
        -1.5
        * j2
        * (EARTH_RADIUS_KM**2)
        * mean_motion
        * math.cos(inclination_rad)
        / (sma**2 * (1 - eccentricity**2) ** 2)
    )
    days = np.arange(0, 31)
    raan_drift = np.degrees(raan_rate * days * 86400.0)

    drag_stats = inputs.monte_carlo_summary.get("max_abs_cross_track_km", {})
    altitude_loss = np.zeros_like(days, dtype=float)
    if drag_stats:
        # Approximate altitude decay by scaling centroid cross-track spread.
        centroid_p95 = inputs.monte_carlo_summary.get("centroid_abs_cross_track_km_p95", 0.0)
        altitude_loss = np.linspace(0.0, centroid_p95 * 0.02, len(days))

    srp_shift = 0.5 * 4.56e-6 * 1.3 * 1.1 / 165.0 * (days * 86400.0) ** 2 / 1e3

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, raan_drift, label="RAAN drift [deg]")
    ax.plot(days, altitude_loss, label="Altitude change [km]")
    ax.plot(days, srp_shift, label="Along-track SRP shift [km]")
    ax.set_xlabel("Elapsed days without maintenance")
    ax.set_ylabel("Magnitude")
    ax.set_title("Perturbation-driven evolution without corrective burns")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(plot_dir / "perturbation_effects.svg", format="svg")
    plt.close(fig)


def _plot_maintenance(inputs: RunInputs, plot_dir: Path) -> None:
    metrics = inputs.deterministic_summary.get("metrics", {}).get("cross_track", {})
    vehicle_metrics = metrics.get("vehicles", []) if isinstance(metrics, list | tuple) else metrics
    data = []
    if isinstance(vehicle_metrics, list):
        for entry in vehicle_metrics:
            identifier = entry.get("identifier")
            abs_eval = entry.get("abs_cross_track_at_evaluation_km")
            if identifier and isinstance(abs_eval, (int, float)):
                data.append((identifier, float(abs_eval) * 0.02))
    fig, ax = plt.subplots(figsize=(7, 4))
    if data:
        satellites, deltas = zip(*data)
        ax.bar(satellites, deltas, color="#80b1d3")
    else:
        satellites = ["FSAT-LDR", "FSAT-DP1", "FSAT-DP2"]
        ax.bar(satellites, [0.0, 0.0, 0.0], color="#c7c7c7")
        ax.text(1.0, 0.02, "Maintenance log unavailable\nusing proxy metric", ha="center", va="bottom")
    ax.set_ylabel("Proxy annual Δv [m/s]")
    ax.set_xlabel("Spacecraft")
    ax.set_title("Estimated maintenance effort from cross-track offsets")
    fig.tight_layout()
    fig.savefig(plot_dir / "maintenance_delta_v.svg", format="svg")
    plt.close(fig)


def _plot_monte_carlo(inputs: RunInputs, plot_dir: Path) -> None:
    summary = inputs.monte_carlo_summary
    evaluation = summary.get("evaluation_abs_cross_track_km", {})
    if not isinstance(evaluation, Mapping) or not evaluation:
        return
    satellites = sorted(evaluation)
    means = [evaluation[sat].get("mean", float("nan")) for sat in satellites]
    p95s = [evaluation[sat].get("p95", float("nan")) for sat in satellites]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(satellites))
    width = 0.35
    ax.bar(x - width / 2, means, width, label="Mean")
    ax.bar(x + width / 2, p95s, width, label="95th percentile")
    centroid_mean = summary.get("centroid_abs_cross_track_km_mean")
    centroid_p95 = summary.get("centroid_abs_cross_track_km_p95")
    if centroid_mean is not None and centroid_p95 is not None:
        ax.text(
            0.98,
            0.02,
            f"Centroid mean: {centroid_mean:.2f} km\nCentroid p95: {centroid_p95:.2f} km",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7, edgecolor="#cccccc"),
        )
    ax.set_xticks(x)
    ax.set_xticklabels(satellites)
    ax.set_ylabel("Absolute cross-track at evaluation [km]")
    ax.set_title("Monte Carlo dispersion statistics")
    ax.grid(True, axis="y", linestyle=":", linewidth=0.5)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(plot_dir / "monte_carlo_sensitivity.svg", format="svg")
    plt.close(fig)


def _plot_groundtrack_comparison(inputs: RunInputs, plot_dir: Path) -> None:
    if inputs.groundtrack is None or inputs.groundtrack.empty:
        return
    deterministic = inputs.deterministic.copy()
    deterministic = deterministic.set_index("time_utc").sort_index()
    target_lat, target_lon = _target_location(inputs.scenario_summary)
    approx_lat = target_lat + np.degrees(deterministic.mean(axis=1) / EARTH_RADIUS_KM)
    approx_lon = np.full_like(approx_lat, target_lon)
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(inputs.groundtrack["longitude_deg"], inputs.groundtrack["latitude_deg"], label="STK ground track", linewidth=1.5)
    ax.plot(approx_lon, approx_lat, linestyle="--", label="Analytical cross-track approximation")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Analytical versus STK ground track comparison")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(plot_dir / "analytical_vs_stk_groundtrack.svg", format="svg")
    plt.close(fig)


def _plot_performance_metrics(inputs: RunInputs, plot_dir: Path) -> None:
    metrics = inputs.deterministic_summary.get("metrics", {})
    centroid = metrics.get("centroid_cross_track_at_evaluation_km", 0.0)
    worst = metrics.get("worst_vehicle_cross_track_at_evaluation_km", 0.0)
    limits = metrics.get("cross_track_limits_km", {})
    primary = limits.get("primary", 30.0)
    waiver = limits.get("waiver", 70.0)
    categories = ["Centroid", "Worst spacecraft"]
    values = [centroid, worst]
    thresholds = [primary, waiver]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(categories))
    width = 0.35
    ax.bar(x - width / 2, values, width, label="Measured")
    ax.bar(x + width / 2, thresholds, width, label="Requirement")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Cross-track [km]")
    ax.set_title("Performance metrics against cross-track limits")
    ax.legend(loc="upper left")
    ax.grid(True, axis="y", linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(plot_dir / "performance_metrics.svg", format="svg")
    plt.close(fig)


def _plot_access_sensitivity(inputs: RunInputs, plot_dir: Path, grid: int) -> None:
    base_config = json.loads(inputs.config_path.read_text(encoding="utf-8"))
    elements = base_config.get("orbital_elements", {}).get("classical", {})
    base_alt = float(elements.get("semi_major_axis_km", 6880.0))
    base_inc = float(elements.get("inclination_deg", 97.7))
    alt_offsets = np.linspace(-20.0, 20.0, grid)
    inc_offsets = np.linspace(-0.2, 0.2, grid)
    durations = np.zeros((grid, grid))
    window_start, window_end = _imaging_window(inputs.scenario_summary)
    base_duration = (window_end - window_start).total_seconds()
    alt_scale = 1.4
    inc_scale = 420.0
    for i, d_alt in enumerate(alt_offsets):
        for j, d_inc in enumerate(inc_offsets):
            penalty = abs(d_alt) * alt_scale + abs(d_inc) * inc_scale
            durations[i, j] = max(base_duration - penalty, 0.0)
    fig, ax = plt.subplots(figsize=(8, 6))
    contour = ax.contourf(
        inc_offsets + base_inc,
        alt_offsets + base_alt,
        durations,
        levels=12,
        cmap="viridis",
    )
    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_label("Approximate compliant duration [s]")
    ax.set_xlabel("Inclination [deg]")
    ax.set_ylabel("Semi-major axis [km]")
    ax.set_title("Sensitivity of compliance to orbital parameters")
    fig.tight_layout()
    fig.savefig(plot_dir / "access_sensitivity_contour.svg", format="svg")
    plt.close(fig)


def generate_daily_pass_plots(run_dir: Path, config_path: Path, contour_grid: int) -> None:
    inputs = _load_inputs(run_dir, config_path)
    plot_dir = _ensure_plot_dir(run_dir)
    _plot_ground_tracks(inputs, plot_dir)
    _plot_triangle_snapshot(inputs, plot_dir)
    _plot_orbital_planes(inputs, plot_dir)
    _plot_orbital_elements(inputs, plot_dir)
    _plot_relative_positions(inputs, plot_dir)
    _plot_pairwise_distances(inputs, plot_dir)
    _plot_access_timeline(inputs, plot_dir)
    _plot_perturbations(inputs, plot_dir)
    _plot_maintenance(inputs, plot_dir)
    _plot_monte_carlo(inputs, plot_dir)
    _plot_groundtrack_comparison(inputs, plot_dir)
    _plot_performance_metrics(inputs, plot_dir)
    _plot_access_sensitivity(inputs, plot_dir, contour_grid)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="Artefact directory for the scenario run.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/scenarios/tehran_daily_pass.json"),
        help="Scenario configuration providing baseline orbital elements.",
    )
    parser.add_argument(
        "--contour-grid",
        type=int,
        default=5,
        help="Grid resolution per axis for the access sensitivity contour.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    namespace = parse_args(argv)
    run_dir = namespace.run_dir
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory {run_dir} does not exist.")
    generate_daily_pass_plots(run_dir, namespace.config, namespace.contour_grid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
