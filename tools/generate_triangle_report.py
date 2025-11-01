"""Generate analytical figures for a Tehran triangle formation run."""
from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sim.formation.triangle import simulate_triangle_formation
from src.constellation.frames import eci_to_lvlh
from src.constellation.orbit import (
    EARTH_EQUATORIAL_RADIUS_M,
    MU_EARTH,
)

J2_COEFFICIENT = 1.08262668e-3
SOLAR_PRESSURE_PA = 4.56e-6
REFLECTIVITY_COEFF = 1.3
SECONDS_PER_DAY = 86_400


@dataclass
class RunData:
    times: np.ndarray
    positions: dict[str, np.ndarray]
    latitudes: dict[str, np.ndarray]
    longitudes: dict[str, np.ndarray]
    altitudes: dict[str, np.ndarray]
    time_step: float


@dataclass
class SummaryData:
    run: RunData
    metrics: dict[str, object]
    geometry: dict[str, object]
    samples: list[dict[str, object]]


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to the artefact directory produced by run_triangle.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/scenarios/tehran_triangle.json"),
        help="Scenario configuration used for supplementary propagation.",
    )
    parser.add_argument(
        "--contour-grid",
        type=int,
        default=5,
        help="Grid resolution per axis for the access sensitivity contour.",
    )
    return parser.parse_args(argv)


def load_summary(run_dir: Path) -> SummaryData:
    summary_path = run_dir / "triangle_summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    geometry = payload.get("geometry", {})
    samples = payload.get("samples", [])
    metrics = payload.get("metrics", {})

    time_strings = geometry.get("times", [])
    time_objects = [_parse_iso8601(ts) for ts in time_strings]
    times = np.array(time_objects, dtype=object)
    time_step = 0.0
    if len(time_objects) > 1 and time_objects[0] and time_objects[1]:
        delta = (time_objects[1] - time_objects[0]).total_seconds()
        time_step = float(delta)

    positions = {
        sat_id: np.asarray(geometry.get("positions_m", {}).get(sat_id, []), dtype=float)
        for sat_id in geometry.get("satellite_ids", [])
    }
    latitudes = {
        sat_id: np.asarray(geometry.get("latitudes_rad", {}).get(sat_id, []), dtype=float)
        for sat_id in geometry.get("satellite_ids", [])
    }
    longitudes = {
        sat_id: np.asarray(geometry.get("longitudes_rad", {}).get(sat_id, []), dtype=float)
        for sat_id in geometry.get("satellite_ids", [])
    }
    altitudes = {
        sat_id: np.asarray(geometry.get("altitudes_m", {}).get(sat_id, []), dtype=float)
        for sat_id in geometry.get("satellite_ids", [])
    }

    run = RunData(
        times=times,
        positions=positions,
        latitudes=latitudes,
        longitudes=longitudes,
        altitudes=altitudes,
        time_step=time_step,
    )
    return SummaryData(run=run, metrics=metrics, geometry=geometry, samples=samples)


def ensure_output_directory(run_dir: Path) -> Path:
    plot_dir = run_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


def generate_ground_track_figure(
    summary: SummaryData, config_path: Path, plot_dir: Path
) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config_long = deepcopy(config)
    formation = config_long.setdefault("formation", {})
    formation["duration_s"] = float(SECONDS_PER_DAY)
    formation["time_step_s"] = 60.0
    long_result = simulate_triangle_formation(config_long, output_directory=None)

    lat_deg = {
        sat: np.degrees(vals)
        for sat, vals in long_result.latitudes_rad.items()
    }
    lon_deg = {
        sat: np.degrees(vals)
        for sat, vals in long_result.longitudes_rad.items()
    }

    window = summary.metrics.get("formation_window", {})
    start = _parse_iso8601(window.get("start"))
    end = _parse_iso8601(window.get("end"))

    fig, ax = plt.subplots(figsize=(10, 6))
    sat_ids = sorted(lat_deg)
    colours = _satellite_colours(sat_ids)
    for sat in sat_ids:
        ax.plot(
            lon_deg[sat],
            lat_deg[sat],
            label=f"{sat} ground track",
            color=colours[sat],
        )

    if start and end:
        mask = np.array(
            [bool(t and start <= t <= end) for t in summary.run.times], dtype=bool
        )
        for sat, lats in summary.run.latitudes.items():
            if sat not in summary.run.longitudes:
                continue
            lon = summary.run.longitudes[sat]
            if len(lon) != len(mask):
                continue
            ax.scatter(
                np.degrees(lon[mask]),
                np.degrees(lats[mask]),
                s=20,
                label=f"{sat} 90 s window",
                color=colours.get(sat, "#333333"),
            )

    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Twenty-four-hour ground tracks with ninety-second Tehran window")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks.svg", format="svg")
    plt.close(fig)


