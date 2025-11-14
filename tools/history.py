"""History tracking for simulation runs."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

# This assumes the script is in 'tools/', so the project root is one level up.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def update_history_file(run_id: str, scenario_path: str, notes: str | None) -> None:
    """Appends a record to the project's main history CSV file."""
    history_path = PROJECT_ROOT / "artefacts" / "history.csv"
    file_exists = history_path.exists()

    try:
        with open(history_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["run_id", "timestamp_utc", "scenario_path", "notes"])
            
            writer.writerow([
                run_id,
                datetime.now(timezone.utc).isoformat(),
                str(scenario_path),
                notes or "",
            ])
    except IOError as e:
        print(f"Warning: Failed to update history file at {history_path}: {e}")
