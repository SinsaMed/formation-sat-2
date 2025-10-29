"""Generate SVG and HTML visualisations for debug artefacts.

This utility reads the CSV exports produced by ``run_debug.py`` for the
Tehran triangle scenario and renders time-series charts alongside an
interactive three-dimensional formation view. The charts are emitted as
SVG files to preserve reviewability in version control, whilst the 3D
representation is stored as a standalone HTML document powered by Plotly.
"""

from __future__ import annotations

import argparse
import math
import json
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.lines import Line2D


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


def _plot_ground_track(latitudes: pd.DataFrame, longitudes: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 8))
    for satellite in latitudes.columns:
        if satellite == "time_utc":
            continue
        lat_deg = np.rad2deg(latitudes[satellite].to_numpy())
        lon_deg = np.rad2deg(longitudes[satellite].to_numpy())
        ax.plot(lon_deg, lat_deg, label=satellite)

    ax.set_title("Ground track projection over Tehran")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.legend(loc="best")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle=":", linewidth=0.5)

    output_path = output_dir / "ground_track.svg"
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


def _render_3d_formation(times: pd.Series, positions: pd.DataFrame, output_dir: Path) -> Path:
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
    output_path = output_dir / "formation_3d.html"
    pio.write_html(figure, file=output_path, include_plotlyjs="cdn", auto_play=False)
    return output_path


def generate_visualisations(run_directory: Path) -> dict[str, Path]:
    latitudes, longitudes = _load_lat_lon(run_directory)
    positions = _load_positions(run_directory)
    orbital_elements = _load_orbital_elements(run_directory)
    formation_start, formation_end = _load_formation_window(run_directory)
    orbital_pivots = _reshape_orbital_elements(orbital_elements)
    output_dir = _ensure_output_directory(run_directory)

    time_index = latitudes["time_utc"]
    outputs = {
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
        description="Render SVG charts and a 3D HTML plot for a debug run directory."
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
    for label, path in outputs.items():
        print(f"Generated {label} visualisation at {path}")


if __name__ == "__main__":
    main()
