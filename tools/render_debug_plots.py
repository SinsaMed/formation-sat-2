"""Generate SVG and HTML visualisations for debug artefacts.

This utility reads the CSV exports produced by ``run_debug.py`` for the
Tehran triangle scenario and renders time-series charts alongside an
interactive three-dimensional formation view. The canonical three-dimensional
representation is emitted as an SVG for archival review, whilst an HTML scene
remains available for exploratory analysis via Plotly.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # Required for 3D projection

try:  # pragma: no cover - optional dependency
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
except Exception:  # pragma: no cover - optional dependency
    ccrs = None
    cfeature = None


LOGGER = logging.getLogger(__name__)


CLASSICAL_ELEMENT_FIELDS = (
    "semi_major_axis_km",
    "eccentricity",
    "inclination_deg",
    "raan_deg",
    "argument_of_perigee_deg",
    "mean_anomaly_deg",
)

CLASSICAL_ELEMENT_LABELS = {
    "semi_major_axis_km": "Semi-major axis (km)",
    "eccentricity": "Eccentricity (–)",
    "inclination_deg": "Inclination (deg)",
    "raan_deg": "RAAN (deg)",
    "argument_of_perigee_deg": "Argument of perigee (deg)",
    "mean_anomaly_deg": "Mean anomaly (deg)",
}


TEHRAN_LATITUDE_DEG = 35.6892
TEHRAN_LONGITUDE_DEG = 51.3890


def _wrap_longitudes_around_tehran(longitudes_rad: np.ndarray) -> np.ndarray:
    """Normalise longitudes around Tehran to avoid map discontinuities."""

    unwrapped = np.rad2deg(np.unwrap(longitudes_rad))
    centred = ((unwrapped - TEHRAN_LONGITUDE_DEG + 180.0) % 360.0) - 180.0
    return centred + TEHRAN_LONGITUDE_DEG


def _load_lat_lon(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    lat_path = run_dir / "latitudes_rad.csv"
    lon_path = run_dir / "longitudes_rad.csv"
    if not lat_path.exists() or not lon_path.exists():
        raise FileNotFoundError(
            "Expected latitudes_rad.csv and longitudes_rad.csv within the run directory."
        )

    lat_df = pd.read_csv(lat_path, parse_dates=["time_utc"])
    lon_df = pd.read_csv(lon_path, parse_dates=["time_utc"])
    return lat_df, lon_df


def _load_positions(run_dir: Path) -> pd.DataFrame:
    pos_path = run_dir / "positions_m.csv"
    if not pos_path.exists():
        raise FileNotFoundError("Expected positions_m.csv within the run directory.")

    return pd.read_csv(pos_path, parse_dates=["time_utc"])


def _load_orbital_elements(run_dir: Path) -> pd.DataFrame:
    orbital_path = run_dir / "orbital_elements.csv"
    if not orbital_path.exists():
        raise FileNotFoundError(
            "Expected orbital_elements.csv within the run directory."
        )

    dataframe = pd.read_csv(orbital_path, parse_dates=["time_utc"])
    value_columns = [
        column
        for column in dataframe.columns
        if column not in {"time_utc", "satellite_id"}
    ]
    dataframe[value_columns] = dataframe[value_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return dataframe


def _load_formation_window(run_dir: Path) -> Tuple[pd.Timestamp, pd.Timestamp]:
    summary_path = run_dir / "triangle_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            "Expected triangle_summary.json within the run directory to derive formation window."
        )

    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)

    try:
        window = summary["metrics"]["formation_window"]
        start = pd.to_datetime(window["start"], utc=True)
        end = pd.to_datetime(window["end"], utc=True)
    except (KeyError, TypeError) as exc:  # pragma: no cover - defensive
        raise KeyError(
            "triangle_summary.json is missing metrics.formation_window start/end entries."
        ) from exc

    if pd.isna(start) or pd.isna(end):
        raise ValueError("Formation window timestamps could not be parsed into datetimes.")

    if start >= end:
        raise ValueError("Formation window start time must precede the end time.")

    return start, end


def _reshape_orbital_elements(
    dataframe: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Pivot the orbital elements into per-satellite time series."""

    if dataframe.empty:
        raise ValueError("Orbital elements CSV is empty.")

    missing_columns = [
        field for field in CLASSICAL_ELEMENT_FIELDS if field not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(
            "Orbital elements CSV is missing columns: " + ", ".join(missing_columns)
        )

    dataframe = dataframe.sort_values("time_utc").copy()
    satellites = sorted(dataframe["satellite_id"].unique())
    pivots: dict[str, pd.DataFrame] = {}
    for field in CLASSICAL_ELEMENT_FIELDS:
        pivot = dataframe.pivot(
            index="time_utc", columns="satellite_id", values=field
        )
        pivot = pivot.reindex(columns=satellites)
        pivots[field] = pivot
    return pivots


def _extract_satellite_labels(columns: Iterable[str]) -> List[str]:
    sats: List[str] = []
    for column in columns:
        if column == "time_utc":
            continue
        label = column.split("_")[0]
        if label not in sats:
            sats.append(label)
    return sats


def _ensure_output_directory(run_dir: Path) -> Path:
    output_dir = run_dir / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _plot_latitude(times: pd.Series, latitudes: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    for satellite in latitudes.columns:
        if satellite == "time_utc":
            continue
        ax.plot(times, np.rad2deg(latitudes[satellite]), label=satellite)

    ax.set_title("Latitude evolution for Tehran triangle formation")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Latitude (degrees)")
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    output_path = output_dir / "latitude_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_longitude(times: pd.Series, longitudes: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    for satellite in longitudes.columns:
        if satellite == "time_utc":
            continue
        wrapped = np.rad2deg(np.unwrap(longitudes[satellite].to_numpy()))
        wrapped = ((wrapped + 180.0) % 360.0) - 180.0
        ax.plot(times, wrapped, label=satellite)

    ax.set_title("Longitude evolution for Tehran triangle formation")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Longitude (degrees)")
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    output_path = output_dir / "longitude_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_ground_track(
    latitudes: pd.DataFrame, longitudes: pd.DataFrame, output_dir: Path
) -> Path:
    columns = [column for column in latitudes.columns if column != "time_utc"]
    output_path = output_dir / "ground_track_tehran_map.svg"

    if ccrs is None:
        LOGGER.warning(
            "Cartopy is unavailable; generating planar ground-track plot instead."
        )
        fig, ax = plt.subplots(figsize=(8, 8))
        for satellite in columns:
            lat_deg = np.rad2deg(latitudes[satellite].to_numpy())
            lon_wrapped = _wrap_longitudes_around_tehran(
                longitudes[satellite].to_numpy()
            )
            ax.plot(lon_wrapped, lat_deg, label=satellite)

        ax.scatter(
            [TEHRAN_LONGITUDE_DEG],
            [TEHRAN_LATITUDE_DEG],
            color="red",
            marker="*",
            s=120,
            label="Tehran",
        )
        ax.set_title("Ground track projection over Tehran")
        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")
        ax.legend(loc="best")
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, linestyle=":", linewidth=0.5)
        fig.savefig(output_path, format="svg", bbox_inches="tight")
        plt.close(fig)
        return output_path

    projection = ccrs.PlateCarree()
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=projection)
    extent = (
        TEHRAN_LONGITUDE_DEG - 20.0,
        TEHRAN_LONGITUDE_DEG + 20.0,
        TEHRAN_LATITUDE_DEG - 12.0,
        TEHRAN_LATITUDE_DEG + 12.0,
    )
    ax.set_extent(extent, crs=projection)

    ax.coastlines(resolution="110m", linewidth=0.6, zorder=1)
    if cfeature is not None:  # pragma: no branch - follows cartopy import
        ax.add_feature(cfeature.BORDERS, linewidth=0.4, edgecolor="grey", zorder=1)
        ax.add_feature(cfeature.LAND, facecolor="#f5f5f5", zorder=0)
        ax.add_feature(cfeature.OCEAN, facecolor="#dce9f5", zorder=0)

    gridlines = ax.gridlines(
        draw_labels=True,
        linestyle=":",
        linewidth=0.4,
        color="grey",
        x_inline=False,
        y_inline=False,
    )
    gridlines.top_labels = False
    gridlines.right_labels = False

    for satellite in columns:
        lat_deg = np.rad2deg(latitudes[satellite].to_numpy())
        lon_wrapped = _wrap_longitudes_around_tehran(
            longitudes[satellite].to_numpy()
        )
        ax.plot(
            lon_wrapped,
            lat_deg,
            transform=ccrs.Geodetic(),
            label=satellite,
            linewidth=1.5,
        )

    ax.scatter(
        [TEHRAN_LONGITUDE_DEG],
        [TEHRAN_LATITUDE_DEG],
        color="red",
        marker="*",
        s=120,
        transform=projection,
        zorder=5,
        label="Tehran",
    )
    ax.text(
        TEHRAN_LONGITUDE_DEG + 0.5,
        TEHRAN_LATITUDE_DEG + 0.5,
        "Tehran",
        transform=projection,
        fontsize=10,
        fontweight="bold",
        zorder=5,
    )

    ax.set_title("Ground tracks over Tehran in regional context")
    ax.legend(loc="upper right")

    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_orbital_elements(
    pivots: dict[str, pd.DataFrame], output_dir: Path
) -> Path:
    fig, axes = plt.subplots(
        len(CLASSICAL_ELEMENT_FIELDS), 1, sharex=True, figsize=(12, 18)
    )
    if not isinstance(axes, np.ndarray):  # pragma: no cover - defensive
        axes = np.array([axes])

    line_handles: list[Line2D] = []
    legend_labels: list[str] = []
    for index, field in enumerate(CLASSICAL_ELEMENT_FIELDS):
        axis = axes[index]
        pivot = pivots[field]
        for column in pivot.columns:
            line, = axis.plot(pivot.index, pivot[column], label=column)
            if column not in legend_labels:
                legend_labels.append(column)
                line_handles.append(line)
        axis.set_ylabel(CLASSICAL_ELEMENT_LABELS[field])
        axis.grid(True, linestyle=":", linewidth=0.5)

    axes[-1].set_xlabel("Time (UTC)")
    fig.suptitle("Classical orbital elements per satellite")
    fig.legend(line_handles, legend_labels, loc="upper center", ncol=len(legend_labels))
    fig.autofmt_xdate()
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))

    output_path = output_dir / "orbital_elements_timeseries.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_orbital_elements_formation_window(
    pivots: dict[str, pd.DataFrame],
    formation_start: pd.Timestamp,
    formation_end: pd.Timestamp,
    output_dir: Path,
) -> Path:
    fig, axes = plt.subplots(
        len(CLASSICAL_ELEMENT_FIELDS), 1, sharex=True, figsize=(12, 18)
    )
    if not isinstance(axes, np.ndarray):  # pragma: no cover - defensive
        axes = np.array([axes])

    line_handles: list[Line2D] = []
    legend_labels: list[str] = []

    for index, field in enumerate(CLASSICAL_ELEMENT_FIELDS):
        axis = axes[index]
        pivot = pivots[field]
        if pivot.index.tz is None:
            start_cmp = formation_start.tz_convert("UTC").tz_localize(None)
            end_cmp = formation_end.tz_convert("UTC").tz_localize(None)
        else:
            start_cmp = formation_start.tz_convert("UTC")
            end_cmp = formation_end.tz_convert("UTC")

        window_slice = pivot.loc[(pivot.index >= start_cmp) & (pivot.index <= end_cmp)]
        if window_slice.empty:
            raise ValueError(
                "Orbital elements time series do not contain samples within the formation window."
            )

        for column in window_slice.columns:
            line, = axis.plot(window_slice.index, window_slice[column], label=column)
            if column not in legend_labels:
                legend_labels.append(column)
                line_handles.append(line)
        axis.set_ylabel(CLASSICAL_ELEMENT_LABELS[field])
        axis.grid(True, linestyle=":", linewidth=0.5)

    axes[-1].set_xlabel("Time (UTC)")
    start_label = formation_start.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%SZ")
    end_label = formation_end.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%SZ")
    fig.suptitle(
        "Classical orbital elements during formation window\n"
        f"{start_label} to {end_label}"
    )
    fig.legend(line_handles, legend_labels, loc="upper center", ncol=len(legend_labels))
    fig.autofmt_xdate()
    fig.tight_layout(rect=(0.0, 0.05, 1.0, 0.92))
    fig.text(
        0.5,
        0.01,
        f"Formation window applied: {start_label} – {end_label} (UTC)",
        ha="center",
        va="bottom",
    )

    output_path = output_dir / "orbital_elements_formation_window.svg"
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _set_3d_equal_aspect(ax: plt.Axes, points: np.ndarray) -> None:
    """Set equal aspect ratios for three-dimensional axes."""

    ranges = points.max(axis=0) - points.min(axis=0)
    max_range = ranges.max() / 2.0
    centres = (points.max(axis=0) + points.min(axis=0)) / 2.0

    if max_range == 0.0:
        max_range = 1.0

    x_centre, y_centre, z_centre = centres
    ax.set_xlim(x_centre - max_range, x_centre + max_range)
    ax.set_ylim(y_centre - max_range, y_centre + max_range)
    ax.set_zlim(z_centre - max_range, z_centre + max_range)

    if hasattr(ax, "set_box_aspect"):
        ax.set_box_aspect((1, 1, 1))


