r"""Command-line entry point for the lightweight scenario pipeline.

The runner orchestrates the placeholder formation-flying workflow used by the
continuous integration (CI) smoke tests.  Although the numerical models remain
rudimentary, the script reflects the order of operations expected from the
future high-fidelity pipeline:

1. Discover access nodes describing imaging and downlink opportunities.
2. Translate nodes into mission phases with basic timing metadata.
3. Propagate the constellation with a two-body approximation.
4. Propagate with a high-fidelity \(J_2\)+drag force model capturing cross-track
   behaviour for each vehicle.
5. Derive headline metrics that downstream reporting utilities can consume.

Each stage records a summary that is serialisable to JavaScript Object Notation
(JSON) and therefore importable into Systems Tool Kit (STK 11.2) validation
workflows.  The CLI accepts either a named scenario (resolved relative to the
``config/scenarios`` directory) or an explicit configuration file path.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import fmean
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

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
from . import perturbation_analysis

LOGGER = logging.getLogger(__name__)

MU_EARTH_KM3_S2 = 398_600.4418
EARTH_RADIUS_KM = 6_378.1363
EARTH_ROTATION_RATE_RAD_S = 7.2921159e-5


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

    raan_alignment = _resolve_raan_alignment(scenario)
    if raan_alignment:
        stage_sequence.append("raan_alignment")
        best = raan_alignment.get("best_evaluation", {})
        LOGGER.info(
            "Optimised RAAN from %.6f° to %.6f°; centroid |cross-track| at midpoint: %.3f km.",
            raan_alignment.get("initial_raan_deg", 0.0),
            raan_alignment.get("optimised_raan_deg", 0.0),
            float(best.get("centroid_abs_cross_track_km", math.inf)),
        )

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

    perturbed, propagation_artefacts = _apply_j2_drag(
        two_body,
        phases,
        scenario,
        output_directory=output_directory,
        raan_alignment=raan_alignment,
    )
    stage_sequence.append("high_fidelity_j2_drag_propagation")
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

    stk_export_summary: MutableMapping[str, object] = {}
    if output_directory is not None:
        export_dir = Path(output_directory)
        stk_export_summary = _export_stk_products(
            export_dir,
            scenario,
            nodes,
            two_body,
        )
        if stk_export_summary:
            stage_sequence.append("stk_export")
            LOGGER.info(
                "STK export created with artefacts: %s.",
                stk_export_summary.get("stk_export_files", []),
            )
    else:
        LOGGER.debug("Skipping STK export because no output directory was provided.")

    summary: MutableMapping[str, object] = {
        "configuration_summary": _summarise_configuration(scenario),
        "nodes": [node.as_dict() for node in nodes],
        "phases": [phase.as_dict() for phase in phases],
        "propagation": {"two_body": two_body, "j2_drag": perturbed},
        "metrics": metrics,
        "stage_sequence": stage_sequence,
    }

    if raan_alignment:
        summary["raan_alignment"] = raan_alignment

    artefacts: MutableMapping[str, Optional[str] | object] = {"summary_path": None}
    artefacts.update(propagation_artefacts)
    artefacts.update(stk_export_summary)
    if output_directory:
        output_dir = Path(output_directory)
        artefacts["summary_path"] = str(output_dir / "scenario_summary.json")
        summary["artefacts"] = artefacts
        output_path = _write_summary(output_dir, summary)
        LOGGER.info("Scenario summary written to %s", output_path)
    else:
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


def _resolve_raan_alignment(
    scenario: MutableMapping[str, object]
) -> MutableMapping[str, object]:
    """Optimise the RAAN to minimise centroid cross-track at the window midpoint."""

    orbital = scenario.get("orbital_elements")
    if not isinstance(orbital, MutableMapping):
        return {}
    classical = orbital.get("classical")
    if not isinstance(classical, MutableMapping):
        return {}
    if "raan_deg" not in classical:
        return {}

    solver_config = scenario.get("raan_alignment")
    if isinstance(solver_config, bool) and not solver_config:
        return {}
    if not isinstance(solver_config, Mapping):
        solver_config = {}

    midpoint = _parse_time(solver_config.get("midpoint_utc"))
    if midpoint is None:
        midpoint = _raan_target_midpoint(scenario)
    if midpoint is None:
        return {}

    initial_raan = float(_coerce_float(classical, "raan_deg", 0.0))

    window_duration = float(solver_config.get("window_duration_s", 90.0))
    time_step = float(solver_config.get("time_step_s", 10.0))
    search_span = float(solver_config.get("search_span_deg", 5.0))
    samples = max(int(solver_config.get("samples_per_iteration", 9)), 3)
    iterations = max(int(solver_config.get("iterations", 4)), 1)
    coarse_samples = max(int(solver_config.get("coarse_samples", 36)), 3)
    span_hours = float(solver_config.get("evaluation_span_hours", 2.0))
    if span_hours <= 0.0:
        span_hours = 2.0
    coarse_range = solver_config.get("coarse_range_deg", (0.0, 360.0))
    if (
        isinstance(coarse_range, Sequence)
        and len(coarse_range) == 2
        and all(isinstance(value, (int, float)) for value in coarse_range)
    ):
        coarse_lower = float(coarse_range[0])
        coarse_upper = float(coarse_range[1])
    else:
        coarse_lower, coarse_upper = 0.0, 360.0

    half_window = timedelta(hours=span_hours)
    start_time = midpoint - half_window
    stop_time = midpoint + half_window

    epoch_time = _parse_time(orbital.get("epoch_utc")) or start_time

    evaluations: list[MutableMapping[str, object]] = []
    best_result: MutableMapping[str, object] | None = None

    for index in range(coarse_samples):
        if coarse_samples == 1:
            candidate = coarse_lower
        else:
            fraction = index / (coarse_samples - 1)
            candidate = coarse_lower + (coarse_upper - coarse_lower) * fraction
        result = _evaluate_raan_candidate(
            scenario,
            candidate,
            start_time,
            stop_time,
            epoch_time,
            time_step,
            window_duration,
        )
        evaluations.append(result)
        if not best_result or (
            result.get("centroid_abs_cross_track_km", math.inf)
            < best_result.get("centroid_abs_cross_track_km", math.inf)
        ):
            best_result = result

    if not best_result:
        return {}

    centre_raan = float(best_result.get("raan_deg", initial_raan))
    lower = centre_raan - search_span
    upper = centre_raan + search_span

    for _ in range(iterations):
        iteration_results: list[MutableMapping[str, object]] = []
        for index in range(samples):
            if samples == 1:
                candidate = lower
            else:
                fraction = index / (samples - 1)
                candidate = lower + (upper - lower) * fraction
            result = _evaluate_raan_candidate(
                scenario,
                candidate,
                start_time,
                stop_time,
                epoch_time,
                time_step,
                window_duration,
            )
            evaluations.append(result)
            iteration_results.append(result)
            if not best_result or (
                result.get("centroid_abs_cross_track_km", math.inf)
                < best_result.get("centroid_abs_cross_track_km", math.inf)
            ):
                best_result = result

        if not iteration_results:
            break

        iteration_best = min(
            iteration_results,
            key=lambda item: item.get("centroid_abs_cross_track_km", math.inf),
        )
        centre = float(iteration_best.get("raan_deg", initial_raan))
        span = max((upper - lower) / max(samples - 1, 1), 1e-4)
        lower = centre - span
        upper = centre + span

    optimised_raan = float(best_result.get("raan_deg", initial_raan))
    classical["raan_deg"] = optimised_raan

    summary: MutableMapping[str, object] = {
        "initial_raan_deg": float(initial_raan),
        "optimised_raan_deg": optimised_raan,
        "target_midpoint_utc": _format_time(midpoint),
        "window_duration_s": window_duration,
        "time_step_s": time_step,
        "evaluations": evaluations,
        "best_evaluation": best_result,
    }

    worst_vehicle = float(best_result.get("worst_vehicle_abs_cross_track_km", math.inf))
    summary["worst_vehicle_abs_cross_track_km"] = worst_vehicle
    summary["centroid_abs_cross_track_km"] = float(
        best_result.get("centroid_abs_cross_track_km", math.inf)
    )

    return summary


def _raan_target_midpoint(scenario: Mapping[str, object]) -> Optional[datetime]:
    """Return the midpoint of the primary access window for RAAN alignment."""

    orbital = scenario.get("orbital_elements")
    if isinstance(orbital, Mapping):
        epoch = _parse_time(orbital.get("epoch_utc"))
        if epoch is not None:
            return epoch

    timing = scenario.get("timing")
    if isinstance(timing, Mapping):
        windows = timing.get("daily_access_windows")
        if isinstance(windows, Sequence) and windows:
            first = windows[0] if isinstance(windows[0], Mapping) else {}
            start = _parse_time(first.get("start_utc"))
            end = _parse_time(first.get("end_utc"))
            if start and end:
                midpoint = start + (end - start) / 2
                return midpoint
            if start:
                return start + timedelta(seconds=45.0)

    start = _parse_time(_extract_planning_horizon(scenario, "start_utc"))
    stop = _parse_time(_extract_planning_horizon(scenario, "stop_utc"))
    if start and stop:
        return start + (stop - start) / 2
    if start:
        return start + timedelta(seconds=45.0)
    return None


def _evaluate_raan_candidate(
    scenario: Mapping[str, object],
    raan_deg: float,
    start_time: datetime,
    stop_time: datetime,
    epoch_time: datetime,
    time_step_s: float,
    window_duration_s: float,
) -> MutableMapping[str, object]:
    """Evaluate centroid cross-track performance for a RAAN candidate."""

    scenario_copy = deepcopy(scenario)
    orbital = scenario_copy.setdefault("orbital_elements", {})
    classical = orbital.setdefault("classical", {})
    normalised_raan = _normalise_raan_deg(raan_deg)
    classical["raan_deg"] = normalised_raan

    settings = perturbation_analysis.PropagatorSettings(
        start_time=start_time,
        epoch_time=epoch_time,
        stop_time=stop_time,
        time_step_s=time_step_s,
        drag_coefficient=2.2,
        ballistic_coefficient_m2_per_kg=0.025,
        solar_flux_index=perturbation_analysis.SOLAR_FLUX_BASE,
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        perturbation_analysis.propagate_constellation(
            scenario_copy,
            output_directory=Path(tmp_dir),
            settings=settings,
            monte_carlo={"enabled": False, "runs": 0},
        )
        cross_track_path = Path(tmp_dir) / "deterministic_cross_track.csv"
        samples = _load_cross_track_series(cross_track_path)

    best_time = None
    best_values: MutableMapping[str, float] = {}
    centroid = math.inf
    for timestamp, values in samples:
        if not values:
            continue
        current_centroid = fmean(values.values())
        abs_value = abs(current_centroid)
        if abs_value < abs(centroid):
            centroid = current_centroid
            best_time = timestamp
            best_values = values

    if best_time is None:
        best_time = start_time
        best_values = {}
        centroid = math.inf

    abs_values = {identifier: abs(value) for identifier, value in best_values.items()}
    window_half = timedelta(seconds=0.5 * window_duration_s)
    window_start = best_time - window_half
    window_end = best_time + window_half

    result: MutableMapping[str, object] = {
        "raan_deg": normalised_raan,
        "evaluation_time_utc": _format_time(best_time),
        "centroid_cross_track_km": float(centroid),
        "centroid_abs_cross_track_km": float(abs(centroid)),
        "window_start_utc": _format_time(window_start),
        "window_end_utc": _format_time(window_end),
        "vehicle_cross_track_km": {k: float(v) for k, v in best_values.items()},
        "vehicle_abs_cross_track_km": {k: float(v) for k, v in abs_values.items()},
        "worst_vehicle_abs_cross_track_km": float(max(abs_values.values(), default=math.inf)),
    }

    return result


def _load_cross_track_series(
    csv_path: Path,
) -> list[tuple[datetime, MutableMapping[str, float]]]:
    """Return the cross-track series from *csv_path* as timestamped samples."""

    samples: list[tuple[datetime, MutableMapping[str, float]]] = []
    if not csv_path.exists():
        return samples

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            timestamp = _parse_time(row.get("time_iso"))
            if timestamp is None:
                continue
            values: MutableMapping[str, float] = {}
            for key, value in row.items():
                if key == "time_iso":
                    continue
                try:
                    values[key] = float(value)
                except (TypeError, ValueError):
                    continue
            samples.append((timestamp, values))

    return samples


def _normalise_raan_deg(value: float) -> float:
    """Wrap *value* into the [0, 360) interval."""

    normalised = math.fmod(value, 360.0)
    if normalised < 0.0:
        normalised += 360.0
    if normalised == 360.0:
        normalised = 0.0
    return normalised


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
    *,
    output_directory: Optional[Path | str] = None,
    raan_alignment: Optional[Mapping[str, object]] = None,
) -> tuple[
    MutableMapping[str, object],
    MutableMapping[str, str],
]:
    r"""Propagate the constellation with \(J_2\) and drag perturbations."""

    del phases  # Phases are retained for compatibility with earlier signatures.

    propagation_summary, artefacts = perturbation_analysis.propagate_constellation(
        scenario,
        output_directory=Path(output_directory) if output_directory else None,
    )

    _update_centroid_alignment_metrics(
        artefacts,
        propagation_summary,
        raan_alignment,
    )

    orbital_period = float(propagation_summary.get("orbital_period_s", 0.0))
    nominal_period = float(two_body.get("orbital_period_s", orbital_period))
    propagation_summary.setdefault("two_body_period_s", nominal_period)
    propagation_summary.setdefault("orbital_period_s", orbital_period or nominal_period)
    propagation_summary.setdefault(
        "period_delta_s",
        float(propagation_summary.get("orbital_period_s", nominal_period)) - nominal_period,
    )

    return propagation_summary, artefacts


def _update_centroid_alignment_metrics(
    artefacts: Mapping[str, str],
    propagation_summary: MutableMapping[str, object],
    raan_alignment: Optional[Mapping[str, object]],
) -> None:
    """Inject centroid alignment results into the propagation artefacts."""

    if not isinstance(raan_alignment, Mapping):
        return
    best = raan_alignment.get("best_evaluation")
    if not isinstance(best, Mapping):
        return

    centroid_metrics = {
        "min_cross_track_km": float(best.get("centroid_cross_track_km", math.inf)),
        "min_abs_cross_track_km": float(best.get("centroid_abs_cross_track_km", math.inf)),
        "time_of_min_abs_cross_track": best.get("evaluation_time_utc"),
        "vehicle_cross_track_km": {
            key: float(value) for key, value in (best.get("vehicle_cross_track_km") or {}).items()
        },
        "vehicle_abs_cross_track_km": {
            key: float(value) for key, value in (best.get("vehicle_abs_cross_track_km") or {}).items()
        },
        "worst_vehicle_abs_cross_track_km": float(
            best.get("worst_vehicle_abs_cross_track_km", math.inf)
        ),
    }

    propagation_summary["centroid_alignment"] = centroid_metrics

    summary_path = artefacts.get("deterministic_summary_json")
    if not summary_path:
        return

    path = Path(summary_path)
    if not path.exists():
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    metrics = data.setdefault("metrics", {})
    metrics["centroid_cross_track"] = centroid_metrics
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


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

    cross_track = perturbed.get("cross_track") if isinstance(perturbed, Mapping) else None
    if isinstance(cross_track, Mapping):
        overall = float(cross_track.get("overall_max_abs_cross_track_km", 0.0))
        metrics["overall_max_cross_track_km"] = overall
        metrics["overall_min_cross_track_km"] = float(
            cross_track.get("overall_min_abs_cross_track_km", 0.0)
        )
        vehicles = cross_track.get("vehicles")
        if isinstance(vehicles, Sequence) and vehicles:
            worst_vehicle = max(
                (
                    float(vehicle.get("max_abs_cross_track_km", 0.0))
                    for vehicle in vehicles
                    if isinstance(vehicle, Mapping)
                ),
                default=0.0,
            )
            metrics["worst_vehicle_cross_track_km"] = worst_vehicle
            worst_min = max(
                (
                    float(vehicle.get("min_abs_cross_track_km", 0.0))
                    for vehicle in vehicles
                    if isinstance(vehicle, Mapping)
                ),
                default=0.0,
            )
            compliant_count = sum(
                1
                for vehicle in vehicles
                if isinstance(vehicle, Mapping) and vehicle.get("compliant")
            )
            metrics["worst_vehicle_min_cross_track_km"] = worst_min
            metrics["deterministic_compliance_fraction"] = (
                compliant_count / len(vehicles)
            )

    monte_carlo = perturbed.get("monte_carlo") if isinstance(perturbed, Mapping) else None
    if isinstance(monte_carlo, Mapping):
        metrics["monte_carlo_fleet_compliance_probability"] = float(
            monte_carlo.get("fleet_compliance_probability", 0.0)
        )
        metrics["monte_carlo_run_count"] = float(monte_carlo.get("runs", 0))

    plane_intersection = perturbed.get("plane_intersection") if isinstance(perturbed, Mapping) else None
    if isinstance(plane_intersection, Mapping):
        metrics["plane_intersection_distance_km"] = float(
            plane_intersection.get("target_distance_km", 0.0)
        )
        metrics["plane_intersection_compliant"] = 1.0 if plane_intersection.get("compliant") else 0.0

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


def _export_stk_products(
    base_output_dir: Path,
    scenario: Mapping[str, object],
    nodes: Sequence[Node],
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
) -> MutableMapping[str, object]:
    """Generate STK artefacts for the scenario and return metadata about the export."""

    export_dir = base_output_dir / "stk_export"
    export_dir.mkdir(parents=True, exist_ok=True)

    metadata = _build_scenario_metadata(scenario, two_body)
    state_history, ground_track = _generate_state_history(scenario, metadata, two_body)
    contacts = _collect_ground_contacts(nodes, state_history.satellite_id)
    facilities = _collect_facilities(scenario, contacts)

    sim_results = SimulationResults(
        state_histories=[state_history],
        ground_tracks=[ground_track],
        ground_contacts=contacts,
        facilities=facilities,
    )

    export_simulation_to_stk(sim_results, export_dir, metadata)

    exported_files = sorted(
        [path.name for path in export_dir.iterdir() if path.is_file()]
    )

    return {
        "stk_export_directory": str(export_dir),
        "stk_export_files": exported_files,
        "stk_scenario_start_epoch": metadata.start_epoch.isoformat().replace("+00:00", "Z"),
    }


def _build_scenario_metadata(
    scenario: Mapping[str, object],
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
) -> ScenarioMetadata:
    """Construct metadata describing the STK scenario context."""

    metadata = scenario.get("metadata") if isinstance(scenario.get("metadata"), Mapping) else {}
    scenario_name = "Scenario"
    if isinstance(metadata, Mapping):
        scenario_name = str(
            metadata.get("scenario_name")
            or metadata.get("identifier")
            or metadata.get("mission_name")
            or scenario_name
        )

    orbital_elements = scenario.get("orbital_elements")
    epoch = None
    if isinstance(orbital_elements, Mapping):
        epoch = _parse_time(orbital_elements.get("epoch_utc"))

    if epoch is None:
        epoch = _parse_time(_extract_planning_horizon(scenario, "start_utc"))

    if epoch is None:
        epoch = datetime.now(timezone.utc)

    stop = _parse_time(_extract_planning_horizon(scenario, "stop_utc"))
    if stop is None:
        duration = _estimate_duration(scenario)
        if not duration:
            duration = float(two_body.get("orbital_period_s", 0.0))
        stop = epoch + timedelta(seconds=duration or 5_400.0)

    period = float(two_body.get("orbital_period_s", 0.0))
    if period <= 0.0:
        period = 5_400.0
    step = max(min(period / 60.0, 900.0), 60.0)

    return ScenarioMetadata(
        scenario_name=scenario_name,
        start_epoch=epoch,
        stop_epoch=stop,
        central_body="Earth",
        coordinate_frame="TEME",
        ephemeris_step_seconds=step,
        animation_step_seconds=step,
    )


def _generate_state_history(
    scenario: Mapping[str, object],
    metadata: ScenarioMetadata,
    two_body: Mapping[str, float | Sequence[Mapping[str, float]]],
) -> tuple[PropagatedStateHistory, GroundTrack]:
    """Synthesise a representative propagation history for STK export."""

    classical = {}
    orbital_elements = scenario.get("orbital_elements")
    if isinstance(orbital_elements, Mapping):
        classical = orbital_elements.get("classical") or {}

    semi_major_axis = _coerce_float(classical, "semi_major_axis_km", 7_000.0)
    eccentricity = _coerce_float(classical, "eccentricity", 0.0)
    inclination = math.radians(_coerce_float(classical, "inclination_deg", 0.0))
    raan = math.radians(_coerce_float(classical, "raan_deg", 0.0))
    argument_of_perigee = math.radians(
        _coerce_float(classical, "argument_of_perigee_deg", 0.0)
    )
    mean_anomaly = math.radians(_coerce_float(classical, "mean_anomaly_deg", 0.0))

    satellite_id = _select_satellite_identifier(scenario)

    if metadata.stop_epoch is None:
        stop_epoch = metadata.start_epoch + timedelta(
            seconds=float(two_body.get("orbital_period_s", 5_400.0))
        )
    else:
        stop_epoch = metadata.stop_epoch

    step = metadata.ephemeris_step_seconds or 600.0
    duration_seconds = max((stop_epoch - metadata.start_epoch).total_seconds(), step)
    sample_count = int(math.ceil(duration_seconds / step)) + 1

    state_samples: list[StateSample] = []
    ground_track_points: list[GroundTrackPoint] = []

    mean_motion = math.sqrt(MU_EARTH_KM3_S2 / (semi_major_axis**3))
    if not math.isfinite(mean_motion) or mean_motion <= 0.0:
        mean_motion = 0.0011635528346628863  # ~95-minute orbit fallback

    for index in range(sample_count):
        epoch = metadata.start_epoch + timedelta(seconds=index * step)
        delta_t = (epoch - metadata.start_epoch).total_seconds()
        mean_anomaly_current = mean_anomaly + mean_motion * delta_t
        mean_anomaly_current = math.fmod(mean_anomaly_current, 2.0 * math.pi)
        if mean_anomaly_current < 0.0:
            mean_anomaly_current += 2.0 * math.pi

        eccentric_anomaly = _solve_kepler(mean_anomaly_current, eccentricity)
        true_anomaly = _eccentric_to_true_anomaly(eccentric_anomaly, eccentricity)

        radius = semi_major_axis * (1.0 - eccentricity * math.cos(eccentric_anomaly))
        semi_latus_rectum = semi_major_axis * (1.0 - eccentricity**2)
        if semi_latus_rectum <= 0.0:
            semi_latus_rectum = semi_major_axis
        sqrt_mu_over_p = math.sqrt(MU_EARTH_KM3_S2 / semi_latus_rectum)

        position_pqw = (
            radius * math.cos(true_anomaly),
            radius * math.sin(true_anomaly),
            0.0,
        )
        velocity_pqw = (
            -sqrt_mu_over_p * math.sin(true_anomaly),
            sqrt_mu_over_p * (eccentricity + math.cos(true_anomaly)),
            0.0,
        )

        position_eci = _pqw_to_eci(position_pqw, raan, argument_of_perigee, inclination)
        velocity_eci = _pqw_to_eci(velocity_pqw, raan, argument_of_perigee, inclination)

        state_samples.append(
            StateSample(
                epoch=epoch,
                position_eci_km=position_eci,
                velocity_eci_kms=velocity_eci,
            )
        )

        latitude, longitude, altitude = _eci_to_geodetic(position_eci, metadata.start_epoch, epoch)
        ground_track_points.append(
            GroundTrackPoint(
                epoch=epoch,
                latitude_deg=latitude,
                longitude_deg=longitude,
                altitude_km=altitude,
            )
        )

    return (
        PropagatedStateHistory(satellite_id=satellite_id, samples=state_samples),
        GroundTrack(satellite_id=satellite_id, points=ground_track_points),
    )


def _coerce_float(data: Mapping[str, object], key: str, default: float) -> float:
    value = data.get(key) if isinstance(data, Mapping) else None
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _solve_kepler(mean_anomaly: float, eccentricity: float) -> float:
    """Solve Kepler's equation for the eccentric anomaly."""

    if abs(eccentricity) < 1e-8:
        return mean_anomaly

    eccentric_anomaly = mean_anomaly
    for _ in range(12):
        delta = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly) - mean_anomaly
        derivative = 1.0 - eccentricity * math.cos(eccentric_anomaly)
        if derivative == 0.0:
            break
        correction = delta / derivative
        eccentric_anomaly -= correction
        if abs(correction) < 1e-12:
            break
    return eccentric_anomaly