def generate_ground_track_zoom_figure(summary: SummaryData, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.latitudes)
    if not sat_ids:
        return

    target = summary.geometry.get("target", {})
    target_lat = float(target.get("latitude_deg", 35.6892))
    target_lon = float(target.get("longitude_deg", 51.3890))

    colours = _satellite_colours(sat_ids)
    fig, ax = plt.subplots(figsize=(7, 7))

    window = summary.metrics.get("formation_window", {})
    start = _parse_iso8601(window.get("start"))
    end = _parse_iso8601(window.get("end"))
    mask = None
    if start and end:
        mask = np.array(
            [bool(t and start <= t <= end) for t in summary.run.times],
            dtype=bool,
        )

    has_window_entry = False
    for sat in sat_ids:
        lat = np.degrees(summary.run.latitudes.get(sat, np.array([])))
        lon = np.degrees(summary.run.longitudes.get(sat, np.array([])))
        if lat.size == 0 or lon.size == 0:
            continue
        east, north = _project_to_local_plane(lat, lon, target_lat, target_lon)
        ax.plot(east, north, color=colours[sat], linewidth=1.6, label=f"{sat} ground track")
        if mask is not None and mask.size == east.size and np.any(mask):
            label = None if has_window_entry else "Ninety-second access arc"
            ax.scatter(
                east[mask],
                north[mask],
                color=colours[sat],
                s=45,
                edgecolor="black",
                linewidth=0.4,
                label=label,
            )
            has_window_entry = True

    ax.scatter(0.0, 0.0, marker="*", color="#000000", s=140, label="Tehran")
    ax.axhline(0.0, color="#bdbdbd", linestyle=":", linewidth=0.8)
    ax.axvline(0.0, color="#bdbdbd", linestyle=":", linewidth=0.8)

    limits = np.array([
        ax.get_xlim()[0],
        ax.get_xlim()[1],
        ax.get_ylim()[0],
        ax.get_ylim()[1],
    ])
    max_extent = np.max(np.abs(limits))
    if np.isfinite(max_extent) and max_extent > 0.0:
        padding = 0.05 * max_extent
        bound = max_extent + padding
        ax.set_xlim(-bound, bound)
        ax.set_ylim(-bound, bound)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("East of Tehran [km]")
    ax.set_ylabel("North of Tehran [km]")
    ax.set_title("Tehran access ground tracks (local tangent plane)")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_track_tehran_zoom.svg", format="svg")
    plt.close(fig)


