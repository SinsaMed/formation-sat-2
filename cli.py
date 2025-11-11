"""Main command-line interface for the formation-sat project."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence, TYPE_CHECKING

# --- Project-wide constants ---
PROJECT_ROOT = Path(__file__).resolve().parent

if TYPE_CHECKING:  # pragma: no cover - used only for static typing
    from sim.formation.triangle import TriangleFormationResult

# --- Helper Functions ---

def _resolve_output_directory(
    candidate: Optional[Path], default_root: Path, timestamp_format: str = "run_%Y%m%d_%H%MZ"
) -> Path:
    """Resolves and creates a unique, timestamped output directory."""
    if candidate is None:
        timestamp = datetime.now(timezone.utc).strftime(timestamp_format)
        output_dir = default_root / timestamp
    else:
        output_dir = candidate
        if not output_dir.is_absolute():
            output_dir = (PROJECT_ROOT / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _resolve_configuration_path(config_path: Path) -> Path:
    """Resolves a configuration path, preferring an absolute path if one exists."""
    if config_path.is_absolute():
        return config_path
    candidate = (PROJECT_ROOT / config_path).resolve()
    return candidate if candidate.exists() else config_path


# --- Triangle Simulation Logic (from sim/scripts/run_triangle.py) ---

DEFAULT_TRIANGLE_CONFIG = PROJECT_ROOT / "config" / "scenarios" / "tehran_triangle.json"
DEFAULT_TRIANGLE_OUTPUT_ROOT = PROJECT_ROOT / "artefacts" / "triangle"

def _safe_generate_debug_plots(output_dir: Path) -> Mapping[str, object]:
    """Safely generates debug visualisations, catching exceptions."""
    from tools.render_debug_plots import generate_visualisations
    try:
        return generate_visualisations(output_dir)
    except Exception as exc:
        print(f"Warning: failed to generate debug visualisations: {exc}")
        return {}

def _safe_generate_triangle_report(output_dir: Path, config_path: Path) -> None:
    """Safely generates the triangle report, catching exceptions."""
    from tools.generate_triangle_report import main as generate_triangle_report_main
    argv = ["--run-dir", str(output_dir)]
    if config_path.exists():
        argv.extend(["--config", str(config_path)])
    try:
        generate_triangle_report_main(argv)
    except Exception as exc:
        print(f"Warning: failed to generate triangle report plots: {exc}")

def run_triangle_simulation(args: argparse.Namespace) -> int:
    """Main function for the 'triangle' command."""
    from sim.formation import simulate_triangle_formation
    from sim.formation.triangle_artefacts import export_triangle_time_series

    output_dir = _resolve_output_directory(args.output_dir, DEFAULT_TRIANGLE_OUTPUT_ROOT)
    config_path = _resolve_configuration_path(args.config)
    
    # Load configuration
    with open(config_path, "r") as f:
        config = json.load(f)

    # Override duration if provided via CLI
    if args.duration_days is not None:
        config.setdefault("formation", {})["duration_s"] = args.duration_days * 86400.0
    
    result = simulate_triangle_formation(config, output_directory=output_dir)

    csv_bundle = export_triangle_time_series(result, output_dir)
    debug_outputs = _safe_generate_debug_plots(output_dir)
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
    # (The rest of the print statements from the original script can be added here if desired)
    return 0

# --- Debug Simulation Logic (from run_debug.py) ---

DEFAULT_DEBUG_ROOT = PROJECT_ROOT / "artefacts" / "debug"
LOG_PATH = PROJECT_ROOT / "debug.txt"

def setup_debug_logging():
    """Configures logging for the debug command."""
    logging.basicConfig(
        level=logging.DEBUG,
        filename=LOG_PATH,
        filemode="a",
        encoding="utf-8",
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.getLogger().addHandler(stream_handler)
    return logging.getLogger("cli_debug")

def run_debug_simulation(args: argparse.Namespace) -> int:
    """Main function for the 'debug' command."""
    from sim.formation import simulate_triangle_formation
    from sim.formation.triangle_artefacts import export_triangle_time_series
    
    logger = setup_debug_logging()
    
    output_dir = _resolve_output_directory(
        args.output_root, DEFAULT_DEBUG_ROOT, timestamp_format="%Y%m%dT%H%M%SZ"
    )
    logger.info("Artefacts will be stored in %s", output_dir)

    config_path = _resolve_configuration_path(args.triangle_config)
    logger.info("Running triangle formation from %s", config_path)
    
    # Load configuration
    with open(config_path, "r") as f:
        config = json.load(f)

    # Override duration if provided via CLI
    if args.duration_days is not None:
        config.setdefault("formation", {})["duration_s"] = args.duration_days * 86400.0

    result = simulate_triangle_formation(config, output_directory=output_dir)
    export_triangle_time_series(result, output_dir)

    window = result.metrics.get("formation_window", {})
    duration = float(window.get("duration_s", 0.0)) if isinstance(window, Mapping) else 0.0
    print(f"Debug run complete. Formation window: {duration:.1f}s. Artefacts in {output_dir}")
    print(f"See {LOG_PATH} for detailed logs.")
    return 0

# --- Stub Simulation Logic (from tools/run_simulation_stub.py) ---

DEFAULT_STUB_OUTPUT_ROOT = PROJECT_ROOT / "artefacts" / "plots"

def _stub_synthesise_outline(samples: int = 361) -> tuple[np.ndarray, np.ndarray]:
    """Creates a simple relative motion envelope for the formation."""
    import numpy as np
    angles = np.linspace(0.0, 2.0 * np.pi, samples)
    modulation = 1.0 + 0.05 * np.cos(3.0 * angles)
    return modulation * np.cos(angles), modulation * np.sin(angles)

def _stub_render_plot(output_dir: Path) -> Path:
    """Renders the placeholder formation plot."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x_track, y_track = _stub_synthesise_outline()
    figure, axis = plt.subplots(figsize=(6, 6))
    axis.plot(x_track, y_track, label="Relative motion envelope", color="#003f5c")
    axis.set_title("Nominal triangular formation envelope")
    axis.set_xlabel("Along-track offset [km]")
    axis.set_ylabel("Cross-track offset [km]")
    axis.set_aspect("equal", adjustable="box")
    axis.grid(True, linestyle="--", linewidth=0.5)
    axis.legend()

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "formation_outline.png"
    figure.savefig(image_path, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return image_path

def _stub_write_metadata(output_dir: Path, artefacts: Iterable[Path]) -> Path:
    """Persists metadata describing the generated stub artefacts."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record = {
        "generated_at": timestamp.replace("+00:00", "Z"),
        "artefacts": [str(path.name) for path in artefacts],
        "status": "Stub simulation executed successfully.",
        "notes": "Placeholder products illustrating simulation outputs.",
    }
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return metadata_path

def run_stub_simulation(args: argparse.Namespace) -> int:
    """Main function for the 'stub' command."""
    output_dir = _resolve_output_directory(args.output_dir, DEFAULT_STUB_OUTPUT_ROOT)
    plot_path = _stub_render_plot(output_dir)
    metadata_path = _stub_write_metadata(output_dir, [plot_path])
    print(f"Generated stub artefacts: {plot_path} and {metadata_path}.")
    return 0

# --- Main CLI Parser ---

def main(argv: Iterable[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Command-line interface for the formation-sat project."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Triangle command ---
    parser_triangle = subparsers.add_parser(
        "triangle", help="Run the full Tehran triangle formation simulation."
    )
    parser_triangle.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_TRIANGLE_CONFIG,
        help="Path to the triangle formation configuration file.",
    )
    parser_triangle.add_argument(
        "--output-dir",
        type=Path,
        help="Directory in which to write simulation artefacts.",
    )
    parser_triangle.add_argument(
        "--duration-days",
        type=float,
        help="Override the simulation duration in days. Will be converted to seconds.",
    )
    parser_triangle.set_defaults(func=run_triangle_simulation)

    # --- Debug command ---
    parser_debug = subparsers.add_parser(
        "debug", help="Run a debug version of the triangle simulation with verbose logging."
    )
    parser_debug.add_argument(
        "--triangle-config",
        type=Path,
        default=DEFAULT_TRIANGLE_CONFIG,
        help="Override the triangle formation configuration file path.",
    )
    parser_debug.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_DEBUG_ROOT,
        help="Directory under which timestamped debug artefacts are created.",
    )
    parser_debug.add_argument(
        "--duration-days",
        type=float,
        help="Override the simulation duration in days. Will be converted to seconds.",
    )
    parser_debug.set_defaults(func=run_debug_simulation)

    # --- Stub command ---
    parser_stub = subparsers.add_parser(
        "stub", help="Generate placeholder simulation artefacts and verify interfaces."
    )
    parser_stub.add_argument(
        "--output-dir",
        type=Path,
        help="Directory in which to store generated artefacts.",
    )
    parser_stub.set_defaults(func=run_stub_simulation)

    # --- Parse args and call function ---
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
