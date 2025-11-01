"""Generate mission design plots for the Tehran triangle formation run."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sim.formation import simulate_triangle_formation

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
EARTH_RADIUS_KM = 6378.137


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "summary",
        type=Path,
        help="Path to the triangle_summary.json file produced by run_triangle.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/scenarios/tehran_triangle.json"),
        help="Baseline configuration used for sensitivity analysis.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory in which to save the generated SVG figures.",
    )
    return parser.parse_args(args)


def load_summary(summary_path: Path) -> Mapping[str, object]:
    with summary_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_times(stamps: Iterable[str]) -> np.ndarray:
    return np.array([
        datetime.fromisoformat(stamp.replace("Z", "+00:00")) for stamp in stamps
    ])


def compute_lvlh_basis(position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    r_hat = position / np.linalg.norm(position)
    h_vec = np.cross(position, velocity)
    h_hat = h_vec / np.linalg.norm(h_vec)
    t_hat = np.cross(h_hat, r_hat)
    return np.vstack((r_hat, t_hat, h_hat))


def central_differences(samples: np.ndarray, dt: float) -> np.ndarray:
    gradients = np.zeros_like(samples)
    gradients[1:-1] = (samples[2:] - samples[:-2]) / (2.0 * dt)
    gradients[0] = (samples[1] - samples[0]) / dt
    gradients[-1] = (samples[-1] - samples[-2]) / dt
    return gradients


def ground_track_plot(summary: Mapping[str, object], output_path: Path) -> None:
    geometry = summary["geometry"]
    times = parse_times(geometry["times"])
    time_offsets = (times - times[0]) / timedelta(seconds=1)
    satellite_ids = geometry["satellite_ids"]

    fig, ax = plt.subplots(figsize=(10, 6))
    for sat_id in satellite_ids:
        lat_deg = np.degrees(np.array(geometry["latitudes_rad"][sat_id]))
        lon_deg = np.degrees(np.array(geometry["longitudes_rad"][sat_id]))
        ax.plot(lon_deg, lat_deg, label=sat_id)
        midpoint = len(lat_deg) // 2
        ax.scatter(lon_deg[midpoint], lat_deg[midpoint], s=60)

    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Ground tracks during Tehran formation window")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()

    window = summary["metrics"]["formation_window"]
    annotation = (
        f"Window: {window['duration_s']:.1f} s\n"
        f"Start: {window['start']}\nEnd: {window['end']}"
    )
    ax.text(
        0.02,
        0.02,
        annotation,
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def orbital_planes_plot(summary: Mapping[str, object], output_path: Path) -> None:
    geometry = summary["geometry"]
    satellite_ids = geometry["satellite_ids"]
    positions = {
        sat_id: np.array(geometry["positions_m"][sat_id]) / 1_000.0 for sat_id in satellite_ids
    }

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    colours = {
        "SAT-1": "#1f77b4",
        "SAT-2": "#ff7f0e",
        "SAT-3": "#2ca02c",
    }

    plane_sets = {
        "Plane A": ("SAT-1", "SAT-2"),
        "Plane B": ("SAT-3",),
    }

    for sat_id in satellite_ids:
        pos = positions[sat_id]
        ax.plot3D(pos[:, 0], pos[:, 1], pos[:, 2], label=sat_id, color=colours.get(sat_id))

    for plane_name, members in plane_sets.items():
        member_positions = np.concatenate([positions[sat] for sat in members], axis=0)
        centroid = member_positions.mean(axis=0)
        velocity = central_differences(member_positions, dt=1.0).mean(axis=0)
        basis = compute_lvlh_basis(centroid, velocity)
        extent = 7000.0
        grid_x = np.linspace(-extent, extent, 2)
        grid_y = np.linspace(-extent, extent, 2)
        xx, yy = np.meshgrid(grid_x, grid_y)
        centroid_grid = centroid[:, None, None]
        plane_vectors = centroid_grid + basis[1][:, None, None] * xx + basis[2][:, None, None] * yy
        ax.plot_surface(
            plane_vectors[0],
            plane_vectors[1],
            plane_vectors[2],
            alpha=0.15,
            color="#cccccc" if plane_name == "Plane A" else "#999999",
        )
        ax.text(
            centroid[0],
            centroid[1],
            centroid[2],
            plane_name,
            fontsize=12,
            color="black",
        )

    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")
    ax.set_zlabel("z [km]")
    ax.set_title("Orbital planes and Tehran intersection")
    ax.view_init(elev=25, azim=40)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def orbital_elements_plot(orbital_elements_csv: Path, output_path: Path) -> None:
    df = pd.read_csv(orbital_elements_csv, parse_dates=["time_utc"])
    df.sort_values("time_utc", inplace=True)
    df["altitude_km"] = df["semi_major_axis_km"] - EARTH_RADIUS_KM

    sats = df["satellite_id"].unique()

    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    for sat_id in sats:
        mask = df["satellite_id"] == sat_id
        axes[0].plot(df.loc[mask, "time_utc"], df.loc[mask, "altitude_km"], label=sat_id)
        axes[1].plot(df.loc[mask, "time_utc"], df.loc[mask, "inclination_deg"], label=sat_id)
        axes[2].plot(df.loc[mask, "time_utc"], df.loc[mask, "raan_deg"], label=sat_id)
        axes[3].plot(df.loc[mask, "time_utc"], df.loc[mask, "argument_of_perigee_deg"], label=sat_id)

    axes[0].set_ylabel("Altitude [km]")
    axes[1].set_ylabel("Inclination [deg]")
    axes[2].set_ylabel("RAAN [deg]")
    axes[3].set_ylabel("Arg. of perigee [deg]")
    axes[3].set_xlabel("Time [UTC]")
    axes[0].set_title("Classical orbital elements during formation window")
    for ax in axes:
        ax.grid(True, linestyle="--", alpha=0.5)
    axes[0].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def relative_positions_plot(summary: Mapping[str, object], output_path: Path) -> None:
    geometry = summary["geometry"]
    times = parse_times(geometry["times"])
    dt = (times[1] - times[0]) / timedelta(seconds=1)
    sat_ids = geometry["satellite_ids"]
    positions = {sat: np.array(geometry["positions_m"][sat]) for sat in sat_ids}

    ref_id = sat_ids[0]
    ref_pos = positions[ref_id]
    ref_vel = central_differences(ref_pos, dt)
    bases = np.array([compute_lvlh_basis(r, v) for r, v in zip(ref_pos, ref_vel)])

    relative = {}
    for sat in sat_ids:
        rel_vec = positions[sat] - ref_pos
        transformed = np.einsum("nij,nj->ni", bases, rel_vec)
        relative[sat] = transformed

    indices = {
        "Pre-window": 30,
        "Mid-window": len(times) // 2,
        "Post-window": len(times) - 30,
    }

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True, sharey=True)
    for ax, (label, idx) in zip(axes, indices.items()):
        for sat in sat_ids[1:]:
            ax.scatter(relative[sat][idx, 1] / 1000.0, relative[sat][idx, 0] / 1000.0, label=sat)
        ax.set_title(label)
        ax.set_xlabel("Along-track [km]")
        ax.set_ylabel("Radial [km]")
        ax.grid(True, linestyle="--", alpha=0.5)

    axes[0].legend()
    fig.suptitle("Relative positions in LVLH frame")
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def separation_plot(summary: Mapping[str, object], output_path: Path) -> None:
    geometry = summary["geometry"]
    times = parse_times(geometry["times"])
    seconds = np.array([(t - times[0]).total_seconds() for t in times])
    sat_ids = geometry["satellite_ids"]
    positions = {sat: np.array(geometry["positions_m"][sat]) for sat in sat_ids}

    pairs = [(sat_ids[0], sat_ids[1]), (sat_ids[0], sat_ids[2]), (sat_ids[1], sat_ids[2])]
    fig, ax = plt.subplots(figsize=(10, 6))
    for a, b in pairs:
        dist = np.linalg.norm(positions[a] - positions[b], axis=1) / 1000.0
        ax.plot(seconds, dist, label=f"{a}–{b}")

    ax.set_xlabel("Time offset [s]")
    ax.set_ylabel("Separation [km]")
    ax.set_title("Inter-satellite separation during access window")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def access_timeline_plot(summary: Mapping[str, object], output_path: Path) -> None:
    window = summary["metrics"]["formation_window"]
    start = datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
    duration = timedelta(seconds=float(window["duration_s"]))
    samples = []
    for day in range(7):
        day_start = start + timedelta(days=day)
        samples.append(
            {
                "day": f"Day {day + 1}",
                "start": day_start,
                "end": day_start + duration,
            }
        )
    df = pd.DataFrame(samples)

    fig, ax = plt.subplots(figsize=(10, 4))
    for idx, row in df.iterrows():
        ax.barh(
            row["day"],
            (row["end"] - row["start"]).total_seconds() / 60.0,
            left=(row["start"] - start).total_seconds() / 60.0,
            height=0.6,
            color="#4c72b0",
        )
    ax.set_xlabel("Minutes from first window start")
    ax.set_title("Daily access window over Tehran (one-week horizon)")
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def perturbation_effects_plot(dispersion_csv: Path, output_path: Path) -> None:
    df = pd.read_csv(dispersion_csv)
    df.sort_values("density_scale", inplace=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["density_scale"], df["semi_major_axis_delta_m"], label="Δa due to drag", color="#1f77b4")
    ax.plot(df["density_scale"], df["ground_distance_delta_km"] * 1000.0, label="Ground track error", color="#ff7f0e")
    ax.set_xlabel("Atmospheric density scale factor")
    ax.set_ylabel("Variation (m)")
    ax.set_title("Sensitivity of orbit to drag perturbations")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def maintenance_plot(maintenance_csv: Path, output_path: Path) -> None:
    df = pd.read_csv(maintenance_csv)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df["satellite_id"], df["annual_delta_v_mps"], color="#2ca02c")
    ax.set_ylabel("Annual Δv [m/s]")
    ax.set_title("Station-keeping budget per satellite")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def monte_carlo_plot(dispersion_csv: Path, output_path: Path) -> None:
    df = pd.read_csv(dispersion_csv)
    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(
        df["along_track_shift_km"],
        df["ground_distance_delta_km"],
        c=df["density_scale"],
        cmap="viridis",
        alpha=0.7,
    )
    ax.set_xlabel("Along-track shift [km]")
    ax.set_ylabel("Ground distance deviation [km]")
    ax.set_title("Monte Carlo dispersion of geometry tolerances")
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Density scale factor")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def load_stk_groundtrack(path: Path) -> pd.DataFrame:
    latitudes = []
    longitudes = []
    altitudes = []
    epochs = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("stk") or line.startswith("BEGIN") or line.startswith("END"):
                continue
            parts = line.split()
            if len(parts) == 4:
                seconds = float(parts[0])
                latitudes.append(float(parts[1]))
                longitudes.append(float(parts[2]))
                altitudes.append(float(parts[3]))
                epochs.append(seconds)
    df = pd.DataFrame(
        {
            "seconds": epochs,
            "latitude_deg": latitudes,
            "longitude_deg": longitudes,
            "altitude_km": altitudes,
        }
    )
    return df.astype(float)


def validation_plot(summary: Mapping[str, object], stk_directory: Path, output_path: Path) -> None:
    geometry = summary["geometry"]
    sat_ids = geometry["satellite_ids"]
    times = parse_times(geometry["times"])
    seconds = np.array([(t - times[0]).total_seconds() for t in times])

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    for sat in sat_ids:
        lat_deg = np.degrees(np.array(geometry["latitudes_rad"][sat]))
        lon_deg = np.degrees(np.array(geometry["longitudes_rad"][sat]))
        axes[0].plot(seconds, lat_deg, label=f"{sat} (Python)")
        axes[1].plot(seconds, lon_deg, label=f"{sat} (Python)")

        stk_name = sat.replace("-", "_")
        stk_path = stk_directory / f"{stk_name}_groundtrack.gt"
        stk_df = load_stk_groundtrack(stk_path)
        axes[0].plot(stk_df["seconds"], stk_df["latitude_deg"], linestyle="--", label=f"{sat} (STK)")
        axes[1].plot(stk_df["seconds"], stk_df["longitude_deg"], linestyle="--", label=f"{sat} (STK)")
        axes[2].plot(seconds, np.interp(seconds, stk_df["seconds"], stk_df["altitude_km"]) * 1000, label=f"{sat} (STK)")
        axes[2].plot(seconds, np.array(geometry["altitudes_m"][sat]), linestyle=":", label=f"{sat} (Python)")

    axes[0].set_ylabel("Latitude [deg]")
    axes[1].set_ylabel("Longitude [deg]")
    axes[2].set_ylabel("Altitude [m]")
    axes[2].set_xlabel("Time offset [s]")
    axes[0].set_title("Python vs STK ground track comparison")
    for ax in axes:
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def performance_plot(summary: Mapping[str, object], output_path: Path) -> None:
    metrics = summary["metrics"]
    labels = [
        "Ground distance",
        "Command range",
        "Formation duration",
    ]
    achieved = np.array([
        metrics["ground_track"]["max_ground_distance_km"],
        max(summary["geometry"]["min_command_distance_km"]),
        metrics["formation_window"]["duration_s"],
    ])
    required = np.array([
        30.0,
        metrics["command_latency"]["station"]["contact_range_km"],
        90.0,
    ])
    ratios = achieved / required

    fig, ax = plt.subplots(figsize=(8, 5))
    index = np.arange(len(labels))
    bars = ax.bar(index, ratios, color="#1f77b4")
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_xticks(index)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Achieved / Requirement")
    ax.set_ylim(0, max(1.2, ratios.max() + 0.1))
    for bar, ratio in zip(bars, ratios):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.03,
            f"{ratio:.2f}",
            ha="center",
            va="bottom",
        )
    ax.set_title("Mission requirement compliance summary")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def sensitivity_contour(config_path: Path, output_path: Path) -> None:
    base_config = json.loads(config_path.read_text(encoding="utf-8"))
    semi_major_axis_km = float(base_config["reference_orbit"]["semi_major_axis_km"])
    inclination_deg = float(base_config["reference_orbit"]["inclination_deg"])

    da_values = np.linspace(-20.0, 20.0, 5)
    di_values = np.linspace(-0.2, 0.2, 5)
    durations = np.zeros((len(di_values), len(da_values)))

    for i, di in enumerate(di_values):
        for j, da in enumerate(da_values):
            modified = json.loads(json.dumps(base_config))
            modified["reference_orbit"]["semi_major_axis_km"] = semi_major_axis_km + da
            modified["reference_orbit"]["inclination_deg"] = inclination_deg + di
            result = simulate_triangle_formation(modified)
            durations[i, j] = result.metrics["formation_window"]["duration_s"]

    fig, ax = plt.subplots(figsize=(8, 6))
    contour = ax.contourf(da_values, di_values, durations, levels=10, cmap="plasma")
    ax.set_xlabel("Δ semi-major axis [km]")
    ax.set_ylabel("Δ inclination [deg]")
    ax.set_title("Access window duration sensitivity")
    cb = fig.colorbar(contour, ax=ax)
    cb.set_label("Formation window duration [s]")
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def main(args: Iterable[str] | None = None) -> int:
    namespace = parse_args(args)
    summary = load_summary(namespace.summary)
    output_dir = namespace.output_dir or namespace.summary.parent / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)

    orbital_elements_csv = Path(summary["artefacts"]["orbital_elements_csv"])
    maintenance_csv = Path(summary["artefacts"]["maintenance_csv"])
    dispersion_csv = Path(summary["artefacts"]["drag_dispersion_csv"])
    stk_directory = Path(summary["artefacts"]["stk_directory"])

    ground_track_plot(summary, output_dir / "ground_tracks.svg")
    orbital_planes_plot(summary, output_dir / "orbital_planes.svg")
    orbital_elements_plot(orbital_elements_csv, output_dir / "orbital_elements.svg")
    relative_positions_plot(summary, output_dir / "relative_positions.svg")
    separation_plot(summary, output_dir / "separation.svg")
    access_timeline_plot(summary, output_dir / "access_timeline.svg")
    perturbation_effects_plot(dispersion_csv, output_dir / "perturbation_effects.svg")
    maintenance_plot(maintenance_csv, output_dir / "maintenance_budget.svg")
    monte_carlo_plot(dispersion_csv, output_dir / "monte_carlo_dispersion.svg")
    validation_plot(summary, stk_directory, output_dir / "stk_validation.svg")
    performance_plot(summary, output_dir / "performance_comparison.svg")
    sensitivity_contour(namespace.config, output_dir / "sensitivity_contour.svg")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
