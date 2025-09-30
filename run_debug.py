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
    ]

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
