"""Generate SVG visualisations for scenario pipeline artefacts.

This module reads the deterministic and Monte Carlo exports produced by
``sim.scripts.run_scenario`` when an ``output_directory`` is provided.
It assembles briefing-ready time-series and statistical plots so that
scenario runs executed through either ``run_debug.py`` or the web
application expose the same level of diagnostic coverage as the
triangle-specific workflows.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

LOGGER = logging.getLogger(__name__)


DEFAULT_PLOT_DIRNAME = "plots"
CROSS_TRACK_CSV = "deterministic_cross_track.csv"
ORBITAL_ELEMENTS_CSV = "deterministic_orbital_elements.csv"
MONTE_CARLO_CSV = "monte_carlo_cross_track.csv"
RELATIVE_CSV = "relative_cross_track.csv"


def generate_visualisations(run_directory: Path) -> Dict[str, str]:
    """Create diagnostic scenario plots under *run_directory*.

    Parameters
    ----------
    run_directory:
        Root directory containing scenario artefacts such as
        ``deterministic_cross_track.csv``.  The function writes SVG plots
        into the ``plots`` subdirectory and returns their absolute paths.

    Returns
    -------
    Dict[str, str]
        Mapping from descriptive identifiers to the generated plot paths.
    """

    plot_directory = run_directory / DEFAULT_PLOT_DIRNAME
    plot_directory.mkdir(parents=True, exist_ok=True)

    outputs: Dict[str, str] = {}

    try:
        cross_track_path = _plot_cross_track_series(
            run_directory / CROSS_TRACK_CSV, plot_directory
        )
    except FileNotFoundError:
        LOGGER.warning("Cross-track CSV %s not found; skipping time-series plot.", CROSS_TRACK_CSV)
    else:
        if cross_track_path:
            outputs["deterministic_cross_track_svg"] = str(cross_track_path)

    try:
        orbital_path = _plot_orbital_elements(
            run_directory / ORBITAL_ELEMENTS_CSV, plot_directory
        )
    except FileNotFoundError:
        LOGGER.warning(
            "Orbital elements CSV %s not found; skipping orbital trend plot.",
            ORBITAL_ELEMENTS_CSV,
        )
    else:
        if orbital_path:
            outputs["orbital_elements_svg"] = str(orbital_path)

    try:
        monte_carlo_path = _plot_monte_carlo_statistics(
            run_directory / MONTE_CARLO_CSV, plot_directory
        )
    except FileNotFoundError:
        LOGGER.warning(
            "Monte Carlo CSV %s not found; skipping dispersion summary plot.",
            MONTE_CARLO_CSV,
        )
    else:
        if monte_carlo_path:
            outputs["monte_carlo_statistics_svg"] = str(monte_carlo_path)

    try:
        relative_path = _plot_relative_cross_track(
            run_directory / RELATIVE_CSV, plot_directory
        )
    except FileNotFoundError:
        LOGGER.info(
            "Relative cross-track CSV %s not found; skipping differential plot.",
            RELATIVE_CSV,
        )
    else:
        if relative_path:
            outputs["relative_cross_track_svg"] = str(relative_path)

    return outputs


def _plot_cross_track_series(csv_path: Path, plot_directory: Path) -> Path | None:
    """Render deterministic cross-track offsets as a time series."""

    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    vehicle_columns = [column for column in dataframe.columns if column != "time_iso"]
    if not vehicle_columns:
        LOGGER.warning("Cross-track CSV %s does not expose vehicle columns.", csv_path)
        return None

    figure, axis = plt.subplots(figsize=(8.0, 4.8))
    for column in vehicle_columns:
        axis.plot(
            dataframe["time_iso"],
            dataframe[column],
            label=column,
            linewidth=1.6,
        )

    axis.set_title("Deterministic cross-track offsets")
    axis.set_xlabel("UTC time")
    axis.set_ylabel("Cross-track offset (km)")
    axis.legend(loc="upper right")
    axis.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    figure.autofmt_xdate()

    output_path = plot_directory / "deterministic_cross_track.svg"
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)
    return output_path


def _plot_orbital_elements(csv_path: Path, plot_directory: Path) -> Path | None:
    """Render key orbital-element trends for each spacecraft."""

    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    if dataframe.empty:
        LOGGER.warning("Orbital-element CSV %s is empty.", csv_path)
        return None

    required_fields = [
        "semi_major_axis_km",
        "inclination_deg",
        "raan_deg",
    ]
    available = [column for column in required_fields if column in dataframe.columns]
    if not available:
        LOGGER.warning("Orbital-element CSV %s lacks required fields.", csv_path)
        return None

    satellites = sorted(dataframe["satellite_id"].dropna().unique())
    if not satellites:
        LOGGER.warning("Orbital-element CSV %s lacks satellite identifiers.", csv_path)
        return None

    figure, axes = plt.subplots(len(available), 1, figsize=(8.0, 3.2 * len(available)), sharex=True)
    if len(available) == 1:
        axes = [axes]

    for axis, field in zip(axes, available):
        for satellite in satellites:
            subset = dataframe[dataframe["satellite_id"] == satellite]
            if subset.empty:
                continue
            axis.plot(
                subset["time_iso"],
                subset[field],
                label=satellite,
                linewidth=1.4,
            )
        axis.set_ylabel(field.replace("_", " "))
        axis.grid(True, linestyle=":", linewidth=0.5, alpha=0.7)
    axes[-1].set_xlabel("UTC time")
    axes[0].legend(loc="best")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    figure.autofmt_xdate()
    figure.suptitle("Deterministic orbital-element evolution", y=0.98)

    output_path = plot_directory / "orbital_elements.svg"
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    figure.savefig(output_path, format="svg")
    plt.close(figure)
    return output_path


def _plot_monte_carlo_statistics(csv_path: Path, plot_directory: Path) -> Path | None:
    """Render Monte Carlo dispersion statistics as comparative bars."""

    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    dataframe = pd.read_csv(csv_path)
    if dataframe.empty:
        LOGGER.warning("Monte Carlo CSV %s is empty.", csv_path)
        return None

    if "vehicle_id" not in dataframe.columns:
        LOGGER.warning("Monte Carlo CSV %s is missing vehicle identifiers.", csv_path)
        return None

    if "max_abs_cross_track_km_p95" not in dataframe.columns:
        LOGGER.warning(
            "Monte Carlo CSV %s lacks the 'max_abs_cross_track_km_p95' column.",
            csv_path,
        )
        return None

    dataframe = dataframe.sort_values("vehicle_id")
    figure, axis = plt.subplots(figsize=(8.0, 4.8))
    axis.bar(
        dataframe["vehicle_id"],
        dataframe["max_abs_cross_track_km_p95"],
        color="#1f77b4",
    )

    axis.set_title("Monte Carlo cross-track dispersion (95th percentile)")
    axis.set_xlabel("Vehicle identifier")
    axis.set_ylabel("Cross-track offset (km)")
    axis.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.6)

    output_path = plot_directory / "monte_carlo_cross_track.svg"
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)
    return output_path


def _plot_relative_cross_track(csv_path: Path, plot_directory: Path) -> Path | None:
    """Render differential cross-track offsets between spacecraft planes."""

    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    dataframe = pd.read_csv(csv_path, parse_dates=["time_iso"])
    columns = [column for column in dataframe.columns if column != "time_iso"]
    if not columns:
        LOGGER.info("Relative cross-track CSV %s is empty; no plot generated.", csv_path)
        return None

    figure, axis = plt.subplots(figsize=(8.0, 4.0))
    for column in columns:
        axis.plot(
            dataframe["time_iso"],
            dataframe[column],
            label=column,
            linewidth=1.5,
        )

    axis.set_title("Relative cross-track separation")
    axis.set_xlabel("UTC time")
    axis.set_ylabel("Offset (km)")
    axis.legend(loc="upper right")
    axis.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    figure.autofmt_xdate()

    output_path = plot_directory / "relative_cross_track.svg"
    figure.tight_layout()
    figure.savefig(output_path, format="svg")
    plt.close(figure)
    return output_path


def _build_argument_parser() -> argparse.ArgumentParser:
    """Return the command-line parser for the standalone utility."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate SVG scenario diagnostics by reading the CSV artefacts "
            "produced by sim.scripts.run_scenario."
        )
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Directory containing the scenario CSV artefacts.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity for diagnostic output.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point providing ``python -m tools.render_scenario_plots`` execution."""

    namespace = _build_argument_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, namespace.log_level))

    outputs = generate_visualisations(namespace.run_dir)
    if outputs:
        LOGGER.info("Generated %d scenario plots under %s.", len(outputs), namespace.run_dir)
        for name, path in outputs.items():
            LOGGER.info("  %s -> %s", name, path)
    else:
        LOGGER.warning("No scenario plots generated for %s.", namespace.run_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI
    raise SystemExit(main())
