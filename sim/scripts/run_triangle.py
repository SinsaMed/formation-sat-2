"""Command-line entry point for the Tehran triangular-formation simulation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Optional

from sim.formation import simulate_triangle_formation
from sim.formation.triangle_artefacts import export_triangle_time_series
from tools.generate_triangle_report import main as generate_triangle_report_main
from tools.render_debug_plots import generate_visualisations as generate_debug_visualisations

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "scenarios" / "tehran_triangle.json"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "artefacts" / "triangle"


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the triangle formation configuration file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory in which to write simulation artefacts.",
    )
    parser.add_argument(
        "--extended-days",
        type=float,
        help="Extend the formation propagation horizon to the specified number of days.",
    )
    parser.add_argument(
        "--time-step-s",
        type=float,
        help="Override the formation propagation time step in seconds.",
    )
    return parser.parse_args(args)


def main(args: Optional[Iterable[str]] = None) -> int:
    namespace = parse_args(args)

    output_dir = _resolve_output_directory(namespace.output_dir)
    result = simulate_triangle_formation(
        namespace.config,
        output_directory=output_dir,
        extended_days=namespace.extended_days,
        sample_step_s=namespace.time_step_s,
    )

    csv_bundle = export_triangle_time_series(result, output_dir)
    debug_outputs = _safe_generate_debug_plots(output_dir)
    config_path = _resolve_configuration_path(namespace.config)
    _safe_generate_triangle_report(output_dir, config_path)

    window = result.metrics.get("formation_window", {})
    duration = float(window.get("duration_s", 0.0)) if isinstance(window, Mapping) else 0.0
    start = window.get("start") if isinstance(window, Mapping) else None
    end = window.get("end") if isinstance(window, Mapping) else None
    print(
        "Formation window {:.1f} s centred over Tehran. Start: {} End: {}".format(
            duration, start or "n/a", end or "n/a"
        )
    )

    print(f"Artefacts written to {output_dir}")
    for label in (
        "positions_m",
        "velocities_mps",
        "latitudes_rad",
        "longitudes_rad",
        "altitudes_m",
        "triangle_geometry",
        "ground_ranges",
        "orbital_elements",
    ):
        path = csv_bundle.csv_paths.get(label)
        if path is not None:
            print(f"  • {label} CSV: {path}")

    if csv_bundle.per_satellite_csvs:
        print("  • per-satellite orbital elements:")
        for sat_id, path in sorted(csv_bundle.per_satellite_csvs.items()):
            print(f"      - {sat_id}: {path}")

    artefacts = result.artefacts if isinstance(result.artefacts, Mapping) else {}
    summary_path = artefacts.get("summary_path")
    if summary_path:
        print(f"  • triangle_summary.json: {summary_path}")
    stk_dir = artefacts.get("stk_directory")
    if stk_dir:
        print(f"  • STK export directory: {stk_dir}")
    for key, label in (
        ("maintenance_csv", "maintenance summary"),
        ("command_windows_csv", "command windows"),
        ("injection_recovery_csv", "injection recovery samples"),
        ("drag_dispersion_csv", "drag dispersion samples"),
    ):
        path = artefacts.get(key)
        if path:
            print(f"  • {label}: {path}")

    if debug_outputs:
        print("  • debug plots:")
        for label, produced in sorted(debug_outputs.items()):
            if isinstance(produced, Mapping):
                svg_path = produced.get("svg")
                if svg_path:
                    print(f"      - {label} (svg): {svg_path}")
                for fmt, path in sorted(produced.items()):
                    if fmt == "svg":
                        continue
                    print(f"      - {label} ({fmt}): {path}")
            else:
                print(f"      - {label}: {produced}")

    return 0


def _resolve_output_directory(candidate: Optional[Path]) -> Path:
    if candidate is None:
        timestamp = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%MZ")
        output_dir = DEFAULT_OUTPUT_ROOT / timestamp
    else:
        output_dir = candidate
        if not output_dir.is_absolute():
            output_dir = (PROJECT_ROOT / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _resolve_configuration_path(config_path: Path) -> Path:
    if config_path.is_absolute():
        return config_path
    candidate = (PROJECT_ROOT / config_path).resolve()
    return candidate if candidate.exists() else config_path


def _safe_generate_debug_plots(output_dir: Path) -> Mapping[str, object]:
    try:
        return generate_debug_visualisations(output_dir)
    except Exception as exc:  # pragma: no cover - defensive logging only
        print(f"Warning: failed to generate debug visualisations: {exc}")
        return {}


def _safe_generate_triangle_report(output_dir: Path, config_path: Path) -> None:
    argv = ["--run-dir", str(output_dir)]
    if config_path.exists():
        argv.extend(["--config", str(config_path)])
    try:
        generate_triangle_report_main(argv)
    except Exception as exc:  # pragma: no cover - defensive logging only
        print(f"Warning: failed to generate triangle report plots: {exc}")


if __name__ == "__main__":  # pragma: no cover - exercised via CLI tests.
    raise SystemExit(main())