def generate_orbital_plane_figure(summary: SummaryData, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.positions)
    if not sat_ids:
        return

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    colours = _satellite_colours(sat_ids)

    earth_radius_km = EARTH_EQUATORIAL_RADIUS_M / 1e3
    u = np.linspace(0.0, 2.0 * math.pi, 90)
    v = np.linspace(-0.5 * math.pi, 0.5 * math.pi, 45)
    uu, vv = np.meshgrid(u, v)
    sphere_x = earth_radius_km * np.cos(vv) * np.cos(uu)
    sphere_y = earth_radius_km * np.cos(vv) * np.sin(uu)
    sphere_z = earth_radius_km * np.sin(vv)
    ax.plot_surface(
        sphere_x,
        sphere_y,
        sphere_z,
        color="#f0f0f0",
        edgecolor="none",
        alpha=0.6,
        zorder=0,
    )

    centre_index = len(summary.run.times) // 2
    plotted_points = []
    for sat in sat_ids:
        pos = summary.run.positions[sat] / 1e3
        ax.plot(pos[:, 0], pos[:, 1], pos[:, 2], color=colours[sat], label=sat)
        if 0 <= centre_index < len(pos):
            ax.scatter(
                pos[centre_index, 0],
                pos[centre_index, 1],
                pos[centre_index, 2],
                color=colours[sat],
                s=55,
                edgecolor="black",
                linewidth=0.4,
            )
            plotted_points.append(pos[centre_index])

        velocities = _differentiate(summary.run.positions[sat], summary.run.time_step)
        if not np.any(velocities) and len(summary.run.times) >= 2:
            time_axis = _time_axis_seconds(summary.run.times)
            if time_axis is not None:
                velocities = np.gradient(summary.run.positions[sat], time_axis, axis=0, edge_order=2)
        if velocities.size == 0 or centre_index >= len(velocities):
            continue
        normal = np.cross(summary.run.positions[sat][centre_index], velocities[centre_index])
        if np.linalg.norm(normal) == 0.0:
            continue
        normal /= np.linalg.norm(normal)
        tangent = np.cross(normal, np.array([1.0, 0.0, 0.0]))
        if np.linalg.norm(tangent) < 1e-8:
            tangent = np.cross(normal, np.array([0.0, 1.0, 0.0]))
        tangent /= np.linalg.norm(tangent)
        bitangent = np.cross(normal, tangent)
        orbit_radius = np.linalg.norm(summary.run.positions[sat][centre_index]) / 1e3
        plane_extent = orbit_radius * 1.4
        u_plane = np.linspace(-plane_extent, plane_extent, 30)
        v_plane = np.linspace(-plane_extent, plane_extent, 30)
        uu_plane, vv_plane = np.meshgrid(u_plane, v_plane)
        plane_points = (
            uu_plane[..., None] * tangent[None, None, :]
            + vv_plane[..., None] * bitangent[None, None, :]
        )
        ax.plot_surface(
            plane_points[:, :, 0],
            plane_points[:, :, 1],
            plane_points[:, :, 2],
            alpha=0.15,
            color=colours[sat],
            linewidth=0,
        )

    target = summary.geometry.get("target", {})
    target_lat = float(target.get("latitude_deg", 35.6892))
    target_lon = float(target.get("longitude_deg", 51.3890))
    target_point = _geodetic_to_ecef(target_lat, target_lon, 0.0) / 1e3
    ax.scatter(
        target_point[0],
        target_point[1],
        target_point[2],
        color="#000000",
        marker="*",
        s=140,
        label="Tehran",
    )
    ax.plot(
        [0.0, target_point[0]],
        [0.0, target_point[1]],
        [0.0, target_point[2]],
        color="#636363",
        linestyle="--",
        linewidth=1.0,
    )

    all_points = np.concatenate(
        [
            sphere_x.reshape(-1, 1),
            sphere_y.reshape(-1, 1),
            sphere_z.reshape(-1, 1),
        ],
        axis=1,
    )
    if plotted_points:
        all_points = np.vstack([all_points, np.asarray(plotted_points)])
    all_points = np.vstack([all_points, target_point[None, :]])
    _set_axes_equal(ax, all_points)
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.set_zlabel("Z [km]")
    ax.set_title("Orbital planes and satellite locations above Tehran")
    ax.view_init(elev=22.0, azim=135.0)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "orbital_planes_3d.svg", format="svg")
    plt.close(fig)