def _render_formation_svg(
    positions: pd.DataFrame,
    satellites: list[str],
    earth_radius: float,
    output_path: Path,
) -> None:
    """Create a static SVG visualisation of the formation using Matplotlib."""

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    theta = np.linspace(0, 2 * math.pi, 120)
    phi = np.linspace(0, math.pi, 60)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    earth_x = earth_radius * np.sin(phi_grid) * np.cos(theta_grid)
    earth_y = earth_radius * np.sin(phi_grid) * np.sin(theta_grid)
    earth_z = earth_radius * np.cos(phi_grid)
    ax.plot_surface(
        earth_x,
        earth_y,
        earth_z,
        rstride=1,
        cstride=1,
        linewidth=0,
        antialiased=True,
        alpha=0.25,
        color="#1f78b4",
        edgecolor="none",
    )

    point_clouds = [
        np.column_stack((earth_x.ravel(), earth_y.ravel(), earth_z.ravel()))
    ]

    for satellite in satellites:
        x = positions[f"{satellite}_x_m"].to_numpy()
        y = positions[f"{satellite}_y_m"].to_numpy()
        z = positions[f"{satellite}_z_m"].to_numpy()
        ax.plot(x, y, z, label=satellite, linewidth=2.0)
        point_clouds.append(np.column_stack((x, y, z)))

    stacked_points = np.vstack(point_clouds)
    _set_3d_equal_aspect(ax, stacked_points)

    ax.set_title("Tehran triangle formation in Earth-centred coordinates")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.view_init(elev=20.0, azim=45.0)
    ax.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def _render_3d_formation(times: pd.Series, positions: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    satellites = _extract_satellite_labels(positions.columns)
    traces: List[go.Scatter3d] = []
    if times.dt.tz is not None:
        utc_times = times.dt.tz_convert("UTC")
    else:
        utc_times = times.dt.tz_localize("UTC")
    iso_times = utc_times.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    for satellite in satellites:
        x = positions[f"{satellite}_x_m"]
        y = positions[f"{satellite}_y_m"]
        z = positions[f"{satellite}_z_m"]
        traces.append(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                name=satellite,
                line=dict(width=4),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "x: %{x:.0f} m<br>"
                    "y: %{y:.0f} m<br>"
                    "z: %{z:.0f} m"
                ),
                text=[f"{satellite} @ {t}" for t in iso_times],
            )
        )

    # Generate a translucent Earth sphere for context.
    theta = np.linspace(0, 2 * math.pi, 60)
    phi = np.linspace(0, math.pi, 30)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    earth_radius = 6_371_000.0
    x = earth_radius * np.sin(phi_grid) * np.cos(theta_grid)
    y = earth_radius * np.sin(phi_grid) * np.sin(theta_grid)
    z = earth_radius * np.cos(phi_grid)
    earth_surface = go.Surface(
        x=x,
        y=y,
        z=z,
        colorscale=[[0, "#1f78b4"], [1, "#a6cee3"]],
        opacity=0.25,
        showscale=False,
        name="Earth",
    )

    layout = go.Layout(
        title="Tehran triangle formation in Earth-Centred coordinates",
        scene=dict(
            xaxis=dict(title="x (m)"),
            yaxis=dict(title="y (m)"),
            zaxis=dict(title="z (m)"),
            aspectmode="data",
        ),
        legend=dict(x=0.0, y=1.0),
    )

    figure = go.Figure(data=[earth_surface, *traces], layout=layout)
    html_path = output_dir / "formation_3d.html"
    pio.write_html(figure, file=html_path, include_plotlyjs="cdn", auto_play=False)

    svg_path = output_dir / "formation_3d.svg"
    _render_formation_svg(positions, satellites, earth_radius, svg_path)

    return {"svg": svg_path, "html": html_path}


