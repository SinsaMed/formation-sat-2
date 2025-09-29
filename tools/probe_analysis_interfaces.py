"""Probe baseline and metric extraction interfaces for CI visibility."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sim.scripts import baseline_generation, metric_extraction


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="config/pending.yml",
        help="Configuration artefact placeholder passed to the interfaces.",
    )
    return parser.parse_args(args)


def probe_baseline(config: str) -> str:
    """Attempt to generate a baseline product and report the status."""

    try:
        baseline_generation.generate_baseline(config)
    except NotImplementedError as exc:  # pragma: no cover - explicit placeholder reporting.
        return f"Baseline generation pending implementation: {exc}"
    return "Baseline generation completed without raising NotImplementedError."


def probe_metrics() -> str:
    """Attempt to extract metrics and report the status."""

    try:
        metric_extraction.extract_metrics({})
    except NotImplementedError as exc:  # pragma: no cover - explicit placeholder reporting.
        return f"Metric extraction pending implementation: {exc}"
    return "Metric extraction completed without raising NotImplementedError."


def main(args: Iterable[str] | None = None) -> int:
    """Entrypoint used by automation wrappers."""

    namespace = parse_args(args)
    baseline_status = probe_baseline(namespace.config)
    metric_status = probe_metrics()
    print(baseline_status)
    print(metric_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
