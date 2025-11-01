"""Generate analytical figures for a Tehran triangle formation run."""
from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.patheffects as patheffects  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from sim.formation.triangle import TriangleFormationResult, simulate_triangle_formation
from src.constellation.frames import eci_to_lvlh
from src.constellation.orbit import (
    EARTH_EQUATORIAL_RADIUS_M,
    MU_EARTH,
)

J2_COEFFICIENT = 1.08262668e-3
SOLAR_PRESSURE_PA = 4.56e-6
REFLECTIVITY_COEFF = 1.3
SECONDS_PER_DAY = 86_400

# Outline extracted from OpenStreetMap (ODbL) via polygons.openstreetmap.fr.
TEHRAN_BOUNDARY_PATH = Path(__file__).resolve().parents[1] / "data" / "tehran_boundary.geojson"


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


def _simulate_extended_pass(
    config_path: Path,
    duration_s: float = SECONDS_PER_DAY,
    time_step_s: float = 60.0,
) -> Optional[TriangleFormationResult]:
    if not config_path.exists():
        return None
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config_long = deepcopy(config)
    formation = config_long.setdefault("formation", {})
    formation["duration_s"] = float(duration_s)
    formation["time_step_s"] = float(time_step_s)
    return simulate_triangle_formation(config_long, output_directory=None)


def _wrap_longitudes(longitudes_deg: np.ndarray, geometry: dict[str, object] | None) -> np.ndarray:
    target = geometry.get("target", {}) if geometry else {}
    centre = float(target.get("longitude_deg", 0.0))
    wrapped = ((longitudes_deg - centre + 180.0) % 360.0) - 180.0 + centre
    return wrapped


@lru_cache(maxsize=1)
def _load_tehran_boundary_polygons() -> list[np.ndarray]:
    if not TEHRAN_BOUNDARY_PATH.exists():
        return []
    try:
        raw = json.loads(TEHRAN_BOUNDARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    polygons: list[np.ndarray] = []
    geometry_type = raw.get("type")
    coordinates = raw.get("coordinates")

    if not coordinates:
        return []

    if geometry_type == "MultiPolygon":
        polygon_iterable = coordinates
    elif geometry_type == "Polygon":
        polygon_iterable = [coordinates]
    else:
        return []

    for polygon in polygon_iterable:
        if not polygon:
            continue
        outer_ring = polygon[0]
        if not outer_ring:
            continue
        xy = np.array([[float(lon), float(lat)] for lon, lat in outer_ring], dtype=float)
        polygons.append(xy)

    return polygons


def _select_local_segment(
    latitudes: np.ndarray,
    longitudes: np.ndarray,
    target_lat: float,
    target_lon: float,
    lat_half_width: float = 0.6,
    lon_half_width: float = 0.8,
) -> np.ndarray:
    if latitudes.size == 0 or longitudes.size == 0:
        return np.zeros_like(latitudes, dtype=bool)
    mask = (
        (np.abs(latitudes - target_lat) <= lat_half_width)
        & (np.abs(longitudes - target_lon) <= lon_half_width)
    )
    if np.any(mask):
        return mask
    # Fallback: highlight neighbourhood around closest sample to Tehran.
    angular_distance = np.hypot(
        latitudes - target_lat,
        (longitudes - target_lon) * math.cos(math.radians(target_lat)),
    )
    closest_index = int(np.argmin(angular_distance))
    lower = max(closest_index - 2, 0)
    upper = min(closest_index + 3, latitudes.size)
    mask = np.zeros_like(latitudes, dtype=bool)
    mask[lower:upper] = True
    return mask


def generate_ground_track_figure(
    summary: SummaryData, config_path: Path, plot_dir: Path
) -> Optional[TriangleFormationResult]:
    long_result = _simulate_extended_pass(config_path)
    if long_result is None:
        return None

    lat_deg = {
        sat: np.degrees(vals)
        for sat, vals in long_result.latitudes_rad.items()
    }
    lon_deg = {
        sat: _wrap_longitudes(np.degrees(vals), summary.geometry)
        for sat, vals in long_result.longitudes_rad.items()
    }

    window = summary.metrics.get("formation_window", {})
    start = _parse_iso8601(window.get("start"))
    end = _parse_iso8601(window.get("end"))

    fig, ax = plt.subplots(figsize=(10, 6))
    for sat in sorted(lat_deg):
        ax.plot(lon_deg[sat], lat_deg[sat], label=f"{sat} ground track")

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
                _wrap_longitudes(np.degrees(lon[mask]), summary.geometry),
                np.degrees(lats[mask]),
                s=20,
                label=f"{sat} 90 s window",
            )

    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Twenty-four-hour ground tracks with ninety-second Tehran window")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks.svg", format="svg")
    plt.close(fig)

    generate_ground_track_zoom_figure(summary, long_result, plot_dir)

    return long_result


