"""Generate extended analytical figures for the Tehran daily-pass locked run."""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping, Optional

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
from matplotlib import dates as mdates  # noqa: E402
from matplotlib import patheffects as patheffects  # noqa: E402
from matplotlib import pyplot as plt  # noqa: E402
from matplotlib import patches as mpatches  # noqa: E402
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401,E402

from tools import render_debug_plots as rdp
from src.constellation.frames import rotation_matrix_eci_to_lvlh
from src.constellation.orbit import cartesian_to_classical, propagate_kepler
from src.constellation.roe import MU_EARTH, OrbitalElements

EARTH_ROTATION_RATE_RAD_S = 7.2921159e-5
EARTH_RADIUS_M = 6_378_136.3
TEHRAN_LATITUDE_DEG = 35.6892
TEHRAN_LONGITUDE_DEG = 51.3890
TEHRAN_BOUNDARY_PATH = Path(__file__).resolve().parents[1] / "data" / "tehran_boundary.geojson"
BASE_ASSET = "tehran_daily_pass"
BASE_SATELLITE = "FSAT-LDR"


@dataclass
class DailyPassData:
    times_actual: np.ndarray
    times_aligned: np.ndarray
    time_step: float
    cross_track: pd.DataFrame
    relative_cross_track: pd.DataFrame
    scenario_summary: Mapping[str, object]
    monte_carlo_summary: Mapping[str, object]
    nodes: list[Mapping[str, object]]
    raan_evaluations: list[Mapping[str, object]]
    z_axes: np.ndarray
    base_positions: np.ndarray
    base_velocities: np.ndarray
    sat_positions: dict[str, np.ndarray]
    sat_velocities: dict[str, np.ndarray]
    latitudes: dict[str, np.ndarray]
    longitudes: dict[str, np.ndarray]
    altitudes: dict[str, np.ndarray]
    analytic_positions: np.ndarray
    analytic_latitudes: np.ndarray
    analytic_longitudes: np.ndarray
    analytic_altitudes: np.ndarray
    analytic_velocity: np.ndarray


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to the artefact directory for run_20251020_1900Z_tehran_daily_pass_locked.",
    )
    return parser.parse_args(argv)


def _ensure_output_directory(run_dir: Path) -> Path:
    plot_dir = run_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


def _wrap_longitudes(longitudes_deg: np.ndarray, centre: float = TEHRAN_LONGITUDE_DEG) -> np.ndarray:
    return ((longitudes_deg - centre + 180.0) % 360.0) - 180.0 + centre


