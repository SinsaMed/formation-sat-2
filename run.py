"""Web entry points for running formation simulations and scenario pipelines."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from sim.formation import simulate_triangle_formation
from sim.formation.triangle import TriangleFormationResult
from sim.formation.triangle_artefacts import export_triangle_time_series
from sim.scripts.configuration import resolve_scenario_path
from sim.scripts.run_scenario import run_scenario
from sim.scripts import extract_metrics as metrics_module
from src.constellation.orbit import EARTH_EQUATORIAL_RADIUS_M
from src.constellation.web.jobs import JobManager, SubprocessJob
from tools.generate_triangle_report import main as generate_triangle_report_main
from tools.render_debug_plots import generate_visualisations as generate_debug_visualisations

PROJECT_ROOT = Path(__file__).resolve().parent
SCENARIO_DIR = PROJECT_ROOT / "config" / "scenarios"
WEB_UI_DIR = PROJECT_ROOT / "src" / "constellation" / "web" / "ui"
WEB_STATIC_DIR = WEB_UI_DIR / "static"
WEB_TEMPLATE_PATH = WEB_UI_DIR / "index.html"
WEB_ARTEFACT_DIR = PROJECT_ROOT / "artefacts" / "web_runs"
WEB_ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)
RUN_LOG_PATH = WEB_ARTEFACT_DIR / "run_log.jsonl"
DEBUG_LOG_PATH = PROJECT_ROOT / "debug.txt"
DEFAULT_TRIANGLE_SCENARIO = "tehran_triangle"
DEFAULT_PIPELINE_SCENARIO = "tehran_daily_pass"

LOGGER = logging.getLogger(__name__)


def _load_json(path: Path) -> Mapping[str, Any]:
    """Return JSON content from *path* if available."""

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _load_gravitational_parameter() -> float:
    """Extract the Earth's gravitational parameter from the project configuration."""

    project_path = PROJECT_ROOT / "config" / "project.yaml"
    try:
        content = project_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return 398_600.4418 * 1e9
    match = re.search(r"gravitational_parameter_km3_s2:\s*([0-9.+-eE]+)", content)
    if not match:
        return 398_600.4418 * 1e9
    value_km3 = float(match.group(1))
    return value_km3 * 1e9


def _ensure_mutable_triangle_artefacts(
    result: TriangleFormationResult,
) -> MutableMapping[str, Any]:
    """Return a mutable artefact mapping for *result*, cloning if required."""

    artefacts = result.artefacts
    if isinstance(artefacts, MutableMapping):
        return artefacts
    mutable: MutableMapping[str, Any] = dict(artefacts)
    setattr(result, "artefacts", mutable)
    return mutable