def generate_orbital_elements_timeseries(run_dir: Path, plot_dir: Path) -> None:
    orbital_path = run_dir / "orbital_elements.csv"
    if not orbital_path.exists():
        return
    data = pd.read_csv(orbital_path, parse_dates=["time_utc"])
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    axes = axes.ravel()

    for sat_id, group in data.groupby("satellite_id"):
        axes[0].plot(group["time_utc"], group["semi_major_axis_km"], label=sat_id)
        axes[1].plot(group["time_utc"], group["inclination_deg"], label=sat_id)
        axes[2].plot(group["time_utc"], group["raan_deg"], label=sat_id)
        axes[3].plot(group["time_utc"], group["argument_of_perigee_deg"], label=sat_id)

    axes[0].set_ylabel("Semi-major axis [km]")
    axes[1].set_ylabel("Inclination [deg]")
    axes[2].set_ylabel("RAAN [deg]")
    axes[3].set_ylabel("Argument of perigee [deg]")
    axes[3].set_xlabel("UTC")
    for ax in axes:
        ax.grid(True, linestyle=":", linewidth=0.6)
    axes[0].set_title("Orbital element stability over the formation window")
    axes[0].legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "orbital_elements_timeseries.svg", format="svg")
    plt.close(fig)


def generate_relative_position_plots(summary: SummaryData, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.positions)
    if len(sat_ids) < 3:
        return
    centroid_positions = np.mean([summary.run.positions[sat] for sat in sat_ids], axis=0)
    centroid_velocities = _differentiate(centroid_positions, summary.run.time_step)

    snapshots = np.linspace(0, len(summary.run.times) - 1, 3, dtype=int)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, snap in enumerate(snapshots):
        ax = axes[idx]
        for sat in sat_ids:
            rel_vec = summary.run.positions[sat][snap] - centroid_positions[snap]
            lvlh = eci_to_lvlh(centroid_positions[snap], centroid_velocities[snap], rel_vec)
            ax.scatter(lvlh[1] / 1e3, lvlh[0] / 1e3, s=80, label=sat)
            ax.annotate(sat, (lvlh[1] / 1e3, lvlh[0] / 1e3), textcoords="offset points", xytext=(5, 5))
        ax.set_xlabel("Along-track [km]")
        ax.set_ylabel("Radial [km]")
        timestamp = summary.run.times[snap]
        timestamp_str = timestamp.isoformat().replace("+00:00", "Z") if timestamp else "n/a"
        ax.set_title(f"Snapshot {idx + 1}: {timestamp_str}")
        ax.grid(True, linestyle=":", linewidth=0.6)
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].legend(handles, labels, loc="upper right", fontsize="small")
    fig.suptitle("Relative LVLH positions spanning the Tehran access window")
    fig.tight_layout()
    fig.savefig(plot_dir / "relative_positions.svg", format="svg")
    plt.close(fig)


def generate_pairwise_distance_plot(summary: SummaryData, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.positions)
    if len(sat_ids) < 3:
        return
    pairs = [(sat_ids[0], sat_ids[1]), (sat_ids[0], sat_ids[2]), (sat_ids[1], sat_ids[2])]
    fig, ax = plt.subplots(figsize=(10, 5))
    time_axis = [t for t in summary.run.times]
    for a, b in pairs:
        dist = np.linalg.norm(summary.run.positions[a] - summary.run.positions[b], axis=1) / 1e3
        ax.plot(time_axis, dist, label=f"{a}–{b}")
    ax.axhline(6.0, color="grey", linestyle="--", linewidth=1.0)
    ax.set_ylabel("Separation [km]")
    ax.set_xlabel("UTC")
    ax.set_title("Pairwise separation during the ninety-second window")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "pairwise_distances.svg", format="svg")
    plt.close(fig)


def generate_access_timeline(summary: SummaryData, plot_dir: Path) -> None:
    window = summary.metrics.get("formation_window", {})
    start = _parse_iso8601(window.get("start"))
    end = _parse_iso8601(window.get("end"))
    if not start or not end:
        return
    duration = end - start
    periods = [start + timedelta(days=day) for day in range(7)]
    fig, ax = plt.subplots(figsize=(10, 3))
    for day_start in periods:
        ax.plot([day_start, day_start + duration], [1, 1], linewidth=6)
    ax.set_ylim(0, 2)
    ax.set_yticks([])
    ax.set_xlabel("UTC date")
    ax.set_title("Daily recurrence of the ninety-second access window")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(plot_dir / "access_timeline.svg", format="svg")
    plt.close(fig)