def generate_visualisations(run_directory: Path) -> dict[str, Path | dict[str, Path]]:
    latitudes, longitudes = _load_lat_lon(run_directory)
    positions = _load_positions(run_directory)
    orbital_elements = _load_orbital_elements(run_directory)
    formation_start, formation_end = _load_formation_window(run_directory)
    orbital_pivots = _reshape_orbital_elements(orbital_elements)
    output_dir = _ensure_output_directory(run_directory)

    time_index = latitudes["time_utc"]
    outputs: dict[str, Path | dict[str, Path]] = {
        "latitude": _plot_latitude(time_index, latitudes, output_dir),
        "longitude": _plot_longitude(time_index, longitudes, output_dir),
        "ground_track": _plot_ground_track(latitudes, longitudes, output_dir),
        "formation_3d": _render_3d_formation(time_index, positions, output_dir),
        "orbital_elements_timeseries": _plot_orbital_elements(
            orbital_pivots, output_dir
        ),
        "orbital_elements_formation_window": _plot_orbital_elements_formation_window(
            orbital_pivots, formation_start, formation_end, output_dir
        ),
    }
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render SVG charts, a canonical 3D SVG, and an HTML Plotly scene for a debug run directory."
    )
    parser.add_argument(
        "run_directory",
        type=Path,
        help="Path to the timestamped debug run directory (e.g. artefacts/debug/20250930T185811Z)",
    )
    args = parser.parse_args()

    run_directory = args.run_directory
    if not run_directory.exists():
        raise FileNotFoundError(f"Run directory {run_directory} does not exist.")

    outputs = generate_visualisations(run_directory)
    for label, artefact in outputs.items():
        if isinstance(artefact, dict):
            canonical = artefact.get("svg")
            if canonical is not None:
                print(
                    f"Generated {label} visualisation at {canonical} (canonical SVG)"
                )
            for fmt, path in artefact.items():
                if fmt == "svg":
                    continue
                print(f"Generated {label} visualisation at {path} ({fmt})")
        else:
            print(f"Generated {label} visualisation at {artefact}")


if __name__ == "__main__":
    main()
