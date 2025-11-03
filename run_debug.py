"""Debug CLI for running formation or scenario simulations with structured logging."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used only for static typing
    from sim.formation.triangle import TriangleFormationResult

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


CLASSICAL_ELEMENT_FIELDS = (
    "semi_major_axis_km",
    "eccentricity",
    "inclination_deg",
    "raan_deg",
    "argument_of_perigee_deg",
    "mean_anomaly_deg",
)

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

    csv_paths: MutableMapping[str, Path] = {}
    csv_paths["positions_m"] = _write_mapping_csv(
        output_directory / "positions_m.csv",
        times,
        satellite_ids,
        result.positions_m,
        ("x_m", "y_m", "z_m"),
    )
    csv_paths["velocities_mps"] = _write_mapping_csv(
        output_directory / "velocities_mps.csv",
        times,
        satellite_ids,
        result.velocities_mps,
        ("vx_mps", "vy_mps", "vz_mps"),
    )
    csv_paths["latitudes_rad"] = _write_mapping_csv(
        output_directory / "latitudes_rad.csv",
        times,
        satellite_ids,
        result.latitudes_rad,
        None,
    )
    csv_paths["longitudes_rad"] = _write_mapping_csv(
        output_directory / "longitudes_rad.csv",
        times,
        satellite_ids,
        result.longitudes_rad,
        None,
    )
    csv_paths["altitudes_m"] = _write_mapping_csv(
        output_directory / "altitudes_m.csv",
        times,
        satellite_ids,
        result.altitudes_m,
        None,
    )
    csv_paths["triangle_geometry"] = _write_triangle_geometry_csv(
        output_directory / "triangle_geometry.csv",
        times,
        result.triangle_area_m2,
        result.triangle_aspect_ratio,
        result.triangle_sides_m,
    )
    csv_paths["ground_ranges"] = _write_ground_ranges_csv(
        output_directory / "ground_ranges.csv",
        times,
        result.max_ground_distance_km,
        result.min_command_distance_km,
    )
    orbital_csv = _write_orbital_elements_csv(
        output_directory / "orbital_elements.csv",
        times,
        result.classical_elements,
    )
    csv_paths["orbital_elements"] = orbital_csv
    per_satellite_paths = _write_orbital_elements_per_satellite(
        output_directory / "orbital_elements",
        times,
        result.classical_elements,
    )

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

    return summary_lines


def _write_mapping_csv(
    path: Path,
    times: Sequence[datetime],
    satellite_ids: Sequence[str],
    data: Mapping[str, Sequence[Sequence[float]] | Sequence[float]],
    component_labels: Sequence[str] | None,
) -> Path:
    """Serialise mapping data keyed by satellite into a CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        header = ["time_utc"]
        if component_labels:
            for sat_id in satellite_ids:
                for label in component_labels:
                    header.append(f"{sat_id}_{label}")
        else:
            header.extend(satellite_ids)
        writer.writerow(header)

        for index, epoch in enumerate(times):
            row = [_format_time(epoch)]
            for sat_id in satellite_ids:
                sample = data[sat_id][index]
                if component_labels:
                    for component_index in range(len(component_labels)):
                        row.append(_format_number(sample[component_index]))
                else:
                    row.append(_format_number(sample))
            writer.writerow(row)
    return path


def _write_triangle_geometry_csv(
    path: Path,
    times: Sequence[datetime],
    areas_m2: Sequence[float],
    aspects: Sequence[float],
    sides_m: Sequence[Sequence[float]],
) -> Path:
    """Export triangle geometry diagnostics to CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time_utc",
                "triangle_area_m2",
                "triangle_aspect_ratio",
                "side_length_1_m",
                "side_length_2_m",
                "side_length_3_m",
            ]
        )
        for index, epoch in enumerate(times):
            row = [
                _format_time(epoch),
                _format_number(areas_m2[index]),
                _format_number(aspects[index]),
            ]
            side_samples = sides_m[index]
            for component in range(3):
                try:
                    value = side_samples[component]
                except (IndexError, TypeError):
                    value = float("nan")
                row.append(_format_number(value))
            writer.writerow(row)
    return path


def _write_ground_ranges_csv(
    path: Path,
    times: Sequence[datetime],
    max_ground_distance_km: Sequence[float],
    min_command_distance_km: Sequence[float],
) -> Path:
    """Serialise ground- and command-range diagnostics to CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time_utc",
                "max_ground_distance_km",
                "min_command_distance_km",
            ]
        )
        for index, epoch in enumerate(times):
            writer.writerow(
                [
                    _format_time(epoch),
                    _format_number(max_ground_distance_km[index]),
                    _format_number(min_command_distance_km[index]),
                ]
            )
    return path


def _write_orbital_elements_csv(
    path: Path,
    times: Sequence[datetime],
    series: Mapping[str, Mapping[str, Sequence[float]]],
) -> Path:
    """Serialise orbital-element histories into a consolidated CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        header = ["time_utc", "satellite_id", *CLASSICAL_ELEMENT_FIELDS]
        writer.writerow(header)
        for index, epoch in enumerate(times):
            timestamp = _format_time(epoch)
            for sat_id in sorted(series):
                elements = series.get(sat_id) or {}
                row = [timestamp, sat_id]
                for field in CLASSICAL_ELEMENT_FIELDS:
                    values = elements.get(field)
                    try:
                        sample = values[index]  # type: ignore[index]
                    except (TypeError, IndexError):
                        sample = float("nan")
                    row.append(_format_number(sample))
                writer.writerow(row)
    return path


def _write_orbital_elements_per_satellite(
    directory: Path,
    times: Sequence[datetime],
    series: Mapping[str, Mapping[str, Sequence[float]]],
) -> Mapping[str, Path]:
    """Write per-spacecraft orbital-element CSVs and return their paths."""

    directory.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for sat_id, elements in series.items():
        path = directory / f"{sat_id.lower().replace(' ', '_')}_orbital_elements.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["time_utc", *CLASSICAL_ELEMENT_FIELDS])
            for index, epoch in enumerate(times):
                row = [_format_time(epoch)]
                for field in CLASSICAL_ELEMENT_FIELDS:
                    values = elements.get(field)
                    try:
                        sample = values[index]  # type: ignore[index]
                    except (TypeError, IndexError):
                        sample = float("nan")
                    row.append(_format_number(sample))
                writer.writerow(row)
        paths[sat_id] = path
    return paths


def _format_time(value: datetime) -> str:
    """Render timestamps in a stable ISO 8601 format."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _format_number(value: float) -> str:
    """Convert numerical values to compact string form for CSV output."""

    return f"{float(value):.9g}"


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