def _load_tehran_boundary_polygons() -> list[np.ndarray]:
    if not TEHRAN_BOUNDARY_PATH.exists():
        return []
    try:
        payload = json.loads(TEHRAN_BOUNDARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    geometry_type = payload.get("type")
    coordinates = payload.get("coordinates")
    if not coordinates:
        return []
    if geometry_type == "MultiPolygon":
        polygon_iterable = coordinates
    elif geometry_type == "Polygon":
        polygon_iterable = [coordinates]
    else:
        return []
    polygons: list[np.ndarray] = []
    for polygon in polygon_iterable:
        if not polygon:
            continue
        outer = polygon[0]
        xy = np.array([[float(lon), float(lat)] for lon, lat in outer], dtype=float)
        polygons.append(xy)
    return polygons


def _eci_to_geodetic(position: np.ndarray, reference_epoch: pd.Timestamp, epoch: pd.Timestamp) -> tuple[float, float, float]:
    dt = (epoch - reference_epoch).total_seconds()
    angle = EARTH_ROTATION_RATE_RAD_S * dt
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    x_eci, y_eci, z_eci = position
    x_ecef = cos_angle * x_eci + sin_angle * y_eci
    y_ecef = -sin_angle * x_eci + cos_angle * y_eci
    z_ecef = z_eci
    horizontal = math.hypot(x_ecef, y_ecef)
    latitude = math.degrees(math.atan2(z_ecef, horizontal))
    longitude = math.degrees(math.atan2(y_ecef, x_ecef))
    longitude = ((longitude + 180.0) % 360.0) - 180.0
    radius = math.sqrt(x_ecef**2 + y_ecef**2 + z_ecef**2)
    altitude = max(radius - EARTH_RADIUS_M, 0.0)
    return latitude, longitude, altitude


def _load_run_data(run_dir: Path) -> DailyPassData:
    cross_track_path = run_dir / "deterministic_cross_track.csv"
    relative_path = run_dir / "relative_cross_track.csv"
    scenario_path = run_dir / "scenario_summary.json"
    monte_carlo_path = run_dir / "monte_carlo_summary.json"
    if not cross_track_path.exists():
        raise FileNotFoundError(f"{cross_track_path} not found")
    cross_track = pd.read_csv(cross_track_path, parse_dates=["time_iso"])
    relative = pd.read_csv(relative_path, parse_dates=["time_iso"]) if relative_path.exists() else pd.DataFrame()
    scenario_summary = json.loads(scenario_path.read_text(encoding="utf-8")) if scenario_path.exists() else {}
    monte_carlo_summary = json.loads(monte_carlo_path.read_text(encoding="utf-8")) if monte_carlo_path.exists() else {}
    nodes = scenario_summary.get("nodes", []) if isinstance(scenario_summary.get("nodes"), list) else []
    raan_alignment = scenario_summary.get("raan_alignment", {})
    raan_evaluations = raan_alignment.get("evaluations", []) if isinstance(raan_alignment.get("evaluations"), list) else []

    times_actual = cross_track["time_iso"].to_numpy()
    if times_actual.size < 2:
        raise ValueError("Cross-track catalogue must contain at least two samples.")

    stk_dir = run_dir / "stk_export"
    ephemerides = rdp._load_stk_ephemerides(stk_dir)  # pylint: disable=protected-access
    if BASE_ASSET not in ephemerides:
        raise KeyError(f"STK ephemeris for asset {BASE_ASSET} not found in {stk_dir}")
    base_ephem = ephemerides[BASE_ASSET].sort_values("time_utc")
    reference_epoch = base_ephem["time_utc"].iloc[0]
    time_offset = reference_epoch - cross_track["time_iso"].iloc[0]
    times_aligned = (cross_track["time_iso"] + time_offset).to_numpy()

    ephem_interp = base_ephem.set_index("time_utc")
    interpolation_index = ephem_interp.index.union(pd.Index(times_aligned))
    ephem_interp = ephem_interp.reindex(interpolation_index).interpolate(method="time").loc[times_aligned]
    base_positions = ephem_interp[["x_m", "y_m", "z_m"]].to_numpy(dtype=float)
    aligned_seconds = (pd.to_datetime(times_aligned) - pd.to_datetime(times_aligned[0])).total_seconds()
    aligned_seconds = np.asarray(aligned_seconds, dtype=float)
    if aligned_seconds.size < 2:
        raise ValueError("Aligned times must contain at least two samples.")
    time_deltas = np.gradient(aligned_seconds)
    base_velocities = np.gradient(base_positions, axis=0) / time_deltas[:, None]

    satellites = [col for col in cross_track.columns if col != "time_iso"]
    if BASE_SATELLITE not in satellites:
        raise KeyError(f"Baseline satellite {BASE_SATELLITE} not present in cross-track catalogue")
    base_cross_track = cross_track[BASE_SATELLITE].to_numpy(dtype=float)

    z_axes = []
    sat_positions: dict[str, np.ndarray] = {}
    sat_velocities: dict[str, np.ndarray] = {}
    latitudes: dict[str, np.ndarray] = {}
    longitudes: dict[str, np.ndarray] = {}
    altitudes: dict[str, np.ndarray] = {}

    reference_timestamp = pd.Timestamp(reference_epoch)
    aligned_index = pd.to_datetime(times_aligned)

    offsets = {sat: (cross_track[sat].to_numpy(dtype=float) - base_cross_track) * 1_000.0 for sat in satellites}

    for idx in range(base_positions.shape[0]):
        rotation = rotation_matrix_eci_to_lvlh(base_positions[idx], base_velocities[idx])
        axis_matrix = rotation.T
        z_axes.append(axis_matrix[:, 2])
    z_axes_array = np.vstack(z_axes)

    offset_gradients = {sat: np.gradient(values, aligned_seconds) for sat, values in offsets.items()}

    for sat in satellites:
        positions = base_positions + z_axes_array * offsets[sat][:, None]
        velocities = base_velocities + z_axes_array * offset_gradients[sat][:, None]
        sat_positions[sat] = positions
        sat_velocities[sat] = velocities
        lat_series = []
        lon_series = []
        alt_series = []
        for vec, epoch in zip(positions, aligned_index):
            lat, lon, alt = _eci_to_geodetic(vec, reference_timestamp, epoch)
            lat_series.append(lat)
            lon_series.append(lon)
            alt_series.append(alt)
        latitudes[sat] = np.asarray(lat_series, dtype=float)
        longitudes[sat] = _wrap_longitudes(np.asarray(lon_series, dtype=float))
        altitudes[sat] = np.asarray(alt_series, dtype=float)

    classical = cartesian_to_classical(base_positions[0], base_velocities[0], mu=MU_EARTH)
    orbital_elements = OrbitalElements(
        semi_major_axis=classical.semi_major_axis,
        eccentricity=classical.eccentricity,
        inclination=classical.inclination,
        raan=classical.raan,
        arg_perigee=classical.arg_perigee,
        mean_anomaly=classical.mean_anomaly,
    )
    analytic_positions: list[np.ndarray] = []
    analytic_velocities: list[np.ndarray] = []
    analytic_latitudes: list[float] = []
    analytic_longitudes: list[float] = []
    analytic_altitudes: list[float] = []
    for dt, epoch in zip(aligned_seconds, aligned_index):
        position, velocity = propagate_kepler(orbital_elements, dt, mu=MU_EARTH)
        analytic_positions.append(position)
        analytic_velocities.append(velocity)
        lat, lon, alt = _eci_to_geodetic(position, reference_timestamp, epoch)
        analytic_latitudes.append(lat)
        analytic_longitudes.append(lon)
        analytic_altitudes.append(alt)
    analytic_positions_array = np.vstack(analytic_positions)
    analytic_velocity_array = np.vstack(analytic_velocities)
    analytic_longitudes_array = _wrap_longitudes(np.asarray(analytic_longitudes, dtype=float))

    time_step = float(np.median(np.diff(aligned_seconds)))

    return DailyPassData(
        times_actual=times_actual,
        times_aligned=times_aligned,
        time_step=time_step,
        cross_track=cross_track,
        relative_cross_track=relative,
        scenario_summary=scenario_summary,
        monte_carlo_summary=monte_carlo_summary,
        nodes=nodes,
        raan_evaluations=raan_evaluations,
        z_axes=z_axes_array,
        base_positions=base_positions,
        base_velocities=base_velocities,
        sat_positions=sat_positions,
        sat_velocities=sat_velocities,
        latitudes=latitudes,
        longitudes=longitudes,
        altitudes=altitudes,
        analytic_positions=analytic_positions_array,
        analytic_latitudes=np.asarray(analytic_latitudes, dtype=float),
        analytic_longitudes=analytic_longitudes_array,
        analytic_altitudes=np.asarray(analytic_altitudes, dtype=float),
        analytic_velocity=analytic_velocity_array,
    )


def _format_time_labels(ax: plt.Axes, times: np.ndarray) -> None:
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.figure.autofmt_xdate()


def _nearest_time_index(times: np.ndarray, target: pd.Timestamp) -> int:
    deltas = np.abs(pd.to_datetime(times) - target)
    return int(np.argmin(deltas.to_numpy()))


def generate_ground_tracks(data: DailyPassData, plot_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    for sat, lon in data.longitudes.items():
        lat = data.latitudes[sat]
        ax.plot(lon, lat, label=sat)
    ax.axhline(TEHRAN_LATITUDE_DEG, color="#d95f02", linestyle="--", linewidth=1.2, label="Tehran latitude")
    ax.axvline(TEHRAN_LONGITUDE_DEG, color="#1b9e77", linestyle=":", linewidth=1.0, label="Tehran longitude")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Ground tracks derived from STK ephemeris with cross-track offsets")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks.svg", format="svg")
    plt.close(fig)

    boundary_polygons = _load_tehran_boundary_polygons()
    if boundary_polygons:
        fig, ax = plt.subplots(figsize=(6.5, 6.0))
        ax.set_facecolor("#f5f5f5")
        for polygon in boundary_polygons:
            patch = mpatches.Polygon(
                polygon,
                closed=True,
                facecolor="#f4efe8",
                edgecolor="#b07d62",
                linewidth=0.8,
                alpha=0.9,
                zorder=1,
            )
            ax.add_patch(patch)
    else:
        fig, ax = plt.subplots(figsize=(6.5, 6.0))
    colours = {sat: colour for sat, colour in zip(sorted(data.longitudes), ["#1b9e77", "#d95f02", "#7570b3", "#66a61e", "#e7298a"])}
    stroke = [patheffects.Stroke(linewidth=4.0, foreground="#ffffff"), patheffects.Normal()]
    for sat, lon in data.longitudes.items():
        lat = data.latitudes[sat]
        ax.plot(lon, lat, color=colours.get(sat, "#3182bd"), linewidth=2.0, label=sat, path_effects=stroke)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Tehran access ground-track focus")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks_tehran.svg", format="svg")
    plt.close(fig)