def _eccentric_to_true_anomaly(eccentric_anomaly: float, eccentricity: float) -> float:
    """Convert eccentric anomaly to true anomaly."""

    if abs(eccentricity - 1.0) < 1e-8:
        return eccentric_anomaly

    numerator = math.sqrt(1.0 + eccentricity) * math.sin(eccentric_anomaly / 2.0)
    denominator = math.sqrt(1.0 - eccentricity) * math.cos(eccentric_anomaly / 2.0)
    true_anomaly = 2.0 * math.atan2(numerator, denominator)
    return true_anomaly


def _pqw_to_eci(
    vector: Sequence[float],
    raan: float,
    argument_of_perigee: float,
    inclination: float,
) -> tuple[float, float, float]:
    """Rotate a vector from the orbital plane into the inertial frame."""

    cos_omega = math.cos(raan)
    sin_omega = math.sin(raan)
    cos_arg = math.cos(argument_of_perigee)
    sin_arg = math.sin(argument_of_perigee)
    cos_inc = math.cos(inclination)
    sin_inc = math.sin(inclination)

    x_p, y_p, z_p = vector

    rotation_11 = cos_omega * cos_arg - sin_omega * sin_arg * cos_inc
    rotation_12 = -cos_omega * sin_arg - sin_omega * cos_arg * cos_inc
    rotation_21 = sin_omega * cos_arg + cos_omega * sin_arg * cos_inc
    rotation_22 = -sin_omega * sin_arg + cos_omega * cos_arg * cos_inc
    rotation_31 = sin_arg * sin_inc
    rotation_32 = cos_arg * sin_inc

    x = rotation_11 * x_p + rotation_12 * y_p
    y = rotation_21 * x_p + rotation_22 * y_p
    z = rotation_31 * x_p + rotation_32 * y_p

    return (x, y, z)


