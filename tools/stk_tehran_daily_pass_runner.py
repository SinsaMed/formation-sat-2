"""Automate STK 11.2 playback for the Tehran daily pass scenario export."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import comtypes
import comtypes.client


def _get_stk_application():
    """Return a running STK 11.2 application instance."""

    try:
        application = comtypes.client.GetActiveObject("STK11.Application")
    except (OSError, comtypes.COMError):
        application = comtypes.client.CreateObject("STK11.Application")
    application.Visible = True
    application.UserControl = True
    return application


def _load_scenario(root, scenario_file: Path) -> None:
    """Load the exported scenario file into STK."""

    if root.CurrentScenario is not None:
        root.CloseScenario()
    root.LoadScenario(str(scenario_file))


def _extract_satellite_name(sat_file: Path) -> str:
    """Read the satellite name from the exported `.sat` file."""

    for line in sat_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("Name "):
            return line.split(" ", 1)[1].strip()
    return sat_file.stem


def _extract_facility_name(facility_file: Path) -> str:
    """Read the facility name from the exported `.fac` file."""

    for line in facility_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("Name "):
            return line.split(" ", 1)[1].strip()
    return facility_file.stem.replace("Facility_", "")


def _configure_scene(root, summary: dict[str, object], satellite: str, facilities: list[str]) -> None:
    """Set the animation timeline, camera framing, and graphics overlays."""

    configuration = summary.get("configuration_summary", {})
    planning = configuration.get("planning_horizon", {}) if isinstance(configuration, dict) else {}
    start_iso = planning.get("start_utc")
    stop_iso = planning.get("stop_utc")
    if isinstance(start_iso, str) and isinstance(stop_iso, str):
        start_epoch = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        stop_epoch = datetime.fromisoformat(stop_iso.replace("Z", "+00:00"))
        root.ExecuteCommand(
            "SetTimePeriod * "
            f"{start_epoch.strftime('%d %b %Y %H:%M:%S.%f')[:-3]} "
            f"{stop_epoch.strftime('%d %b %Y %H:%M:%S.%f')[:-3]}"
        )
        root.ExecuteCommand("Animate * Reset")
    root.ExecuteCommand(f"Graphics */Satellite/{satellite} Attitude Update Off")
    root.ExecuteCommand(f"Graphics */Satellite/{satellite} Pass3D Show On")
    root.ExecuteCommand(f"Graphics */Satellite/{satellite} GroundTrack Show On")
    root.ExecuteCommand(f"VO */Satellite/{satellite} Lighting Sunlight On")

    if facilities:
        facility = facilities[0]
        root.ExecuteCommand(
            f"VO * ViewFromTo Normal */Facility/{facility} */Satellite/{satellite} Fixed"
        )
        root.ExecuteCommand(f"VO */Satellite/{satellite} ShowTrailingLeadVectors GroundTrack Both 3600")


def _import_auxiliary_products(root, export_dir: Path, satellite: str, facilities: list[str]) -> None:
    """Load ground-track and contact interval files into the active scenario."""

    ground_track = export_dir / f"{satellite}_groundtrack.gt"
    if ground_track.exists():
        root.ExecuteCommand(
            f"ImportDataFile */Satellite/{satellite} GroundTrack \"{ground_track}\""
        )

    for facility in facilities:
        interval_file = export_dir / f"Contacts_{facility}.int"
        if interval_file.exists():
            root.ExecuteCommand(
                f"ImportDataFile */Satellite/{satellite} IntervalList \"{interval_file}\""
            )


def _load_facilities(root, export_dir: Path, facilities: list[str]) -> None:
    """Ensure facility geometry is present in the scenario."""

    for facility_file in export_dir.glob("Facility_*.fac"):
        root.ExecuteCommand(f"Load / */Facility \"{facility_file}\"")

    for facility in facilities:
        root.ExecuteCommand(f"VO */Facility/{facility} ShowAzElMask Off")
        root.ExecuteCommand(f"VO */Facility/{facility} ShowAxes Off")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "run_directory",
        type=Path,
        help="Directory containing `scenario_summary.json` and the `stk_export` artefacts.",
    )
    return parser.parse_args()


def main() -> int:
    namespace = parse_args()
    run_directory = namespace.run_directory.resolve()
    summary_path = run_directory / "scenario_summary.json"
    export_dir = run_directory / "stk_export"

    if not summary_path.exists():
        raise FileNotFoundError(f"Could not locate scenario summary: {summary_path}")
    if not export_dir.exists():
        raise FileNotFoundError(f"Could not locate STK export directory: {export_dir}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    scenario_files = sorted(export_dir.glob("*.sc"))
    if not scenario_files:
        raise FileNotFoundError("No STK scenario file (*.sc) found in export directory.")
    scenario_file = scenario_files[0]

    satellite_files = sorted(export_dir.glob("*.sat"))
    if not satellite_files:
        raise FileNotFoundError("No satellite definition (*.sat) found in export directory.")
    satellite_name = _extract_satellite_name(satellite_files[0])

    facility_files = sorted(export_dir.glob("Facility_*.fac"))
    facilities = [_extract_facility_name(path) for path in facility_files]

    application = _get_stk_application()
    root = application.Personality2

    _load_scenario(root, scenario_file)
    _load_facilities(root, export_dir, facilities)
    _import_auxiliary_products(root, export_dir, satellite_name, facilities)
    _configure_scene(root, summary, satellite_name, facilities)

    application.Visible = True
    application.UserControl = True
    return 0


if __name__ == "__main__":  # pragma: no cover - manual STK integration script
    raise SystemExit(main())