def generate_analytical_vs_stk(data: DailyPassData, plot_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data.analytic_longitudes, data.analytic_latitudes, label="Two-body propagation", linestyle="--")
    base_lon = data.longitudes[BASE_SATELLITE]
    base_lat = data.latitudes[BASE_SATELLITE]
    ax.plot(base_lon, base_lat, label="STK (J2+drag)")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Analytical versus STK ground track comparison")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(plot_dir / "analytical_vs_stk_groundtrack.svg", format="svg")
    plt.close(fig)


def generate_access_timeline(data: DailyPassData, plot_dir: Path) -> None:
    windows = [node for node in data.nodes if node.get("type") == "access_window"]
    if not windows:
        return
    fig, ax = plt.subplots(figsize=(9, 3.5))
    for idx, window in enumerate(windows):
        start = pd.to_datetime(window.get("start"))
        end = pd.to_datetime(window.get("end"))
        if pd.isna(start) or pd.isna(end):
            continue
        label = window.get("label", f"Window {idx+1}")
        ax.barh(idx, (end - start).total_seconds() / 60.0, left=mdates.date2num(start), height=0.6, align="center", label=label)
    ax.set_xlabel("Time (UTC)")
    ax.set_yticks(range(len(windows)))
    ax.set_yticklabels([window.get("label", f"Window {i+1}") for i, window in enumerate(windows)])
    ax.set_title("Access timeline overview")
    _format_time_labels(ax, np.array([pd.to_datetime(window.get("start")) for window in windows]))
    fig.tight_layout()
    fig.savefig(plot_dir / "access_timeline.svg", format="svg")
    plt.close(fig)


