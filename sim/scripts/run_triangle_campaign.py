"""Automate quarterly triangle-formation reruns with drag dispersions."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, Optional

from sim.formation import simulate_triangle_formation

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "scenarios" / "tehran_triangle.json"
ARTEFACT_ROOT = PROJECT_ROOT / "artefacts"
CAMPAIGN_ROOT = ARTEFACT_ROOT / "triangle_campaign"
HISTORY_PATH = CAMPAIGN_ROOT / "history.csv"


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario",
        nargs="?",
        default=str(DEFAULT_CONFIG),
        help="Path to the triangle-formation configuration JSON.",
    )
    parser.add_argument(
        "--cadence-days",
        type=float,
        default=90.0,
        help="Minimum days between reruns before a new execution is triggered.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override cadence checks and force execution.",
    )
    parser.add_argument(
        "--notes",
        type=str,
        default="",
        help="Optional free-text notes captured alongside the run metadata.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ARTEFACT_ROOT,
        help="Root directory in which run_YYYYMMDD_hhmmZ folders are created.",
    )
    return parser.parse_args(args)


def main(args: Optional[Iterable[str]] = None) -> int:
    namespace = parse_args(args)
    scenario_path = Path(namespace.scenario)
    cadence = max(namespace.cadence_days, 0.0)

    CAMPAIGN_ROOT.mkdir(parents=True, exist_ok=True)
    history = _load_history(HISTORY_PATH)
    now = datetime.now(timezone.utc)

    if history and not namespace.force:
        last_record = history[-1]
        next_due = last_record["next_due"]
        if next_due and now < next_due:
            remaining = next_due - now
            print(
                "Next rerun not yet due. Remaining interval: {:.1f} days.".format(
                    remaining.total_seconds() / 86_400.0
                )
            )
            return 0

    run_id = _generate_run_id(now)
    run_dir = namespace.output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Executing triangle simulation for run {run_id}…")
    result = simulate_triangle_formation(scenario_path, output_directory=run_dir)

    metadata = _build_metadata(
        run_id=run_id,
        timestamp=now,
        cadence_days=cadence,
        scenario_path=scenario_path,
        notes=namespace.notes,
        metrics=result.metrics,
        artefacts=result.artefacts,
    )

    metadata_path = run_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    next_due = now + timedelta(days=cadence) if cadence > 0.0 else None
    _append_history(
        HISTORY_PATH,
        run_id=run_id,
        timestamp=now,
        next_due=next_due,
        scenario_path=scenario_path,
        notes=namespace.notes,
    )

    print(f"Run artefacts captured under {run_dir}.")
    if namespace.notes:
        print(f"Notes: {namespace.notes}")
    return 0


def _load_history(path: Path) -> list[Mapping[str, Optional[datetime]]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = ["run_id", "timestamp_utc", "next_due_utc", "scenario_path", "notes"]
        if reader.fieldnames != expected:
            raise ValueError("Unexpected history header: {}".format(reader.fieldnames))
        records: list[Mapping[str, Optional[datetime]]] = []
        for row in reader:
            timestamp_text = row.get("timestamp_utc", "")
            next_due_text = row.get("next_due_utc", "")
            if not timestamp_text:
                continue
            timestamp = datetime.fromisoformat(timestamp_text)
            next_due = datetime.fromisoformat(next_due_text) if next_due_text else None
            scenario_text = row.get("scenario_path", "")
            notes = row.get("notes", "")
            records.append(
                {
                    "run_id": row.get("run_id", ""),
                    "timestamp": timestamp,
                    "next_due": next_due,
                    "scenario_path": Path(scenario_text) if scenario_text else Path(),
                    "notes": notes,
                }
            )
    return records


def _append_history(
    path: Path,
    *,
    run_id: str,
    timestamp: datetime,
    next_due: Optional[datetime],
    scenario_path: Path,
    notes: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "run_id",
                "timestamp_utc",
                "next_due_utc",
                "scenario_path",
                "notes",
            ],
        )
        if is_new_file:
            writer.writeheader()
        writer.writerow(
            {
                "run_id": run_id,
                "timestamp_utc": timestamp.isoformat(),
                "next_due_utc": next_due.isoformat() if next_due else "",
                "scenario_path": str(scenario_path),
                "notes": notes,
            }
        )


def _generate_run_id(timestamp: datetime) -> str:
    return timestamp.strftime("run_%Y%m%d_%H%MZ")


def _build_metadata(
    *,
    run_id: str,
    timestamp: datetime,
    cadence_days: float,
    scenario_path: Path,
    notes: str,
    metrics: Mapping[str, object],
    artefacts: Mapping[str, Optional[str]],
) -> Mapping[str, object]:
    drag_metrics = metrics.get("drag_dispersion", {}) if isinstance(metrics, Mapping) else {}
    return {
        "run_id": run_id,
        "timestamp_utc": timestamp.isoformat().replace("+00:00", "Z"),
        "cadence_days": cadence_days,
        "scenario_path": str(scenario_path),
        "notes": notes,
        "drag_dispersion_summary": drag_metrics,
        "artefacts": artefacts,
    }


if __name__ == "__main__":  # pragma: no cover - exercised via CLI tests.
    raise SystemExit(main())
