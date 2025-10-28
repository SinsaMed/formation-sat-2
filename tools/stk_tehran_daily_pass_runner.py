"""Automate STK 11.2 playback for the Tehran daily pass scenario export."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import comtypes
import comtypes.client


@dataclass(frozen=True)
class FacilityArtefact:
    """Container for exported facility metadata."""

    path: Path
    name: str
    alias: str


def _format_object_path(object_type: str, identifier: str) -> str:
    """Return a Connect object path, quoting the identifier when needed."""

    escaped = identifier.replace("\"", r"\"")
    if any(char.isspace() for char in escaped) or any(char in escaped for char in "\\/"):
        escaped = f'"{escaped}"'
    return f"*/{object_type}/{escaped}"


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


def _configure_scene(
    root,
    summary: dict[str, object],
    satellite_name: str,
    facilities: list[FacilityArtefact],
) -> None:
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
    satellite_path = _format_object_path("Satellite", satellite_name)
    root.ExecuteCommand(f"Graphics {satellite_path} Attitude Update Off")
    root.ExecuteCommand(f"Graphics {satellite_path} Pass3D Show On")
    root.ExecuteCommand(f"Graphics {satellite_path} GroundTrack Show On")
    root.ExecuteCommand(f"VO {satellite_path} Lighting Sunlight On")

    if facilities:
        facility = facilities[0]
        facility_path = _format_object_path("Facility", facility.name)
        root.ExecuteCommand(
            f"VO * ViewFromTo Normal {facility_path} {satellite_path} Fixed"
        )
        root.ExecuteCommand(
            f"VO {satellite_path} ShowTrailingLeadVectors GroundTrack Both 3600"
        )


def _import_auxiliary_products(
    root,
    export_dir: Path,
    satellite_name: str,
    satellite_alias: str,
    facilities: list[FacilityArtefact],
) -> None:
    """Load ground-track and contact interval files into the active scenario."""

    satellite_path = _format_object_path("Satellite", satellite_name)
    ground_track = export_dir / f"{satellite_alias}_groundtrack.gt"
    if ground_track.exists():
        root.ExecuteCommand(
            f"ImportDataFile {satellite_path} GroundTrack \"{ground_track}\""
        )

    for facility in facilities:
        interval_file = export_dir / f"Contacts_{facility.alias}.int"
        if interval_file.exists():
            root.ExecuteCommand(
                f"ImportDataFile {satellite_path} IntervalList \"{interval_file}\""
            )


def _load_facilities(root, facilities: list[FacilityArtefact]) -> None:
    """Ensure facility geometry is present in the scenario."""

    for facility in facilities:
        root.ExecuteCommand(f"Load / */Facility \"{facility.path}\"")

    for facility in facilities:
        facility_path = _format_object_path("Facility", facility.name)
        root.ExecuteCommand(f"VO {facility_path} ShowAzElMask Off")
        root.ExecuteCommand(f"VO {facility_path} ShowAxes Off")


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
    satellite_file = satellite_files[0]
    satellite_name = _extract_satellite_name(satellite_file)
    satellite_alias = satellite_file.stem

    facility_files = sorted(export_dir.glob("Facility_*.fac"))
    facilities = [
        FacilityArtefact(
            path=facility_file,
            name=_extract_facility_name(facility_file),
            alias=facility_file.stem.replace("Facility_", ""),
        )
        for facility_file in facility_files
    ]

    application = _get_stk_application()
    root = application.Personality2

    _load_scenario(root, scenario_file)
    _load_facilities(root, facilities)
    _import_auxiliary_products(root, export_dir, satellite_name, satellite_alias, facilities)
    _configure_scene(root, summary, satellite_name, facilities)

    application.Visible = True
    application.UserControl = True
    return 0


if __name__ == "__main__":  # pragma: no cover - manual STK integration script
    raise SystemExit(main())