def _serialise_plot_outputs(
    outputs: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Convert plot artefact mappings into JSON-serialisable structures."""

    serialised: Dict[str, Any] = {}
    for key, value in outputs.items():
        if isinstance(value, Mapping):
            serialised[key] = {inner_key: str(inner_value) for inner_key, inner_value in value.items()}
        else:
            serialised[key] = str(value)
    return serialised


def _persist_triangle_configuration(
    configuration_source: Mapping[str, Any] | Path | str,
    output_directory: Path,
) -> Optional[Path]:
    """Ensure a configuration file exists for supplementary plot generation."""

    if isinstance(configuration_source, Mapping):
        config_path = output_directory / "triangle_configuration.json"
        config_path.write_text(json.dumps(configuration_source, indent=2), encoding="utf-8")
        return config_path

    candidate: Optional[Path] = None
    if isinstance(configuration_source, Path):
        candidate = configuration_source
    elif isinstance(configuration_source, str):
        candidate = Path(configuration_source)

    if candidate is None:
        return None

    if not candidate.is_absolute():
        potential = (PROJECT_ROOT / candidate).resolve()
        if potential.exists():
            candidate = potential

    return candidate if candidate.exists() else None


def _generate_triangle_documentation(
    result: TriangleFormationResult,
    output_directory: Path,
    configuration_source: Mapping[str, Any] | Path | str,
) -> None:
    """Generate comprehensive artefact documentation for web-triggered runs."""

    artefacts = _ensure_mutable_triangle_artefacts(result)

    csv_bundle = export_triangle_time_series(result, output_directory)
    artefacts.setdefault(
        "time_series_csv",
        {key: str(path) for key, path in sorted(csv_bundle.csv_paths.items())},
    )
    if csv_bundle.per_satellite_csvs:
        artefacts.setdefault(
            "orbital_elements_per_satellite",
            {sat_id: str(path) for sat_id, path in sorted(csv_bundle.per_satellite_csvs.items())},
        )

    try:
        debug_outputs = generate_debug_visualisations(output_directory)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning(
            "Debug visualisation generation failed for %s: %s",
            output_directory,
            exc,
        )
        debug_outputs = {}
    else:
        if debug_outputs:
            artefacts["debug_plots"] = _serialise_plot_outputs(debug_outputs)

    config_path = _persist_triangle_configuration(configuration_source, output_directory)
    if config_path is None:
        LOGGER.warning(
            "Triangle configuration could not be resolved for supplementary plots in %s.",
            output_directory,
        )
    else:
        argv = ["--run-dir", str(output_directory), "--config", str(config_path)]
        try:
            generate_triangle_report_main(argv)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning(
                "Triangle report generation failed for %s using %s: %s",
                output_directory,
                config_path,
                exc,
            )

    plots_dir = output_directory / "plots"
    if plots_dir.exists():
        artefacts["plots_directory"] = str(plots_dir)
        plot_entries = {
            path.name: str(path)
            for path in sorted(plots_dir.iterdir())
            if path.is_file()
        }
        if plot_entries:
            artefacts["plot_files"] = plot_entries


def _persian_digits(value: str) -> str:
    """Convert western digits in *value* to Persian numerals."""

    mapping = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
        ".": "٫",
    }
    return "".join(mapping.get(char, char) for char in value)


def _format_duration_label(days: float) -> str:
    """Return a human-readable label for *days* expressed in Persian."""

    if abs(days - round(days)) < 1e-6:
        text = str(int(round(days)))
    else:
        text = f"{days:.1f}"
    return f"{_persian_digits(text)} روز"


def _describe_duration_source(identifier: str) -> str:
    """Provide contextual text for duration origins."""

    mapping = {
        "repeat_ground_track": "برگرفته از دوره تکرار زمینی سناریوى عبور روزانه.",
        "planning_horizon": "مطابق افق برنامه‌ریزى سناریوى تهران در فایل پیکربندى.",
        "manoeuvre_cadence": "هم‌راستا با دوره مانور نگهداشت تعریف‌شده در project.yaml.",
    }
    return mapping.get(identifier, "")


def _derive_duration_options() -> List[Mapping[str, object]]:
    """Aggregate representative scenario durations from repository configurations."""

    options: List[tuple[float, str]] = []

    daily_pass = _load_json(SCENARIO_DIR / "tehran_daily_pass.json")
    repeat_cycle = (
        daily_pass.get("orbital_elements", {})
        .get("repeat_ground_track", {})
        .get("repeat_cycle_days")
    )
    if isinstance(repeat_cycle, (int, float)):
        options.append((float(repeat_cycle), "repeat_ground_track"))

    planning = daily_pass.get("timing", {}).get("planning_horizon", {})
    start = planning.get("start_utc")
    stop = planning.get("stop_utc")
    if isinstance(start, str) and isinstance(stop, str):
        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            stop_dt = datetime.fromisoformat(stop.replace("Z", "+00:00"))
        except ValueError:
            pass
        else:
            horizon_days = (stop_dt - start_dt).total_seconds() / 86_400.0
            if horizon_days > 0.1:
                options.append((float(horizon_days), "planning_horizon"))

    project_text = ""
    try:
        project_text = (PROJECT_ROOT / "config" / "project.yaml").read_text(encoding="utf-8")
    except FileNotFoundError:
        project_text = ""
    match = re.search(r"manoeuvre_cadence_days:\s*([0-9.+-eE]+)", project_text)
    if match:
        try:
            options.append((float(match.group(1)), "manoeuvre_cadence"))
        except ValueError:
            pass

    unique: Dict[float, Mapping[str, object]] = {}
    for value, source in options:
        if value <= 0.0:
            continue
        key = round(value, 6)
        if key not in unique:
            unique[key] = {"days": value, "source": source}

    labelled: List[Mapping[str, object]] = []
    for key in sorted(unique):
        entry = unique[key]
        days = entry["days"]
        source = str(entry["source"])
        labelled.append(
            {
                "days": days,
                "label": _format_duration_label(days),
                "source": source,
                "explanation": _describe_duration_source(source),
            }
        )
    return labelled


def _extract_city_option(triangle_config: Mapping[str, Any]) -> Mapping[str, object]:
    """Return the default city entry derived from the triangle scenario."""

    formation = triangle_config.get("formation", {}) if isinstance(triangle_config, Mapping) else {}
    target = formation.get("target", {}) if isinstance(formation, Mapping) else {}
    latitude = float(target.get("latitude_deg", 35.6892))
    longitude = float(target.get("longitude_deg", 51.3890))
    return {
        "id": "tehran",
        "label": "تهران",
        "latitude_deg": latitude,
        "longitude_deg": longitude,
    }


EARTH_GRAVITATIONAL_PARAMETER_M3_S2 = _load_gravitational_parameter()
TRIANGLE_BASE_CONFIGURATION = _load_json(SCENARIO_DIR / f"{DEFAULT_TRIANGLE_SCENARIO}.json")
SCENARIO_DURATION_OPTIONS = _derive_duration_options()
DEFAULT_CITY_OPTION = _extract_city_option(TRIANGLE_BASE_CONFIGURATION)


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Set up global resources required by the FastAPI application."""

    WEB_ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Formation SAT Run Service", lifespan=_lifespan)
router = APIRouter(prefix="/runs")
app.mount("/web_runs", StaticFiles(directory=WEB_ARTEFACT_DIR, html=False), name="web_runs")
if WEB_STATIC_DIR.exists():
    app.mount("/web/static", StaticFiles(directory=WEB_STATIC_DIR, html=False), name="web-static")
JOB_MANAGER = JobManager()


class TriangleRunRequest(BaseModel):
    """Request payload for triangle formation simulations."""

    scenario_id: Optional[str] = Field(
        default=None,
        description="Identifier of the stored triangle scenario configuration.",
    )
    configuration: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Inline configuration overriding the stored scenario file.",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Documented assumptions associated with the run.",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional random seed recorded alongside the run metadata.",
    )

    @model_validator(mode="before")
    @classmethod
    def _ensure_source_present(cls, values: Any) -> Any:
        if not isinstance(values, Mapping):
            return values
        data = dict(values)
        scenario = data.get("scenario_id")
        configuration = data.get("configuration")
        if not scenario and not configuration:
            data["scenario_id"] = DEFAULT_TRIANGLE_SCENARIO
        return data