def generate_perturbation_effects(summary: SummaryData, run_dir: Path, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.positions)
    if not sat_ids:
        return
    sample_index = len(summary.run.times) // 2
    reference_position = summary.run.positions[sat_ids[0]][sample_index]
    semi_major_axis = np.linalg.norm(reference_position)
    inclination = math.acos(
        reference_position[2] / np.linalg.norm(reference_position)
    )
    eccentricity = 0.0

    mean_motion = math.sqrt(MU_EARTH / semi_major_axis**3)
    raan_rate = (
        -1.5
        * J2_COEFFICIENT
        * (EARTH_EQUATORIAL_RADIUS_M**2)
        * mean_motion
        * math.cos(inclination)
        / (semi_major_axis**2 * (1 - eccentricity**2) ** 2)
    )
    days = np.arange(0, 31)
    raan_drift = np.degrees(raan_rate * days * SECONDS_PER_DAY)

    drag_path = run_dir / "drag_dispersion.csv"
    altitude_loss = np.zeros_like(days, dtype=float)
    if drag_path.exists():
        drag_data = pd.read_csv(drag_path)
        if not drag_data.empty:
            mean_alt_drop = drag_data["altitude_delta_m"].mean()
            horizon_orbits = float(summary.metrics.get("drag_dispersion", {}).get("assumptions", {}).get("time_horizon_orbits", 12.0))
            orbital_period = 2.0 * math.pi / mean_motion
            per_orbit_loss = mean_alt_drop / horizon_orbits if horizon_orbits else 0.0
            altitude_loss = (per_orbit_loss / 1e3) * (days * SECONDS_PER_DAY / orbital_period)

    area = 1.1
    mass = 165.0
    srp_accel = SOLAR_PRESSURE_PA * REFLECTIVITY_COEFF * area / mass
    along_track_shift = 0.5 * srp_accel * (days * SECONDS_PER_DAY) ** 2 / 1e3

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, raan_drift, label="RAAN drift due to $J_2$")
    ax.plot(days, altitude_loss, label="Altitude change due to drag")
    ax.plot(days, along_track_shift, label="Along-track shift due to SRP")
    ax.set_xlabel("Elapsed days without maintenance")
    ax.set_ylabel("Magnitude [deg or km]")
    ax.set_title("Perturbation-driven orbital element evolution")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(plot_dir / "perturbation_effects.svg", format="svg")
    plt.close(fig)


def generate_maintenance_plot(run_dir: Path, plot_dir: Path) -> None:
    path = run_dir / "maintenance_summary.csv"
    if not path.exists():
        return
    data = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(data["satellite_id"], data["annual_delta_v_mps"], color="#80b1d3")
    ax.set_ylabel("Annual Δv [m/s]")
    ax.set_xlabel("Satellite")
    ax.set_title("Maintenance manoeuvre budget by spacecraft")
    fig.tight_layout()
    fig.savefig(plot_dir / "maintenance_delta_v.svg", format="svg")
    plt.close(fig)


def generate_monte_carlo_plot(run_dir: Path, plot_dir: Path) -> None:
    path = run_dir / "injection_recovery.csv"
    if not path.exists():
        return
    data = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(8, 5))
    colours = data["success"].map({True: "#4daf4a", False: "#e41a1c"})
    ax.scatter(data["position_error_m"], data["delta_v_mps"], c=colours, alpha=0.6)
    ax.set_xlabel("Initial position error [m]")
    ax.set_ylabel("Recovery Δv [m/s]")
    ax.set_title("Monte Carlo recovery effort distribution")
    fig.tight_layout()
    fig.savefig(plot_dir / "monte_carlo_sensitivity.svg", format="svg")
    plt.close(fig)


