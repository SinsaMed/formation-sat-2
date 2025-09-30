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
from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


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
    output_dir = _ensure_output_directory(run_directory)

    time_index = latitudes["time_utc"]
    outputs = {
        "latitude": _plot_latitude(time_index, latitudes, output_dir),
        "longitude": _plot_longitude(time_index, longitudes, output_dir),
        "ground_track": _plot_ground_track(latitudes, longitudes, output_dir),
        "formation_3d": _render_3d_formation(time_index, positions, output_dir),
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