class ScenarioRunRequest(BaseModel):
    """Request payload for the general scenario pipeline."""

    scenario_id: Optional[str] = Field(
        default=None,
        description="Identifier of the stored scenario configuration.",
    )
    configuration: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Inline configuration overriding the stored scenario file.",
    )
    metrics_specification: Optional[List[str]] = Field(
        default=None,
        description="Optional subset of metrics prioritised in the output summary.",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Documented assumptions associated with the run.",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional random seed recorded alongside the run metadata.",
    )

    @model_validator(mode="before")
    @classmethod
    def _ensure_source_present(cls, values: Any) -> Any:
        if not isinstance(values, Mapping):
            return values
        data = dict(values)
        scenario = data.get("scenario_id")
        configuration = data.get("configuration")
        if not scenario and not configuration:
            data["scenario_id"] = DEFAULT_PIPELINE_SCENARIO
        return data


class DebugRunRequest(BaseModel):
    """Request payload for orchestrating ``run_debug.py`` executions."""

    mode: str = Field(
        ...,
        pattern="^(triangle|scenario)$",
        description="Select between the triangle simulation or the generic scenario pipeline.",
    )
    scenario_id: Optional[str] = Field(
        default=None,
        description="Identifier used when mode='scenario'. Defaults to tehran_daily_pass.",
    )
    triangle_config: Optional[str] = Field(
        default=None,
        description="Optional override path for the triangle configuration when mode='triangle'.",
    )
    output_root: Optional[str] = Field(
        default=None,
        description="Optional directory root for storing debug artefacts.",
    )

    @model_validator(mode="after")
    def _validate_mode_arguments(self) -> "DebugRunRequest":
        if self.mode == "triangle":
            self.scenario_id = None
        elif self.mode == "scenario" and self.scenario_id is None:
            self.scenario_id = "tehran_daily_pass"
        return self