def generate_analytical_vs_stk(summary: SummaryData, run_dir: Path, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.latitudes)
    if not sat_ids:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    for sat in sat_ids:
        ax.plot(
            np.degrees(summary.run.longitudes[sat]),
            np.degrees(summary.run.latitudes[sat]),
            label=f"{sat} analytical",
        )
        stk_path = run_dir / "stk" / f"{sat}_groundtrack.gt"
        if stk_path.exists():
            lon, lat = _load_stk_groundtrack(stk_path)
            ax.plot(lon, lat, linestyle="--", label=f"{sat} STK")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Analytical propagation versus STK export")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="best", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "analytical_vs_stk_groundtrack.svg", format="svg")
    plt.close(fig)


def generate_performance_metrics(summary: SummaryData, plot_dir: Path) -> None:
    triangle = summary.metrics.get("triangle", {})
    ground = summary.metrics.get("ground_track", {})
    window = summary.metrics.get("formation_window", {})
    metrics = {
        "Aspect ratio": triangle.get("aspect_ratio_max"),
        "Mean side [km]": np.mean(triangle.get("mean_side_lengths_m", [6000.0])) / 1e3,
        "Ground distance [km]": ground.get("max_ground_distance_km"),
        "Window [s]": window.get("duration_s"),
    }
    tolerances = {
        "Aspect ratio": 1.02,
        "Mean side [km]": 6.0,
        "Ground distance [km]": 350.0,
        "Window [s]": 90.0,
    }
    categories = list(metrics)
    values = [metrics[name] for name in categories]
    limits = [tolerances[name] for name in categories]

    x = np.arange(len(categories))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, values, width, label="Measured")
    ax.bar(x + width / 2, limits, width, label="Requirement")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Value")
    ax.set_title("Performance metrics against mission thresholds")
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_dir / "performance_metrics.svg", format="svg")
    plt.close(fig)


