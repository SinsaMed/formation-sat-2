"""Command-line entry point for the lightweight scenario pipeline.

The runner orchestrates the placeholder formation-flying workflow used by the
continuous integration (CI) smoke tests.  Although the numerical models remain
rudimentary, the script reflects the order of operations expected from the
future high-fidelity pipeline:

1. Discover access nodes describing imaging and downlink opportunities.
2. Translate nodes into mission phases with basic timing metadata.
3. Propagate the constellation with a two-body approximation.
4. Apply simple corrections representing J2 and atmospheric drag effects.
5. Derive headline metrics that downstream reporting utilities can consume.

Each stage records a summary that is serialisable to JavaScript Object Notation
(JSON) and therefore importable into Systems Tool Kit (STK 11.2) validation
workflows.  The CLI accepts either a named scenario (resolved relative to the
``config/scenarios`` directory) or an explicit configuration file path.
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

from constellation.orbit import geodetic_coordinates, inertial_to_ecef, propagate_kepler
from constellation.roe import OrbitalElements

from tools.stk_export import (
    FacilityDefinition,
    GroundContactInterval,
    GroundTrack,
    GroundTrackPoint,
    PropagatedStateHistory,
    ScenarioMetadata,
    SimulationResults,
    StateSample,
    export_simulation_to_stk,
)

from . import configuration

LOGGER = logging.getLogger(__name__)

MU_EARTH_KM3_S2 = 398_600.4418
EARTH_RADIUS_KM = 6_378.1363
MU_EARTH_M3_S2 = 3.986_004_418e14

_KNOWN_FACILITY_COORDINATES = {
    "Svalbard": (78.229, 15.407, 0.0),
    "Inuvik": (68.360, -133.703, 0.0),
}


@dataclass
class Node:
    """Mission node capturing contact opportunities or operational windows."""

    identifier: int
    label: str
    kind: str
    start: Optional[datetime]
    end: Optional[datetime]
    duration_s: float
    attributes: MutableMapping[str, object]

    def as_dict(self) -> MutableMapping[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "id": self.identifier,
            "label": self.label,
            "type": self.kind,
            "start": _format_time(self.start),
            "end": _format_time(self.end),
            "duration_s": float(self.duration_s),
            "attributes": dict(self.attributes),
        }


@dataclass
class Phase:
    """Mission phase derived from the access node plan."""

    identifier: int
    node_id: Optional[int]
    objective: str
    start: Optional[datetime]
    end: Optional[datetime]
    duration_s: float

    def as_dict(self) -> MutableMapping[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "id": self.identifier,
            "node_id": self.node_id,
            "objective": self.objective,
            "start": _format_time(self.start),
            "end": _format_time(self.end),
            "duration_s": float(self.duration_s),
        }


def run_scenario(
    config_source: configuration.ConfigSource,
    output_directory: Optional[Path | str] = None,
    *,
    metrics_specification: Optional[Sequence[str]] = None,
) -> MutableMapping[str, object]:
    """Execute the sequential scenario pipeline."""

    scenario = _load_configuration(config_source)
    LOGGER.debug("Loaded scenario configuration with keys: %s", list(scenario))

    stage_sequence: list[str] = []

    nodes = _generate_nodes(scenario)
    stage_sequence.append("access_nodes")
    LOGGER.info("Identified %d mission nodes.", len(nodes))

    phases = _generate_phases(scenario, nodes)
    stage_sequence.append("mission_phases")
    LOGGER.info("Synthesised %d mission phases.", len(phases))

    two_body = _propagate_two_body(scenario, phases)
    stage_sequence.append("two_body_propagation")
    LOGGER.info(
        "Two-body propagation yielded an orbital period of %.2f s.",
        two_body["orbital_period_s"],
    )

    perturbed = _apply_j2_drag(two_body, phases, scenario)
    stage_sequence.append("j2_drag_propagation")
    LOGGER.info(
        "Perturbed propagation adjusts the orbital period by %.3f s.",
        perturbed["orbital_period_s"] - two_body["orbital_period_s"],
    )

    metrics = _summarise_metrics(nodes, phases, two_body, perturbed, metrics_specification)
    stage_sequence.append("metric_extraction")
    LOGGER.info(
        "Metric extraction complete: %s.",
        {key: metrics[key] for key in ("node_count", "phase_count", "total_contact_duration_s")},
    )

    summary = {
        "configuration_summary": _summarise_configuration(scenario),
        "nodes": [node.as_dict() for node in nodes],
        "phases": [phase.as_dict() for phase in phases],
        "propagation": {"two_body": two_body, "j2_drag": perturbed},
        "metrics": metrics,
        "stage_sequence": stage_sequence,
    }

    artefacts: MutableMapping[str, Optional[str]] = {"summary_path": None, "stk_directory": None}
    if output_directory:
        output_root = Path(output_directory)
        output_path = _write_summary(output_root, summary)
        artefacts["summary_path"] = str(output_path)
        LOGGER.info("Scenario summary written to %s", output_path)

        try:
            stk_dir = _export_stk_products(
                output_root / "stk_export",
                scenario,
                two_body,
            )
        except Exception as exc:
            LOGGER.error("Failed to export STK artefacts: %s", exc)
            stk_dir = None
        else:
            artefacts["stk_directory"] = str(stk_dir)
            stage_sequence.append("stk_export")
            LOGGER.info("STK artefacts written to %s", stk_dir)

    summary["artefacts"] = artefacts
    return summary


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the scenario runner."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario",
        nargs="?",
        help=(
            "Scenario identifier or configuration file path."
            " Defaults to the canonical Tehran daily pass scenario."
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Explicit configuration file path overriding the scenario identifier.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory in which to store the pipeline summary JSON file.",
    )
    parser.add_argument(
        "--metrics",
        nargs="*",
        metavar="METRIC",
        help="Optional list of metric identifiers to prioritise in the summary.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity for diagnostic output.",
    )
    return parser.parse_args(args)


def main(args: Optional[Iterable[str]] = None) -> int:
    """Entry point enabling ``python -m sim.scripts.run_scenario`` execution."""

    namespace = parse_args(args)
    logging.basicConfig(level=getattr(logging, namespace.log_level))

    config_source: configuration.ConfigSource
    if namespace.config:
        config_source = namespace.config
    elif namespace.scenario:
        config_source = namespace.scenario
    else:
        config_source = "tehran_daily_pass"

    results = run_scenario(
        config_source,
        output_directory=namespace.output_dir,
        metrics_specification=namespace.metrics,
    )

    stage_description = ", ".join(results["stage_sequence"])
    identifier = results["configuration_summary"].get("identifier")
    display_name = results["configuration_summary"].get("name", identifier or "scenario")
    print(f"Executed scenario '{display_name}' with stages: {stage_description}.")
    summary_path = results["artefacts"].get("summary_path")
    if summary_path:
        print(f"Summary written to {summary_path}.")
    return 0


def _load_configuration(source: configuration.ConfigSource) -> MutableMapping[str, object]:
    """Load or copy the scenario configuration from *source*."""

    if isinstance(source, Mapping):
        return dict(source)
    return configuration.load_scenario(source)


def _generate_nodes(scenario: Mapping[str, object]) -> list[Node]:
    """Create mission nodes from access windows or contact plans."""

    nodes: list[Node] = []
    timing = scenario.get("timing", {}) if isinstance(scenario.get("timing"), Mapping) else {}
    windows = timing.get("daily_access_windows", [])

    if isinstance(windows, Sequence) and windows:
        for index, window in enumerate(windows, start=1):
            if not isinstance(window, Mapping):
                continue
            start = _parse_time(window.get("start_utc"))
            end = _parse_time(window.get("end_utc"))
            duration = _duration_seconds(start, end)
            attributes = {
                key: value
                for key, value in window.items()
                if key not in {"label", "start_utc", "end_utc"}
            }
            nodes.append(
                Node(
                    identifier=index,
                    label=str(window.get("label", f"window-{index}")),
                    kind="access_window",
                    start=start,
                    end=end,
                    duration_s=duration,
                    attributes=dict(attributes),
                )
            )

    if nodes:
        return nodes

    contact_plan = scenario.get("contact_plan")
    ground_sites: Iterable[Mapping[str, object]] = []
    if isinstance(contact_plan, Mapping):
        sites = contact_plan.get("ground_sites", [])
        if isinstance(sites, Sequence):
            ground_sites = [site for site in sites if isinstance(site, Mapping)]

    for index, site in enumerate(ground_sites, start=1):
        attributes = {key: value for key, value in site.items() if key != "name"}
        nodes.append(
            Node(
                identifier=index,
                label=str(site.get("name", f"ground-site-{index}")),
                kind="ground_contact",
                start=None,
                end=None,
                duration_s=0.0,
                attributes=dict(attributes),
            )
        )

    if not nodes:
        nodes.append(
            Node(
                identifier=1,
                label="mission_start",
                kind="initial_condition",
                start=_parse_time(_extract_planning_horizon(scenario, "start_utc")),
                end=None,
                duration_s=0.0,
                attributes={},
            )
        )

    return nodes


def _generate_phases(scenario: Mapping[str, object], nodes: Sequence[Node]) -> list[Phase]:
    """Create mission phases aligned with the access nodes."""

    phases: list[Phase] = []
    planning_start = _parse_time(_extract_planning_horizon(scenario, "start_utc"))
    planning_end = _parse_time(_extract_planning_horizon(scenario, "stop_utc"))

    if nodes:
        for index, node in enumerate(nodes, start=1):
            start = node.start or planning_start
            end = node.end or planning_end or start
            duration = _duration_seconds(start, end)
            objective = (
                f"Support {node.label}" if node.kind == "ground_contact" else node.label
            )
            phases.append(
                Phase(
                    identifier=index,
                    node_id=node.identifier,
                    objective=objective,
                    start=start,
                    end=end,
                    duration_s=duration,
                )
            )

    if not phases:
        duration = _estimate_duration(scenario)
        phases.append(
            Phase(
                identifier=1,
                node_id=None,
                objective="Mission timeline",
                start=planning_start,
                end=planning_end,
                duration_s=duration,
            )
        )

    return phases


def _propagate_two_body(
    scenario: Mapping[str, object],
    phases: Sequence[Phase],
) -> MutableMapping[str, float | Sequence[MutableMapping[str, float]]]:
    """Compute a coarse two-body propagation summary."""

    semi_major_axis_km = _infer_semi_major_axis_km(scenario)
    period = 2.0 * math.pi * math.sqrt((semi_major_axis_km**3) / MU_EARTH_KM3_S2)
    mean_motion_rev_per_day = 86_400.0 / period if period else 0.0

    phase_revolutions = []
    for phase in phases:
        revolutions = phase.duration_s / period if period else 0.0
        phase_revolutions.append(
            {
                "phase_id": float(phase.identifier),
                "revolutions": float(revolutions),
            }
        )

    return {
        "model": "two_body",
        "semi_major_axis_km": float(semi_major_axis_km),
        "orbital_period_s": float(period),
        "mean_motion_rev_per_day": float(mean_motion_rev_per_day),
        "phase_revolutions": phase_revolutions,
    }


def _apply_j2_drag(
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
    phases: Sequence[Phase],
    scenario: Mapping[str, object],
) -> MutableMapping[str, float | Sequence[MutableMapping[str, float]]]:
    """Apply simplified J2 and drag corrections to the propagation."""

    period = float(two_body.get("orbital_period_s", 0.0))
    semi_major_axis = float(two_body.get("semi_major_axis_km", 0.0))
    altitude = max(semi_major_axis - EARTH_RADIUS_KM, 0.0)

    j2_factor = 1.0 - 1.5e-6 * altitude
    average_phase_duration = sum(phase.duration_s for phase in phases) / max(len(phases), 1)
    drag_factor = 1.0 - 5.0e-6 * (average_phase_duration / 600.0)
    correction = max(j2_factor * drag_factor, 0.0)

    perturbed_period = period * correction if period else 0.0
    period_delta = perturbed_period - period

    decay_per_orbit_m = altitude * 1_000.0 * 1.0e-5

    phase_decay: list[MutableMapping[str, float]] = []
    for phase in phases:
        revolutions = phase.duration_s / period if period else 0.0
        phase_decay.append(
            {
                "phase_id": float(phase.identifier),
                "expected_decay_m": float(revolutions * decay_per_orbit_m),
            }
        )

    simulation = scenario.get("simulation")
    force_notes = "J2+drag"
    if isinstance(simulation, Mapping):
        force_models = simulation.get("force_models")
        if isinstance(force_models, Mapping):
            enabled = [model for model, flag in force_models.items() if flag]
            if enabled:
                force_notes = "+".join(enabled)

    return {
        "model": force_notes,
        "orbital_period_s": float(perturbed_period),
        "period_delta_s": float(period_delta),
        "average_drag_decay_m": float(decay_per_orbit_m),
        "phase_decay": phase_decay,
    }


def _summarise_metrics(
    nodes: Sequence[Node],
    phases: Sequence[Phase],
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
    perturbed: Mapping[str, float | Sequence[Mapping[str, float]]],
    metrics_specification: Optional[Sequence[str]] = None,
) -> MutableMapping[str, float]:
    """Return descriptive metrics for quick-look validation."""

    node_count = float(len(nodes))
    phase_count = float(len(phases))
    total_contact = float(sum(node.duration_s for node in nodes))

    orbital_period_nominal = float(two_body.get("orbital_period_s", 0.0))
    orbital_period_perturbed = float(perturbed.get("orbital_period_s", 0.0))
    orbital_delta = orbital_period_perturbed - orbital_period_nominal

    phase_revolutions = two_body.get("phase_revolutions", [])
    average_revolutions = 0.0
    if isinstance(phase_revolutions, Sequence) and phase_revolutions:
        average_revolutions = float(
            sum(item.get("revolutions", 0.0) for item in phase_revolutions)
            / len(phase_revolutions)
        )

    metrics: MutableMapping[str, float] = {
        "node_count": node_count,
        "phase_count": phase_count,
        "total_contact_duration_s": total_contact,
        "orbital_period_nominal_s": orbital_period_nominal,
        "orbital_period_perturbed_s": orbital_period_perturbed,
        "orbital_period_delta_s": float(orbital_delta),
        "average_revolutions_per_phase": average_revolutions,
    }

    if metrics_specification:
        # Retain ordering requested by the caller while keeping the full set in the map.
        prioritised = {metric: metrics.get(metric, 0.0) for metric in metrics_specification}
        metrics.update({f"priority::{key}": value for key, value in prioritised.items()})

    return metrics


def _summarise_configuration(scenario: Mapping[str, object]) -> MutableMapping[str, object]:
    """Condense salient configuration fields for reporting."""

    summary: MutableMapping[str, object] = {}
    metadata = scenario.get("metadata")
    if isinstance(metadata, Mapping):
        summary["identifier"] = metadata.get("identifier") or metadata.get("scenario_name")
        summary["name"] = metadata.get("scenario_name") or metadata.get("identifier")
        if "description" in metadata:
            summary["description"] = metadata["description"]
        if "author" in metadata:
            summary["author"] = metadata["author"]
        if "validated_against_stk_export" in metadata:
            summary["validated_against_stk_export"] = bool(
                metadata["validated_against_stk_export"]
            )

    if "mission_name" in scenario and "name" not in summary:
        summary["name"] = scenario["mission_name"]
    if "mission_name" in scenario and "identifier" not in summary:
        summary["identifier"] = scenario["mission_name"]

    duration_hours = scenario.get("duration_hours")
    if isinstance(duration_hours, (int, float)):
        summary["duration_hours"] = float(duration_hours)

    timing = scenario.get("timing")
    if isinstance(timing, Mapping):
        planning_horizon = timing.get("planning_horizon")
        if isinstance(planning_horizon, Mapping):
            summary["planning_horizon"] = {
                key: planning_horizon.get(key)
                for key in ("start_utc", "stop_utc")
                if planning_horizon.get(key) is not None
            }

    return summary


def _write_summary(output_dir: Path, summary: Mapping[str, object]) -> Path:
    """Persist the pipeline summary to *output_dir*."""

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "scenario_summary.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _export_stk_products(
    export_dir: Path,
    scenario: Mapping[str, object],
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
) -> Path:
    """Generate STK artefacts derived from the simplified propagation."""

    elements, epoch = _scenario_elements_and_epoch(scenario)
    state_samples, ground_track_points, step = _sample_state_history(elements, epoch, two_body)

    satellite_id = _scenario_satellite_identifier(scenario)
    contacts = _derive_ground_contacts(scenario, satellite_id)
    facilities = _derive_facilities(scenario, contacts)

    if state_samples:
        start_epoch = state_samples[0].epoch
        stop_epoch = state_samples[-1].epoch
    else:  # pragma: no cover - guard against degenerate sampling
        start_epoch = epoch
        stop_epoch = epoch

    scenario_metadata = ScenarioMetadata(
        scenario_name=_scenario_name(scenario),
        start_epoch=start_epoch,
        stop_epoch=stop_epoch,
        central_body="Earth",
        coordinate_frame="TEME",
        ephemeris_step_seconds=step,
        animation_step_seconds=step,
    )

    results = SimulationResults(
        state_histories=[
            PropagatedStateHistory(satellite_id=satellite_id, samples=state_samples)
        ],
        ground_tracks=[GroundTrack(satellite_id=satellite_id, points=ground_track_points)],
        ground_contacts=contacts,
        facilities=facilities,
    )

    export_dir.mkdir(parents=True, exist_ok=True)
    export_simulation_to_stk(results, export_dir, scenario_metadata)
    return export_dir


def _scenario_name(scenario: Mapping[str, object]) -> str:
    metadata = scenario.get("metadata")
    if isinstance(metadata, Mapping):
        for key in ("scenario_name", "name", "identifier"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return "scenario"


def _scenario_satellite_identifier(scenario: Mapping[str, object]) -> str:
    metadata = scenario.get("metadata")
    if isinstance(metadata, Mapping):
        identifier = metadata.get("identifier") or metadata.get("scenario_name")
        if isinstance(identifier, str) and identifier.strip():
            return f"{identifier}_spacecraft"
    return "mission_spacecraft"


def _scenario_elements_and_epoch(
    scenario: Mapping[str, object]
) -> tuple[OrbitalElements, datetime]:
    orbital = scenario.get("orbital_elements")
    classical = orbital.get("classical", {}) if isinstance(orbital, Mapping) else {}

    semi_major_axis_km = _safe_float(classical.get("semi_major_axis_km"), 7_000.0)
    eccentricity = _safe_float(classical.get("eccentricity"), 0.0)
    inclination_deg = _safe_float(classical.get("inclination_deg"), 0.0)
    raan_deg = _safe_float(classical.get("raan_deg"), 0.0)
    arg_perigee_deg = _safe_float(classical.get("argument_of_perigee_deg"), 0.0)
    mean_anomaly_deg = _safe_float(classical.get("mean_anomaly_deg"), 0.0)

    elements = OrbitalElements(
        semi_major_axis=float(semi_major_axis_km) * 1_000.0,
        eccentricity=float(eccentricity),
        inclination=math.radians(float(inclination_deg)),
        raan=math.radians(float(raan_deg)),
        arg_perigee=math.radians(float(arg_perigee_deg)),
        mean_anomaly=math.radians(float(mean_anomaly_deg)),
    )

    epoch = None
    if isinstance(orbital, Mapping):
        epoch = _parse_time(orbital.get("epoch_utc"))
    if epoch is None:
        epoch = _parse_time(_extract_planning_horizon(scenario, "start_utc"))
    if epoch is None:
        epoch = datetime.now(timezone.utc)

    return elements, epoch


def _sample_state_history(
    elements: OrbitalElements,
    epoch: datetime,
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
) -> tuple[list[StateSample], list[GroundTrackPoint], float]:
    period = float(two_body.get("orbital_period_s", 0.0)) or 5_400.0
    sample_step = _determine_sample_step(period)
    sample_count = max(int(math.ceil(period / sample_step)) + 1, 2)

    samples: list[StateSample] = []
    ground_points: list[GroundTrackPoint] = []

    for index in range(sample_count):
        delta_t = float(index) * sample_step
        sample_epoch = epoch + timedelta(seconds=delta_t)
        position_m, velocity_mps = propagate_kepler(elements, delta_t, mu=MU_EARTH_M3_S2)
        position_km = np.asarray(position_m, dtype=float) / 1_000.0
        velocity_kms = np.asarray(velocity_mps, dtype=float) / 1_000.0
        samples.append(
            StateSample(
                epoch=sample_epoch,
                position_eci_km=position_km,
                velocity_eci_kms=velocity_kms,
                frame="TEME",
            )
        )

        ecef_position = inertial_to_ecef(position_m, sample_epoch)
        latitude, longitude, altitude = geodetic_coordinates(ecef_position)
        ground_points.append(
            GroundTrackPoint(
                epoch=sample_epoch,
                latitude_deg=math.degrees(latitude),
                longitude_deg=_wrap_longitude(math.degrees(longitude)),
                altitude_km=float(altitude) / 1_000.0,
            )
        )

    return samples, ground_points, sample_step


def _determine_sample_step(period: float) -> float:
    if period <= 0.0:
        return 60.0
    return float(max(10.0, min(period / 120.0, 120.0)))


def _derive_ground_contacts(
    scenario: Mapping[str, object], satellite_id: str
) -> list[GroundContactInterval]:
    contacts: list[GroundContactInterval] = []
    timing = scenario.get("timing")
    windows = timing.get("daily_access_windows", []) if isinstance(timing, Mapping) else []

    for window in windows:
        if not isinstance(window, Mapping):
            continue
        start = _parse_time(window.get("start_utc"))
        end = _parse_time(window.get("end_utc"))
        if start is None or end is None:
            continue
        facility = window.get("ground_station") or window.get("target") or window.get("label")
        facility_name = str(facility) if facility is not None else "access_window"
        contacts.append(
            GroundContactInterval(
                satellite_id=satellite_id,
                facility_name=facility_name,
                start=start,
                end=end,
            )
        )

    return contacts


def _derive_facilities(
    scenario: Mapping[str, object], contacts: Sequence[GroundContactInterval]
) -> list[FacilityDefinition]:
    facilities: list[FacilityDefinition] = []
    recorded: set[str] = set()

    def add_facility(name: str, latitude: float, longitude: float, altitude: float = 0.0) -> None:
        if name in recorded:
            return
        facilities.append(
            FacilityDefinition(
                name=name,
                latitude_deg=float(latitude),
                longitude_deg=float(longitude),
                altitude_km=float(altitude),
            )
        )
        recorded.add(name)

    metadata = scenario.get("metadata")
    region_coordinates: Optional[tuple[float, float, float]] = None
    if isinstance(metadata, Mapping):
        region = metadata.get("region")
        if isinstance(region, Mapping):
            latitude = region.get("latitude_deg")
            longitude = region.get("longitude_deg")
            if latitude is not None and longitude is not None:
                target_name = str(region.get("target_name") or region.get("city") or "Target")
                latitude_f = float(latitude)
                longitude_f = float(longitude)
                region_coordinates = (latitude_f, longitude_f, 0.0)
                add_facility(target_name, latitude_f, longitude_f, 0.0)

    timing = scenario.get("timing")
    windows = timing.get("daily_access_windows", []) if isinstance(timing, Mapping) else []
    for window in windows:
        if not isinstance(window, Mapping):
            continue
        ground_station = window.get("ground_station")
        if isinstance(ground_station, str):
            coordinates = _KNOWN_FACILITY_COORDINATES.get(ground_station)
            if coordinates is not None:
                add_facility(ground_station, *coordinates)
        target_name = window.get("target")
        if isinstance(target_name, str) and region_coordinates is not None:
            add_facility(target_name, *region_coordinates)

    for contact in contacts:
        if contact.facility_name not in recorded:
            add_facility(contact.facility_name, 0.0, 0.0, 0.0)

    return facilities


def _wrap_longitude(longitude_deg: float) -> float:
    wrapped = (longitude_deg + 180.0) % 360.0 - 180.0
    if wrapped == -180.0:
        return 180.0
    return wrapped


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float(default)


def _parse_time(value: object) -> Optional[datetime]:
    """Parse ISO 8601 timestamps into timezone-aware datetimes."""

    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
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


def _format_time(value: Optional[datetime]) -> Optional[str]:
    """Convert datetimes back to ISO 8601 strings with ``Z`` designators."""

    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _duration_seconds(start: Optional[datetime], end: Optional[datetime]) -> float:
    """Return the non-negative duration between *start* and *end*."""

    if start is None or end is None:
        return 0.0
    return max((end - start).total_seconds(), 0.0)


def _extract_planning_horizon(scenario: Mapping[str, object], key: str) -> Optional[str]:
    """Fetch a planning horizon field from the configuration if present."""

    timing = scenario.get("timing")
    if not isinstance(timing, Mapping):
        return None
    horizon = timing.get("planning_horizon")
    if not isinstance(horizon, Mapping):
        return None
    value = horizon.get(key)
    return str(value) if value is not None else None


def _estimate_duration(scenario: Mapping[str, object]) -> float:
    """Derive a representative mission duration in seconds."""

    duration_hours = scenario.get("duration_hours")
    if isinstance(duration_hours, (int, float)):
        return float(duration_hours) * 3_600.0

    start = _parse_time(_extract_planning_horizon(scenario, "start_utc"))
    end = _parse_time(_extract_planning_horizon(scenario, "stop_utc"))
    return _duration_seconds(start, end)


def _infer_semi_major_axis_km(scenario: Mapping[str, object]) -> float:
    """Infer the semi-major axis from the configuration with sensible defaults."""

    orbital_elements = scenario.get("orbital_elements")
    if isinstance(orbital_elements, Mapping):
        classical = orbital_elements.get("classical")
        if isinstance(classical, Mapping) and "semi_major_axis_km" in classical:
            try:
                return float(classical["semi_major_axis_km"])
            except (TypeError, ValueError):
                pass

    spacecraft = scenario.get("spacecraft")
    if isinstance(spacecraft, Sequence) and spacecraft:
        axes: list[float] = []
        for craft in spacecraft:
            if not isinstance(craft, Mapping):
                continue
            state = craft.get("initial_state")
            if not isinstance(state, Mapping):
                continue
            semi_major_axis_m = state.get("semi_major_axis_m")
            if isinstance(semi_major_axis_m, (int, float)):
                axes.append(float(semi_major_axis_m) / 1_000.0)
        if axes:
            return sum(axes) / len(axes)

    return 7_000.0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI tests.
    raise SystemExit(main())