def _eci_to_geodetic(
    position_eci: Sequence[float],
    reference_epoch: datetime,
    epoch: datetime,
) -> tuple[float, float, float]:
    """Approximate conversion from ECI to geodetic latitude, longitude, and altitude."""

    dt = (epoch - reference_epoch).total_seconds()
    angle = EARTH_ROTATION_RATE_RAD_S * dt
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    x_eci, y_eci, z_eci = position_eci
    x_ecef = cos_angle * x_eci + sin_angle * y_eci
    y_ecef = -sin_angle * x_eci + cos_angle * y_eci
    z_ecef = z_eci

    horizontal_distance = math.sqrt(x_ecef**2 + y_ecef**2)
    latitude = math.degrees(math.atan2(z_ecef, horizontal_distance))
    longitude = math.degrees(math.atan2(y_ecef, x_ecef))
    longitude = ((longitude + 180.0) % 360.0) - 180.0
    radius = math.sqrt(x_ecef**2 + y_ecef**2 + z_ecef**2)
    altitude = max(radius - EARTH_RADIUS_KM, 0.0)
    return latitude, longitude, altitude


def _collect_ground_contacts(
    nodes: Sequence[Node],
    satellite_id: str,
) -> list[GroundContactInterval]:
    """Create contact intervals based on mission nodes."""

    contacts: list[GroundContactInterval] = []
    for node in nodes:
        if node.start and node.end:
            facility_name = _contact_facility_name(node)
            contacts.append(
                GroundContactInterval(
                    satellite_id=satellite_id,
                    facility_name=facility_name,
                    start=node.start,
                    end=node.end,
                )
            )
    return contacts


