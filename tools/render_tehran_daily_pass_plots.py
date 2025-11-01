"""Render canonical SVG plots for the locked Tehran daily-pass scenario.

The locked daily-pass alignment campaign archives deterministic and
Monte-Carlo cross-track catalogues together with the STK export suite.  This
utility consumes the textual artefacts already present in the run directory and
generates publication-grade SVG graphics that describe the behaviour of all
three spacecraft.  The figures are intended to support mission reviews and
presentation material without regenerating the underlying simulation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLOT_COLORS = {
    "FSAT-DP1": "#1b9e77",
    "FSAT-DP2": "#d95f02",
    "FSAT-LDR": "#7570b3",
    "centroid": "#4d4d4d",
}


def _load_deterministic_cross_track(run_directory: Path) -> pd.DataFrame:
    csv_path = run_directory / "deterministic_cross_track.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Deterministic cross-track catalogue not found at {csv_path}."
        )

    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    dataframe = dataframe.rename(columns={"time_iso": "time_utc"})
    return dataframe.set_index("time_utc").sort_index()


def _load_relative_cross_track(run_directory: Path) -> pd.DataFrame:
    csv_path = run_directory / "relative_cross_track.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Relative cross-track catalogue not found at {csv_path}."
        )

    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    dataframe = dataframe.rename(columns={"time_iso": "time_utc"})
    return dataframe.set_index("time_utc").sort_index()


def _load_deterministic_summary(run_directory: Path) -> dict:
    summary_path = run_directory / "deterministic_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"Deterministic summary JSON not found at {summary_path}."
        )

    with summary_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_monte_carlo_summary(run_directory: Path) -> pd.DataFrame:
    csv_path = run_directory / "monte_carlo_cross_track.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Monte Carlo catalogue not found at {csv_path}."
        )

    dataframe = pd.read_csv(csv_path)
    return dataframe.set_index("vehicle_id")


def _ensure_output_directory(run_directory: Path) -> Path:
    output_dir = run_directory / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _plot_deterministic_cross_track(
    cross_track: pd.DataFrame,
    summary: dict,
    output_dir: Path,
) -> tuple[Path, Path]:
    vehicles = [
        column
        for column in cross_track.columns
        if column.startswith("FSAT-")
    ]
    if not vehicles:
        raise ValueError("No spacecraft columns were found in the deterministic table.")

    evaluation_time = pd.to_datetime(
        summary["metrics"]["cross_track"]["evaluation"]["time_utc"], utc=True
    )
    primary_limit = float(summary["metrics"]["cross_track"]["primary_limit_km"])
    waiver_limit = float(summary["metrics"]["cross_track"]["waiver_limit_km"])

    centroid = cross_track[vehicles].mean(axis=1)

    signed_path = output_dir / "deterministic_cross_track_signed.svg"
    absolute_path = output_dir / "deterministic_cross_track_absolute.svg"

    time_index = cross_track.index

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for vehicle in vehicles:
        ax.plot(
            time_index,
            cross_track[vehicle],
            label=vehicle,
            color=PLOT_COLORS.get(vehicle, None),
        )
    ax.plot(
        time_index,
        centroid,
        label="Centroid",
        color=PLOT_COLORS["centroid"],
        linestyle="--",
    )
    ax.axhline(0.0, color="#333333", linewidth=0.8)
    for limit, style in ((primary_limit, "-"), (waiver_limit, ":")):
        ax.axhline(limit, color="#999999", linestyle=style, linewidth=0.8)
        ax.axhline(-limit, color="#999999", linestyle=style, linewidth=0.8)
    ax.axvline(evaluation_time, color="#666666", linestyle="--", linewidth=0.9)
    ax.set_ylabel("Cross-track offset (km)")
    ax.set_xlabel("UTC time")
    ax.set_title("Deterministic cross-track geometry")
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(signed_path, format="svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for vehicle in vehicles:
        ax.plot(
            time_index,
            cross_track[vehicle].abs(),
            label=vehicle,
            color=PLOT_COLORS.get(vehicle, None),
        )
    ax.plot(
        time_index,
        centroid.abs(),
        label="Centroid",
        color=PLOT_COLORS["centroid"],
        linestyle="--",
    )
    for limit, style in ((primary_limit, "-"), (waiver_limit, ":")):
        ax.axhline(limit, color="#999999", linestyle=style, linewidth=0.8)
    ax.axvline(evaluation_time, color="#666666", linestyle="--", linewidth=0.9)
    ax.set_ylabel("Absolute cross-track offset (km)")
    ax.set_xlabel("UTC time")
    ax.set_title("Deterministic absolute cross-track geometry")
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(absolute_path, format="svg")
    plt.close(fig)

    return signed_path, absolute_path


def _plot_relative_cross_track(
    relative: pd.DataFrame, summary: dict, output_dir: Path
) -> Path:
    evaluation_time = pd.to_datetime(
        summary["metrics"]["cross_track"]["evaluation"]["time_utc"], utc=True
    )

    fig, ax = plt.subplots(figsize=(8, 4.0))
    ax.plot(
        relative.index,
        relative["relative_cross_track_km"],
        color="#e7298a",
        label="Plane separation",
    )
    ax.plot(
        relative.index,
        relative["relative_cross_track_km"].abs(),
        color="#66a61e",
        linestyle="--",
        label="Absolute separation",
    )
    ax.axvline(evaluation_time, color="#666666", linestyle="--", linewidth=0.9)
    ax.set_ylabel("Cross-track separation (km)")
    ax.set_xlabel("UTC time")
    ax.set_title("Relative cross-track alignment between planes")
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()

    output_path = output_dir / "relative_cross_track.svg"
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    return output_path


def _plot_monte_carlo_metrics(summary: pd.DataFrame, output_dir: Path) -> Path:
    vehicles = [identifier for identifier in summary.index if identifier.startswith("FSAT-")]
    if not vehicles:
        raise ValueError("Monte Carlo table does not contain spacecraft entries.")

    min_abs = summary.loc[vehicles, "min_abs_cross_track_km_p95"]
    max_abs = summary.loc[vehicles, "max_abs_cross_track_km_p95"]

    indices = np.arange(len(vehicles))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.0))
    ax.bar(indices - width / 2, min_abs, width=width, label="Minimum |x| p95")
    ax.bar(indices + width / 2, max_abs, width=width, label="Maximum |x| p95")
    ax.set_xticks(indices)
    ax.set_xticklabels(vehicles)
    ax.set_ylabel("Cross-track magnitude (km)")
    ax.set_title("Monte Carlo cross-track dispersion (95th percentile)")
    ax.legend(loc="upper left")
    fig.tight_layout()

    output_path = output_dir / "monte_carlo_cross_track_p95.svg"
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    return output_path


def render_daily_pass_plots(run_directory: Path) -> dict[str, Path | tuple[Path, Path]]:
    cross_track = _load_deterministic_cross_track(run_directory)
    relative = _load_relative_cross_track(run_directory)
    summary = _load_deterministic_summary(run_directory)
    monte_carlo = _load_monte_carlo_summary(run_directory)

    output_dir = _ensure_output_directory(run_directory)

    signed, absolute = _plot_deterministic_cross_track(cross_track, summary, output_dir)
    relative_plot = _plot_relative_cross_track(relative, summary, output_dir)
    monte_carlo_plot = _plot_monte_carlo_metrics(monte_carlo, output_dir)

    return {
        "deterministic_cross_track": (signed, absolute),
        "relative_cross_track": relative_plot,
        "monte_carlo_cross_track": monte_carlo_plot,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render deterministic and Monte Carlo cross-track plots for the locked Tehran "
            "daily-pass alignment run."
        )
    )
    parser.add_argument(
        "run_directory",
        type=Path,
        help=(
            "Path to the scenario artefact directory (e.g. "
            "artefacts/run_20251020_1900Z_tehran_daily_pass_locked)."
        ),
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    namespace = build_parser().parse_args(argv)
    run_directory = namespace.run_directory
    if not run_directory.exists():
        raise FileNotFoundError(f"Run directory {run_directory} does not exist.")

    outputs = render_daily_pass_plots(run_directory)
    for label, artefact in outputs.items():
        if isinstance(artefact, tuple):
            for variant in artefact:
                print(f"Generated {label} plot at {variant}")
        else:
            print(f"Generated {label} plot at {artefact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
