"""Generate deterministic and Monte Carlo visualisations for the locked Tehran pass.

This utility focuses on the authoritative evidence package stored under
``artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass_locked``.  It reads the
cross-track CSV catalogues and associated JSON summaries to construct
publication-ready SVG plots that describe how each spacecraft behaves
relative to the mission's primary and waiver limits.

The script emits three figures by default:

1. A deterministic time history of the great-circle cross-track distance
   for the leader and two deputies, including the formation centroid and
   compliance limits.
2. The fleet-relative cross-track separation sampled every ten seconds
   during the access window.
3. A Monte Carlo summary chart that contrasts the mean, standard
   deviation, and 95th-percentile absolute cross-track offsets at the
   evaluation epoch.

All figures are saved as SVG files within the run's ``plots`` directory to
respect the repository's artefact policy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PRIMARY_COLOUR = "#004b87"
DEPUTY_COLOURS = ["#009f81", "#f47920"]
CENTROID_COLOUR = "#6f42c1"
LIMIT_COLOUR_PRIMARY = "#d62728"
LIMIT_COLOUR_WAIVER = "#ffbf00"
RELATIVE_COLOUR = "#2ca02c"


def _load_deterministic_series(run_dir: Path) -> pd.DataFrame:
    """Return the deterministic cross-track history as a time-indexed frame."""

    csv_path = run_dir / "deterministic_cross_track.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Deterministic cross-track catalogue {csv_path} is missing."
        )
    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    dataframe = dataframe.rename(columns={"time_iso": "time_utc"})
    value_columns = [column for column in dataframe.columns if column != "time_utc"]
    dataframe[value_columns] = dataframe[value_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return dataframe.set_index("time_utc").sort_index()


def _load_relative_series(run_dir: Path) -> pd.DataFrame:
    """Return the fleet-relative cross-track history."""

    csv_path = run_dir / "relative_cross_track.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Relative cross-track catalogue {csv_path} is missing."
        )
    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    dataframe = dataframe.rename(columns={"time_iso": "time_utc"})
    dataframe["relative_cross_track_km"] = pd.to_numeric(
        dataframe["relative_cross_track_km"], errors="coerce"
    )
    return dataframe.set_index("time_utc").sort_index()


def _load_monte_carlo_summary(run_dir: Path) -> dict:
    """Return the Monte Carlo statistics ledger."""

    summary_path = run_dir / "monte_carlo_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"Monte Carlo summary file {summary_path} is missing."
        )
    with summary_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_deterministic_summary(run_dir: Path) -> dict:
    """Return the deterministic cross-track summary."""

    summary_path = run_dir / "deterministic_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"Deterministic summary file {summary_path} is missing."
        )
    with summary_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _ensure_plots_directory(run_dir: Path) -> Path:
    """Return the plots directory, creating it if required."""

    plots_dir = run_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    return plots_dir


def _format_time_axis(ax: plt.Axes) -> None:
    """Apply a consistent UTC formatter to the horizontal axis."""

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
    ax.grid(True, which="both", axis="both", linestyle="--", linewidth=0.5)


def _plot_deterministic_history(
    dataframe: pd.DataFrame,
    summary: dict,
    output_dir: Path,
) -> Path:
    """Plot the deterministic cross-track evolution for each spacecraft."""

    if dataframe.empty:
        raise ValueError("Deterministic cross-track dataframe is empty.")

    evaluation = summary["metrics"]["cross_track"]["evaluation"]
    evaluation_time = pd.to_datetime(evaluation["time_utc"], utc=True)
    primary_limit = float(summary["metrics"]["cross_track"]["primary_limit_km"])
    waiver_limit = float(summary["metrics"]["cross_track"]["waiver_limit_km"])

    vehicles = [column for column in dataframe.columns if column.startswith("FSAT")]  # type: ignore[arg-type]
    if not vehicles:
        raise ValueError("No spacecraft columns were found in the deterministic catalogue.")

    centroid = dataframe[vehicles].mean(axis=1)

    fig, ax = plt.subplots(figsize=(10, 6))
    colours = DEPUTY_COLOURS + [PRIMARY_COLOUR]
    for colour, vehicle in zip(colours, vehicles, strict=False):
        ax.plot(
            dataframe.index,
            dataframe[vehicle],
            label=vehicle,
            color=colour,
            linewidth=1.6,
        )
    ax.plot(
        dataframe.index,
        centroid,
        label="Centroid",
        color=CENTROID_COLOUR,
        linewidth=1.8,
        linestyle="-.",
    )

    ax.axhline(primary_limit, color=LIMIT_COLOUR_PRIMARY, linestyle=":", linewidth=1.2)
    ax.axhline(-primary_limit, color=LIMIT_COLOUR_PRIMARY, linestyle=":", linewidth=1.2)
    ax.axhline(waiver_limit, color=LIMIT_COLOUR_WAIVER, linestyle="--", linewidth=1.0)
    ax.axhline(-waiver_limit, color=LIMIT_COLOUR_WAIVER, linestyle="--", linewidth=1.0)
    ax.axvline(evaluation_time, color="black", linestyle="--", linewidth=1.0)

    ax.set_title("Deterministic cross-track geometry over Tehran")
    ax.set_ylabel("Cross-track distance to target (km)")
    ax.set_xlabel("UTC time on 2026-03-21")
    ax.legend(loc="upper right")
    _format_time_axis(ax)

    output_path = output_dir / "cross_track_deterministic.svg"
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    return output_path


def _plot_relative_history(dataframe: pd.DataFrame, output_dir: Path) -> Path:
    """Plot the fleet-relative cross-track separation."""

    if dataframe.empty:
        raise ValueError("Relative cross-track dataframe is empty.")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(
        dataframe.index,
        dataframe["relative_cross_track_km"],
        color=RELATIVE_COLOUR,
        linewidth=1.8,
    )
    ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
    ax.set_title("Fleet-relative cross-track separation during the access window")
    ax.set_ylabel("Relative cross-track (km)")
    ax.set_xlabel("UTC time on 2026-03-21")
    _format_time_axis(ax)

    output_path = output_dir / "cross_track_relative.svg"
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    return output_path


def _plot_monte_carlo_bars(summary: dict, output_dir: Path) -> Path:
    """Render a bar chart summarising Monte Carlo evaluation statistics."""

    stats = summary["evaluation_abs_cross_track_km"]
    centroid_stats = summary["centroid_abs_cross_track_km"]
    primary_limit = float(summary["cross_track_limits_km"]["primary"])
    waiver_limit = float(summary["cross_track_limits_km"]["waiver"])
    evaluation_time = pd.to_datetime(summary["evaluation_time_utc"], utc=True)

    vehicles = sorted(stats.keys())
    means = np.array([float(stats[vehicle]["mean"]) for vehicle in vehicles])
    stds = np.array([float(stats[vehicle]["std"]) for vehicle in vehicles])
    p95 = np.array([float(stats[vehicle]["p95"]) for vehicle in vehicles])

    indices = np.arange(len(vehicles))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(indices, means, color="#4c78a8", label="Mean")
    ax.errorbar(indices, means, yerr=stds, fmt="none", ecolor="black", capsize=6, label="±1σ")

    for bar, p95_value in zip(bars, p95, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            p95_value + 0.5,
            f"p95 = {p95_value:.2f} km",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.axhline(primary_limit, color=LIMIT_COLOUR_PRIMARY, linestyle=":", linewidth=1.2, label="Primary limit")
    ax.axhline(waiver_limit, color=LIMIT_COLOUR_WAIVER, linestyle="--", linewidth=1.0, label="Waiver limit")
    ax.axhline(
        float(centroid_stats["p95"]),
        color=CENTROID_COLOUR,
        linestyle="-.",
        linewidth=1.4,
        label="Centroid p95",
    )

    ax.set_xticks(indices, vehicles)
    ax.set_ylabel("Absolute cross-track at evaluation (km)")
    timestamp = evaluation_time.strftime("%Y-%m-%d %H:%M:%SZ")
    ax.set_title(
        "Monte Carlo cross-track dispersion at the evaluation epoch\n"
        f"1000 samples evaluated at {timestamp}"
    )
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", linewidth=0.5)

    output_path = output_dir / "cross_track_monte_carlo.svg"
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    return output_path


def generate_plots(run_directory: Path) -> Dict[str, Path]:
    """Generate all Tehran daily pass plots and return their locations."""

    deterministic_series = _load_deterministic_series(run_directory)
    relative_series = _load_relative_series(run_directory)
    monte_carlo_summary = _load_monte_carlo_summary(run_directory)
    deterministic_summary = _load_deterministic_summary(run_directory)

    plots_dir = _ensure_plots_directory(run_directory)

    outputs: Dict[str, Path] = {}
    outputs["deterministic"] = _plot_deterministic_history(
        deterministic_series, deterministic_summary, plots_dir
    )
    outputs["relative"] = _plot_relative_history(relative_series, plots_dir)
    outputs["monte_carlo"] = _plot_monte_carlo_bars(monte_carlo_summary, plots_dir)
    return outputs


def _parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render Tehran daily pass cross-track visualisations.",
    )
    parser.add_argument(
        "run_directory",
        type=Path,
        help="Path to the locked Tehran daily pass run directory.",
    )
    return parser.parse_args(args=args)


def main() -> Dict[str, Path]:
    """Entry point for the command-line interface."""

    namespace = _parse_args()
    outputs = generate_plots(namespace.run_directory)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return outputs


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
