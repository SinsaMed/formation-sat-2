"""Generate documentation figures for the Tehran triangle formation run."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sim.formation import simulate_triangle_formation

DEFAULT_CONFIG = Path("config/scenarios/tehran_triangle.json")
SOLAR_PRESSURE = 4.56e-6  # N m^-2 at 1 AU.
SRP_COEFFICIENT = 1.3


class TriangleRunData:
    """Container for the simulation run geometry and metrics."""

    def __init__(self, payload: Mapping[str, object]):
        geometry = payload["geometry"]
        self.times = np.array(
            [
                datetime.fromisoformat(sample.replace("Z", "+00:00"))
                for sample in geometry["times"]
            ],
            dtype=object,
        )
        self.positions = {
            sat_id: np.asarray(points, dtype=float)
            for sat_id, points in geometry["positions_m"].items()
        }
        self.latitudes = {
            sat_id: np.asarray(values, dtype=float)
            for sat_id, values in geometry["latitudes_rad"].items()
        }
        self.longitudes = {
            sat_id: np.asarray(values, dtype=float)
            for sat_id, values in geometry["longitudes_rad"].items()
        }
        self.altitudes = {
            sat_id: np.asarray(values, dtype=float)
            for sat_id, values in geometry["altitudes_m"].items()
        }
        self.metrics = payload.get("metrics", {})
        self.samples = payload.get("samples", [])

    @property
    def time_seconds(self) -> np.ndarray:
        reference = self.times[0]
        return np.array(
            [float((epoch - reference).total_seconds()) for epoch in self.times],
            dtype=float,
        )


def parse_arguments(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to the artefact directory produced by sim.scripts.run_triangle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory in which to place the generated SVG figures.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Triangle configuration to regenerate extended ground tracks.",
    )
    return parser.parse_args(argv)


def load_summary(run_dir: Path) -> TriangleRunData:
    summary_path = run_dir / "triangle_summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    return TriangleRunData(payload)


def load_dataframe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Expected artefact missing: {path}")
    return pd.read_csv(path)


def regenerate_ground_track(config_path: Path) -> TriangleRunData:
    configuration = json.loads(config_path.read_text(encoding="utf-8"))
    formation = configuration.get("formation", {})
    formation["duration_s"] = 86_400.0
    formation["time_step_s"] = 60.0
    configuration["formation"] = formation
    result = simulate_triangle_formation(configuration)
    return TriangleRunData(result.to_summary())


def ensure_output_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def plot_ground_tracks(
    short_run: TriangleRunData,
    long_run: TriangleRunData,
    output_path: Path,
) -> None:
    plt.style.use("seaborn-v0_8")
    figure, axis = plt.subplots(figsize=(10, 6))
    target_lat_deg = 35.6892
    target_lon_deg = 51.3890

    for sat_id, latitudes in long_run.latitudes.items():
        axis.plot(
            np.degrees(long_run.longitudes[sat_id]),
            np.degrees(latitudes),
            label=f"{sat_id} (24 h)",
            linewidth=1.0,
        )

    centre_index = len(short_run.times) // 2
    window_mask = slice(max(centre_index - 45, 0), min(centre_index + 45, len(short_run.times)))
    for sat_id in short_run.latitudes:
        axis.plot(
            np.degrees(short_run.longitudes[sat_id][window_mask]),
            np.degrees(short_run.latitudes[sat_id][window_mask]),
            linewidth=2.0,
            linestyle="--",
            label=f"{sat_id} (90 s window)",
        )

    axis.scatter([target_lon_deg], [target_lat_deg], color="black", marker="x", s=60, label="Tehran")
    axis.set_xlabel("Longitude [deg]")
    axis.set_ylabel("Latitude [deg]")
    axis.set_title("Ground tracks over Tehran triangular formation window")
    axis.legend(loc="best", fontsize="small")
    axis.grid(True, linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def _central_velocity(positions: np.ndarray, times: np.ndarray) -> np.ndarray:
    step = (times[1] - times[0]).total_seconds() if len(times) > 1 else 1.0
    derivatives = np.zeros_like(positions)
    for index in range(len(positions)):
        if 0 < index < len(positions) - 1:
            derivatives[index] = (positions[index + 1] - positions[index - 1]) / (2.0 * step)
        elif index == 0:
            derivatives[index] = (positions[index + 1] - positions[index]) / step
        else:
            derivatives[index] = (positions[index] - positions[index - 1]) / step
    return derivatives


def _lvlh_frame(position: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    r_hat = position / np.linalg.norm(position)
    h = np.cross(position, velocity)
    k_hat = h / np.linalg.norm(h)
    j_hat = np.cross(k_hat, r_hat)
    j_hat /= np.linalg.norm(j_hat)
    return np.column_stack((r_hat, j_hat, k_hat))


def plot_orbital_planes(run: TriangleRunData, output_path: Path) -> None:
    figure = plt.figure(figsize=(10, 8))
    axis = figure.add_subplot(111, projection="3d")

    centre_index = len(run.times) // 2
    colours = {"SAT-1": "#004c6d", "SAT-2": "#ff7f0e", "SAT-3": "#2ca02c"}
    plane_assignments = run.metrics["orbital_elements"]["plane_assignments"]

    velocities = {
        sat_id: _central_velocity(positions, run.times)
        for sat_id, positions in run.positions.items()
    }

    for sat_id, positions in run.positions.items():
        axis.plot(
            positions[:, 0] / 1_000.0,
            positions[:, 1] / 1_000.0,
            positions[:, 2] / 1_000.0,
            label=f"{sat_id} trajectory",
            color=colours.get(sat_id, None),
        )

    for plane_name in sorted(set(plane_assignments.values())):
        members = [sat for sat, plane in plane_assignments.items() if plane == plane_name]
        if not members:
            continue
        vectors = []
        for sat_id in members:
            frame = _lvlh_frame(run.positions[sat_id][centre_index], velocities[sat_id][centre_index])
            vectors.append(frame[:, 2])
        normal = np.mean(vectors, axis=0)
        normal /= np.linalg.norm(normal)
        reference = np.mean([run.positions[sat_id][centre_index] for sat_id in members], axis=0)
        u = np.cross(normal, [1.0, 0.0, 0.0])
        if np.linalg.norm(u) < 1e-8:
            u = np.cross(normal, [0.0, 1.0, 0.0])
        u /= np.linalg.norm(u)
        v = np.cross(normal, u)
        scale = 200.0
        grid_u = np.linspace(-scale, scale, 2)
        grid_v = np.linspace(-scale, scale, 2)
        mesh_u, mesh_v = np.meshgrid(grid_u, grid_v)
        surface = reference[None, None, :] + mesh_u[..., None] * u + mesh_v[..., None] * v
        axis.plot_surface(
            surface[:, :, 0] / 1_000.0,
            surface[:, :, 1] / 1_000.0,
            surface[:, :, 2] / 1_000.0,
            alpha=0.2,
            color="#888888",
            edgecolor="none",
        )
        axis.text(
            reference[0] / 1_000.0,
            reference[1] / 1_000.0,
            reference[2] / 1_000.0,
            plane_name,
        )

    axis.set_xlabel("x [km]")
    axis.set_ylabel("y [km]")
    axis.set_zlabel("z [km]")
    axis.set_title("Orbital plane geometry over Tehran")
    axis.legend(loc="upper left", fontsize="small")
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_orbital_elements(elements_csv: Path, output_path: Path) -> None:
    dataframe = load_dataframe(elements_csv)
    dataframe["time_utc"] = pd.to_datetime(dataframe["time_utc"], utc=True)
    figure, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    axes = axes.flatten()
    for sat_id, group in dataframe.groupby("satellite_id"):
        axes[0].plot(group["time_utc"], group["semi_major_axis_km"], label=sat_id)
        axes[1].plot(group["time_utc"], group["inclination_deg"], label=sat_id)
        axes[2].plot(group["time_utc"], group["raan_deg"], label=sat_id)
        axes[3].plot(group["time_utc"], group["argument_of_perigee_deg"], label=sat_id)
    axes[0].set_ylabel("a [km]")
    axes[1].set_ylabel("i [deg]")
    axes[2].set_ylabel("RAAN [deg]")
    axes[3].set_ylabel("ω [deg]")
    axes[3].set_xlabel("Time [UTC]")
    axes[0].set_title("Semi-major axis evolution")
    axes[1].set_title("Inclination evolution")
    axes[2].set_title("RAAN evolution")
    axes[3].set_title("Argument of perigee evolution")
    axes[0].legend(loc="upper right", fontsize="small")
    for axis in axes:
        axis.grid(True, linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_relative_positions(run: TriangleRunData, output_path: Path) -> None:
    indices = [0, len(run.times) // 2, len(run.times) - 1]
    labels = ["-90 s", "0 s", "+90 s"]
    figure, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True, sharey=True)
    for axis, index, label in zip(axes, indices, labels):
        centroid = sum(run.positions[sat_id][index] for sat_id in run.positions) / len(run.positions)
        frame = _lvlh_frame(run.positions["SAT-1"][index], _central_velocity(run.positions["SAT-1"], run.times)[index])
        for sat_id in run.positions:
            relative = run.positions[sat_id][index] - centroid
            local = frame.T @ relative
            axis.scatter(local[1] / 1_000.0, local[0] / 1_000.0, label=sat_id)
        axis.set_title(f"Centred frame {label}")
        axis.set_xlabel("Along-track [km]")
        axis.set_ylabel("Radial [km]")
        axis.grid(True, linestyle=":", linewidth=0.5)
    axes[0].legend(loc="upper right", fontsize="small")
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_pairwise_distances(run: TriangleRunData, output_path: Path) -> None:
    time_axis = run.time_seconds - run.time_seconds[len(run.time_seconds) // 2]
    figure, axis = plt.subplots(figsize=(10, 6))
    for sat_a, sat_b in combinations(run.positions.keys(), 2):
        distances = np.linalg.norm(run.positions[sat_a] - run.positions[sat_b], axis=1) / 1_000.0
        axis.plot(time_axis, distances, label=f"{sat_a}-{sat_b}")
    axis.set_xlabel("Time offset [s]")
    axis.set_ylabel("Separation [km]")
    axis.set_title("Pairwise separation across the access window")
    axis.legend(loc="upper right")
    axis.grid(True, linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_access_timeline(run: TriangleRunData, output_path: Path) -> None:
    window = run.metrics["formation_window"]
    start = datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
    duration = timedelta(seconds=float(window["duration_s"]))
    dates = [start + timedelta(days=offset) for offset in range(7)]
    figure, axis = plt.subplots(figsize=(10, 3))
    for day_index, day_start in enumerate(dates):
        axis.broken_barh(
            [(day_start.timestamp(), duration.total_seconds())],
            (day_index - 0.4, 0.8),
            facecolors="#1f77b4",
        )
    axis.set_yticks(range(7))
    axis.set_yticklabels([(start + timedelta(days=i)).strftime("%d %b") for i in range(7)])
    axis.set_xlabel("UTC timestamp")
    axis.set_title("Daily 96 s formation access over Tehran")
    axis.grid(True, axis="x", linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_perturbation_drift(
    run: TriangleRunData,
    drag_csv: Path,
    output_path: Path,
) -> None:
    drag = load_dataframe(drag_csv)
    mean_altitude_drop = drag["altitude_delta_m"].mean()
    orbits = 12.0
    drop_per_orbit = mean_altitude_drop / orbits
    semi_major_axis = float(run.metrics["orbital_elements"]["per_satellite"]["SAT-1"]["semi_major_axis_km"]) * 1_000.0
    inclination_deg = float(run.metrics["orbital_elements"]["per_satellite"]["SAT-1"]["inclination_deg"])
    mu = 3.986004418e14
    earth_radius = 6_378_137.0
    days = np.linspace(0.0, 30.0, 301)
    period = 2.0 * np.pi * np.sqrt(semi_major_axis**3 / mu)
    orbits_per_day = 86_400.0 / period
    drag_drift = drop_per_orbit * orbits_per_day * days
    e = float(run.metrics["orbital_elements"]["per_satellite"]["SAT-1"]["eccentricity"])
    inclination = np.radians(inclination_deg)
    raan_rate = -1.5 * np.sqrt(mu) * (earth_radius**2) * 1.08262668e-3
    raan_rate /= ((semi_major_axis**3) * (1 - e**2) ** 2)
    raan_rate *= np.cos(inclination)
    raan_drift = np.degrees(raan_rate * days * 86_400.0)
    area = 1.1
    mass = 165.0
    srp_accel = SOLAR_PRESSURE * SRP_COEFFICIENT * area / mass
    srp_shift = 0.5 * srp_accel * (days * 86_400.0) ** 2 / 1_000.0

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(days, drag_drift / 1_000.0, label="Drag-induced altitude decay [km]")
    axis.plot(days, raan_drift, label="J2 RAAN drift [deg]")
    axis.plot(days, srp_shift, label="SRP transverse displacement [km]")
    axis.set_xlabel("Elapsed days")
    axis.set_title("Perturbation-driven drift over thirty days")
    axis.grid(True, linestyle=":", linewidth=0.5)
    axis.legend(loc="best")
    axis.set_ylabel("Magnitude")
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_maintenance_delta_v(csv_path: Path, output_path: Path) -> None:
    dataframe = load_dataframe(csv_path)
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.bar(
        dataframe["satellite_id"],
        dataframe["annual_delta_v_mps"],
        color="#6baed6",
    )
    axis.set_ylabel("Annual Δv [m s⁻¹]")
    axis.set_title("Maintenance delta-v demand per spacecraft")
    axis.grid(True, axis="y", linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_monte_carlo(csv_path: Path, output_path: Path) -> None:
    dataframe = load_dataframe(csv_path)
    colours = dataframe["success"].map({True: "#2ca02c", False: "#d62728"})
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(
        dataframe["position_error_m"],
        dataframe["delta_v_mps"],
        c=colours,
        alpha=0.7,
        edgecolor="none",
    )
    axis.set_xlabel("Initial position error [m]")
    axis.set_ylabel("Required Δv [m s⁻¹]")
    axis.set_title("Monte Carlo recovery effort")
    axis.grid(True, linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_analytical_vs_stk(
    run: TriangleRunData,
    stk_groundtrack: Path,
    output_path: Path,
) -> None:
    with stk_groundtrack.open("r", encoding="utf-8") as handle:
        lines = handle.readlines()
    start = lines.index("    BEGIN Points\n") + 1
    stop = lines.index("    END Points\n")
    points = [line.strip().split() for line in lines[start:stop]]
    stk_lon = np.array([float(entry[2]) for entry in points], dtype=float)
    stk_lat = np.array([float(entry[1]) for entry in points], dtype=float)

    sat_id = list(run.latitudes.keys())[0]
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(np.degrees(run.longitudes[sat_id]), np.degrees(run.latitudes[sat_id]), label="Python propagation")
    axis.plot(stk_lon, stk_lat, linestyle="--", label="STK export")
    axis.set_xlabel("Longitude [deg]")
    axis.set_ylabel("Latitude [deg]")
    axis.set_title("Analytical vs STK ground track (SAT-1)")
    axis.legend(loc="best")
    axis.grid(True, linestyle=":", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_performance_metrics(run: TriangleRunData, output_path: Path) -> None:
    triangle_metrics = run.metrics["triangle"]
    ground_metrics = run.metrics["ground_track"]
    data = {
        "Metric": [
            "Mean area [km²]",
            "Aspect ratio max",
            "Ground distance max [km]",
            "Window duration [s]",
        ],
        "Value": [
            triangle_metrics["mean_area_m2"] / 1_000_000.0,
            triangle_metrics["aspect_ratio_max"],
            ground_metrics["max_ground_distance_km"],
            run.metrics["formation_window"]["duration_s"],
        ],
        "Threshold": [
            0.036,
            1.02,
            ground_metrics["ground_distance_tolerance_km"],
            90.0,
        ],
    }
    dataframe = pd.DataFrame(data)
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.barh(dataframe["Metric"], dataframe["Threshold"], color="#cccccc", label="Requirement")
    axis.barh(dataframe["Metric"], dataframe["Value"], color="#3182bd", label="Achieved")
    axis.set_xlabel("Magnitude")
    axis.set_title("Formation performance summary")
    axis.legend(loc="lower right")
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def plot_sensitivity_contour(csv_path: Path, output_path: Path) -> None:
    dataframe = load_dataframe(csv_path)
    pivot = dataframe.pivot_table(
        index="density_scale",
        columns="drag_coefficient",
        values="along_track_shift_km",
        aggfunc="mean",
    )
    x = pivot.columns.values
    y = pivot.index.values
    z = pivot.values
    figure, axis = plt.subplots(figsize=(8, 6))
    contour = axis.contourf(x, y, z, levels=12, cmap="viridis")
    figure.colorbar(contour, ax=axis, label="Along-track shift [km]")
    axis.set_xlabel("Drag coefficient")
    axis.set_ylabel("Density scale factor")
    axis.set_title("Drag sensitivity contour (12-orbit horizon)")
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_arguments(argv)
    ensure_output_directory(args.output_dir)
    run = load_summary(args.run_dir)
    long_run = regenerate_ground_track(args.config)

    plot_ground_tracks(
        run,
        long_run,
        args.output_dir / "ground_tracks_tehran.svg",
    )
    plot_orbital_planes(run, args.output_dir / "orbital_planes_3d.svg")
    plot_orbital_elements(
        args.run_dir / "orbital_elements.csv",
        args.output_dir / "orbital_elements_time_series.svg",
    )
    plot_relative_positions(run, args.output_dir / "relative_positions_snapshots.svg")
    plot_pairwise_distances(run, args.output_dir / "pairwise_distance_evolution.svg")
    plot_access_timeline(run, args.output_dir / "access_window_timeline.svg")
    plot_perturbation_drift(
        run,
        args.run_dir / "drag_dispersion.csv",
        args.output_dir / "perturbation_drift_components.svg",
    )
    plot_maintenance_delta_v(
        args.run_dir / "maintenance_summary.csv",
        args.output_dir / "maintenance_delta_v.svg",
    )
    plot_monte_carlo(
        args.run_dir / "injection_recovery.csv",
        args.output_dir / "monte_carlo_recovery.svg",
    )
    plot_analytical_vs_stk(
        run,
        args.run_dir / "stk" / "SAT_1_groundtrack.gt",
        args.output_dir / "analytical_vs_stk_groundtrack.svg",
    )
    plot_performance_metrics(run, args.output_dir / "performance_metrics.svg")
    plot_sensitivity_contour(
        args.run_dir / "drag_dispersion.csv",
        args.output_dir / "sensitivity_contours.svg",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