def generate_ground_track_zoom_figure(
    summary: SummaryData, long_result: TriangleFormationResult, plot_dir: Path
) -> None:
    sat_ids = sorted(long_result.latitudes_rad)
    if not sat_ids:
        return

    target = summary.geometry.get("target", {})
    target_lat = float(target.get("latitude_deg", 35.6892))
    target_lon = float(target.get("longitude_deg", 51.3890))

    latitudes = {
        sat: np.degrees(long_result.latitudes_rad[sat]) for sat in sat_ids
    }
    longitudes = {
        sat: _wrap_longitudes(np.degrees(long_result.longitudes_rad[sat]), summary.geometry)
        for sat in sat_ids
    }

    local_segments: dict[str, np.ndarray] = {}
    local_longitudes: dict[str, np.ndarray] = {}
    collected_lat: list[np.ndarray] = []
    collected_lon: list[np.ndarray] = []

    for sat in sat_ids:
        mask = _select_local_segment(latitudes[sat], longitudes[sat], target_lat, target_lon)
        if not np.any(mask):
            continue
        local_segments[sat] = latitudes[sat][mask]
        local_longitudes[sat] = longitudes[sat][mask]
        collected_lat.append(local_segments[sat])
        collected_lon.append(local_longitudes[sat])

    if not collected_lat:
        return

    track_lat = np.concatenate(collected_lat)
    track_lon = np.concatenate(collected_lon)
    lat_span = track_lat.max() - track_lat.min()
    lon_span = track_lon.max() - track_lon.min()
    lat_margin = max(0.05, lat_span * 0.2)
    lon_margin = max(0.08, lon_span * 0.2)

    fig, ax = plt.subplots(figsize=(6.5, 6.0))
    ax.set_facecolor("#f5f5f5")
    boundary_polygons = _load_tehran_boundary_polygons()
    for polygon in boundary_polygons:
        if polygon.size == 0:
            continue
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
    colours = {
        sat: colour
        for sat, colour in zip(sat_ids, ["#1b9e77", "#d95f02", "#7570b3", "#66a61e", "#e7298a"])
    }

    stroke = [patheffects.Stroke(linewidth=4.0, foreground="#ffffff"), patheffects.Normal()]

    window = summary.metrics.get("formation_window", {})
    start = _parse_iso8601(window.get("start"))
    end = _parse_iso8601(window.get("end"))
    if isinstance(summary.run.times, np.ndarray):
        times = list(summary.run.times)
    else:
        times = list(summary.run.times)
    start_index = _find_nearest_epoch_index(times, start) if start else None

    for sat in sat_ids:
        if sat not in local_segments:
            continue
        ax.plot(
            local_longitudes[sat],
            local_segments[sat],
            color=colours.get(sat, "#3182bd"),
            linewidth=2.2,
            zorder=3,
            label=f"{sat} ground track",
            path_effects=stroke,
        )

        if start_index is not None:
            lat_series = summary.run.latitudes.get(sat)
            lon_series = summary.run.longitudes.get(sat)
            if (
                lat_series is not None
                and lon_series is not None
                and 0 <= start_index < len(lat_series)
                and len(lat_series) == len(lon_series)
            ):
                start_lat = float(np.degrees(lat_series[start_index]))
                start_lon = float(
                    _wrap_longitudes(np.degrees(lon_series[start_index]), summary.geometry)
                )
                ax.scatter(
                    start_lon,
                    start_lat,
                    s=75,
                    marker="s",
                    color=colours.get(sat, "#3182bd"),
                    edgecolor="#1a1a1a",
                    linewidths=0.6,
                    zorder=5,
                    label=f"{sat} window start",
                )
                ax.annotate(
                    sat,
                    (start_lon, start_lat),
                    textcoords="offset points",
                    xytext=(6, 5),
                    fontsize="small",
                    color="#1a1a1a",
                    zorder=6,
                )
    if start and end:
        mask = np.array([bool(t and start <= t <= end) for t in summary.run.times], dtype=bool)
        for sat, lats in summary.run.latitudes.items():
            if sat not in summary.run.longitudes:
                continue
            lon = summary.run.longitudes[sat]
            if len(lon) != len(mask):
                continue
            wrapped_lon = _wrap_longitudes(np.degrees(lon[mask]), summary.geometry)
            wrapped_lat = np.degrees(lats[mask])
            ax.scatter(
                wrapped_lon,
                wrapped_lat,
                s=55,
                edgecolor="#ffffff",
                linewidths=0.5,
                color=colours.get(sat, "#3182bd"),
                marker="o",
                label=f"{sat} window samples",
            )

    ax.scatter(
        target_lon,
        target_lat,
        color="#000000",
        marker="*",
        s=140,
        label="Tehran",
        zorder=6,
    )

    axis_lat = [track_lat, np.array([target_lat])]
    axis_lon = [track_lon, np.array([target_lon])]
    for polygon in boundary_polygons:
        if polygon.size == 0:
            continue
        axis_lon.append(polygon[:, 0])
        axis_lat.append(polygon[:, 1])

    combined_lat = np.concatenate(axis_lat)
    combined_lon = np.concatenate(axis_lon)

    ax.set_xlim(combined_lon.min() - lon_margin, combined_lon.max() + lon_margin)
    ax.set_ylim(combined_lat.min() - lat_margin, combined_lat.max() + lat_margin)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Tehran-local ground tracks during overflight")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="best", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "ground_tracks_tehran.svg", format="svg")
    plt.close(fig)