def _contact_facility_name(node: Node) -> str:
    attributes = node.attributes
    if isinstance(attributes, Mapping):
        if "ground_station" in attributes:
            return str(attributes["ground_station"])
        if "target" in attributes:
            return str(attributes["target"])
    return node.label


def _collect_facilities(
    scenario: Mapping[str, object],
    contacts: Sequence[GroundContactInterval],
) -> list[FacilityDefinition]:
    """Build facility definitions referenced by the contact catalogue."""

    facilities: dict[str, FacilityDefinition] = {}
    metadata = scenario.get("metadata") if isinstance(scenario.get("metadata"), Mapping) else {}
    region = metadata.get("region") if isinstance(metadata, Mapping) else None
    region_lat = None
    region_lon = None
    if isinstance(region, Mapping):
        region_lat = _coerce_float(region, "latitude_deg", 0.0)
        region_lon = _coerce_float(region, "longitude_deg", 0.0)

    for interval in contacts:
        name = interval.facility_name
        if name in facilities:
            continue
        coords = _lookup_facility_coordinates(name, region_lat, region_lon)
        facilities[name] = FacilityDefinition(
            name=name,
            latitude_deg=coords[0],
            longitude_deg=coords[1],
            altitude_km=coords[2],
        )

    if isinstance(region, Mapping):
        descriptive_name = f"{region.get('city', 'Region')} {region.get('country', '').strip()}".strip()
        coords = (
            _coerce_float(region, "latitude_deg", 0.0),
            _coerce_float(region, "longitude_deg", 0.0),
            _coerce_float(region, "altitude_km", 1.5),
        )
        facilities.setdefault(
            descriptive_name or "AreaOfInterest",
            FacilityDefinition(
                name=descriptive_name or "AreaOfInterest",
                latitude_deg=coords[0],
                longitude_deg=coords[1],
                altitude_km=coords[2],
            ),
        )

    return list(facilities.values())


