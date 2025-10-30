"""Web entry points for running formation simulations and scenario pipelines."""

from __future__ import annotations

import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, root_validator

from sim.formation import simulate_triangle_formation
from sim.formation.triangle import TriangleFormationResult
from sim.scripts.configuration import resolve_scenario_path
from sim.scripts.run_scenario import run_scenario
from sim.scripts import extract_metrics as metrics_module
from src.constellation.orbit import EARTH_EQUATORIAL_RADIUS_M
from src.constellation.web.jobs import JobManager, SubprocessJob

PROJECT_ROOT = Path(__file__).resolve().parent
SCENARIO_DIR = PROJECT_ROOT / "config" / "scenarios"
WEB_ARTEFACT_DIR = PROJECT_ROOT / "artefacts" / "web_runs"
WEB_ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)
RUN_LOG_PATH = WEB_ARTEFACT_DIR / "run_log.jsonl"
DEBUG_LOG_PATH = PROJECT_ROOT / "debug.txt"
DEFAULT_TRIANGLE_SCENARIO = "tehran_triangle"
DEFAULT_PIPELINE_SCENARIO = "tehran_daily_pass"


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

app = FastAPI(title="Formation SAT Run Service")
router = APIRouter(prefix="/runs")
app.mount("/web_runs", StaticFiles(directory=WEB_ARTEFACT_DIR, html=False), name="web_runs")
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

    @root_validator(pre=True)
    def _ensure_source_present(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        scenario = values.get("scenario_id")
        configuration = values.get("configuration")
        if not scenario and not configuration:
            values["scenario_id"] = DEFAULT_TRIANGLE_SCENARIO
        return values


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

    @root_validator(pre=True)
    def _ensure_source_present(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        scenario = values.get("scenario_id")
        configuration = values.get("configuration")
        if not scenario and not configuration:
            values["scenario_id"] = DEFAULT_PIPELINE_SCENARIO
        return values


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

    @root_validator(skip_on_failure=True)
    def _validate_mode_arguments(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        mode = values.get("mode")
        if mode == "triangle":
            values["scenario_id"] = None
        elif mode == "scenario":
            values.setdefault("scenario_id", "tehran_daily_pass")
        return values


@app.on_event("startup")
def _initialise_directories() -> None:
    """Ensure that artefact directories exist before handling requests."""

    WEB_ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)


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

    formation_window = (
        summary.get("metrics", {}).get("formation_window")
        if isinstance(summary.get("metrics"), Mapping)
        else None
    )
    window_events: List[Mapping[str, Any]] = []
    if isinstance(formation_window, Mapping):
        start = formation_window.get("start")
        end = formation_window.get("end")
        if start and end:
            window_events.append({"start": start, "end": end})

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

    base_config_json = json.dumps(TRIANGLE_BASE_CONFIGURATION, ensure_ascii=False)
    duration_options_json = json.dumps(SCENARIO_DURATION_OPTIONS, ensure_ascii=False)
    city_json = json.dumps(DEFAULT_CITY_OPTION, ensure_ascii=False)
    development_text = "این وب‌اپلیکیشن در حال توسعه است و تکمیل آن ادامه دارد."

    return f"""<!DOCTYPE html>
<html lang="fa">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>سامانه کنترل فورمیشن ماهواره‌ای</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700&display=swap" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js" defer></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: 'Vazirmatn', 'Inter', system-ui, sans-serif;
      background: radial-gradient(circle at top, #102641, #020b1a 65%);
      color: #ecf5ff;
      direction: rtl;
    }}
    h1, h2, h3 {{
      margin: 0 0 0.75rem 0;
      font-weight: 600;
    }}
    p {{
      margin: 0 0 0.65rem 0;
      line-height: 1.6;
    }}
    a {{ color: #7fd0ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(220px, 20%) 1fr 1fr;
      gap: 1.25rem;
      padding: 1.5rem;
      min-height: calc(100vh - 60px);
    }}
    .sidebar {{
      background: rgba(8, 23, 43, 0.85);
      border: 1px solid rgba(126, 185, 255, 0.25);
      border-radius: 18px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      backdrop-filter: blur(12px);
      grid-row: 1 / span 2;
    }}
    .sidebar h1 {{
      font-size: 1.4rem;
      letter-spacing: 0.01em;
    }}
    .sidebar nav {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .nav-item {{
      border: 1px solid rgba(126, 185, 255, 0.2);
      background: rgba(18, 52, 86, 0.7);
      color: #f2f6ff;
      padding: 0.65rem 0.9rem;
      border-radius: 12px;
      text-align: center;
      cursor: pointer;
      transition: background 0.2s ease, border 0.2s ease;
      font-weight: 600;
    }}
    .nav-item:hover {{ background: rgba(31, 92, 148, 0.75); }}
    .nav-item.active {{
      border-color: rgba(126, 185, 255, 0.75);
      background: linear-gradient(135deg, rgba(73, 140, 255, 0.85), rgba(142, 81, 255, 0.85));
    }}
    .sidebar-info {{
      background: rgba(12, 32, 58, 0.7);
      border-radius: 14px;
      padding: 1rem;
      border: 1px solid rgba(126, 185, 255, 0.2);
    }}
    .sidebar-info ul {{
      padding: 0;
      margin: 0;
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      font-size: 0.9rem;
      color: #c7ddff;
    }}
    .panel {{
      background: rgba(7, 20, 38, 0.82);
      border: 1px solid rgba(126, 185, 255, 0.25);
      border-radius: 18px;
      padding: 1.5rem;
      backdrop-filter: blur(10px);
      overflow-y: auto;
    }}
    .hidden {{ display: none !important; }}
    form {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    label {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #dce9ff;
    }}
    select, button {{
      padding: 0.6rem 0.8rem;
      border-radius: 12px;
      border: 1px solid rgba(126, 185, 255, 0.25);
      background: rgba(10, 35, 62, 0.9);
      color: #f4f7ff;
      font-size: 0.95rem;
    }}
    select:focus {{
      outline: none;
      border-color: rgba(126, 185, 255, 0.65);
      box-shadow: 0 0 0 2px rgba(126, 185, 255, 0.2);
    }}
    button {{
      cursor: pointer;
      font-weight: 600;
      background: linear-gradient(135deg, #2ca8ff, #8247ff);
      border: none;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    button:hover:not(:disabled) {{
      transform: translateY(-1px);
      box-shadow: 0 12px 28px rgba(41, 163, 255, 0.35);
    }}
    button:disabled {{
      background: #31445f;
      cursor: not-allowed;
      box-shadow: none;
      opacity: 0.7;
    }}
    .status {{
      margin-top: 1rem;
      padding: 0.75rem 1rem;
      border-radius: 14px;
      background: rgba(15, 39, 68, 0.75);
      border: 1px solid rgba(126, 185, 255, 0.2);
      min-height: 3.2rem;
      display: flex;
      align-items: center;
      color: #cde5ff;
    }}
    .status.error {{
      border-color: rgba(255, 120, 120, 0.6);
      background: rgba(80, 22, 32, 0.75);
      color: #ffdede;
    }}
    .summary {{
      margin-top: 1.5rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }}
    .summary-card {{
      border-radius: 14px;
      padding: 1rem;
      background: rgba(12, 32, 58, 0.8);
      border: 1px solid rgba(126, 185, 255, 0.2);
    }}
    .summary-card span {{
      display: block;
      margin-bottom: 0.35rem;
      color: #9fc4ff;
      font-size: 0.85rem;
    }}
    .summary-card strong {{
      font-size: 1.05rem;
      color: #ffffff;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      font-size: 0.9rem;
    }}
    th, td {{
      border: 1px solid rgba(126, 185, 255, 0.15);
      padding: 0.5rem 0.6rem;
      text-align: center;
    }}
    th {{
      background: rgba(18, 47, 84, 0.9);
      color: #e3efff;
    }}
    .visual-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.2rem;
    }}
    figure {{
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    figcaption {{
      font-weight: 600;
      color: #d0e4ff;
    }}
    .three-d-container {{
      position: relative;
      width: 100%;
      height: 360px;
      border-radius: 18px;
      border: 1px solid rgba(126, 185, 255, 0.25);
      background: radial-gradient(circle at 25% 25%, rgba(13, 41, 72, 0.85), rgba(4, 16, 34, 0.9));
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .placeholder {{
      color: #a9c7ff;
      font-size: 0.95rem;
    }}
    canvas {{
      border-radius: 18px;
      background: rgba(5, 18, 33, 0.85);
      border: 1px solid rgba(126, 185, 255, 0.2);
    }}
    #ground-track {{
      width: 100%;
      height: auto;
    }}
    #element-chart {{
      width: 100%;
      height: auto;
    }}
    .settings-status {{
      margin-top: 1.2rem;
      padding: 0.8rem 1rem;
      border-radius: 12px;
      background: rgba(15, 39, 68, 0.8);
      border: 1px solid rgba(126, 185, 255, 0.25);
      color: #d8ecff;
      min-height: 2.5rem;
    }}
    .development-banner {{
      text-align: center;
      padding: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.03em;
      background: rgba(12, 32, 58, 0.85);
      border-top: 1px solid rgba(126, 185, 255, 0.25);
      color: #9fc4ff;
    }}
    @media (max-width: 1100px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        grid-row: auto;
      }}
      #settings-view {{
        grid-column: auto;
      }}
    }}
  </style>
</head>
<body>
  <main class="layout">
    <aside class="sidebar">
      <div>
        <h1>سامانه فورمیشن ماهواره‌ای</h1>
        <p>اجرای تعاملى سناریوهای تشکیل آرایش برای تهران</p>
      </div>
      <nav>
        <button class="nav-item active" data-view="home">خانه</button>
        <button class="nav-item" data-view="settings">تنظیمات</button>
      </nav>
      <section class="sidebar-info">
        <h2>اطلاعات پیکربندى</h2>
        <p>مدت سناریو از فایل‌های پیکربندى موجود در مخزن استخراج شده است.</p>
        <ul id="duration-notes"></ul>
      </section>
    </aside>
    <section id="home-controls" class="panel">
      <h2>اجرای سناریوى شکل‌دهى</h2>
      <form id="scenario-form">
        <label for="duration-select">مدت اجرای سناریو</label>
        <select id="duration-select"></select>
        <p class="field-hint" id="duration-hint"></p>
        <button type="submit" id="run-button">اجرای سناریو</button>
      </form>
      <div class="status" id="status-message">برای آغاز، مدت سناریو را انتخاب کنید.</div>
      <section class="summary" id="run-summary"></section>
      <section class="table-wrapper">
        <h3>پارامترهای مداری ماهواره‌ها</h3>
        <table id="orbital-table">
          <thead>
            <tr>
              <th>ماهواره</th>
              <th>نیم‌محور بزرگ (km)</th>
              <th>اگزا‌نتریسیته</th>
              <th>میل مدار (°)</th>
              <th>گره صعودى راست (°)</th>
              <th>آرگومان حضیض (°)</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </section>
    </section>
    <section id="home-visual" class="panel">
      <h2>نمایش مسیر و تحلیل‌ها</h2>
      <div class="visual-grid">
        <figure>
          <figcaption>نمای سه‌بعدى مدار و موقعیت تهران</figcaption>
          <div id="three-d-view" class="three-d-container">
            <span class="placeholder">پس از اجراى سناریو، مدل سه‌بعدى نمایش داده مى‌شود.</span>
          </div>
        </figure>
        <figure>
          <figcaption>گراوند ترک متمرکز بر تهران</figcaption>
          <canvas id="ground-track" width="720" height="420"></canvas>
        </figure>
        <figure class="wide">
          <figcaption>تغییر المان‌های مداری طی اجرا</figcaption>
          <canvas id="element-chart" width="900" height="360"></canvas>
        </figure>
      </div>
    </section>
    <section id="settings-view" class="panel hidden" style="grid-column: 2 / span 2;">
      <h2>تنظیمات سناریو</h2>
      <form id="settings-form">
        <label for="city-select">انتخاب شهر هدف</label>
        <select id="city-select"></select>
        <button type="button" id="compute-elements" disabled>محاسبه پارامترهای مداری</button>
        <button type="submit" id="save-settings">ذخیره تغییرات</button>
      </form>
      <div class="settings-status" id="settings-status">تغییرى ثبت نشده است.</div>
    </section>
  </main>
  <footer class="development-banner">در حال توسعه</footer>
  <script>
    const BASE_TRIANGLE_CONFIG = {base_config_json};
    const DURATION_OPTIONS = {duration_options_json};
    const DEFAULT_CITY = {city_json};
    const EARTH_RADIUS_M = {EARTH_EQUATORIAL_RADIUS_M};
    const MU_EARTH = {EARTH_GRAVITATIONAL_PARAMETER_M3_S2};
    const DEVELOPMENT_TEXT = {json.dumps(development_text, ensure_ascii=False)};

    const state = {{
      view: 'home',
      running: false,
      selectedDuration: null,
      lastRun: null,
      city: DEFAULT_CITY,
      threeAnimation: null,
      threeRenderer: null,
    }};

    const navButtons = Array.from(document.querySelectorAll('.nav-item'));
    const durationSelect = document.getElementById('duration-select');
    const durationHint = document.getElementById('duration-hint');
    const statusMessage = document.getElementById('status-message');
    const summaryContainer = document.getElementById('run-summary');
    const orbitalTableBody = document.querySelector('#orbital-table tbody');
    const groundTrackCanvas = document.getElementById('ground-track');
    const elementChartCanvas = document.getElementById('element-chart');
    const threeContainer = document.getElementById('three-d-view');
    const homeControls = document.getElementById('home-controls');
    const homeVisual = document.getElementById('home-visual');
    const settingsView = document.getElementById('settings-view');
    const durationNotes = document.getElementById('duration-notes');
    const citySelect = document.getElementById('city-select');
    const settingsStatus = document.getElementById('settings-status');
    const scenarioForm = document.getElementById('scenario-form');
    const settingsForm = document.getElementById('settings-form');

    function initialiseNavigation() {{
      navButtons.forEach((button) => {{
        button.addEventListener('click', () => {{
          setView(button.dataset.view || 'home');
        }});
      }});
    }}

    function setView(view) {{
      state.view = view;
      navButtons.forEach((button) => {{
        button.classList.toggle('active', button.dataset.view === view);
      }});
      if (view === 'home') {{
        homeControls.classList.remove('hidden');
        homeVisual.classList.remove('hidden');
        settingsView.classList.add('hidden');
      }} else {{
        homeControls.classList.add('hidden');
        homeVisual.classList.add('hidden');
        settingsView.classList.remove('hidden');
      }}
    }}

    function populateDurations() {{
      durationSelect.innerHTML = '';
      const seenNotes = new Set();
      DURATION_OPTIONS.forEach((option, index) => {{
        const element = document.createElement('option');
        element.value = String(option.days);
        element.textContent = option.label;
        if (index === 0) {{
          element.selected = true;
          state.selectedDuration = option;
          durationHint.textContent = option.explanation;
        }}
        durationSelect.appendChild(element);
        if (option.explanation && !seenNotes.has(option.explanation)) {{
          const noteItem = document.createElement('li');
          noteItem.textContent = option.explanation;
          durationNotes.appendChild(noteItem);
          seenNotes.add(option.explanation);
        }}
      }});
      durationSelect.addEventListener('change', () => {{
        const selectedDays = parseFloat(durationSelect.value);
        const match = DURATION_OPTIONS.find((item) => Math.abs(item.days - selectedDays) < 1e-6);
        state.selectedDuration = match || null;
        durationHint.textContent = match ? match.explanation : '';
      }});
    }}

    function populateCities() {{
      citySelect.innerHTML = '';
      const option = document.createElement('option');
      option.value = DEFAULT_CITY.id;
      option.textContent = DEFAULT_CITY.label;
      option.selected = true;
      citySelect.appendChild(option);
      citySelect.addEventListener('change', () => {{
        state.city = DEFAULT_CITY;
      }});
    }}

    function updateStatus(message, isError = false) {{
      statusMessage.textContent = message;
      statusMessage.classList.toggle('error', Boolean(isError));
    }}

    function resetSummaries() {{
      summaryContainer.innerHTML = '';
      orbitalTableBody.innerHTML = '';
      resetGroundTrack();
      resetElementChart();
      resetThreeView();
    }}

    function resetGroundTrack() {{
      if (!groundTrackCanvas) return;
      const ctx = groundTrackCanvas.getContext('2d');
      ctx.clearRect(0, 0, groundTrackCanvas.width, groundTrackCanvas.height);
      ctx.fillStyle = '#061830';
      ctx.fillRect(0, 0, groundTrackCanvas.width, groundTrackCanvas.height);
      ctx.fillStyle = '#94b8ff';
      ctx.font = '16px Vazirmatn, sans-serif';
      ctx.fillText('پس از اجراى سناریو مسیر پوشش نمایش داده خواهد شد.', 30, groundTrackCanvas.height / 2);
    }}

    function resetElementChart() {{
      if (!elementChartCanvas) return;
      const ctx = elementChartCanvas.getContext('2d');
      ctx.clearRect(0, 0, elementChartCanvas.width, elementChartCanvas.height);
      ctx.fillStyle = '#061830';
      ctx.fillRect(0, 0, elementChartCanvas.width, elementChartCanvas.height);
      ctx.fillStyle = '#94b8ff';
      ctx.font = '16px Vazirmatn, sans-serif';
      ctx.fillText('نمودار المان‌ها پس از اجرا نمایش داده مى‌شود.', 40, elementChartCanvas.height / 2);
    }}

    function resetThreeView() {{
      if (state.threeAnimation) {{
        cancelAnimationFrame(state.threeAnimation);
        state.threeAnimation = null;
      }}
      if (state.threeRenderer) {{
        state.threeRenderer.dispose();
        state.threeRenderer = null;
      }}
      threeContainer.innerHTML = '<span class="placeholder">پس از اجراى سناریو، مدل سه‌بعدى نمایش داده مى‌شود.</span>';
    }}

    async function runScenario(event) {{
      event.preventDefault();
      if (state.running) return;
      if (!state.selectedDuration) {{
        updateStatus('ابتدا مدت سناریو را مشخص کنید.', true);
        return;
      }}
      state.running = true;
      updateStatus('در حال ارسال تنظیمات به شبیه‌ساز...');
      resetSummaries();
      try {{
        const payload = buildScenarioPayload();
        const response = await fetch('/runs/triangle', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        if (!response.ok) {{
          let detail = 'اجرای سناریو با خطا مواجه شد.';
          try {{
            const errorPayload = await response.json();
            if (errorPayload && errorPayload.detail) {{
              detail = errorPayload.detail;
            }}
          }} catch (err) {{
            detail = detail;
          }}
          throw new Error(detail);
        }}
        const data = await response.json();
        state.lastRun = data;
        renderRunSummary(data);
        renderOrbitalTable(data.summary);
        renderGroundTrack(data.summary.geometry);
        renderElementChart(data.summary.geometry);
        renderThreeView(data.summary.geometry);
        updateStatus('سناریو با موفقیت اجرا شد.');
      }} catch (error) {{
        updateStatus(error.message || 'خطاى ناشناخته رخ داده است.', true);
      }} finally {{
        state.running = false;
      }}
    }}

    function buildScenarioPayload() {{
      const duration = state.selectedDuration ? state.selectedDuration.days : 1;
      const config = JSON.parse(JSON.stringify(BASE_TRIANGLE_CONFIG || {{}}));
      if (!config.formation) {{
        config.formation = {{}};
      }}
      const durationSeconds = duration * 86_400.0;
      let step = config.formation.time_step_s || 1.0;
      if (durationSeconds > 6 * 3_600) {{
        step = 60.0;
      }}
      if (durationSeconds > 3 * 86_400) {{
        step = 300.0;
      }}
      config.formation.duration_s = durationSeconds;
      config.formation.time_step_s = step;
      config.metadata = config.metadata || {{}};
      config.metadata.notes = config.metadata.notes || [];
      config.metadata.notes.push(`Duration selected in UI: ${duration} days`);
      return {{
        configuration: config,
        assumptions: [
          `duration_days=${duration.toFixed(3)}`,
          `time_step_s=${step.toFixed(3)}`,
          `city=${state.city.id}`,
        ],
      }};
    }}

    function renderRunSummary(data) {{
      summaryContainer.innerHTML = '';
      if (!data) return;
      const {{ run_id: runId, timestamp }} = data;
      const selected = state.selectedDuration ? state.selectedDuration.label : 'نامشخص';
      const cards = [
        {{
          title: 'شناسه اجرا',
          value: runId,
        }},
        {{
          title: 'زمان ثبت',
          value: new Date(timestamp).toLocaleString('fa-IR'),
        }},
        {{
          title: 'مدت انتخاب‌شده',
          value: selected,
        }},
      ];
      cards.forEach((card) => {{
        const wrapper = document.createElement('div');
        wrapper.className = 'summary-card';
        const label = document.createElement('span');
        label.textContent = card.title;
        const value = document.createElement('strong');
        value.textContent = card.value;
        wrapper.append(label, value);
        summaryContainer.appendChild(wrapper);
      }});
    }}

    function renderOrbitalTable(summary) {{
      orbitalTableBody.innerHTML = '';
      if (!summary || !summary.metrics || !summary.metrics.orbital_elements) {{
        return;
      }}
      const entries = summary.metrics.orbital_elements;
      Object.keys(entries).forEach((satId) => {{
        const row = document.createElement('tr');
        const cell = (value) => {{
          const td = document.createElement('td');
          td.textContent = value;
          return td;
        }};
        const parameters = entries[satId];
        row.appendChild(cell(satId));
        row.appendChild(cell(formatNumber(parameters.semi_major_axis_km)));
        row.appendChild(cell(formatNumber(parameters.eccentricity, 6)));
        row.appendChild(cell(formatNumber(parameters.inclination_deg)));
        row.appendChild(cell(formatNumber(parameters.raan_deg)));
        row.appendChild(cell(formatNumber(parameters.argument_of_perigee_deg)));
        orbitalTableBody.appendChild(row);
      }});
    }}

    function renderGroundTrack(geometry) {{
      resetGroundTrack();
      if (!geometry || !geometry.latitudes_rad) return;
      const ctx = groundTrackCanvas.getContext('2d');
      const width = groundTrackCanvas.width;
      const height = groundTrackCanvas.height;
      const latCentre = DEFAULT_CITY.latitude_deg;
      const lonCentre = DEFAULT_CITY.longitude_deg;
      const latRange = 18;
      const lonRange = 28;
      ctx.fillStyle = '#041327';
      ctx.fillRect(0, 0, width, height);
      ctx.strokeStyle = 'rgba(126, 185, 255, 0.25)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.moveTo(width / 2, 0);
      ctx.lineTo(width / 2, height);
      ctx.stroke();
      const toCanvas = (latDeg, lonDeg) => {{
        const x = ((lonDeg - (lonCentre - lonRange)) / (2 * lonRange)) * width;
        const y = height - ((latDeg - (latCentre - latRange)) / (2 * latRange)) * height;
        return [Math.max(0, Math.min(width, x)), Math.max(0, Math.min(height, y))];
      }};
      const colours = ['#7fd0ff', '#ffb74d', '#ce93d8', '#80cbc4'];
      (geometry.satellite_ids || []).forEach((satId, index) => {{
        const lats = geometry.latitudes_rad[satId] || [];
        const lons = geometry.longitudes_rad[satId] || [];
        if (!lats.length || !lons.length) return;
        ctx.beginPath();
        ctx.lineWidth = 2;
        ctx.strokeStyle = colours[index % colours.length];
        lats.forEach((lat, i) => {{
          const latDeg = lat * (180 / Math.PI);
          let lonDeg = lons[i] * (180 / Math.PI);
          if (lonDeg - lonCentre > 180) lonDeg -= 360;
          if (lonDeg - lonCentre < -180) lonDeg += 360;
          const [x, y] = toCanvas(latDeg, lonDeg);
          if (i === 0) {{
            ctx.moveTo(x, y);
          }} else {{
            ctx.lineTo(x, y);
          }}
        }});
        ctx.stroke();
      }});
      const [cx, cy] = toCanvas(latCentre, lonCentre);
      ctx.fillStyle = '#ffd54f';
      ctx.beginPath();
      ctx.arc(cx, cy, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.font = '15px Vazirmatn, sans-serif';
      ctx.fillStyle = '#ffe082';
      ctx.fillText('تهران', cx + 10, cy - 10);
    }}

    function renderElementChart(geometry) {{
      resetElementChart();
      if (!geometry || !geometry.positions_m) return;
      const ctx = elementChartCanvas.getContext('2d');
      const width = elementChartCanvas.width;
      const height = elementChartCanvas.height;
      ctx.fillStyle = '#041327';
      ctx.fillRect(0, 0, width, height);
      const times = (geometry.times || []).map((item) => Date.parse(item));
      if (times.length < 3) return;
      const start = times[0];
      const timeSeconds = times.map((t) => (t - start) / 1000.0);
      const colours = ['#7fd0ff', '#ffb74d', '#ce93d8', '#80cbc4'];
      const metrics = [
        {{ key: 'semiMajorAxis', label: 'نیم‌محور بزرگ (km)' }},
        {{ key: 'inclination', label: 'میل مدار (°)' }},
        {{ key: 'raan', label: 'گره صعودى راست (°)' }},
      ];
      const perSatellite = {{}};
      (geometry.satellite_ids || []).forEach((satId) => {{
        const positions = geometry.positions_m[satId] || [];
        const velocities = estimateVelocities(positions, timeSeconds);
        perSatellite[satId] = computeOrbitalElementsSeries(positions, velocities);
      }});
      metrics.forEach((metric, index) => {{
        const top = index * (height / metrics.length);
        const panelHeight = height / metrics.length;
        drawMetricPanel(ctx, {{
          top,
          height: panelHeight,
          width,
          metric,
          timeSeconds,
          perSatellite,
          colours,
        }});
      }});
      drawLegend(ctx, {{
        colours,
        satelliteIds: geometry.satellite_ids || [],
        width,
        height,
      }});
    }}

    function drawMetricPanel(ctx, config) {{
      const {{ top, height, width, metric, timeSeconds, perSatellite, colours }} = config;
      ctx.save();
      ctx.strokeStyle = 'rgba(126, 185, 255, 0.2)';
      ctx.beginPath();
      ctx.rect(40, top + 10, width - 80, height - 30);
      ctx.stroke();
      const values = [];
      Object.keys(perSatellite).forEach((satId) => {{
        const series = perSatellite[satId][metric.key] || [];
        series.forEach((value) => values.push(value));
      }});
      if (!values.length) {{
        ctx.restore();
        return;
      }}
      const min = Math.min(...values);
      const max = Math.max(...values);
      const margin = (max - min) * 0.1 || 1.0;
      const lower = min - margin;
      const upper = max + margin;
      Object.keys(perSatellite).forEach((satId, index) => {{
        const series = perSatellite[satId][metric.key] || [];
        if (!series.length) return;
        ctx.beginPath();
        ctx.lineWidth = 2;
        ctx.strokeStyle = colours[index % colours.length];
        series.forEach((value, i) => {{
          const x = 40 + ((timeSeconds[i] - timeSeconds[0]) / (timeSeconds[timeSeconds.length - 1] - timeSeconds[0])) * (width - 80);
          const y = top + height - 30 - ((value - lower) / (upper - lower)) * (height - 40);
          if (i === 0) {{
            ctx.moveTo(x, y);
          }} else {{
            ctx.lineTo(x, y);
          }}
        }});
        ctx.stroke();
      }});
      ctx.fillStyle = '#d0e4ff';
      ctx.font = '15px Vazirmatn, sans-serif';
      ctx.fillText(metric.label, 50, top + 30);
      ctx.restore();
    }}

    function drawLegend(ctx, config) {{
      const {{ colours, satelliteIds, width, height }} = config;
      ctx.save();
      const startX = width - 220;
      let currentY = height - 30;
      ctx.font = '14px Vazirmatn, sans-serif';
      satelliteIds.forEach((satId, index) => {{
        ctx.fillStyle = colours[index % colours.length];
        ctx.fillRect(startX + index * 70, currentY - 12, 14, 14);
        ctx.fillStyle = '#d0e4ff';
        ctx.fillText(satId, startX + index * 70 + 20, currentY);
      }});
      ctx.restore();
    }}

    function renderThreeView(geometry) {{
      resetThreeView();
      if (!geometry || !geometry.positions_m || !window.THREE) {{
        return;
      }}
      const width = threeContainer.clientWidth || 480;
      const height = threeContainer.clientHeight || 360;
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x020b1a);
      const camera = new THREE.PerspectiveCamera(45, width / Math.max(height, 1), 0.1, 1000);
      camera.position.set(0, -4.8, 2.6);
      const renderer = new THREE.WebGLRenderer({{ antialias: true }});
      renderer.setSize(width, height);
      threeContainer.innerHTML = '';
      threeContainer.appendChild(renderer.domElement);
      state.threeRenderer = renderer;
      const ambient = new THREE.AmbientLight(0xffffff, 0.65);
      const directional = new THREE.DirectionalLight(0xffffff, 0.55);
      directional.position.set(5, 3, 5);
      scene.add(ambient);
      scene.add(directional);
      const earthGeometry = new THREE.SphereGeometry(1, 48, 48);
      const earthMaterial = new THREE.MeshPhongMaterial({{
        color: 0x0b2542,
        emissive: 0x061628,
        shininess: 18,
        transparent: true,
        opacity: 0.95,
      }});
      const earth = new THREE.Mesh(earthGeometry, earthMaterial);
      scene.add(earth);
      const colours = [0x7fd0ff, 0xffb74d, 0xce93d8, 0x80cbc4];
      (geometry.satellite_ids || []).forEach((satId, index) => {{
        const samples = geometry.positions_m[satId] || [];
        const points = samples.map((point) => {{
          return new THREE.Vector3(point[0] / EARTH_RADIUS_M, point[1] / EARTH_RADIUS_M, point[2] / EARTH_RADIUS_M);
        }});
        if (!points.length) return;
        const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
        const lineMaterial = new THREE.LineBasicMaterial({{ color: colours[index % colours.length], linewidth: 2 }});
        const orbitLine = new THREE.Line(lineGeometry, lineMaterial);
        scene.add(orbitLine);
        const satelliteMesh = new THREE.Mesh(new THREE.SphereGeometry(0.035, 16, 16), new THREE.MeshBasicMaterial({{ color: colours[index % colours.length] }}));
        satelliteMesh.position.copy(points[points.length - 1]);
        scene.add(satelliteMesh);
      }});
      const lat = DEFAULT_CITY.latitude_deg * (Math.PI / 180);
      const lon = DEFAULT_CITY.longitude_deg * (Math.PI / 180);
      const tehranMarker = new THREE.Mesh(new THREE.SphereGeometry(0.04, 16, 16), new THREE.MeshBasicMaterial({{ color: 0xffd54f }}));
      tehranMarker.position.set(
        Math.cos(lat) * Math.cos(lon),
        Math.cos(lat) * Math.sin(lon),
        Math.sin(lat)
      );
      scene.add(tehranMarker);
      function animate() {{
        state.threeAnimation = requestAnimationFrame(animate);
        earth.rotation.y += 0.0008;
        renderer.render(scene, camera);
      }}
      animate();
    }}

    function estimateVelocities(positions, timeSeconds) {{
      const velocities = [];
      if (!positions || positions.length !== timeSeconds.length) {{
        return velocities;
      }}
      for (let i = 0; i < positions.length; i += 1) {{
        let dt;
        let delta;
        if (i === 0) {{
          dt = timeSeconds[i + 1] - timeSeconds[i];
          delta = subtractVectors(positions[i + 1], positions[i]);
        }} else if (i === positions.length - 1) {{
          dt = timeSeconds[i] - timeSeconds[i - 1];
          delta = subtractVectors(positions[i], positions[i - 1]);
        }} else {{
          dt = timeSeconds[i + 1] - timeSeconds[i - 1];
          delta = subtractVectors(positions[i + 1], positions[i - 1]);
        }}
        const scale = dt !== 0 ? 1 / dt : 0;
        velocities.push(scaleVector(delta, scale));
      }}
      return velocities;
    }}

    function computeOrbitalElementsSeries(positions, velocities) {{
      const semiMajorAxis = [];
      const inclination = [];
      const raan = [];
      const eccentricity = [];
      for (let i = 0; i < positions.length; i += 1) {{
        const r = positions[i];
        const v = velocities[i] || [0, 0, 0];
        const rMag = vectorNorm(r);
        const vMag = vectorNorm(v);
        if (rMag === 0) {{
          semiMajorAxis.push(0);
          inclination.push(0);
          raan.push(0);
          eccentricity.push(0);
          continue;
        }}
        const h = crossProduct(r, v);
        const hMag = vectorNorm(h);
        const n = crossProduct([0, 0, 1], h);
        const nMag = vectorNorm(n);
        const eVector = subtractVectors(scaleVector(crossProduct(v, h), 1 / MU_EARTH), scaleVector(r, 1 / rMag));
        const eMag = vectorNorm(eVector);
        eccentricity.push(eMag);
        const energy = (vMag * vMag) / 2 - MU_EARTH / rMag;
        const a = Math.abs(energy) > 1e-9 ? -MU_EARTH / (2 * energy) : Infinity;
        semiMajorAxis.push(a / 1000.0);
        const inc = hMag > 0 ? Math.acos(clamp(h[2] / hMag, -1, 1)) : 0;
        inclination.push(inc * (180 / Math.PI));
        let raanValue = 0;
        if (nMag > 1e-10) {{
          raanValue = Math.acos(clamp(n[0] / nMag, -1, 1));
          if (n[1] < 0) {{
            raanValue = 2 * Math.PI - raanValue;
          }}
        }}
        raan.push(raanValue * (180 / Math.PI));
      }}
      return {{
        semiMajorAxis,
        inclination,
        raan,
        eccentricity,
      }};
    }}

    function clamp(value, min, max) {{
      return Math.max(min, Math.min(max, value));
    }}

    function subtractVectors(a, b) {{
      return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    }}

    function scaleVector(vector, scalar) {{
      return [vector[0] * scalar, vector[1] * scalar, vector[2] * scalar];
    }}

    function crossProduct(a, b) {{
      return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
      ];
    }}

    function vectorNorm(vector) {{
      return Math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2]);
    }}

    function formatNumber(value, digits = 3) {{
      if (value === undefined || value === null || Number.isNaN(value)) {{
        return '—';
      }}
      return Number(value).toFixed(digits);
    }}

    scenarioForm.addEventListener('submit', runScenario);
    settingsForm.addEventListener('submit', (event) => {{
      event.preventDefault();
      settingsStatus.textContent = 'تنظیمات ذخیره شد (محلى). اتصال به سناریو برقرار است.';
    }});

    resetGroundTrack();
    resetElementChart();
    initialiseNavigation();
    populateDurations();
    populateCities();
    settingsStatus.textContent = DEVELOPMENT_TEXT;
  </script>
</body>
</html>
"""



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