def generate_formation_triangle_snapshot(summary: SummaryData, plot_dir: Path) -> None:
    sat_ids = sorted(summary.run.positions)
    if len(sat_ids) < 3:
        return

    window = summary.metrics.get("formation_window", {})
    start = _parse_iso8601(window.get("start"))
    if isinstance(summary.run.times, np.ndarray):
        times = list(summary.run.times)
    else:
        times = list(summary.run.times)
    if not times:
        return

    index = _find_first_valid_formation_index(summary)
    title_context = "first valid formation epoch"
    if index is None:
        index = _find_nearest_epoch_index(times, start) if start else 0
        title_context = "formation window start"
    if index is None:
        index = 0
        title_context = "initial sample"

    time_step = float(summary.run.time_step)
    centroid_positions = np.mean([summary.run.positions[sat] for sat in sat_ids], axis=0)
    if time_step > 0.0:
        centroid_velocities = _differentiate(centroid_positions, time_step)
        satellite_velocities = {
            sat: _differentiate(summary.run.positions[sat], time_step) for sat in sat_ids
        }
    else:
        centroid_velocities = np.zeros_like(centroid_positions)
        satellite_velocities = {
            sat: np.zeros_like(summary.run.positions[sat]) for sat in sat_ids
        }

    centroid_position = centroid_positions[index]
    centroid_velocity = centroid_velocities[index]

    if np.linalg.norm(centroid_velocity) == 0.0:
        for sat in sat_ids:
            sat_velocity = satellite_velocities.get(sat)
            if sat_velocity is not None and sat_velocity.shape[0] > index:
                centroid_velocity = sat_velocity[index]
                if np.linalg.norm(centroid_velocity) != 0.0:
                    break
    if np.linalg.norm(centroid_velocity) == 0.0:
        radial = centroid_position / np.linalg.norm(centroid_position)
        reference = np.array([0.0, 0.0, 1.0])
        if np.allclose(np.cross(reference, radial), 0.0):
            reference = np.array([0.0, 1.0, 0.0])
        tangential = np.cross(reference, radial)
        tangential_norm = np.linalg.norm(tangential)
        if tangential_norm != 0.0:
            tangential /= tangential_norm
            speed = math.sqrt(MU_EARTH / np.linalg.norm(centroid_position))
            centroid_velocity = tangential * speed

    lvlh_coordinates: dict[str, np.ndarray] = {}
    colours = {
        sat: colour
        for sat, colour in zip(sat_ids, ["#1b9e77", "#d95f02", "#7570b3", "#66a61e", "#e7298a"])
    }

    for sat in sat_ids:
        rel_vec = summary.run.positions[sat][index] - centroid_position
        try:
            lvlh = eci_to_lvlh(centroid_position, centroid_velocity, rel_vec)
        except ValueError:
            lvlh = rel_vec
        lvlh_coordinates[sat] = lvlh / 1e3

    angles = {
        sat: math.atan2(lvlh_coordinates[sat][1], lvlh_coordinates[sat][0]) for sat in sat_ids
    }
    ordered = sorted(sat_ids, key=lambda sat: angles[sat])
    cycle = ordered + [ordered[0]]

    fig, ax = plt.subplots(figsize=(6.0, 6.0))

    polygon_y = [lvlh_coordinates[sat][1] for sat in cycle]
    polygon_x = [lvlh_coordinates[sat][0] for sat in cycle]
    ax.fill(polygon_y, polygon_x, color="#d0e2ff", alpha=0.18, zorder=1)
    ax.plot(polygon_y, polygon_x, color="#374151", linewidth=1.8, linestyle="-", zorder=3)

    for sat in ordered:
        coords = lvlh_coordinates[sat]
        ax.scatter(
            coords[1],
            coords[0],
            s=170,
            color=colours.get(sat, "#3182bd"),
            edgecolor="#1a1a1a",
            linewidths=0.8,
            zorder=4,
            label=sat,
        )
        ax.annotate(
            sat,
            (coords[1], coords[0]),
            textcoords="offset points",
            xytext=(8, 6),
            fontsize="small",
            color="#1a1a1a",
            zorder=5,
        )

    for first, second in zip(ordered, ordered[1:] + ordered[:1]):
        separation = (
            np.linalg.norm(
                summary.run.positions[first][index] - summary.run.positions[second][index]
            )
            / 1e3
        )
        midpoint = 0.5 * (lvlh_coordinates[first] + lvlh_coordinates[second])
        ax.text(
            midpoint[1],
            midpoint[0],
            f"{separation:.2f} km",
            fontsize="x-small",
            ha="center",
            va="center",
            color="#2f3b52",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", alpha=0.7, linewidth=0.0),
            zorder=6,
        )

    along = np.array([lvlh_coordinates[sat][1] for sat in sat_ids])
    radial = np.array([lvlh_coordinates[sat][0] for sat in sat_ids])
    along_range = along.max() - along.min()
    radial_range = radial.max() - radial.min()
    max_range = max(along_range, radial_range, 1e-9)
    margin_scale = 0.05
    min_margin = max_range * 0.03
    along_margin = max(0.05, along_range * margin_scale, min_margin)
    radial_margin = max(0.05, radial_range * margin_scale, min_margin)

    timestamp = times[index]
    timestamp_str = (
        timestamp.isoformat().replace("+00:00", "Z") if isinstance(timestamp, datetime) else "n/a"
    )

    ax.set_xlim(along.min() - along_margin, along.max() + along_margin)
    ax.set_ylim(radial.min() - radial_margin, radial.max() + radial_margin)
    ax.set_xlabel("Along-track [km]")
    ax.set_ylabel("Radial [km]")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title(f"Formation geometry at {title_context} ({timestamp_str})")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    fig.savefig(plot_dir / "formation_triangle_snapshot.svg", format="svg")
    plt.close(fig)