@app.get("/", response_class=HTMLResponse)
def serve_interface() -> str:
    """Render the single-page application for interactive operations."""

    return _render_interface()


@router.get("/configs")
def list_configs() -> Mapping[str, List[Mapping[str, Any]]]:
    """Discover stored scenario configurations and summarise their metadata."""

    configurations: List[Mapping[str, Any]] = []
    for path in sorted(SCENARIO_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {
                "id": path.stem,
                "file_name": path.name,
                "error": "Invalid JSON payload.",
                "keys": [],
            }
        else:
            metadata = payload.get("metadata", {}) if isinstance(payload, Mapping) else {}
            summary = {
                "id": path.stem,
                "file_name": path.name,
                "scenario_name": metadata.get("scenario_name"),
                "description": metadata.get("description"),
                "keys": sorted(payload.keys()) if isinstance(payload, Mapping) else [],
            }
        configurations.append(summary)
    return {"scenarios": configurations}


@router.get("/history")
def get_run_history(limit: int = Query(20, ge=1, le=200)) -> Mapping[str, Any]:
    """Return the recorded run history sorted by recency."""

    records = _load_run_history(limit=limit)
    return {"runs": records}


@router.post("/triangle")
def run_triangle(request: TriangleRunRequest) -> Mapping[str, Any]:
    """Execute the triangle formation simulation using the requested configuration."""

    run_id, timestamp = _generate_run_identifiers()
    output_directory = WEB_ARTEFACT_DIR / run_id

    configuration_source: Mapping[str, Any] | Path | str
    source_descriptor: Mapping[str, Any]

    if request.configuration is not None:
        configuration_source = request.configuration
        source_descriptor = {"mode": "inline_configuration"}
    else:
        scenario_path = _resolve_triangle_scenario(request.scenario_id)
        configuration_source = scenario_path
        source_descriptor = {"mode": "stored_scenario", "path": str(scenario_path)}

    try:
        result = simulate_triangle_formation(
            configuration_source,
            output_directory=output_directory,
        )
    except Exception as error:
        _record_run(
            run_id,
            timestamp,
            route="triangle",
            status="failed",
            request_payload=request.dict(),
            source=source_descriptor,
            artefacts={},
            summary=None,
            error=str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error

    _generate_triangle_documentation(result, output_directory, configuration_source)

    summary = result.to_summary()
    artefacts = _collect_triangle_artefacts(result, output_directory)

    _record_run(
        run_id,
        timestamp,
        route="triangle",
        status="completed",
        request_payload=request.dict(),
        source=source_descriptor,
        artefacts=artefacts,
        summary=summary,
    )

    response = {
        "run_id": run_id,
        "timestamp": timestamp,
        "summary": summary,
        "artefacts": artefacts,
    }
    return response


@router.post("/scenario")
def run_scenario_pipeline(request: ScenarioRunRequest) -> Mapping[str, Any]:
    """Execute the general scenario pipeline and expose its summary."""

    run_id, timestamp = _generate_run_identifiers()
    output_directory = WEB_ARTEFACT_DIR / run_id

    if request.configuration is not None:
        configuration_source: Mapping[str, Any] | Path | str = request.configuration
        source_descriptor = {"mode": "inline_configuration"}
    else:
        scenario_path = _resolve_generic_scenario(request.scenario_id)
        configuration_source = scenario_path
        source_descriptor = {"mode": "stored_scenario", "path": str(scenario_path)}

    try:
        result = run_scenario(
            configuration_source,
            output_directory=output_directory,
            metrics_specification=request.metrics_specification,
        )
    except Exception as error:
        _record_run(
            run_id,
            timestamp,
            route="scenario",
            status="failed",
            request_payload=request.dict(),
            source=source_descriptor,
            artefacts={},
            summary=None,
            error=str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error

    artefacts = _collect_scenario_artefacts(result, output_directory)

    _record_run(
        run_id,
        timestamp,
        route="scenario",
        status="completed",
        request_payload=request.dict(),
        source=source_descriptor,
        artefacts=artefacts,
        summary=result,
    )

    response = {
        "run_id": run_id,
        "timestamp": timestamp,
        "summary": result,
        "artefacts": artefacts,
    }
    return response


@router.post("/debug/jobs")
async def launch_debug_job(request: DebugRunRequest) -> Mapping[str, Any]:
    """Start an asynchronous ``run_debug.py`` subprocess and track its lifecycle."""

    command = _build_debug_command(request)
    job = await JOB_MANAGER.create_job(command, cwd=PROJECT_ROOT)

    _schedule_job_cleanup(job)

    response = {"job": job.snapshot()}
    return response


@router.get("/debug/jobs")
async def list_debug_jobs() -> Mapping[str, Any]:
    """Enumerate known debug subprocesses ordered by recency."""

    jobs = await JOB_MANAGER.list_jobs()
    return {"jobs": jobs}


@router.get("/debug/jobs/{job_id}")
async def describe_debug_job(job_id: str) -> Mapping[str, Any]:
    """Return metadata for a specific debug subprocess."""

    job = await JOB_MANAGER.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Debug job '{job_id}' not found.")
    return {"job": job.snapshot()}


@router.delete("/debug/jobs/{job_id}")
async def cancel_debug_job(job_id: str) -> Mapping[str, Any]:
    """Request cancellation of a running debug subprocess."""

    job = await JOB_MANAGER.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Debug job '{job_id}' not found.")
    await job.cancel()
    return {"job": job.snapshot()}


@router.get("/debug/jobs/{job_id}/stream")
async def stream_debug_job(job_id: str, request: Request) -> StreamingResponse:
    """Stream structured log updates from a debug subprocess via SSE."""

    job = await JOB_MANAGER.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Debug job '{job_id}' not found.")

    async def event_generator() -> AsyncIterator[str]:
        async for line in job.iter_lines():
            if await request.is_disconnected():
                break
            payload = json.dumps({"message": line})
            yield f"data: {payload}\n\n"
        if not await request.is_disconnected():
            summary = json.dumps(job.snapshot())
            yield f"event: summary\ndata: {summary}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{run_id}/metrics-report")
def fetch_metrics_report(run_id: str) -> Mapping[str, Any]:
    """Run the post-processing metrics workflow for the selected execution."""

    record = _find_run_record(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    summary = record.get("summary")
    if not isinstance(summary, Mapping):
        raise HTTPException(status_code=400, detail="Run summary unavailable for metrics.")

    geometry = summary.get("geometry") if isinstance(summary, Mapping) else None
    if not isinstance(geometry, Mapping):
        raise HTTPException(status_code=400, detail="Geometry data missing from run summary.")

    artefacts = record.get("artefacts") if isinstance(record, Mapping) else {}
    output_directory = artefacts.get("output_directory") if isinstance(artefacts, Mapping) else None
    if not output_directory:
        raise HTTPException(status_code=400, detail="Run artefacts do not expose an output directory.")

    metrics_dir = Path(output_directory) / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    satellite_ids = geometry.get("satellite_ids") if isinstance(geometry, Mapping) else None
    position_map = geometry.get("positions_m") if isinstance(geometry, Mapping) else None
    time_series = geometry.get("times") if isinstance(geometry, Mapping) else None
    if not satellite_ids or not position_map or not time_series:
        raise HTTPException(status_code=400, detail="Incomplete geometry payload for metrics extraction.")

    triangle_series: List[Mapping[str, Any]] = []
    for index, timestamp in enumerate(time_series):
        vertices: List[Sequence[float]] = []
        for sat_id in satellite_ids:
            samples = position_map.get(sat_id)
            if samples is None or index >= len(samples):
                raise HTTPException(status_code=400, detail=f"Missing position samples for {sat_id}.")
            vertices.append(samples[index])
        triangle_series.append({"time": timestamp, "vertices": vertices})

    metrics_block = summary.get("metrics") if isinstance(summary, Mapping) else {}
    window_events: List[Mapping[str, Any]] = []

    formation_windows = (
        metrics_block.get("formation_windows") if isinstance(metrics_block, Mapping) else None
    )
    if isinstance(formation_windows, Sequence):
        for window in formation_windows:
            if not isinstance(window, Mapping):
                continue
            start = window.get("start")
            end = window.get("end")
            if start and end:
                event: MutableMapping[str, Any] = {"start": start, "end": end}
                duration = window.get("duration_s")
                if duration is not None:
                    event["duration_s"] = duration
                window_events.append(event)

    if not window_events:
        formation_window = (
            metrics_block.get("formation_window") if isinstance(metrics_block, Mapping) else None
        )
        if isinstance(formation_window, Mapping):
            start = formation_window.get("start")
            end = formation_window.get("end")
            if start and end:
                event = {"start": start, "end": end}
                duration = formation_window.get("duration_s")
                if duration is not None:
                    event["duration_s"] = duration
                window_events.append(event)

    delta_v_log = [
        {"spacecraft": sat_id, "delta_v_mps": 0.0}
        for sat_id in satellite_ids
    ]

    data_bundle = {
        "triangle_series": triangle_series,
        "window_events": window_events,
        "delta_v_log": delta_v_log,
        "output_dir": metrics_dir,
    }

    metrics_result = metrics_module.extract_metrics(data_bundle)
    metrics_payload = metrics_result.to_dict()
    tables: MutableMapping[str, List[Mapping[str, Any]]] = {}
    for name, rows in metrics_result.sample_tables.items():
        serialised_rows: List[Mapping[str, Any]] = []
        for row in rows:
            serialised_row: MutableMapping[str, Any] = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    serialised_row[key] = value.isoformat()
                else:
                    serialised_row[key] = value
            serialised_rows.append(serialised_row)
        tables[name] = serialised_rows

    plots = {
        "window_durations": _web_runs_url(metrics_dir / "window_durations.png"),
        "triangle_area": _web_runs_url(metrics_dir / "triangle_area.png"),
    }
    csv_urls = {
        "window_events": _web_runs_url(metrics_dir / "window_events.csv"),
        "triangle_samples": _web_runs_url(metrics_dir / "triangle_geometry.csv"),
        "delta_v_log": _web_runs_url(metrics_dir / "delta_v_usage.csv"),
        "summary": _web_runs_url(metrics_dir / "metrics_summary.json"),
    }

    return {
        "metrics": metrics_payload,
        "tables": tables,
        "plots": plots,
        "csv_urls": csv_urls,
    }


@router.get("/{run_id}/artefacts")
def describe_run_artefacts(run_id: str) -> Mapping[str, Any]:
    """Provide accessible hyperlinks and metadata for run artefacts."""

    record = _find_run_record(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    artefacts = record.get("artefacts") if isinstance(record, Mapping) else {}
    summary = _summarise_artefacts(artefacts if isinstance(artefacts, Mapping) else {})
    return {"artefacts": summary}


def _generate_run_identifiers() -> tuple[str, str]:
    """Generate a run identifier and timestamp conforming to repository policy."""

    now = datetime.now(timezone.utc)
    run_id = now.strftime("run_%Y%m%d_%H%MZ")
    return run_id, now.isoformat().replace("+00:00", "Z")


def _resolve_triangle_scenario(identifier: Optional[str]) -> Path:
    """Resolve triangle scenario identifiers to configuration paths."""

    if identifier is None:
        identifier = DEFAULT_TRIANGLE_SCENARIO
    candidate = SCENARIO_DIR / f"{Path(identifier).stem}.json"
    if not candidate.exists():
        raise HTTPException(status_code=404, detail=f"Scenario '{identifier}' not found.")
    return candidate


def _resolve_generic_scenario(identifier: Optional[str]) -> Path:
    """Resolve general scenario identifiers using the shared configuration loader."""

    if identifier is None:
        identifier = DEFAULT_PIPELINE_SCENARIO
    try:
        return resolve_scenario_path(identifier)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


def _collect_triangle_artefacts(
    result: TriangleFormationResult, output_directory: Path
) -> MutableMapping[str, Optional[str]]:
    """Collect artefact paths for the triangle simulation."""

    artefacts: MutableMapping[str, Optional[str]] = {
        "output_directory": str(output_directory),
    }
    artefacts.update({key: value for key, value in result.artefacts.items()})
    return artefacts


def _collect_scenario_artefacts(
    result: Mapping[str, Any], output_directory: Path
) -> MutableMapping[str, Optional[str]]:
    """Collect artefact paths for the scenario pipeline."""

    artefact_map: MutableMapping[str, Optional[str]] = {
        "output_directory": str(output_directory),
    }
    summary_path = None
    artefacts = result.get("artefacts") if isinstance(result, Mapping) else None
    if isinstance(artefacts, Mapping):
        summary_path = artefacts.get("summary_path")
        artefact_map.update({key: artefacts.get(key) for key in artefacts})
    artefact_map.setdefault("summary_path", summary_path)
    return artefact_map


def _build_debug_command(request: DebugRunRequest) -> List[str]:
    """Compose the ``run_debug.py`` invocation based on the request payload."""

    command: List[str] = [sys.executable, str(PROJECT_ROOT / "run_debug.py")]
    if request.mode == "triangle":
        command.append("--triangle")
        if request.triangle_config:
            command.extend(["--triangle-config", request.triangle_config])
    else:
        command.append("--scenario")
        if request.scenario_id:
            command.append(request.scenario_id)
    if request.output_root:
        command.extend(["--output-root", request.output_root])
    return command


def _schedule_job_cleanup(job: SubprocessJob) -> None:
    """Schedule automatic pruning once the debug subprocess completes."""

    async def _cleanup_task() -> None:
        await job.wait_completed()
        await JOB_MANAGER.prune_completed()

    asyncio.create_task(_cleanup_task())


def _record_run(
    run_id: str,
    timestamp: str,
    *,
    route: str,
    status: str,
    request_payload: Mapping[str, Any],
    source: Mapping[str, Any],
    artefacts: Mapping[str, Any],
    summary: Optional[Mapping[str, Any]],
    error: Optional[str] = None,
) -> None:
    """Append a run record to the repository log."""

    record = {
        "run_id": run_id,
        "timestamp": timestamp,
        "route": route,
        "status": status,
        "request": dict(request_payload),
        "source": dict(source),
        "artefacts": dict(artefacts),
        "summary": summary,
        "error": error,
        "assumptions": request_payload.get("assumptions", []),
        "seed": request_payload.get("seed"),
        "model_versions": {
            "triangle_module": "sim.formation.triangle",
            "scenario_runner": "sim.scripts.run_scenario",
        },
    }
    WEB_ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)
    with RUN_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")


def _iter_run_records() -> Iterable[MutableMapping[str, Any]]:
    """Yield run records stored in the JSON lines artefact."""

    if not RUN_LOG_PATH.exists():
        return ()

    def _generator() -> Iterable[MutableMapping[str, Any]]:
        with RUN_LOG_PATH.open("r", encoding="utf-8") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, Mapping):
                    yield dict(payload)

    return _generator()


def _load_run_history(limit: Optional[int] = None) -> List[MutableMapping[str, Any]]:
    """Collect run records sorted by timestamp, optionally truncated."""

    records = list(_iter_run_records())
    records.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    if limit is not None:
        records = records[:limit]
    return records


def _find_run_record(run_id: str) -> Optional[MutableMapping[str, Any]]:
    """Locate a run record by identifier."""

    for record in _iter_run_records():
        if record.get("run_id") == run_id:
            return record
    return None


def _summarise_artefacts(artefacts: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Transform artefact paths into web-accessible descriptors."""

    summary: MutableMapping[str, Any] = {}
    for key, value in artefacts.items():
        if not value:
            continue
        path = Path(str(value))
        if path.is_file():
            summary[key] = {
                "type": "file",
                "path": str(path),
                "url": _web_runs_url(path),
            }
        elif path.is_dir():
            files = []
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    files.append(
                        {
                            "name": str(child.relative_to(path)),
                            "url": _web_runs_url(child),
                        }
                    )
            summary[key] = {
                "type": "directory",
                "path": str(path),
                "url": _web_runs_url(path),
                "files": files,
            }
        else:
            summary[key] = {
                "type": "missing",
                "path": str(path),
                "url": None,
            }
    return summary


def _web_runs_url(path: Path) -> Optional[str]:
    """Return a web-accessible URL for artefacts stored under ``WEB_ARTEFACT_DIR``."""

    try:
        relative = path.resolve().relative_to(WEB_ARTEFACT_DIR.resolve())
    except ValueError:
        return None
    return f"/web_runs/{relative.as_posix()}"



def _render_interface() -> str:
    """Return the HTML template for the single-page application."""

    bootstrap_payload = {
        "baseConfig": TRIANGLE_BASE_CONFIGURATION,
        "durationOptions": SCENARIO_DURATION_OPTIONS,
        "defaultCity": DEFAULT_CITY_OPTION,
        "constants": {
            "earthRadiusM": EARTH_EQUATORIAL_RADIUS_M,
            "muEarth": EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
        },
        "developmentText": "این وب‌اپلیکیشن در حال توسعه است و تکمیل آن ادامه دارد.",
    }

    try:
        template = WEB_TEMPLATE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as error:  # pragma: no cover - configuration error
        raise RuntimeError("Web interface template is missing.") from error

    if "__BOOTSTRAP_DATA__" not in template:
        raise RuntimeError("Web interface template placeholder missing.")

    bootstrap_json = json.dumps(bootstrap_payload, ensure_ascii=False)
    return template.replace("__BOOTSTRAP_DATA__", bootstrap_json)



@app.get("/debug/log/stream")
async def stream_debug_log(request: Request) -> StreamingResponse:
    """Continuously stream appended ``debug.txt`` content via server-sent events."""

    async def event_generator() -> AsyncIterator[str]:
        last_offset = 0
        while True:
            if await request.is_disconnected():
                break
            if DEBUG_LOG_PATH.exists():
                size = DEBUG_LOG_PATH.stat().st_size
                if size < last_offset:
                    last_offset = 0
                if size > last_offset:
                    with DEBUG_LOG_PATH.open("r", encoding="utf-8", errors="ignore") as handle:
                        handle.seek(last_offset)
                        content = handle.read()
                        last_offset = handle.tell()
                    if content:
                        for line in content.splitlines():
                            payload = json.dumps({"message": line})
                            yield f"data: {payload}\n\n"
            else:
                last_offset = 0
            yield ": heartbeat\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/debug/log/tail")
def tail_debug_log(offset: int = 0) -> Mapping[str, Any]:
    """Return incremental updates from ``debug.txt`` for polling clients."""

    if not DEBUG_LOG_PATH.exists():
        return {"available": False, "content": "", "offset": 0}

    size = DEBUG_LOG_PATH.stat().st_size
    offset = max(0, min(offset, size))
    with DEBUG_LOG_PATH.open("r", encoding="utf-8", errors="ignore") as handle:
        handle.seek(offset)
        content = handle.read()
    return {"available": True, "content": content, "offset": size}


@app.get("/debug/log/download")
def download_debug_log() -> FileResponse:
    """Expose ``debug.txt`` for direct download."""

    if not DEBUG_LOG_PATH.exists():
        raise HTTPException(status_code=404, detail="debug.txt not found.")
    return FileResponse(DEBUG_LOG_PATH, media_type="text/plain", filename="debug.txt")


app.include_router(router)


def _build_cli_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for launching the FastAPI service."""

    parser = argparse.ArgumentParser(
        description=(
            "Launch the interactive formation simulation service using Uvicorn."
        )
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Network interface upon which the server listens.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="TCP port exposed by the service.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable live-reload for local iterative development.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes that Uvicorn should spawn.",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Verbosity level for server diagnostics.",
    )
    return parser


def main(argv: Optional[Sequence[str]] | None = None) -> int:
    """Parse command-line arguments and start the Uvicorn server."""

    arguments = _build_cli_parser().parse_args(
        list(argv) if argv is not None else None
    )
    try:
        import uvicorn
    except ModuleNotFoundError as error:  # pragma: no cover - dependency missing
        raise SystemExit(
            "Uvicorn is required to run the web service. Install it via 'pip install uvicorn'."
        ) from error

    uvicorn.run(
        "run:app",
        host=arguments.host,
        port=arguments.port,
        reload=arguments.reload,
        workers=arguments.workers,
        log_level=arguments.log_level,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI
    raise SystemExit(main())