def generate_access_sensitivity(data: DailyPassData, plot_dir: Path) -> None:
    if not data.raan_evaluations:
        return
    vehicle_set: set[str] = set()
    for entry in data.raan_evaluations:
        vehicle_values = entry.get("vehicle_abs_cross_track_km") or entry.get("vehicle_cross_track_km")
        if isinstance(vehicle_values, Mapping):
            vehicle_set.update(str(key) for key in vehicle_values.keys())
    vehicles = sorted(vehicle_set)
    if not vehicles:
        vehicles = sorted(data.cross_track.columns.drop("time_iso"))
    unique_raan = sorted({float(entry.get("raan_deg", 0.0)) for entry in data.raan_evaluations})
    if not unique_raan or len(vehicles) < 2:
        # Fall back to a simple line plot when contouring is not informative.
        raan = []
        centroid = []
        for entry in data.raan_evaluations:
            raan.append(float(entry.get("raan_deg", 0.0)))
            centroid.append(float(entry.get("centroid_abs_cross_track_km", entry.get("centroid_cross_track_km", 0.0))))
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(raan, centroid, color="#1b9e77", linewidth=2.0)
        ax.set_xlabel("RAAN [deg]")
        ax.set_ylabel("Centroid |cross-track| [km]")
        ax.set_title("Access sensitivity to RAAN adjustments")
        ax.grid(True, linestyle=":", linewidth=0.5)
        fig.tight_layout()
        fig.savefig(plot_dir / "access_sensitivity_contour.svg", format="svg")
        plt.close(fig)
        return
    heatmap = np.zeros((len(vehicles), len(unique_raan)))
    for entry in data.raan_evaluations:
        ra = float(entry.get("raan_deg", 0.0))
        if ra not in unique_raan:
            continue
        idx = unique_raan.index(ra)
        vehicle_values = entry.get("vehicle_abs_cross_track_km") or entry.get("vehicle_cross_track_km")
        if not isinstance(vehicle_values, Mapping):
            continue
        for row, sat in enumerate(vehicles):
            value = float(vehicle_values.get(sat, math.nan))
            heatmap[row, idx] = value
    fig, ax = plt.subplots(figsize=(10, 4.5))
    mesh = ax.contourf(unique_raan, range(len(vehicles)), heatmap, levels=16, cmap="viridis")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("|Cross-track| at midpoint [km]")
    ax.set_ylabel("Spacecraft")
    ax.set_yticks(range(len(vehicles)))
    ax.set_yticklabels(vehicles)
    ax.set_xlabel("RAAN [deg]")
    ax.set_title("Access sensitivity to RAAN adjustments")
    fig.tight_layout()
    fig.savefig(plot_dir / "access_sensitivity_contour.svg", format="svg")
    plt.close(fig)


