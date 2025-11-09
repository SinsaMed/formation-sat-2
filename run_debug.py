"""Debug CLI for running formation or scenario simulations with structured logging."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used only for static typing
    from sim.formation.triangle import TriangleFormationResult

from sim.formation.triangle_artefacts import export_triangle_time_series
from tools.render_debug_plots import generate_visualisations as generate_debug_visualisations
from tools.generate_triangle_report import main as generate_triangle_report_main


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_TRIANGLE_CONFIG = PROJECT_ROOT / "config" / "scenarios" / "tehran_triangle.json"
DEFAULT_DEBUG_ROOT = PROJECT_ROOT / "artefacts" / "debug"
LOG_PATH = PROJECT_ROOT / "debug.txt"


logging.basicConfig(
    level=logging.DEBUG,
    filename=LOG_PATH,
    filemode="a",
    encoding="utf-8",
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    force=True,
)
_STREAM_HANDLER = logging.StreamHandler()
_STREAM_HANDLER.setLevel(logging.INFO)
_STREAM_HANDLER.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logging.getLogger().addHandler(_STREAM_HANDLER)
LOGGER = logging.getLogger("run_debug")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Run targeted debug simulations. Choose between the triangle formation "
            "model and the general scenario pipeline."
        )
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--triangle",
        action="store_true",
        help="Execute the Tehran triangle formation configuration.",
    )
    mode_group.add_argument(
        "--scenario",
        nargs="?",
        const="tehran_daily_pass",
        metavar="SCENARIO_ID",
        help=(
            "Execute the general scenario pipeline. Optionally provide a scenario "
            "identifier; defaults to 'tehran_daily_pass' when omitted."
        ),
    )
    parser.add_argument(
        "--triangle-config",
        type=Path,
        default=DEFAULT_TRIANGLE_CONFIG,
        help=(
            "Override the triangle formation configuration file path. The default "
            "uses the stored Tehran triangle scenario."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_DEBUG_ROOT,
        help="Directory under which timestamped debug artefacts are created.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    """Run the requested debug workflow and report key diagnostic metrics."""

    namespace = build_parser().parse_args(argv)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_directory = (namespace.output_root / timestamp).resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Artefacts will be stored in %s", output_directory)

    if namespace.triangle:
        summary_lines = _handle_triangle_run(namespace.triangle_config, output_directory)
    else:
        scenario_id = namespace.scenario or "tehran_daily_pass"
        summary_lines = _handle_scenario_run(scenario_id, output_directory)

    for line in summary_lines:
        print(line)
    return 0


def _handle_triangle_run(config_path: Path, output_directory: Path) -> Sequence[str]:
    """Execute the triangle simulation and export diagnostic CSV files."""

    from sim.formation.triangle import simulate_triangle_formation

    LOGGER.info("Running triangle formation from %s", config_path)
    result = simulate_triangle_formation(config_path, output_directory=output_directory)

    times = result.times
    satellite_ids = sorted(result.positions_m.keys())

    artefact_bundle = export_triangle_time_series(result, output_directory)
    csv_paths = artefact_bundle.csv_paths
    per_satellite_paths = artefact_bundle.per_satellite_csvs

    formation_window = _extract_mapping(result.metrics, "formation_window")
    ground_track = _extract_mapping(result.metrics, "ground_track")
    triangle_stats = _extract_mapping(result.metrics, "triangle")

    duration_s = float(formation_window.get("duration_s", 0.0))
    start_time = formation_window.get("start")
    end_time = formation_window.get("end")
    max_ground_distance = float(ground_track.get("max_ground_distance_km", 0.0))
    min_ground_distance = float(ground_track.get("min_ground_distance_km", 0.0))
    aspect_ratio_max = float(triangle_stats.get("aspect_ratio_max", 0.0))

    LOGGER.info(
        "Triangle simulation window %.1f s; ground distance %.1f–%.1f km.",
        duration_s,
        min_ground_distance,
        max_ground_distance,
    )

    summary = [
        f"Triangle formation debug artefacts: {output_directory}",
        f"  • positions_m CSV: {csv_paths['positions_m']}",
        f"  • velocities_mps CSV: {csv_paths['velocities_mps']}",
        f"  • latitudes_rad CSV: {csv_paths['latitudes_rad']}",
        f"  • longitudes_rad CSV: {csv_paths['longitudes_rad']}",
        f"  • altitudes_m CSV: {csv_paths['altitudes_m']}",
        f"  • triangle_geometry CSV: {csv_paths['triangle_geometry']}",
        f"  • ground_ranges CSV: {csv_paths['ground_ranges']}",
        f"  • orbital_elements CSV: {csv_paths['orbital_elements']}",
    ]
    if per_satellite_paths:
        summary.append("  • per-satellite orbital elements:")
        for sat_id, path in sorted(per_satellite_paths.items()):
            summary.append(f"      - {sat_id}: {path}")

    window_label = "formation window"
    if start_time and end_time:
        window_label = f"formation window ({start_time} → {end_time})"
    summary.extend(
        [
            f"Key metrics:",
            f"  - {window_label}: {duration_s:.1f} s",
            f"  - Max ground distance: {max_ground_distance:.1f} km",
            f"  - Min ground distance: {min_ground_distance:.1f} km",
            f"  - Peak aspect ratio: {aspect_ratio_max:.3f}",
        ]
    )

    # Generate plots using render_debug_plots.py
    LOGGER.info("Generating debug visualisations...")
    debug_plot_outputs = generate_debug_visualisations(output_directory)
    for label, artefact in debug_plot_outputs.items():
        if isinstance(artefact, dict):
            canonical = artefact.get("svg")
            if canonical is not None:
                LOGGER.info(f"Generated {label} visualisation at {canonical} (canonical SVG)")
            for fmt, path in artefact.items():
                if fmt == "svg":
                    continue
                LOGGER.info(f"Generated {label} visualisation at {path} ({fmt})")
        else:
            LOGGER.info(f"Generated {label} visualisation at {artefact}")

    # Generate plots using generate_triangle_report.py
    LOGGER.info("Generating triangle report plots...")
    import sys
    original_argv = sys.argv
    try:
        sys.argv = ['generate_triangle_report.py', '--run-dir', str(output_directory), '--config', str(config_path)]
        generate_triangle_report_main()
        LOGGER.info("Triangle report plots generated successfully.")
    except Exception as e:
        LOGGER.error(f"Failed to generate triangle report plots: {e}")
    finally:
        sys.argv = original_argv

    # Generate 14-day RGT ground track and plot
    LOGGER.info("Generating 14-day RGT ground track and plot...")
    import sys
    original_argv_rgt = sys.argv
    try:
        # Run propagate_long_duration.py
        propagate_argv = ['propagate_long_duration.py', '--config', str(config_path), '--output-dir', str(output_directory)]
        sys.argv = propagate_argv
        from tools.propagate_long_duration import main as propagate_long_duration_main
        propagate_long_duration_main()
        LOGGER.info("14-day RGT ground track data generated successfully.")

        # Run render_14day_ground_track.py
        plots_dir = output_directory / "plots"
        render_argv = ['render_14day_ground_track.py', '--input-csv', str(output_directory / "ground_track_14day.csv"), '--output-dir', str(plots_dir)]
        sys.argv = render_argv
        from tools.render_14day_ground_track import main as render_14day_ground_track_main
        render_14day_ground_track_main()
        LOGGER.info("14-day RGT ground track plot generated successfully.")

        summary.append(f"  • 14-day Ground Track CSV: {output_directory / 'ground_track_14day.csv'}")
        summary.append(f"  • 14-day Ground Track SVG: {plots_dir / '14day_ground_track.svg'}")

    except Exception as e:
        LOGGER.error(f"Failed to generate 14-day RGT ground track and plot: {e}")
    finally:
        sys.argv = original_argv_rgt

    return summary


def _handle_scenario_run(scenario_id: str, output_directory: Path) -> Sequence[str]:
    """Execute the general scenario pipeline and record the stage sequence."""

    from sim.scripts.run_scenario import run_scenario

    LOGGER.info("Running scenario pipeline for '%s'", scenario_id)
    summary = run_scenario(scenario_id, output_directory=output_directory)

    stage_sequence = list(summary.get("stage_sequence", []))
    if stage_sequence:
        listing = "\n".join(f"{index}. {name}" for index, name in enumerate(stage_sequence, start=1))
        LOGGER.debug("Scenario stage sequence:\n%s", listing)

    json_path = output_directory / "scenario_debug_summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    LOGGER.info("Scenario summary written to %s", json_path)

    metrics = _extract_mapping(summary, "metrics")
    node_count = float(metrics.get("node_count", 0.0))
    phase_count = float(metrics.get("phase_count", 0.0))
    total_contact = float(metrics.get("total_contact_duration_s", 0.0))
    orbital_delta = float(metrics.get("orbital_period_delta_s", 0.0))
    orbital_nominal = float(metrics.get("orbital_period_nominal_s", 0.0))

    LOGGER.info(
        "Scenario produced %.0f nodes, %.0f phases, %.1f s contact window.",
        node_count,
        phase_count,
        total_contact,
    )

    summary_lines = [
        f"Scenario pipeline debug artefacts: {output_directory}",
        f"  • summary JSON: {json_path}",
        "Key metrics:",
        f"  - Mission nodes: {node_count:.0f}",
        f"  - Mission phases: {phase_count:.0f}",
        f"  - Total contact duration: {total_contact:.1f} s",
        f"  - Nominal orbital period: {orbital_nominal:.1f} s",
        f"  - Perturbation delta: {orbital_delta:.3f} s",
    ]

    artefact_map = _extract_mapping(summary, "artefacts")
    scenario_plots = _extract_mapping(artefact_map, "scenario_plots")
    if scenario_plots:
        summary_lines.append("Generated plots:")
        for label, path in sorted(scenario_plots.items()):
            summary_lines.append(f"  - {label}: {path}")

    return summary_lines


def _extract_mapping(
    payload: Mapping[str, object], key: str
) -> Mapping[str, object]:
    """Safely extract a nested mapping from *payload*."""

    value = payload.get(key, {}) if isinstance(payload, Mapping) else {}
    if isinstance(value, Mapping):
        return value
    return {}


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
