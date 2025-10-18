"""Automate construction of the Tehran formation scenario inside STK 11.2.

The entry point couples the repository's lightweight propagation utilities
with the STK COM automation interface so analysts can recreate the
three-spacecraft formation without manually configuring the desktop
application. The workflow synthesises equilateral offsets for the formation,
exports STK-compliant ephemerides, and dispatches a sequence of Connect
commands that load the spacecraft, enable ground-track visualisations, and
configure the animation timeline. When STK is unavailable (for example on
non-Windows platforms) the script writes the Connect sequence to disk so it can
be executed later from an STK console session.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

import numpy as np

try:  # pragma: no cover - pywin32 is optional for non-Windows environments
    import win32com.client  # type: ignore
except Exception:  # pragma: no cover - maintain portability on Linux/macOS
    win32com = None  # type: ignore

from tools.stk_export import (
    GroundTrack,
    GroundTrackPoint,
    PropagatedStateHistory,
    ScenarioMetadata,
    SimulationResults,
    StateSample,
    export_simulation_to_stk,
)

from . import configuration
from . import run_scenario

LOGGER = logging.getLogger(__name__)


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Return command-line arguments guiding the automation flow."""

    parser = argparse.ArgumentParser(
        description=(
            "Automate STK 11.2 playback for the Tehran formation scenario, "
            "including ephemeris loading, ground tracks, and camera views."
        )
    )
    parser.add_argument(
        "scenario",
        nargs="?",
        default="tehran_triangle.json",
        help=(
            "Scenario identifier or path describing the Tehran formation. "
            "Defaults to 'tehran_triangle.json'."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artefacts") / "stk_runs",
        help="Directory for exported STK products and Connect scripts.",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Ensure the STK UI is visible when automation connects.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Skip COM execution and emit the Connect command sequence to "
            "disk for manual execution."
        ),
    )
    parser.add_argument(
        "--formation-side-length-km",
        type=float,
        default=None,
        help=(
            "Override the equilateral formation side length in kilometres. "
            "When omitted the configuration value is used."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity for the automation session.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Program entry point executed by the ``if __name__ == '__main__'`` guard."""

    args = parse_arguments(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    scenario_mapping = configuration.load_scenario(args.scenario)
    scenario_data = _normalise_scenario(scenario_mapping)

    LOGGER.info("Loaded scenario '%s'.", scenario_data["metadata"]["scenario_name"])

    nodes = run_scenario._generate_nodes(scenario_data)
    phases = run_scenario._generate_phases(scenario_data, nodes)
    two_body = run_scenario._propagate_two_body(scenario_data, phases)
    metadata = run_scenario._build_scenario_metadata(scenario_data, two_body)

    LOGGER.debug("Scenario start: %s, stop: %s.", metadata.start_epoch, metadata.stop_epoch)

    base_history, base_ground_track = run_scenario._generate_state_history(
        scenario_data, metadata, two_body
    )

    formation_spec = _derive_formation_specification(scenario_data, args.formation_side_length_km)
    histories, ground_tracks = _synthesise_formation_products(
        base_history,
        base_ground_track,
        metadata,
        formation_spec,
    )

    contacts = _duplicate_contacts(nodes, formation_spec.satellite_ids)
    facilities = run_scenario._collect_facilities(scenario_data, contacts)

    sim_results = SimulationResults(
        state_histories=histories,
        ground_tracks=ground_tracks,
        ground_contacts=contacts,
        facilities=facilities,
    )

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    export_dir = output_dir / "stk_export"
    export_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Exporting ephemerides to %s.", export_dir)
    export_simulation_to_stk(sim_results, export_dir, metadata)

    metrics = _summarise_formation_metrics(histories, metadata)
    _write_metrics(output_dir, metrics)
    _write_ground_tracks(output_dir, ground_tracks)

    commands = _compose_connect_commands(metadata, histories, export_dir, formation_spec)
    script_path = _write_connect_script(output_dir, commands)

    if args.dry_run:
        LOGGER.warning("Dry-run enabled; Connect commands saved to %s.", script_path)
        return 0

    if win32com is None:
        LOGGER.error(
            "pywin32 is unavailable. Install it and rerun without --dry-run to automate STK."
        )
        return 2

    _execute_connect_commands(commands, visible=args.visible)
    LOGGER.info("STK automation complete.")
    return 0


@dataclass(frozen=True)
class FormationSpecification:
    """Describe the satellites participating in the Tehran formation."""

    satellite_ids: Sequence[str]
    offsets_rtn_km: Sequence[Sequence[float]]
    side_length_km: float


def _normalise_scenario(source: Mapping[str, object]) -> MutableMapping[str, object]:
    """Translate legacy Tehran formation configs into the pipeline schema."""

    scenario = dict(source)
    metadata = scenario.get("metadata") if isinstance(scenario.get("metadata"), Mapping) else {}
    metadata = dict(metadata) if isinstance(metadata, Mapping) else {}
    metadata.setdefault("scenario_name", metadata.get("identifier", "Tehran Formation"))
    metadata.setdefault("identifier", metadata.get("scenario_name", "tehran_formation"))
    scenario["metadata"] = metadata

    if "orbital_elements" not in scenario:
        reference_orbit = scenario.get("reference_orbit")
        if isinstance(reference_orbit, Mapping):
            classical = {
                "semi_major_axis_km": float(reference_orbit.get("semi_major_axis_km", 7_000.0)),
                "eccentricity": float(reference_orbit.get("eccentricity", 0.0)),
                "inclination_deg": float(reference_orbit.get("inclination_deg", 97.7)),
                "raan_deg": float(reference_orbit.get("raan_deg", 0.0)),
                "argument_of_perigee_deg": float(reference_orbit.get("argument_of_perigee_deg", 0.0)),
                "mean_anomaly_deg": float(reference_orbit.get("mean_anomaly_deg", 0.0)),
            }
            scenario["orbital_elements"] = {
                "epoch_utc": reference_orbit.get("epoch_utc"),
                "frame": reference_orbit.get("frame", "TEME"),
                "classical": classical,
            }

    timing = scenario.get("timing") if isinstance(scenario.get("timing"), Mapping) else {}
    timing = dict(timing) if isinstance(timing, Mapping) else {}
    if "planning_horizon" not in timing:
        start = _parse_time(
            scenario.get("orbital_elements", {}).get("epoch_utc")
            if isinstance(scenario.get("orbital_elements"), Mapping)
            else None
        ) or datetime.now(timezone.utc)
        duration = 6_000.0
        formation = scenario.get("formation")
        if isinstance(formation, Mapping):
            duration = float(formation.get("duration_s", duration))
        timing["planning_horizon"] = {
            "start_utc": start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "stop_utc": (start + timedelta(seconds=duration)).astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
    timing.setdefault("daily_access_windows", [])
    scenario["timing"] = timing

    scenario.setdefault("payload_constraints", {})
    scenario.setdefault("operational_constraints", {})
    return scenario


def _parse_time(value: object) -> Optional[datetime]:
    """Parse ISO 8601 timestamps into aware datetimes."""

    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        text = value.replace("Z", "+00:00") if value.endswith("Z") else value
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def _derive_formation_specification(
    scenario: Mapping[str, object], override_side_length_km: Optional[float]
) -> FormationSpecification:
    """Determine satellite identifiers and RTN offsets for the formation."""

    formation = scenario.get("formation") if isinstance(scenario.get("formation"), Mapping) else {}
    plane_allocations = formation.get("plane_allocations") if isinstance(formation, Mapping) else {}
    if isinstance(plane_allocations, Mapping) and plane_allocations:
        satellite_ids = list(plane_allocations.keys())
    else:
        satellite_ids = ["SAT-1", "SAT-2", "SAT-3"]

    side_length_km = override_side_length_km
    if side_length_km is None:
        side_length_m = float(formation.get("side_length_m", 6_000.0)) if isinstance(formation, Mapping) else 6_000.0
        side_length_km = side_length_m / 1_000.0

    radius = side_length_km / math.sqrt(3.0)
    offsets = [
        (0.0, radius, 0.0),
        (-0.5 * side_length_km, -0.5 * radius, 0.0),
        (0.5 * side_length_km, -0.5 * radius, 0.0),
    ]
    if len(satellite_ids) > 3:
        extra_count = len(satellite_ids) - 3
        for index in range(extra_count):
            angle = 2.0 * math.pi * (index + 1) / len(satellite_ids)
            offsets.append(
                (
                    radius * math.cos(angle),
                    radius * math.sin(angle),
                    0.0,
                )
            )

    return FormationSpecification(
        satellite_ids=satellite_ids,
        offsets_rtn_km=offsets[: len(satellite_ids)],
        side_length_km=side_length_km,
    )


def _synthesise_formation_products(
    base_history: PropagatedStateHistory,
    base_ground_track: GroundTrack,
    metadata: ScenarioMetadata,
    formation_spec: FormationSpecification,
) -> tuple[list[PropagatedStateHistory], list[GroundTrack]]:
    """Apply RTN offsets to generate per-spacecraft histories and ground tracks."""

    histories: list[PropagatedStateHistory] = []
    ground_tracks: list[GroundTrack] = []

    for satellite_id, offset in zip(formation_spec.satellite_ids, formation_spec.offsets_rtn_km):
        samples: list[StateSample] = []
        track_points: list[GroundTrackPoint] = []
        for state_sample, track_point in zip(base_history.samples, base_ground_track.points):
            new_position = _apply_rtn_offset(state_sample.position_eci_km, state_sample.velocity_eci_kms, offset)
            samples.append(
                StateSample(
                    epoch=state_sample.epoch,
                    position_eci_km=new_position,
                    velocity_eci_kms=state_sample.velocity_eci_kms,
                )
            )

            latitude, longitude, altitude = run_scenario._eci_to_geodetic(
                new_position, metadata.start_epoch, state_sample.epoch
            )
            track_points.append(
                GroundTrackPoint(
                    epoch=track_point.epoch,
                    latitude_deg=latitude,
                    longitude_deg=longitude,
                    altitude_km=altitude,
                )
            )

        histories.append(PropagatedStateHistory(satellite_id=satellite_id, samples=samples))
        ground_tracks.append(GroundTrack(satellite_id=satellite_id, points=track_points))

    return histories, ground_tracks


def _apply_rtn_offset(
    position_eci_km: Sequence[float],
    velocity_eci_kms: Sequence[float],
    offset_rtn_km: Sequence[float],
) -> np.ndarray:
    """Translate an inertial position vector by an RTN offset in kilometres."""

    r_vec = np.asarray(position_eci_km, dtype=float)
    v_vec = np.asarray(velocity_eci_kms, dtype=float)
    offset = np.asarray(offset_rtn_km, dtype=float)

    r_norm = np.linalg.norm(r_vec)
    if r_norm == 0.0:
        return r_vec.copy()

    r_hat = r_vec / r_norm
    h_vec = np.cross(r_vec, v_vec)
    h_norm = np.linalg.norm(h_vec)
    if h_norm == 0.0:
        h_hat = np.array([0.0, 0.0, 1.0])
    else:
        h_hat = h_vec / h_norm
    t_hat = np.cross(h_hat, r_hat)

    offset_vector = offset[0] * r_hat + offset[1] * t_hat + offset[2] * h_hat
    return r_vec + offset_vector


def _duplicate_contacts(nodes: Sequence[run_scenario.Node], satellite_ids: Sequence[str]):
    """Copy ground-contact intervals for every satellite in the formation."""

    contacts = []
    for satellite_id in satellite_ids:
        contacts.extend(run_scenario._collect_ground_contacts(nodes, satellite_id))
    return contacts


def _summarise_formation_metrics(
    histories: Sequence[PropagatedStateHistory], metadata: ScenarioMetadata
) -> MutableMapping[str, object]:
    """Report separation statistics across the formation."""

    if not histories:
        return {"message": "No formation histories available."}

    by_epoch: dict[datetime, list[np.ndarray]] = {}
    for history in histories:
        for sample in history.samples:
            by_epoch.setdefault(sample.epoch, []).append(np.asarray(sample.position_eci_km, dtype=float))

    separation_records: list[float] = []
    for positions in by_epoch.values():
        if len(positions) < 2:
            continue
        for idx, primary in enumerate(positions[:-1]):
            for secondary in positions[idx + 1 :]:
                separation_records.append(float(np.linalg.norm(primary - secondary)))

    if not separation_records:
        return {"message": "Insufficient separation samples to compute metrics."}

    return {
        "scenario_name": metadata.scenario_name,
        "sample_count": len(separation_records),
        "mean_separation_km": float(np.mean(separation_records)),
        "min_separation_km": float(np.min(separation_records)),
        "max_separation_km": float(np.max(separation_records)),
    }


def _write_metrics(output_dir: Path, metrics: Mapping[str, object]) -> Path:
    """Persist formation metrics as a JSON document."""

    path = output_dir / "formation_metrics.json"
    path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    LOGGER.info("Formation metrics saved to %s.", path)
    return path


def _write_ground_tracks(output_dir: Path, tracks: Sequence[GroundTrack]) -> None:
    """Write CSV ground-track overlays for visual verification."""

    track_dir = output_dir / "ground_tracks"
    track_dir.mkdir(parents=True, exist_ok=True)

    for track in tracks:
        path = track_dir / f"{track.satellite_id.lower().replace(' ', '_')}_ground_track.csv"
        with path.open("w", encoding="utf-8") as handle:
            handle.write("epoch_utc,latitude_deg,longitude_deg,altitude_km\n")
            for point in track.points:
                handle.write(
                    f"{point.epoch.isoformat().replace('+00:00', 'Z')},{point.latitude_deg:.6f},{point.longitude_deg:.6f},{point.altitude_km:.3f}\n"
                )
        LOGGER.debug("Ground track written to %s.", path)


def _compose_connect_commands(
    metadata: ScenarioMetadata,
    histories: Sequence[PropagatedStateHistory],
    export_dir: Path,
    formation_spec: FormationSpecification,
) -> list[str]:
    """Assemble STK Connect commands that configure the scenario."""

    def fmt(epoch: datetime) -> str:
        return epoch.strftime("%d %b %Y %H:%M:%S.%f")[:-3]

    start = fmt(metadata.start_epoch)
    stop = fmt(metadata.stop_epoch or metadata.start_epoch + timedelta(hours=1))
    step = metadata.animation_step_seconds or 60.0

    commands = [
        "UnloadAll /",
        f"New / Scenario {metadata.scenario_name}",
        f"SetTimePeriod * \"{start}\" \"{stop}\"",
        "Animate * Reset",
        f"Animate * SetValues TimeStep {step:.1f}",
    ]

    primary_id = histories[0].satellite_id if histories else "SAT-1"
    colours = ["red", "green", "blue", "yellow", "cyan", "magenta"]

    for index, history in enumerate(histories):
        satellite_id = history.satellite_id
        colour = colours[index % len(colours)]
        ephemeris_path = export_dir / f"{satellite_id}.e"
        commands.extend(
            [
                f"New / */Satellite {satellite_id}",
                f"SetState */Satellite/{satellite_id} External File \"{ephemeris_path}\"",
                f"Graphics */Satellite/{satellite_id} TrackType GroundTrack On",
                f"Graphics */Satellite/{satellite_id} GroundTrack Show On",
                f"Graphics */Satellite/{satellite_id} GroundTrack LineColor {colour}",
                f"VO */Satellite/{satellite_id} Inherit Off",
                f"VO */Satellite/{satellite_id} ModelAttributes ShowLabel On",
            ]
        )

    commands.extend(
        [
            f"VO * View FromTo FromObject */Satellite/{primary_id} ToObject */Earth",
            f"VO * View Attach Center */Earth Fixed {formation_spec.side_length_km * 3.0:.1f}",
            "VO * Lighting Sun On",
            "Animate * Start",
        ]
    )

    return commands


def _write_connect_script(output_dir: Path, commands: Sequence[str]) -> Path:
    """Persist Connect commands for manual execution inside STK."""

    script_path = output_dir / "stk_connect_script.txt"
    script_path.write_text("\n".join(commands) + "\n", encoding="utf-8")
    LOGGER.info("Connect commands saved to %s.", script_path)
    return script_path


def _execute_connect_commands(commands: Iterable[str], *, visible: bool) -> None:
    """Send Connect commands to an STK 11.2 instance via COM automation."""

    LOGGER.info("Connecting to STK 11.2 via COM automation.")
    application = win32com.client.Dispatch("STK11.Application")
    application.Visible = bool(visible)
    application.UserControl = True
    root = application.Personality2

    for command in commands:
        LOGGER.debug("Executing: %s", command)
        root.ExecuteCommand(command)


if __name__ == "__main__":  # pragma: no cover - command-line execution guard
    raise SystemExit(main())
