"""Command-line entry point for the Tehran triangular-formation simulation.

The script provides a thin wrapper around :func:`sim.formation.simulate_triangle_formation`
so analysts can reproduce the ninety-second access window directly from the
terminal. In addition to generating the JSON summary, the command optionally
writes Systems Tool Kit (STK 11.2) artefacts that may be imported for
visualisation and further analysis.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

from sim.formation import simulate_triangle_formation

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "scenarios" / "tehran_triangle.json"


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
        help="Directory in which to write the simulation summary and STK export.",
    )
    return parser.parse_args(args)


def main(args: Optional[Iterable[str]] = None) -> int:
    namespace = parse_args(args)
    result = simulate_triangle_formation(namespace.config, output_directory=namespace.output_dir)

    window = result.metrics["formation_window"]
    duration = window.get("duration_s", 0.0)
    start = window.get("start")
    end = window.get("end")
    print(
        "Formation window {:.1f} s centred over Tehran. Start: {} End: {}".format(
            duration, start or "n/a", end or "n/a"
        )
    )

    summary_path = result.artefacts.get("summary_path")
    if summary_path:
        print(f"Summary written to {summary_path}.")
    stk_dir = result.artefacts.get("stk_directory")
    if stk_dir:
        print(f"STK export available under {stk_dir}.")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI tests.
    raise SystemExit(main())