def _lookup_facility_coordinates(
    name: str,
    region_lat: Optional[float],
    region_lon: Optional[float],
) -> tuple[float, float, float]:
    """Return coordinates for known facilities, defaulting to the scenario region."""

    catalogue: dict[str, tuple[float, float, float]] = {
        "svalbard": (78.223, 15.646, 0.4),
        "inuvik": (68.355, -133.721, 0.1),
        "tehran urban core": (35.6892, 51.3890, 1.2),
        "tehran": (35.6892, 51.3890, 1.2),
    }

    key = name.lower()
    if key in catalogue:
        return catalogue[key]

    if region_lat is not None and region_lon is not None:
        return (region_lat, region_lon, 0.0)

    return (0.0, 0.0, 0.0)


def _select_satellite_identifier(scenario: Mapping[str, object]) -> str:
    """Derive a stable satellite identifier from the scenario metadata."""

    metadata = scenario.get("metadata") if isinstance(scenario.get("metadata"), Mapping) else {}
    identifier = None
    if isinstance(metadata, Mapping):
        identifier = metadata.get("identifier") or metadata.get("scenario_name")

    if identifier is None and "mission_name" in scenario:
        identifier = scenario["mission_name"]

    if not identifier:
        identifier = "scenario_asset"

    safe_identifier = str(identifier).strip().replace(" ", "_")
    return safe_identifier


def _write_summary(output_dir: Path, summary: Mapping[str, object]) -> Path:
    """Persist the pipeline summary to *output_dir*."""

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "scenario_summary.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return path


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