def generate_pairwise_distances(data: DailyPassData, plot_dir: Path) -> None:
    times = pd.to_datetime(data.times_actual)
    fig, ax = plt.subplots(figsize=(10, 5))
    for sat_a, sat_b in combinations(sorted(data.sat_positions), 2):
        separation = np.linalg.norm(data.sat_positions[sat_a] - data.sat_positions[sat_b], axis=1) / 1_000.0
        ax.plot(times, separation, label=f"{sat_a}–{sat_b}")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Separation [km]")
    ax.set_title("Pairwise distances across the access interval")
    ax.grid(True, linestyle=":", linewidth=0.5)
    _format_time_labels(ax, times)
    ax.legend(loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(plot_dir / "pairwise_distances.svg", format="svg")
    plt.close(fig)


def generate_relative_positions(data: DailyPassData, plot_dir: Path) -> None:
    times = pd.to_datetime(data.times_actual)
    centroid = np.mean(np.stack(list(data.sat_positions.values())), axis=0)
    axes = rotation_matrix_eci_to_lvlh(data.base_positions[0], data.base_velocities[0]).T
    fig, axes_arr = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for sat, positions in data.sat_positions.items():
        rel = positions - centroid
        radial = np.einsum("ij,ij->i", rel, axes[:, 0][None, :]) / 1_000.0
        along = np.einsum("ij,ij->i", rel, axes[:, 1][None, :]) / 1_000.0
        cross = np.einsum("ij,ij->i", rel, axes[:, 2][None, :]) / 1_000.0
        axes_arr[0].plot(times, radial, label=sat)
        axes_arr[1].plot(times, along, label=sat)
        axes_arr[2].plot(times, cross, label=sat)
    axes_arr[0].set_ylabel("Radial [km]")
    axes_arr[1].set_ylabel("Along-track [km]")
    axes_arr[2].set_ylabel("Cross-track [km]")
    axes_arr[2].set_xlabel("Time (UTC)")
    for ax in axes_arr:
        ax.grid(True, linestyle=":", linewidth=0.5)
    axes_arr[0].set_title("Relative LVLH coordinates w.r.t. constellation centroid")
    axes_arr[0].legend(loc="upper right")
    _format_time_labels(axes_arr[2], times)
    fig.tight_layout()
    fig.savefig(plot_dir / "relative_positions.svg", format="svg")
    plt.close(fig)


def generate_triangle_snapshot(data: DailyPassData, plot_dir: Path) -> None:
    evaluation = data.scenario_summary.get("metrics", {}).get("cross_track", {}).get("evaluation", {})
    midpoint = pd.to_datetime(evaluation.get("time_utc")) if evaluation else pd.Timestamp(data.times_actual[len(data.times_actual) // 2])
    idx = _nearest_time_index(data.times_actual, midpoint)
    centroid = np.mean(np.stack([positions[idx] for positions in data.sat_positions.values()]), axis=0)
    axes = rotation_matrix_eci_to_lvlh(data.base_positions[idx], data.base_velocities[idx]).T
    fig, ax = plt.subplots(figsize=(6.5, 6.0))
    colours = {sat: colour for sat, colour in zip(sorted(data.sat_positions), ["#1b9e77", "#d95f02", "#7570b3"])}
    for sat, positions in data.sat_positions.items():
        rel = positions[idx] - centroid
        along = float(rel @ axes[:, 1]) / 1_000.0
        cross = float(rel @ axes[:, 2]) / 1_000.0
        ax.scatter(along, cross, s=100, color=colours.get(sat, "#3182bd"), label=sat, edgecolor="#1a1a1a", linewidths=0.6)
        ax.annotate(sat, (along, cross), textcoords="offset points", xytext=(6, 4))
    ax.set_xlabel("Along-track [km]")
    ax.set_ylabel("Cross-track [km]")
    ax.set_title(f"Formation snapshot at {midpoint.strftime('%Y-%m-%d %H:%M:%SZ')}")
    ax.axhline(0.0, color="#cccccc", linewidth=0.8)
    ax.axvline(0.0, color="#cccccc", linewidth=0.8)
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(plot_dir / "formation_triangle_snapshot.svg", format="svg")
    plt.close(fig)


def generate_performance_metrics(data: DailyPassData, plot_dir: Path) -> None:
    evaluation = data.scenario_summary.get("metrics", {}).get("cross_track", {}).get("evaluation", {})
    centroid = float(evaluation.get("centroid_abs_cross_track_km", 0.0))
    worst = float(evaluation.get("worst_vehicle_abs_cross_track_km", 0.0))
    relative_max = float(data.relative_cross_track["relative_cross_track_km"].abs().max()) if not data.relative_cross_track.empty else 0.0
    raan_alignment = data.scenario_summary.get("raan_alignment", {})
    delta_raan = abs(float(raan_alignment.get("initial_raan_deg", 0.0)) - float(raan_alignment.get("optimised_raan_deg", 0.0)))
    categories = ["Centroid |x|", "Worst vehicle", "Max relative", "|ΔRAAN|"]
    values = [centroid, worst, relative_max, delta_raan]
    limits = [30.0, 70.0, 0.5, 0.3]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(categories))
    width = 0.35
    ax.bar(x - width / 2, values, width, label="Measured")
    ax.bar(x + width / 2, limits, width, label="Threshold")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Magnitude [km / deg]")
    ax.set_title("Performance metrics against mission thresholds")
    ax.legend(loc="upper left")
    ax.grid(True, axis="y", linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(plot_dir / "performance_metrics.svg", format="svg")
    plt.close(fig)


def generate_maintenance_delta_v(data: DailyPassData, plot_dir: Path) -> None:
    if not data.raan_evaluations:
        return
    a = float(data.scenario_summary.get("orbital_elements", {}).get("classical", {}).get("semi_major_axis_km", 6880.0)) * 1_000.0
    orbital_speed = math.sqrt(MU_EARTH / a)
    best_raan = float(data.scenario_summary.get("raan_alignment", {}).get("optimised_raan_deg", 0.0))
    raan = []
    centroid_abs = []
    estimated_delta_v = []
    for entry in data.raan_evaluations:
        ra = float(entry.get("raan_deg", 0.0))
        centroid_abs.append(float(entry.get("centroid_abs_cross_track_km", entry.get("centroid_cross_track_km", 0.0))))
        raan.append(ra)
        delta = abs(math.radians(ra - best_raan))
        estimated_delta_v.append(2.0 * orbital_speed * math.sin(delta / 2.0) / 1_000.0)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(raan, centroid_abs, color="#1b9e77", linewidth=2.0)
    ax.set_xlabel("RAAN [deg]")
    ax.set_ylabel("Centroid |cross-track| [km]")
    ax.set_title("RAAN alignment sweep and estimated manoeuvre cost")
    twin = ax.twinx()
    twin.plot(raan, estimated_delta_v, color="#d95f02", linestyle="--", linewidth=1.8)
    twin.set_ylabel("Estimated Δv [km/s]")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(plot_dir / "maintenance_delta_v.svg", format="svg")
    plt.close(fig)


def generate_monte_carlo_sensitivity(data: DailyPassData, plot_dir: Path) -> None:
    summary = data.monte_carlo_summary
    evaluation = summary.get("evaluation_abs_cross_track_km", {}) if isinstance(summary.get("evaluation_abs_cross_track_km"), Mapping) else {}
    vehicles = sorted(evaluation.keys())
    if not vehicles:
        vehicles = sorted(data.cross_track.columns.drop("time_iso"))
    centroid_stats = summary.get("centroid_abs_cross_track_km", {})
    worst_stats = summary.get("worst_vehicle_abs_cross_track_km", {})
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for sat in vehicles:
        stats = evaluation.get(sat, {})
        mean = stats.get("mean")
        p95 = stats.get("p95")
        ax.scatter(mean, p95, s=60, label=sat)
        ax.annotate(sat, (mean, p95), textcoords="offset points", xytext=(6, 4))
    if centroid_stats:
        ax.scatter(centroid_stats.get("mean"), centroid_stats.get("p95"), marker="s", s=70, color="#1b9e77", label="Centroid")
    if worst_stats:
        ax.scatter(worst_stats.get("mean"), worst_stats.get("p95"), marker="^", s=70, color="#d95f02", label="Worst")
    ax.set_xlabel("Mean |cross-track| [km]")
    ax.set_ylabel("95th percentile |cross-track| [km]")
    ax.set_title("Monte Carlo dispersion sensitivity")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(plot_dir / "monte_carlo_sensitivity.svg", format="svg")
    plt.close(fig)


def generate_orbital_elements_timeseries(data: DailyPassData, plot_dir: Path) -> None:
    times = pd.to_datetime(data.times_actual)
    fig, axes_arr = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for sat in sorted(data.sat_positions):
        positions = data.sat_positions[sat]
        velocities = data.sat_velocities[sat]
        sma = []
        inclination = []
        raan = []
        for pos, vel in zip(positions, velocities):
            elements = cartesian_to_classical(pos, vel, mu=MU_EARTH)
            sma.append(elements.semi_major_axis / 1_000.0)
            inclination.append(math.degrees(elements.inclination))
            raan.append(math.degrees(elements.raan))
        axes_arr[0].plot(times, sma, label=sat)
        axes_arr[1].plot(times, inclination, label=sat)
        axes_arr[2].plot(times, raan, label=sat)
    axes_arr[0].set_ylabel("a [km]")
    axes_arr[1].set_ylabel("i [deg]")
    axes_arr[2].set_ylabel("Ω [deg]")
    axes_arr[2].set_xlabel("Time (UTC)")
    for ax in axes_arr:
        ax.grid(True, linestyle=":", linewidth=0.5)
    axes_arr[0].set_title("Orbital elements reconstructed from propagated states")
    axes_arr[0].legend(loc="upper right")
    _format_time_labels(axes_arr[2], times)
    fig.tight_layout()
    fig.savefig(plot_dir / "orbital_elements_timeseries.svg", format="svg")
    plt.close(fig)


def generate_orbital_planes_3d(data: DailyPassData, plot_dir: Path) -> None:
    fig = plt.figure(figsize=(7.5, 7.0))
    ax = fig.add_subplot(111, projection="3d")
    for sat, positions in data.sat_positions.items():
        ax.plot(positions[:, 0] / 1_000.0, positions[:, 1] / 1_000.0, positions[:, 2] / 1_000.0, label=sat)
    radius = EARTH_RADIUS_M / 1_000.0
    u = np.linspace(0, 2 * math.pi, 40)
    v = np.linspace(0, math.pi, 20)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, color="#f0f0f0", alpha=0.3, linewidth=0.0)
    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")
    ax.set_zlabel("z [km]")
    ax.set_title("Three-dimensional orbital planes")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(plot_dir / "orbital_planes_3d.svg", format="svg")
    plt.close(fig)


def generate_perturbation_effects(data: DailyPassData, plot_dir: Path) -> None:
    times = pd.to_datetime(data.times_actual)
    altitude_stk = data.altitudes[BASE_SATELLITE] / 1_000.0
    altitude_two_body = data.analytic_altitudes / 1_000.0
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(times, altitude_stk, label="STK (J2+drag)", linewidth=2.0)
    ax.plot(times, altitude_two_body, label="Two-body", linestyle="--")
    ax.fill_between(times, altitude_stk, altitude_two_body, color="#1f77b4", alpha=0.15, label="Perturbation effect")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Altitude [km]")
    ax.set_title("Altitude variation due to perturbations")
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="best")
    _format_time_labels(ax, times)
    fig.tight_layout()
    fig.savefig(plot_dir / "perturbation_effects.svg", format="svg")
    plt.close(fig)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    run_dir: Path = args.run_dir
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory {run_dir} does not exist.")
    plot_dir = _ensure_output_directory(run_dir)
    data = _load_run_data(run_dir)

    generate_ground_tracks(data, plot_dir)
    generate_analytical_vs_stk(data, plot_dir)
    generate_access_timeline(data, plot_dir)
    generate_access_sensitivity(data, plot_dir)
    generate_pairwise_distances(data, plot_dir)
    generate_relative_positions(data, plot_dir)
    generate_triangle_snapshot(data, plot_dir)
    generate_performance_metrics(data, plot_dir)
    generate_maintenance_delta_v(data, plot_dir)
    generate_monte_carlo_sensitivity(data, plot_dir)
    generate_orbital_elements_timeseries(data, plot_dir)
    generate_orbital_planes_3d(data, plot_dir)
    generate_perturbation_effects(data, plot_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