def generate_access_sensitivity(config_path: Path, grid: int, plot_dir: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    reference = config.get("reference_orbit", {})
    base_alt = float(reference.get("semi_major_axis_km", 6898.137))
    base_inc = float(reference.get("inclination_deg", 97.7))

    alt_offsets = np.linspace(-20.0, 20.0, grid)
    inc_offsets = np.linspace(-0.2, 0.2, grid)
    durations = np.zeros((grid, grid), dtype=float)

    for i, d_alt in enumerate(alt_offsets):
        for j, d_inc in enumerate(inc_offsets):
            variant = deepcopy(config)
            variant["reference_orbit"]["semi_major_axis_km"] = base_alt + d_alt
            variant["reference_orbit"]["inclination_deg"] = base_inc + d_inc
            result = simulate_triangle_formation(variant, output_directory=None)
            durations[i, j] = float(result.metrics["formation_window"].get("duration_s", 0.0))

    fig, ax = plt.subplots(figsize=(8, 6))
    contour = ax.contourf(
        inc_offsets + base_inc,
        alt_offsets + base_alt,
        durations,
        levels=12,
        cmap="viridis",
    )
    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_label("Formation window [s]")
    ax.set_xlabel("Inclination [deg]")
    ax.set_ylabel("Semi-major axis [km]")
    ax.set_title("Sensitivity of access duration to orbital parameters")
    fig.tight_layout()
    fig.savefig(plot_dir / "access_sensitivity_contour.svg", format="svg")
    plt.close(fig)


def _project_to_local_plane(
    latitudes_deg: np.ndarray,
    longitudes_deg: np.ndarray,
    centre_lat_deg: float,
    centre_lon_deg: float,
) -> tuple[np.ndarray, np.ndarray]:
    delta_lat = latitudes_deg - centre_lat_deg
    delta_lon = _wrap_longitude(longitudes_deg - centre_lon_deg)
    meters_per_deg_lat = 111_132.0
    meters_per_deg_lon = meters_per_deg_lat * math.cos(math.radians(centre_lat_deg))
    north = delta_lat * meters_per_deg_lat / 1e3
    east = delta_lon * meters_per_deg_lon / 1e3
    return east, north


def _wrap_longitude(delta_lon_deg: np.ndarray | float) -> np.ndarray:
    return (np.asarray(delta_lon_deg) + 180.0) % 360.0 - 180.0


def _satellite_colours(sat_ids: Iterable[str]) -> dict[str, str]:
    palette = [
        "#1b9e77",
        "#d95f02",
        "#7570b3",
        "#e7298a",
        "#66a61e",
        "#e6ab02",
    ]
    colours: dict[str, str] = {}
    for idx, sat in enumerate(sat_ids):
        colours[sat] = palette[idx % len(palette)]
    return colours


def _set_axes_equal(ax, points: np.ndarray) -> None:
    if points.size == 0:
        return
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    centres = (mins + maxs) / 2.0
    extents = maxs - mins
    max_extent = np.max(extents) / 2.0
    if max_extent <= 0.0 or not np.isfinite(max_extent):
        return
    ax.set_xlim(centres[0] - max_extent, centres[0] + max_extent)
    ax.set_ylim(centres[1] - max_extent, centres[1] + max_extent)
    if hasattr(ax, "set_zlim"):
        ax.set_zlim(centres[2] - max_extent, centres[2] + max_extent)


def _time_axis_seconds(times: np.ndarray) -> np.ndarray | None:
    if times.size == 0:
        return None
    reference = times[0]
    if reference is None:
        return None
    seconds = []
    for t in times:
        if t is None:
            return None
        seconds.append((t - reference).total_seconds())
    return np.asarray(seconds, dtype=float)


def _differentiate(series: np.ndarray, step: float) -> np.ndarray:
    if series.size == 0 or step <= 0.0:
        return np.zeros_like(series)
    velocities = np.zeros_like(series)
    velocities[1:-1] = (series[2:] - series[:-2]) / (2.0 * step)
    velocities[0] = (series[1] - series[0]) / step
    velocities[-1] = (series[-1] - series[-2]) / step
    return velocities


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def _geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> np.ndarray:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    a = EARTH_EQUATORIAL_RADIUS_M
    f = 1.0 / 298.257223563
    e_sq = f * (2 - f)
    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    n = a / math.sqrt(1 - e_sq * sin_lat**2)
    x = (n + alt_m) * cos_lat * math.cos(lon)
    y = (n + alt_m) * cos_lat * math.sin(lon)
    z = (n * (1 - e_sq) + alt_m) * sin_lat
    return np.array([x, y, z], dtype=float)


def _load_stk_groundtrack(path: Path) -> tuple[np.ndarray, np.ndarray]:
    lines = path.read_text(encoding="utf-8").splitlines()
    lon = []
    lat = []
    in_points = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("BEGIN Points"):
            in_points = True
            continue
        if stripped.startswith("END Points"):
            break
        if in_points and stripped:
            _, lat_str, lon_str, _ = stripped.split()
            lat.append(float(lat_str))
            lon.append(float(lon_str))
    return np.array(lon, dtype=float), np.array(lat, dtype=float)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    summary = load_summary(args.run_dir)
    plot_dir = ensure_output_directory(args.run_dir)

    generate_ground_track_figure(summary, args.config, plot_dir)
    generate_ground_track_zoom_figure(summary, plot_dir)
    generate_orbital_plane_figure(summary, plot_dir)
    generate_orbital_elements_timeseries(args.run_dir, plot_dir)
    generate_relative_position_plots(summary, plot_dir)
    generate_pairwise_distance_plot(summary, plot_dir)
    generate_access_timeline(summary, plot_dir)
    generate_perturbation_effects(summary, args.run_dir, plot_dir)
    generate_maintenance_plot(args.run_dir, plot_dir)
    generate_monte_carlo_plot(args.run_dir, plot_dir)
    generate_analytical_vs_stk(summary, args.run_dir, plot_dir)
    generate_performance_metrics(summary, plot_dir)
    generate_access_sensitivity(args.config, args.contour_grid, plot_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
