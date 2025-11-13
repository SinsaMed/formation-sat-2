"""Daily sweep utility evaluating locked-RAAN access compliance."""

from __future__ import annotations

import argparse
import csv
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional

from . import configuration, perturbation_analysis


@dataclass
class SweepResult:
    """Container summarising the compliance outcome for a single day."""

    day_offset: int
    date_iso: str
    window_start: str
    window_end: str
    window_duration_s: float
    centroid_km: float
    worst_km: float
    primary_compliant: bool
    waiver_compliant: bool


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the daily sweep helper."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario",
        nargs="?",
        default="tehran_triangle",
        help="Scenario identifier or explicit path to evaluate.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of sequential days to sweep starting from the nominal epoch.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artefacts/sweeps/tehran_30d.csv"),
        help="CSV file recording the sweep summary.",
    )
    return parser.parse_args(args)


def main(args: Optional[Iterable[str]] = None) -> int:
    """Execute the sweep and persist the aggregated results to CSV."""

    namespace = parse_args(args)
    scenario = configuration.load_scenario(namespace.scenario)
    output_path = Path(namespace.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[SweepResult] = []
    failures: list[SweepResult] = []

    for day in range(max(namespace.days, 0)):
        shifted = _shift_scenario(scenario, day)
        sweep_result = _evaluate_day(shifted, day)
        results.append(sweep_result)
        if (
            not sweep_result.primary_compliant
            or sweep_result.centroid_km > 30.0
            or sweep_result.worst_km > 70.0
            or sweep_result.window_duration_s < 90.0
        ):
            failures.append(sweep_result)

    _write_results_csv(output_path, results)

    print(f"Recorded {len(results)} days to {output_path}.")
    if failures:
        print("One or more days violated the 30/70 km limits. Suggested action:")
        print(
            "  Apply a weekly plane-maintenance manoeuvre to recentre the access window and re-run the sweep."
        )
        print("  Non-compliant days:")
        for failure in failures:
            print(
                f"    D+{failure.day_offset:02d} ({failure.date_iso}): centroid={failure.centroid_km:.3f} km,"
                f" worst={failure.worst_km:.3f} km, window={failure.window_duration_s:.1f} s"
            )
        return 1

    print("All days satisfy the 30/70 km compliance criteria.")
    return 0


def _evaluate_day(
    scenario: MutableMapping[str, object],
    day_offset: int,
) -> SweepResult:
    """Propagate the scenario for a single day and extract compliance metrics."""

    access_window = scenario.get("access_window")
    midpoint = _parse_time(access_window.get("midpoint_utc")) if isinstance(access_window, Mapping) else None
    start_time = _parse_time(access_window.get("start_utc")) if isinstance(access_window, Mapping) else None
    end_time = _parse_time(access_window.get("end_utc")) if isinstance(access_window, Mapping) else None

    midpoint_iso = _format_time(midpoint)
    start_iso = _format_time(start_time)
    end_iso = _format_time(end_time)

    propagation, _artefacts = perturbation_analysis.propagate_constellation(
        scenario,
        output_directory=None,
        monte_carlo={"enabled": False, "runs": 0},
    )

    cross_track = propagation.get("cross_track") if isinstance(propagation, Mapping) else {}
    evaluation = cross_track.get("evaluation") if isinstance(cross_track, Mapping) else {}

    centroid = float(evaluation.get("centroid_abs_cross_track_km", float("nan")))
    worst = float(evaluation.get("worst_vehicle_abs_cross_track_km", float("nan")))
    primary_compliant = bool(evaluation.get("primary_compliant", False))
    waiver_compliant = bool(evaluation.get("waiver_compliant", False))

    window_duration = 0.0
    if start_time and end_time:
        window_duration = max((end_time - start_time).total_seconds(), 0.0)

    date_iso = midpoint.date().isoformat() if midpoint else "unknown"

    return SweepResult(
        day_offset=day_offset,
        date_iso=date_iso,
        window_start=start_iso or "",
        window_end=end_iso or "",
        window_duration_s=window_duration,
        centroid_km=centroid,
        worst_km=worst,
        primary_compliant=primary_compliant,
        waiver_compliant=waiver_compliant,
    )


def _write_results_csv(path: Path, results: Iterable[SweepResult]) -> None:
    """Persist the sweep results to *path* using comma-separated values."""

    fieldnames = [
        "day_offset",
        "date",
        "window_start_utc",
        "window_end_utc",
        "window_duration_s",
        "centroid_abs_cross_track_km",
        "worst_vehicle_abs_cross_track_km",
        "primary_compliant",
        "waiver_compliant",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "day_offset": result.day_offset,
                    "date": result.date_iso,
                    "window_start_utc": result.window_start,
                    "window_end_utc": result.window_end,
                    "window_duration_s": f"{result.window_duration_s:.1f}",
                    "centroid_abs_cross_track_km": f"{result.centroid_km:.6f}",
                    "worst_vehicle_abs_cross_track_km": f"{result.worst_km:.6f}",
                    "primary_compliant": "true" if result.primary_compliant else "false",
                    "waiver_compliant": "true" if result.waiver_compliant else "false",
                }
            )


def _shift_scenario(
    base_scenario: Mapping[str, object],
    day_offset: int,
) -> MutableMapping[str, object]:
    """Return a deep-copied scenario with UTC timestamps shifted by *day_offset*."""

    scenario = deepcopy(base_scenario)
    delta = timedelta(days=day_offset)

    _shift_mapping_times(scenario.get("access_window"), delta)

    orbital = scenario.get("orbital_elements")
    if isinstance(orbital, MutableMapping):
        epoch = _parse_time(orbital.get("epoch_utc"))
        if epoch is not None:
            orbital["epoch_utc"] = _format_time(epoch + delta)

    raan_alignment = scenario.get("raan_alignment")
    if isinstance(raan_alignment, MutableMapping):
        midpoint = _parse_time(raan_alignment.get("midpoint_utc"))
        if midpoint is not None:
            raan_alignment["midpoint_utc"] = _format_time(midpoint + delta)

    timing = scenario.get("timing")
    if isinstance(timing, MutableMapping):
        planning = timing.get("planning_horizon")
        if isinstance(planning, MutableMapping):
            _shift_mapping_times(planning, delta)
        propagation = timing.get("propagation")
        if isinstance(propagation, MutableMapping):
            _shift_mapping_times(propagation, delta)
        windows = timing.get("daily_access_windows")
        if isinstance(windows, list):
            for window in windows:
                if isinstance(window, MutableMapping):
                    _shift_mapping_times(window, delta)

    return scenario


def _shift_mapping_times(mapping: Optional[MutableMapping[str, object]], delta: timedelta) -> None:
    """Shift ISO-8601 timestamps stored within *mapping* by *delta*."""

    if not isinstance(mapping, MutableMapping):
        return
    for key in list(mapping.keys()):
        if not isinstance(key, str) or not key.endswith("_utc"):
            continue
        timestamp = _parse_time(mapping.get(key))
        if timestamp is not None:
            mapping[key] = _format_time(timestamp + delta)


def _parse_time(value: object) -> datetime | None:
    """Parse ISO-8601 timestamps into timezone-aware datetimes."""

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        text = value.replace("Z", "+00:00") if value.endswith("Z") else value
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def _format_time(value: datetime | None) -> str | None:
    """Format a timezone-aware datetime back into an ISO-8601 string."""

    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":  # pragma: no cover - CLI behaviour.
    raise SystemExit(main())

