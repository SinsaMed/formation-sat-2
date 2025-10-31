"""Metric extraction utilities for simulation post-processing.

The routines in this module assemble quick-look statistics from simulation
artefacts exported as comma-separated value (CSV) tables or JavaScript Object
Notation (JSON) documents.  They provide a light-weight stand-in for the more
comprehensive analysis pipelines that will eventually integrate directly with
Systems Tool Kit (STK) post-processing exports.  Analysts can employ the
functions in this file to validate numerical experiments, update baseline
reference products, and generate briefing-ready plots summarising the quality of
formation-keeping manoeuvres.

Key capabilities
----------------
1. Parse window-access reports to quantify the availability of the triangular
   formation and report descriptive statistics for the window durations.
2. Evaluate triangle geometry metrics (side lengths, area, aspect ratio) for
   each timestamped sample and quantify deviations relative to a reference
   baseline.
3. Aggregate thruster logs to obtain ΔV usage per spacecraft and across the
   formation, supporting propellant-budget reconciliations.

The :func:`extract_metrics` function orchestrates the analysis flow and writes
tabular summaries alongside diagnostic plots.  Analysts may also execute the
module as a script to operate directly on simulation artefacts residing on
disk.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")  # Ensure headless rendering for automated environments.
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from src.constellation.geometry import (
    triangle_area,
    triangle_aspect_ratio,
    triangle_side_lengths,
)


WINDOW_TABLE_NAME = "window_events.csv"
TRIANGLE_TABLE_NAME = "triangle_geometry.csv"
DELTA_V_TABLE_NAME = "delta_v_usage.csv"
SUMMARY_JSON_NAME = "metrics_summary.json"
WINDOW_PLOT_NAME = "window_durations.png"
TRIANGLE_PLOT_NAME = "triangle_area.png"


@dataclass
class ExtractedMetrics:
    """Container encapsulating the metrics returned by :func:`extract_metrics`."""

    window_statistics: Mapping[str, float]
    triangle_geometry: Mapping[str, float]
    delta_v: Mapping[str, float | Mapping[str, float]]
    sample_tables: Mapping[str, Sequence[Mapping[str, object]]] = field(
        default_factory=dict
    )

    def to_dict(self) -> MutableMapping[str, object]:
        """Convert the dataclass payload into a JSON-serialisable mapping."""

        def serialise_record(record: Mapping[str, object]) -> Mapping[str, object]:
            converted: MutableMapping[str, object] = {}
            for key, value in record.items():
                if isinstance(value, datetime):
                    converted[key] = value.isoformat()
                elif isinstance(value, (list, tuple)):
                    converted[key] = [serialise_value(item) for item in value]
                else:
                    converted[key] = serialise_value(value)
            return converted

        def serialise_value(value: object) -> object:
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, (np.floating, np.integer)):
                return float(value)
            return value

        return {
            "window_statistics": {
                key: serialise_value(val)
                for key, val in self.window_statistics.items()
            },
            "triangle_geometry": {
                key: serialise_value(val)
                for key, val in self.triangle_geometry.items()
            },
            "delta_v": {
                key: serialise_value(val)
                for key, val in self.delta_v.items()
            },
            "sample_tables": {
                name: [serialise_record(rec) for rec in records]
                for name, records in self.sample_tables.items()
            },
        }


def _parse_timestamp(value: object) -> datetime:
    """Normalise a timestamp expressed as ISO 8601 or seconds from the epoch."""

    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float, np.integer, np.floating)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover - defensive message.
            raise ValueError(f"Unsupported timestamp format: {value!r}") from exc
    raise TypeError(f"Cannot interpret timestamp value: {value!r}")


def _normalise_vertices(vertices: Iterable[Iterable[float]]) -> List[np.ndarray]:
    points = [np.asarray(vertex, dtype=float) for vertex in vertices]
    if len(points) != 3:
        raise ValueError("Exactly three vertices are required to describe a triangle.")
    return points


def _load_window_events(path: Path) -> List[Mapping[str, object]]:
    """Load window start and end times from *path* supporting CSV and JSON."""

    records: List[Mapping[str, object]] = []
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping):
            payload = payload.get("windows", [])
        if not isinstance(payload, Sequence):
            raise ValueError("JSON window payload must be a list or contain 'windows'.")
        for item in payload:
            start = _parse_timestamp(item["start"])
            end = _parse_timestamp(item["end"])
            records.append({"start": start, "end": end})
        return records

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            start_key = "start" if "start" in row else "start_time"
            end_key = "end" if "end" in row else "end_time"
            start = _parse_timestamp(row[start_key])
            end = _parse_timestamp(row[end_key])
            records.append({"start": start, "end": end})
    return records


def _compute_window_statistics(
    events: Sequence[Mapping[str, datetime]],
) -> Tuple[Mapping[str, float], List[Mapping[str, object]]]:
    """Return descriptive statistics and per-window durations."""

    durations: List[float] = []
    table: List[Mapping[str, object]] = []
    for event in events:
        start = event["start"]
        end = event["end"]
        duration = max((end - start).total_seconds(), 0.0)
        durations.append(duration)
        table.append({"start": start, "end": end, "duration_s": float(duration)})

    if not durations:
        statistics = {
            "count": 0,
            "mean_duration_s": 0.0,
            "median_duration_s": 0.0,
            "min_duration_s": 0.0,
            "max_duration_s": 0.0,
        }
        return statistics, table

    statistics = {
        "count": float(len(durations)),
        "mean_duration_s": float(mean(durations)),
        "median_duration_s": float(median(durations)),
        "min_duration_s": float(min(durations)),
        "max_duration_s": float(max(durations)),
    }
    return statistics, table


def _load_triangle_series(path: Path) -> List[Mapping[str, object]]:
    """Load timestamped triangle vertices from JSON or CSV sources."""

    records: List[Mapping[str, object]] = []
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping):
            payload = payload.get("triangles", [])
        if not isinstance(payload, Sequence):
            raise ValueError("JSON triangle payload must be a list or contain 'triangles'.")
        for item in payload:
            time = _parse_timestamp(item["time"])
            vertices = _normalise_vertices(item["vertices"])
            records.append({"time": time, "vertices": vertices})
        return records

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            time = _parse_timestamp(row["time"])
            vertices = []
            for index in range(1, 4):
                x = float(row[f"s{index}_x"])
                y = float(row[f"s{index}_y"])
                z = float(row[f"s{index}_z"])
                vertices.append([x, y, z])
            records.append({"time": time, "vertices": _normalise_vertices(vertices)})
    return records


def _compute_triangle_metrics(
    records: Sequence[Mapping[str, object]],
    baseline: Mapping[str, object] | None = None,
) -> Tuple[Mapping[str, float], List[Mapping[str, object]]]:
    """Compute per-sample geometry metrics and aggregate statistics."""

    sample_rows: List[Mapping[str, object]] = []
    areas: List[float] = []
    aspect_ratios: List[float] = []
    side_lengths: List[np.ndarray] = []
    area_errors: List[float] = []
    side_errors: List[np.ndarray] = []

    baseline_sides = None
    baseline_area = None
    baseline_aspect = None
    if baseline:
        if "side_lengths" in baseline:
            baseline_sides = np.asarray(baseline["side_lengths"], dtype=float)
        if "area" in baseline:
            baseline_area = float(baseline["area"])
        if "aspect_ratio" in baseline:
            baseline_aspect = float(baseline["aspect_ratio"])

    for record in records:
        vertices = record["vertices"]
        area = float(triangle_area(vertices))
        aspect = float(triangle_aspect_ratio(vertices))
        sides = np.asarray(triangle_side_lengths(vertices), dtype=float)
        areas.append(area)
        aspect_ratios.append(aspect)
        side_lengths.append(sides)

        side_error_vec = None
        area_error = 0.0
        aspect_error = 0.0
        if baseline_sides is not None:
            side_error_vec = sides - baseline_sides
            side_errors.append(side_error_vec)
        if baseline_area is not None:
            area_error = area - baseline_area
            area_errors.append(area_error)
        if baseline_aspect is not None:
            aspect_error = aspect - baseline_aspect

        sample_rows.append(
            {
                "time": record["time"],
                "area": area,
                "aspect_ratio": aspect,
                "side_lengths": tuple(float(val) for val in sides),
                "area_error": float(area_error),
                "aspect_ratio_error": float(aspect_error),
                "side_errors": tuple(
                    float(val) for val in (side_error_vec if side_error_vec is not None else np.zeros(3))
                ),
            }
        )

    if not areas:
        return {
            "mean_area": 0.0,
            "mean_aspect_ratio": 0.0,
            "area_error_rms": 0.0,
            "side_length_rms_error": 0.0,
            "mean_side_lengths": [0.0, 0.0, 0.0],
        }, sample_rows

    stacked_sides = np.vstack(side_lengths)
    mean_sides = np.mean(stacked_sides, axis=0)
    area_error_rms = (
        math.sqrt(float(np.mean(np.square(area_errors)))) if area_errors else 0.0
    )
    if side_errors:
        all_side_errors = np.vstack(side_errors)
        side_error_rms = float(np.sqrt(np.mean(np.square(all_side_errors))))
    else:
        side_error_rms = 0.0

    metrics = {
        "mean_area": float(mean(areas)),
        "mean_aspect_ratio": float(mean(aspect_ratios)),
        "area_error_rms": float(area_error_rms),
        "side_length_rms_error": side_error_rms,
        "mean_side_lengths": [float(val) for val in mean_sides],
    }
    if baseline_area is not None:
        metrics["baseline_area"] = float(baseline_area)
    if baseline_aspect is not None:
        metrics["baseline_aspect_ratio"] = float(baseline_aspect)
    if baseline_sides is not None:
        metrics["baseline_side_lengths"] = [float(val) for val in baseline_sides]

    return metrics, sample_rows


def _load_delta_v_log(path: Path) -> List[Mapping[str, object]]:
    """Load per-manoeuvre ΔV records from CSV or JSON sources."""

    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping):
            payload = payload.get("delta_v", [])
        if not isinstance(payload, Sequence):
            raise ValueError("JSON delta-v payload must be a list or contain 'delta_v'.")
        return [
            {"spacecraft": rec["spacecraft"], "delta_v_mps": float(rec["delta_v_mps"])}
            for rec in payload
        ]

    records: List[Mapping[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                {
                    "spacecraft": row["spacecraft"],
                    "delta_v_mps": float(row["delta_v_mps"]),
                }
            )
    return records


def _compute_delta_v_statistics(
    records: Sequence[Mapping[str, object]]
) -> Tuple[Mapping[str, object], List[Mapping[str, object]]]:
    """Return aggregated ΔV usage and per-record details."""

    per_spacecraft: MutableMapping[str, float] = {}
    for record in records:
        name = record["spacecraft"]
        per_spacecraft[name] = per_spacecraft.get(name, 0.0) + float(record["delta_v_mps"])

    total = float(sum(per_spacecraft.values()))
    statistics: Mapping[str, object] = {
        "total_delta_v_mps": total,
        "per_spacecraft": {name: float(val) for name, val in per_spacecraft.items()},
    }
    return statistics, [{"spacecraft": r["spacecraft"], "delta_v_mps": float(r["delta_v_mps"])} for r in records]


def _resolve_path(bundle: Mapping[str, object], *candidates: str) -> Optional[Path]:
    for key in candidates:
        if key in bundle and bundle[key] is not None:
            return Path(bundle[key])
    return None


def _load_baseline(path: Optional[Path]) -> Mapping[str, object]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):  # pragma: no cover - defensive guard.
        raise ValueError("Baseline file must contain a JSON object.")
    triangle = payload.get("triangle_geometry", {})
    return triangle if isinstance(triangle, Mapping) else {}


def _persist_baseline(path: Path, metrics: ExtractedMetrics) -> None:
    payload = {
        "window_statistics": metrics.window_statistics,
        "triangle_geometry": {
            "side_lengths": metrics.triangle_geometry.get("mean_side_lengths", [0.0, 0.0, 0.0]),
            "area": metrics.triangle_geometry.get("mean_area", 0.0),
            "aspect_ratio": metrics.triangle_geometry.get("mean_aspect_ratio", 0.0),
        },
        "delta_v": metrics.delta_v,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_window_outputs(output_dir: Path, table: Sequence[Mapping[str, object]]) -> None:
    csv_path = output_dir / WINDOW_TABLE_NAME
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["start", "end", "duration_s"])
        writer.writeheader()
        for row in table:
            writer.writerow(
                {
                    "start": row["start"].isoformat(),
                    "end": row["end"].isoformat(),
                    "duration_s": f"{row['duration_s']:.6f}",
                }
            )

    if not table:
        return

    times = [row["start"] for row in table]
    durations = [row["duration_s"] for row in table]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot_date(times, durations, linestyle="-", marker="o", label="Window duration")
    ax.set_ylabel("Duration [s]")
    ax.set_xlabel("Window start")
    ax.set_title("Formation window durations")
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_dir / WINDOW_PLOT_NAME, dpi=200)
    plt.close(fig)


def _write_triangle_outputs(
    output_dir: Path,
    table: Sequence[Mapping[str, object]],
    metrics: Mapping[str, float],
) -> None:
    csv_path = output_dir / TRIANGLE_TABLE_NAME
    fieldnames = [
        "time",
        "area",
        "aspect_ratio",
        "side_lengths",
        "area_error",
        "aspect_ratio_error",
        "side_errors",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in table:
            writer.writerow(
                {
                    "time": row["time"].isoformat(),
                    "area": f"{row['area']:.8f}",
                    "aspect_ratio": f"{row['aspect_ratio']:.8f}",
                    "side_lengths": ";".join(f"{val:.8f}" for val in row["side_lengths"]),
                    "area_error": f"{row['area_error']:.8f}",
                    "aspect_ratio_error": f"{row['aspect_ratio_error']:.8f}",
                    "side_errors": ";".join(f"{val:.8f}" for val in row["side_errors"]),
                }
            )

    if not table:
        return

    times = [row["time"] for row in table]
    areas = [row["area"] for row in table]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot_date(times, areas, linestyle="-", marker="o", label="Measured area")
    baseline_area = metrics.get("baseline_area")
    if baseline_area is not None:
        ax.axhline(baseline_area, color="tab:red", linestyle="--", label="Baseline area")
    ax.set_ylabel("Area [m²]")
    ax.set_xlabel("Epoch")
    ax.set_title("Triangle area comparison")
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_dir / TRIANGLE_PLOT_NAME, dpi=200)
    plt.close(fig)


def _write_delta_v_outputs(output_dir: Path, table: Sequence[Mapping[str, object]]) -> None:
    csv_path = output_dir / DELTA_V_TABLE_NAME
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["spacecraft", "delta_v_mps"])
        writer.writeheader()
        for row in table:
            writer.writerow(
                {
                    "spacecraft": row["spacecraft"],
                    "delta_v_mps": f"{row['delta_v_mps']:.6f}",
                }
            )


def _write_summary(output_dir: Path, metrics: ExtractedMetrics) -> None:
    summary_path = output_dir / SUMMARY_JSON_NAME
    summary_path.write_text(json.dumps(metrics.to_dict(), indent=2), encoding="utf-8")


def extract_metrics(
    data_bundle: Mapping[str, object],
    metric_specification: Optional[Sequence[str]] = None,
) -> ExtractedMetrics:
    """Extract formation metrics from simulation artefacts.

    The *data_bundle* may provide in-memory data structures or filesystem paths
    using the following keys:

    - ``window_events`` or ``window_file`` (CSV/JSON) – Access window records.
    - ``triangle_series`` or ``triangle_file`` – Triangular geometry samples.
    - ``delta_v_log`` or ``delta_v_file`` – Manoeuvre ΔV usage records.
    - ``baseline_file`` – Optional baseline JSON used for error computations.
    - ``output_dir`` – Directory for summary artefacts (created if absent).
    - ``update_baseline`` – Boolean flag requesting baseline refresh.

    Parameters
    ----------
    data_bundle
        Mapping containing the data sources required for the analysis.
    metric_specification
        Optional sequence selecting a subset of metrics to evaluate.  The current
        implementation accepts the argument for interface compatibility but does
        not filter the outputs.

    Returns
    -------
    ExtractedMetrics
        Dataclass containing summary statistics, per-record tables, and
        references to any baseline data employed during the computation.
    """

    del metric_specification  # Reserved for future filtering functionality.

    windows_data = data_bundle.get("window_events")
    if windows_data is None:
        window_path = _resolve_path(
            data_bundle,
            "window_file",
            "windows_file",
            "window_path",
            "windows_path",
        )
        if window_path is None:
            raise ValueError("Window event data not provided in data bundle.")
        windows = _load_window_events(window_path)
    else:
        windows = [
            {
                "start": _parse_timestamp(record["start"]),
                "end": _parse_timestamp(record["end"]),
            }
            for record in windows_data
        ]

    triangle_data = data_bundle.get("triangle_series")
    if triangle_data is None:
        triangle_path = _resolve_path(
            data_bundle,
            "triangle_file",
            "triangles_file",
            "triangle_path",
        )
        if triangle_path is None:
            raise ValueError("Triangle geometry data not provided in data bundle.")
        triangles = _load_triangle_series(triangle_path)
    else:
        triangles = [
            {
                "time": _parse_timestamp(record["time"]),
                "vertices": _normalise_vertices(record["vertices"]),
            }
            for record in triangle_data
        ]

    delta_v_data = data_bundle.get("delta_v_log")
    if delta_v_data is None:
        delta_v_path = _resolve_path(
            data_bundle,
            "delta_v_file",
            "delta_v_path",
            "delta_v_log",
        )
        if delta_v_path is None:
            raise ValueError("ΔV log data not provided in data bundle.")
        delta_v_records = _load_delta_v_log(delta_v_path)
    else:
        delta_v_records = [
            {
                "spacecraft": record["spacecraft"],
                "delta_v_mps": float(record["delta_v_mps"]),
            }
            for record in delta_v_data
        ]

    baseline_path = _resolve_path(data_bundle, "baseline_file", "baseline_path")
    baseline = _load_baseline(baseline_path)

    window_stats, window_table = _compute_window_statistics(windows)
    triangle_stats, triangle_table = _compute_triangle_metrics(triangles, baseline)
    delta_v_stats, delta_v_table = _compute_delta_v_statistics(delta_v_records)

    metrics = ExtractedMetrics(
        window_statistics=window_stats,
        triangle_geometry=triangle_stats,
        delta_v=delta_v_stats,
        sample_tables={
            "window_events": window_table,
            "triangle_samples": triangle_table,
            "delta_v_log": delta_v_table,
        },
    )

    output_dir = _resolve_path(data_bundle, "output_dir") or Path("artefacts/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_window_outputs(output_dir, window_table)
    _write_triangle_outputs(output_dir, triangle_table, triangle_stats)
    _write_delta_v_outputs(output_dir, delta_v_table)
    _write_summary(output_dir, metrics)

    if baseline_path is not None and data_bundle.get("update_baseline"):
        _persist_baseline(baseline_path, metrics)

    return metrics


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-file", type=Path, required=True, help="Window access CSV/JSON file.")
    parser.add_argument(
        "--triangle-file",
        type=Path,
        required=True,
        help="Triangle geometry CSV/JSON file produced by the simulation.",
    )
    parser.add_argument(
        "--delta-v-file",
        type=Path,
        required=True,
        help="ΔV usage log in CSV/JSON format.",
    )
    parser.add_argument(
        "--baseline-file",
        type=Path,
        help="Optional baseline JSON storing reference triangle metrics.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artefacts/metrics"),
        help="Directory receiving summary tables and plots.",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Persist the newly computed metrics to the baseline file.",
    )
    return parser


def main(args: Optional[Sequence[str]] = None) -> int:
    """Command-line entry point used by automation wrappers."""

    namespace = _build_arg_parser().parse_args(args)
    bundle = {
        "window_file": namespace.window_file,
        "triangle_file": namespace.triangle_file,
        "delta_v_file": namespace.delta_v_file,
        "baseline_file": namespace.baseline_file,
        "output_dir": namespace.output_dir,
        "update_baseline": namespace.update_baseline,
    }
    metrics = extract_metrics(bundle)
    summary = metrics.to_dict()
    print(  # pragma: no cover - console reporting for manual runs.
        json.dumps(
            {
                "window_statistics": summary["window_statistics"],
                "triangle_geometry": {
                    key: summary["triangle_geometry"][key]
                    for key in ("mean_area", "mean_aspect_ratio", "area_error_rms")
                    if key in summary["triangle_geometry"]
                },
                "delta_v": summary["delta_v"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - direct script execution.
    raise SystemExit(main())
