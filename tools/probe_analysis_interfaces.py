"""Probe baseline and metric extraction interfaces for CI visibility."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import importlib

from sim.scripts import baseline_generation, metric_extraction

metrics_module = importlib.import_module("sim.scripts.extract_metrics")


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
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            window_file = workspace_path / "windows.csv"
            window_file.write_text(
                "start,end\n2024-01-01T00:00:00,2024-01-01T00:01:00\n",
                encoding="utf-8",
            )
            triangle_file = workspace_path / "triangles.json"
            triangle_file.write_text(
                json.dumps(
                    [
                        {
                            "time": "2024-01-01T00:00:00",
                            "vertices": [
                                [0.0, 0.0, 0.0],
                                [10.0, 0.0, 0.0],
                                [5.0, 8.660254037844386, 0.0],
                            ],
                        }
                    ],
                    indent=2,
                ),
                encoding="utf-8",
            )
            delta_v_file = workspace_path / "delta_v.csv"
            delta_v_file.write_text(
                "spacecraft,delta_v_mps\nSatA,0.1\n",
                encoding="utf-8",
            )
            baseline_file = workspace_path / "baseline.json"
            baseline_file.write_text(
                json.dumps(
                    {
                        "triangle_geometry": {
                            "area": 43.30127018922193,
                            "aspect_ratio": 1.0,
                            "side_lengths": [10.0, 10.0, 10.0],
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            bundle = {
                "window_file": window_file,
                "triangle_file": triangle_file,
                "delta_v_file": delta_v_file,
                "baseline_file": baseline_file,
                "output_dir": workspace_path / "reports",
            }
            metrics_module.extract_metrics(bundle)
    except Exception as exc:  # pragma: no cover - defensive reporting for CI visibility.
        return f"Metric extraction failed during probing: {exc}"
    return "Metric extraction executed successfully."


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