def generate_orbital_plane_figure(
    summary: SummaryData,
    config_path: Path,
    plot_dir: Path,
    long_result: Optional[TriangleFormationResult] = None,
) -> None:
    if long_result is None:
        long_result = _simulate_extended_pass(config_path, time_step_s=90.0)
    if long_result is None:
        return

    sat_ids = sorted(long_result.positions_m)
    if not sat_ids:
        return

    fig = plt.figure(figsize=(9, 7.5))
    ax = fig.add_subplot(111, projection="3d")

    colours = {
        sat: colour
        for sat, colour in zip(sat_ids, ["#1b9e77", "#d95f02", "#7570b3", "#66a61e", "#e7298a"])
    }

    times = list(long_result.times)
    time_step = 0.0
    if len(times) > 1 and times[0] and times[1]:
        time_step = (times[1] - times[0]).total_seconds()

    window_midpoint = None
    if isinstance(summary.run.times, np.ndarray):
        if summary.run.times.size:
            midpoint_index = int(summary.run.times.size // 2)
            window_midpoint = summary.run.times[midpoint_index]
    elif summary.run.times:
        midpoint_index = len(summary.run.times) // 2
        window_midpoint = summary.run.times[midpoint_index]

    plane_handles: list[mpatches.Patch] = []

    for sat in sat_ids:
        pos_km = long_result.positions_m[sat] / 1e3
        ax.plot(
            pos_km[:, 0],
            pos_km[:, 1],
            pos_km[:, 2],
            color=colours.get(sat, "#3182bd"),
            linewidth=1.4,
            label=f"{sat} orbit",
        )

        if time_step > 0.0:
            velocities = _differentiate(long_result.positions_m[sat], time_step)
        else:
            velocities = np.zeros_like(long_result.positions_m[sat])

        highlight_index = None
        if window_midpoint:
            highlight_index = _find_nearest_epoch_index(times, window_midpoint)
        if highlight_index is None:
            highlight_index = len(pos_km) // 2

        highlight_point = pos_km[highlight_index]
        ax.scatter(
            highlight_point[0],
            highlight_point[1],
            highlight_point[2],
            color=colours.get(sat, "#3182bd"),
            s=65,
            edgecolor="#ffffff",
            linewidths=0.8,
        )

        if velocities.size:
            normal_vec = np.cross(
                long_result.positions_m[sat][highlight_index],
                velocities[highlight_index],
            )
            if np.linalg.norm(normal_vec) > 0.0:
                normal_unit = normal_vec / np.linalg.norm(normal_vec)
                tangent = np.cross(normal_unit, np.array([0.0, 0.0, 1.0]))
                if np.linalg.norm(tangent) == 0.0:
                    tangent = np.array([1.0, 0.0, 0.0])
                tangent /= np.linalg.norm(tangent)
                bitangent = np.cross(normal_unit, tangent)
                extent = EARTH_EQUATORIAL_RADIUS_M / 1e3 * 1.15
                u = np.linspace(-extent, extent, 15)
                v = np.linspace(-extent, extent, 15)
                uu, vv = np.meshgrid(u, v)
                plane_points = (
                    uu[..., None] * tangent[None, None, :]
                    + vv[..., None] * bitangent[None, None, :]
                )
                ax.plot_surface(
                    plane_points[:, :, 0],
                    plane_points[:, :, 1],
                    plane_points[:, :, 2],
                    alpha=0.08,
                    color=colours.get(sat, "#3182bd"),
                    linewidth=0,
                    shade=False,
                )
                plane_handles.append(
                    mpatches.Patch(
                        facecolor=colours.get(sat, "#3182bd"),
                        alpha=0.2,
                        label=f"{sat} plane",
                    )
                )

    earth_radius_km = EARTH_EQUATORIAL_RADIUS_M / 1e3
    u = np.linspace(0, 2 * math.pi, 80)
    v = np.linspace(0, math.pi, 40)
    sphere_x = earth_radius_km * np.outer(np.cos(u), np.sin(v))
    sphere_y = earth_radius_km * np.outer(np.sin(u), np.sin(v))
    sphere_z = earth_radius_km * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(
        sphere_x,
        sphere_y,
        sphere_z,
        color="#f0f0f0",
        alpha=0.35,
        linewidth=0,
        zorder=0,
    )

    target_lat = float(summary.geometry.get("target", {}).get("latitude_deg", 35.6892))
    target_lon = float(summary.geometry.get("target", {}).get("longitude_deg", 51.3890))
    target_point = _geodetic_to_ecef(target_lat, target_lon, 0.0) / 1e3
    ax.scatter(
        target_point[0],
        target_point[1],
        target_point[2],
        color="#000000",
        marker="*",
        s=150,
        label="Tehran",
    )

    patch_half_angle_lat = 2.0
    patch_half_angle_lon = 3.0
    patch_lat = np.radians(
        np.linspace(target_lat - patch_half_angle_lat, target_lat + patch_half_angle_lat, 18)
    )
    patch_lon = np.radians(
        np.linspace(target_lon - patch_half_angle_lon, target_lon + patch_half_angle_lon, 18)
    )
    patch_lon_grid, patch_lat_grid = np.meshgrid(patch_lon, patch_lat)
    patch_radius = earth_radius_km * 1.01
    patch_x = patch_radius * np.cos(patch_lat_grid) * np.cos(patch_lon_grid)
    patch_y = patch_radius * np.cos(patch_lat_grid) * np.sin(patch_lon_grid)
    patch_z = patch_radius * np.sin(patch_lat_grid)
    ax.plot_surface(
        patch_x,
        patch_y,
        patch_z,
        color="#fee391",
        alpha=0.6,
        linewidth=0,
        shade=True,
    )

    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.set_zlabel("Z [km]")
    ax.set_title("Orbital planes intersecting above Tehran")

    handles, labels = ax.get_legend_handles_labels()
    for patch in plane_handles:
        handles.append(patch)
        labels.append(patch.get_label())
    legend_mapping: dict[str, object] = {}
    for handle, label in zip(handles, labels):
        legend_mapping[label] = handle
    ax.legend(
        list(legend_mapping.values()),
        list(legend_mapping.keys()),
        loc="upper left",
        fontsize="small",
    )

    max_extent = earth_radius_km * 1.8
    ax.set_xlim(-max_extent, max_extent)
    ax.set_ylim(-max_extent, max_extent)
    ax.set_zlim(-max_extent, max_extent)

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


def _differentiate(series: np.ndarray, step: float) -> np.ndarray:
    if series.size == 0 or step <= 0.0:
        return np.zeros_like(series)
    velocities = np.zeros_like(series)
    velocities[1:-1] = (series[2:] - series[:-2]) / (2.0 * step)
    velocities[0] = (series[1] - series[0]) / step
    velocities[-1] = (series[-1] - series[-2]) / step
    return velocities


def _find_nearest_epoch_index(times: list[datetime | None], target: datetime | None) -> int | None:
    if target is None or not times:
        return None
    differences: list[tuple[float, int]] = []
    for index, epoch in enumerate(times):
        if epoch is None:
            continue
        delta = abs((epoch - target).total_seconds())
        differences.append((delta, index))
    if not differences:
        return None
    differences.sort(key=lambda item: item[0])
    return differences[0][1]


def _find_first_valid_formation_index(summary: SummaryData) -> int | None:
    for index, sample in enumerate(summary.samples):
        if not isinstance(sample, dict):
            continue
        lengths = sample.get("triangle_side_lengths_m")
        area = sample.get("triangle_area_m2")
        if not lengths or area is None:
            continue
        try:
            numeric_lengths = [float(length) for length in lengths]
            numeric_area = float(area)
        except (TypeError, ValueError):
            continue
        if not all(math.isfinite(length) and length > 0.0 for length in numeric_lengths):
            continue
        if not math.isfinite(numeric_area) or numeric_area <= 0.0:
            continue
        return index
    return None


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

    long_result = generate_ground_track_figure(summary, args.config, plot_dir)
    generate_orbital_plane_figure(summary, args.config, plot_dir, long_result)
    generate_orbital_elements_timeseries(args.run_dir, plot_dir)
    generate_formation_triangle_snapshot(summary, plot_dir)
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
