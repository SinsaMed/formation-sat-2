"""Web entry points for running formation simulations and scenario pipelines."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, root_validator

from sim.formation import simulate_triangle_formation
from sim.formation.triangle import TriangleFormationResult
from sim.scripts.configuration import resolve_scenario_path
from sim.scripts.run_scenario import run_scenario
from sim.scripts import extract_metrics as metrics_module
from src.constellation.orbit import EARTH_EQUATORIAL_RADIUS_M

PROJECT_ROOT = Path(__file__).resolve().parent
SCENARIO_DIR = PROJECT_ROOT / "config" / "scenarios"
WEB_ARTEFACT_DIR = PROJECT_ROOT / "artefacts" / "web_runs"
WEB_ARTEFACT_DIR.mkdir(parents=True, exist_ok=True)
RUN_LOG_PATH = WEB_ARTEFACT_DIR / "run_log.jsonl"
DEBUG_LOG_PATH = PROJECT_ROOT / "debug.txt"
DEFAULT_TRIANGLE_SCENARIO = "tehran_triangle"
DEFAULT_PIPELINE_SCENARIO = "tehran_daily_pass"

app = FastAPI(title="Formation SAT Run Service")
router = APIRouter(prefix="/runs")
app.mount("/web_runs", StaticFiles(directory=WEB_ARTEFACT_DIR, html=False), name="web_runs")


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

    return f"""<!DOCTYPE html>
<html lang=\"fa\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>سامانه اجرای Formation SAT</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap\" rel=\"stylesheet\" />
  <script src=\"https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.27.0/plotly.min.js\" defer></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: radial-gradient(circle at top, #123a5c, #020b1a 70%);
      color: #f5f7fa;
      min-height: 100vh;
      direction: rtl;
    }}
    h1, h2 {{
      font-weight: 600;
      margin: 0 0 0.75rem 0;
    }}
    h3 {{
      font-weight: 600;
      margin: 1rem 0 0.5rem 0;
    }}
    p {{
      line-height: 1.6;
      margin: 0 0 0.5rem 0;
    }}
    a {{ color: #7fd0ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(260px, 320px) minmax(260px, 320px) 1fr;
      gap: 1.5rem;
      padding: 1.5rem;
      height: 100vh;
    }}
    .panel {{
      background: rgba(4, 20, 38, 0.78);
      border: 1px solid rgba(126, 185, 255, 0.2);
      border-radius: 16px;
      padding: 1.25rem;
      overflow-y: auto;
      backdrop-filter: blur(12px);
      box-shadow: 0 18px 40px rgba(0, 20, 40, 0.35);
    }}
    label {{
      display: block;
      font-size: 0.9rem;
      margin-bottom: 0.4rem;
    }}
    input, select, textarea {{
      width: 100%;
      padding: 0.5rem 0.75rem;
      border-radius: 10px;
      border: 1px solid rgba(140, 190, 255, 0.25);
      background: rgba(5, 18, 33, 0.8);
      color: #f5f7fa;
      margin-bottom: 0.8rem;
    }}
    textarea {{
      min-height: 110px;
      resize: vertical;
    }}
    button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      padding: 0.6rem 1.1rem;
      border-radius: 999px;
      border: none;
      background: linear-gradient(135deg, #29a3ff, #8247ff);
      color: #ffffff;
      font-weight: 600;
      cursor: pointer;
      margin-top: 0.4rem;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    button:hover {{
      transform: translateY(-1px);
      box-shadow: 0 10px 25px rgba(41, 163, 255, 0.35);
    }}
    button:disabled {{
      background: #31445f;
      cursor: not-allowed;
      box-shadow: none;
    }}
    ul.history {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .history-item {{
      padding: 0.85rem 1rem;
      border-radius: 14px;
      border: 1px solid rgba(126, 185, 255, 0.15);
      background: rgba(9, 27, 48, 0.65);
      cursor: pointer;
      transition: border 0.2s ease, transform 0.2s ease;
    }}
    .history-item.active {{
      border-color: rgba(126, 185, 255, 0.8);
      transform: translateY(-2px);
    }}
    .history-item:hover {{
      border-color: rgba(126, 185, 255, 0.35);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.1rem 0.55rem;
      border-radius: 999px;
      font-size: 0.75rem;
      margin-left: 0.35rem;
      background: rgba(126, 185, 255, 0.18);
      color: #bcdcff;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.75rem;
      margin-top: 1rem;
    }}
    .summary-card {{
      padding: 0.9rem 1rem;
      border-radius: 12px;
      border: 1px solid rgba(126, 185, 255, 0.25);
      background: rgba(7, 24, 44, 0.8);
    }}
    .charts {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
      margin-top: 1.5rem;
    }}
    .charts figure {{
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .charts img {{
      width: 100%;
      border-radius: 14px;
      border: 1px solid rgba(126, 185, 255, 0.25);
      background: rgba(4, 20, 38, 0.6);
    }}
    canvas {{
      border-radius: 16px;
      border: 1px solid rgba(126, 185, 255, 0.2);
      width: 100%;
      background: rgba(3, 17, 33, 0.6);
    }}
    .artefact-list {{
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }}
    .artefact-entry {{
      border: 1px solid rgba(126, 185, 255, 0.18);
      border-radius: 12px;
      padding: 0.75rem 0.9rem;
      background: rgba(9, 27, 48, 0.58);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 0.6rem;
      font-size: 0.85rem;
    }}
    th, td {{
      border: 1px solid rgba(126, 185, 255, 0.1);
      padding: 0.4rem 0.5rem;
      text-align: center;
    }}
    th {{
      background: rgba(15, 39, 68, 0.9);
    }}
    pre {{
      background: rgba(5, 18, 33, 0.8);
      border-radius: 12px;
      padding: 0.75rem;
      border: 1px solid rgba(126, 185, 255, 0.2);
      max-height: 260px;
      overflow-y: auto;
      direction: ltr;
    }}
    .status-message {{
      margin-top: 0.5rem;
      font-size: 0.85rem;
      color: #9ed3ff;
    }}
    @media (max-width: 1200px) {{
      .layout {{
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        height: auto;
      }}
      body {{
        padding-bottom: 2rem;
      }}
    }}
  </style>
</head>
<body>
  <main class=\"layout\">
    <section id=\"controls\" class=\"panel\">
      <h1>کنترل اجرا</h1>
      <p>سناریو یا تنظیمات درون‌خطی را انتخاب کنید و سپس شبیه‌سازی را اجرا نمایید. نتایج کامل در ستون سمت راست نمایش داده می‌شوند.</p>
      <form id=\"triangle-form\">
        <h2>شبیه‌سازی مثلث</h2>
        <label for=\"triangle-scenario\">شناسه سناریو ذخیره‌شده</label>
        <select id=\"triangle-scenario\" name=\"scenario\"></select>
        <label for=\"triangle-config\">پیکربندی درون‌خطی (JSON اختیاری)</label>
        <textarea id=\"triangle-config\" placeholder=\"{{}}\"></textarea>
        <label for=\"triangle-assumptions\">فرضیات (با ویرگول جدا کنید)</label>
        <input id=\"triangle-assumptions\" placeholder=\"A1, A2\" />
        <label for=\"triangle-seed\">seed تصادفى</label>
        <input id=\"triangle-seed\" type=\"number\" min=\"0\" step=\"1\" />
        <button type=\"submit\">اجرای مثلث</button>
      </form>
      <form id=\"scenario-form\" style=\"margin-top:1.5rem;\">
        <h2>اجرای سناریوى عمومی</h2>
        <label for=\"scenario-id\">شناسه سناریو ذخیره‌شده</label>
        <select id=\"scenario-id\" name=\"scenario\"></select>
        <label for=\"scenario-config\">پیکربندی درون‌خطی (JSON اختیاری)</label>
        <textarea id=\"scenario-config\" placeholder=\"{{}}\"></textarea>
        <label for=\"scenario-metrics\">اولویت متریک‌ها (با ویرگول جدا کنید)</label>
        <input id=\"scenario-metrics\" placeholder=\"metric_a, metric_b\" />
        <label for=\"scenario-assumptions\">فرضیات</label>
        <input id=\"scenario-assumptions\" placeholder=\"Assumption 1\" />
        <label for=\"scenario-seed\">seed تصادفى</label>
        <input id=\"scenario-seed\" type=\"number\" min=\"0\" step=\"1\" />
        <button type=\"submit\">اجرای سناریو</button>
      </form>
      <div class=\"status-message\" id=\"status-message\"></div>
      <button id=\"refresh-history\" style=\"margin-top:1rem;\">به‌روزرسانی تاریخچه</button>
    </section>
    <section id=\"history-panel\" class=\"panel\">
      <h1>تاریخچه اجراها</h1>
      <ul class=\"history\" id=\"run-history\"></ul>
    </section>
    <section id=\"output-panel\" class=\"panel\">
      <h1>نمایش خروجی و نمودارها</h1>
      <div id=\"run-summary\"></div>
      <div id=\"window-info\"></div>
      <div class=\"artefact-list\" id=\"artefact-links\"></div>
      <section class=\"charts\">
        <figure>
          <figcaption>مدت‌زمان پنجره‌ها</figcaption>
          <img id=\"window-plot\" alt=\"نمودار مدت‌زمان پنجره‌ها\" />
          <a id=\"window-csv\" target=\"_blank\">دریافت CSV پنجره‌ها</a>
        </figure>
        <figure>
          <figcaption>مساحت مثلث</figcaption>
          <img id=\"triangle-plot\" alt=\"نمودار مساحت مثلث\" />
          <a id=\"triangle-csv\" target=\"_blank\">دریافت CSV مثلث</a>
        </figure>
      </section>
      <div id=\"metrics-tables\"></div>
      <h2 style=\"margin-top:1.5rem;\">مسیر زمینی</h2>
      <canvas id=\"ground-track\" width=\"720\" height=\"360\"></canvas>
      <h2 style=\"margin-top:1.5rem;\">نمای سه‌بعدى مدار</h2>
      <div id=\"three-d-view\" style=\"width:100%; height:420px;\"></div>
      <section style=\"margin-top:1.5rem;\">
        <h2>گزارش لحظه‌ای debug.txt</h2>
        <div style=\"display:flex; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.5rem;\">
          <button id=\"debug-refresh\" type=\"button\">به‌روزرسانی لاگ</button>
          <a href=\"/debug/log/download\" target=\"_blank\" class=\"badge\">دانلود فایل debug.txt</a>
        </div>
        <pre id=\"debug-log\">(در انتظار به‌روزرسانی)</pre>
      </section>
    </section>
  </main>
  <script defer>
    const EARTH_RADIUS_M = {EARTH_EQUATORIAL_RADIUS_M};
    const state = {{
      runs: [],
      selectedRunId: null,
      debugOffset: 0,
      debugTimer: null,
    }};

    const historyList = document.getElementById('run-history');
    const statusMessage = document.getElementById('status-message');
    const windowInfo = document.getElementById('window-info');
    const artefactContainer = document.getElementById('artefact-links');
    const metricsTables = document.getElementById('metrics-tables');

    async function initialise() {{
      await fetchConfigs();
      await refreshHistory();
      await updateDebugLog();
      if (state.debugTimer) {{
        clearInterval(state.debugTimer);
      }}
      state.debugTimer = setInterval(updateDebugLog, 7000);
    }}

    async function fetchConfigs() {{
      try {{
        const response = await fetch('/runs/configs');
        if (!response.ok) throw new Error('دریافت فهرست سناریوها ناموفق بود.');
        const payload = await response.json();
        populateScenarioSelects(payload.scenarios || []);
      }} catch (error) {{
        statusMessage.textContent = error.message;
      }}
    }}

    function populateScenarioSelects(scenarios) {{
      const triangleSelect = document.getElementById('triangle-scenario');
      const scenarioSelect = document.getElementById('scenario-id');
      triangleSelect.innerHTML = '';
      scenarioSelect.innerHTML = '';
      const fragmentA = document.createDocumentFragment();
      const fragmentB = document.createDocumentFragment();
      scenarios.forEach((entry) => {{
        const option = document.createElement('option');
        option.value = entry.id;
        option.textContent = `${{entry.id}} — ${{entry.scenario_name || 'بدون عنوان'}}`;
        fragmentA.appendChild(option.cloneNode(true));
        fragmentB.appendChild(option);
      }});
      triangleSelect.appendChild(fragmentA);
      scenarioSelect.appendChild(fragmentB);
    }}

    async function refreshHistory() {{
      try {{
        const response = await fetch('/runs/history?limit=30');
        if (!response.ok) throw new Error('بازیابی تاریخچه ممکن نشد.');
        const payload = await response.json();
        state.runs = Array.isArray(payload.runs) ? payload.runs : [];
        renderHistory();
        if (!state.selectedRunId && state.runs.length) {{
          selectRun(state.runs[0].run_id);
        }} else if (state.selectedRunId) {{
          selectRun(state.selectedRunId);
        }}
      }} catch (error) {{
        statusMessage.textContent = error.message;
      }}
    }}

    function renderHistory() {{
      historyList.innerHTML = '';
      if (!state.runs.length) {{
        const empty = document.createElement('li');
        empty.textContent = 'تاکنون اجرایی ثبت نشده است.';
        historyList.appendChild(empty);
        return;
      }}
      state.runs.forEach((record) => {{
        const item = document.createElement('li');
        item.className = 'history-item' + (record.run_id === state.selectedRunId ? ' active' : '');
        const heading = document.createElement('div');
        heading.style.display = 'flex';
        heading.style.justifyContent = 'space-between';
        heading.style.alignItems = 'center';
        const idSpan = document.createElement('span');
        idSpan.textContent = record.run_id;
        const badge = document.createElement('span');
        badge.className = 'badge';
        badge.textContent = record.status;
        heading.appendChild(idSpan);
        heading.appendChild(badge);
        const meta = document.createElement('div');
        meta.style.fontSize = '0.8rem';
        meta.style.opacity = '0.85';
        meta.textContent = `${{record.route}} — ${{record.timestamp}}`;
        item.appendChild(heading);
        item.appendChild(meta);
        item.addEventListener('click', () => selectRun(record.run_id));
        historyList.appendChild(item);
      }});
    }}

    function selectRun(runId) {{
      state.selectedRunId = runId;
      renderHistory();
      const record = state.runs.find((entry) => entry.run_id === runId);
      if (!record) return;
      renderSummary(record);
      fetchMetrics(runId);
      fetchArtefacts(runId);
      renderGroundTrack(record.summary);
      renderThreeD(record.summary);
    }}

    function renderSummary(record) {{
      const container = document.getElementById('run-summary');
      container.innerHTML = '';
      if (!record.summary) {{
        container.textContent = 'گزارشى برای این اجرا ذخیره نشده است.';
        windowInfo.textContent = '';
        return;
      }}
      const metrics = record.summary.metrics || {{}};
      const formationWindow = metrics.formation_window || {{}};
      windowInfo.innerHTML = '';
      if (formationWindow.start && formationWindow.end) {{
        windowInfo.innerHTML = `<div class="summary-grid"><div class="summary-card"><strong>شروع پنجره:</strong><br/>${{formationWindow.start}}</div><div class="summary-card"><strong>پایان پنجره:</strong><br/>${{formationWindow.end}}</div><div class="summary-card"><strong>مدت‌زمان (ثانیه):</strong><br/>${{formationWindow.duration_s}}</div></div>`;
      }}

      const cards = document.createElement('div');
      cards.className = 'summary-grid';

      const triangle = metrics.triangle || {{}};
      const ground = metrics.ground_track || {{}};
      const orbital = metrics.orbital_elements || {{}};

      const triangleCard = document.createElement('div');
      triangleCard.className = 'summary-card';
      triangleCard.innerHTML = `<strong>هندسه مثلث</strong><br/>میانگین مساحت: ${{triangle.mean_area_m2?.toFixed?.(2) ?? '-'}} m²<br/>حداقل مساحت: ${{triangle.min_area_m2?.toFixed?.(2) ?? '-'}} m²<br/>حداکثر نسبت اضلاع: ${{triangle.aspect_ratio_max ?? '-'}}`;

      const groundCard = document.createElement('div');
      groundCard.className = 'summary-card';
      groundCard.innerHTML = `<strong>مسیر زمینی</strong><br/>حداکثر فاصله: ${{ground.max_ground_distance_km ?? '-'}} km<br/>حداقل فاصله: ${{ground.min_ground_distance_km ?? '-'}} km`;

      const orbitalCard = document.createElement('div');
      orbitalCard.className = 'summary-card';
      orbitalCard.innerHTML = `<strong>صفحه‌هاى مداری</strong><br/>فضاپیماها: ${{Object.keys(orbital).length}} مورد`;

      cards.appendChild(triangleCard);
      cards.appendChild(groundCard);
      cards.appendChild(orbitalCard);
      container.appendChild(cards);
    }}

    async function fetchMetrics(runId) {{
      metricsTables.innerHTML = 'در حال محاسبه متریک‌ها...';
      document.getElementById('window-plot').src = '';
      document.getElementById('triangle-plot').src = '';
      document.getElementById('window-csv').removeAttribute('href');
      document.getElementById('triangle-csv').removeAttribute('href');
      try {{
        const response = await fetch(`/runs/${{runId}}/metrics-report`);
        if (!response.ok) {{
          const text = await response.text();
          let message = 'محاسبه متریک‌ها با خطا مواجه شد.';
          try {{
            const info = JSON.parse(text);
            if (info && info.detail) {{
              message = info.detail;
            }} else if (typeof info === 'string' && info.trim()) {{
              message = info;
            }}
          }} catch (parseError) {{
            if (text && text.trim()) {{
              message = text;
            }}
          }}
          throw new Error(message);
        }}
        const payload = await response.json();
        renderMetricsTables(payload.tables || {{}});
        updatePlotLinks(payload.plots || {{}}, payload.csv_urls || {{}});
      }} catch (error) {{
        metricsTables.textContent = error.message;
      }}
    }}

    function renderMetricsTables(tables) {{
      metricsTables.innerHTML = '';
      Object.entries(tables).forEach(([name, rows]) => {{
        const section = document.createElement('section');
        section.innerHTML = `<h3>${{name}}</h3>`;
        const table = document.createElement('table');
        if (!rows.length) {{
          const empty = document.createElement('caption');
          empty.textContent = 'داده‌ای موجود نیست.';
          section.appendChild(empty);
        }} else {{
          const header = document.createElement('tr');
          Object.keys(rows[0]).forEach((key) => {{
            const th = document.createElement('th');
            th.textContent = key;
            header.appendChild(th);
          }});
          table.appendChild(header);
          rows.forEach((row) => {{
            const tr = document.createElement('tr');
            Object.values(row).forEach((value) => {{
              const td = document.createElement('td');
              td.textContent = value;
              tr.appendChild(td);
            }});
            table.appendChild(tr);
          }});
        }}
        section.appendChild(table);
        metricsTables.appendChild(section);
      }});
    }}

    function updatePlotLinks(plots, csvs) {{
      const windowPlot = document.getElementById('window-plot');
      const trianglePlot = document.getElementById('triangle-plot');
      if (plots.window_durations) {{
        windowPlot.src = plots.window_durations;
      }}
      if (plots.triangle_area) {{
        trianglePlot.src = plots.triangle_area;
      }}
      const windowCsv = document.getElementById('window-csv');
      const triangleCsv = document.getElementById('triangle-csv');
      if (csvs.window_events) windowCsv.href = csvs.window_events;
      if (csvs.triangle_samples) triangleCsv.href = csvs.triangle_samples;
    }}

    async function fetchArtefacts(runId) {{
      artefactContainer.innerHTML = '';
      try {{
        const response = await fetch(`/runs/${{runId}}/artefacts`);
        if (!response.ok) throw new Error('نمایش آرتیفکت‌ها ممکن نیست.');
        const payload = await response.json();
        renderArtefacts(payload.artefacts || {{}});
      }} catch (error) {{
        artefactContainer.textContent = error.message;
      }}
    }}

    function renderArtefacts(artefacts) {{
      artefactContainer.innerHTML = '';
      const entries = Object.entries(artefacts);
      if (!entries.length) {{
        artefactContainer.textContent = 'هیچ آرتیفکت در دسترس نیست.';
        return;
      }}
      entries.forEach(([name, descriptor]) => {{
        const card = document.createElement('div');
        card.className = 'artefact-entry';
        const title = document.createElement('strong');
        title.textContent = name;
        card.appendChild(title);
        const path = document.createElement('div');
        path.style.fontSize = '0.8rem';
        path.style.marginTop = '0.35rem';
        path.textContent = descriptor.path;
        card.appendChild(path);
        if (descriptor.url) {{
          const link = document.createElement('a');
          link.href = descriptor.url;
          link.target = '_blank';
          link.textContent = 'مشاهده/دانلود';
          link.style.display = 'inline-block';
          link.style.marginTop = '0.35rem';
          card.appendChild(link);
        }}
        if (Array.isArray(descriptor.files) && descriptor.files.length) {{
          const list = document.createElement('ul');
          list.style.fontSize = '0.8rem';
          list.style.marginTop = '0.5rem';
          descriptor.files.forEach((file) => {{
            const item = document.createElement('li');
            if (file.url) {{
              const link = document.createElement('a');
              link.href = file.url;
              link.target = '_blank';
              link.textContent = file.name;
              item.appendChild(link);
            }} else {{
              item.textContent = file.name;
            }}
            list.appendChild(item);
          }});
          card.appendChild(list);
        }}
        artefactContainer.appendChild(card);
      }});
    }}

    function renderGroundTrack(summary) {{
      const canvas = document.getElementById('ground-track');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!summary || !summary.geometry) return;
      const geometry = summary.geometry;
      const latitudes = geometry.latitudes_rad || {{}};
      const longitudes = geometry.longitudes_rad || {{}};
      const satelliteIds = geometry.satellite_ids || Object.keys(latitudes);
      if (!satelliteIds.length) return;
      const w = canvas.width;
      const h = canvas.height;

      ctx.fillStyle = 'rgba(10, 30, 55, 0.6)';
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = 'rgba(125, 190, 255, 0.2)';
      ctx.lineWidth = 1;
      for (let i = -60; i <= 60; i += 30) {{
        const y = h - ((i + 90) / 180) * h;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }}
      ctx.strokeStyle = 'rgba(125, 190, 255, 0.4)';
      for (let lon = -180; lon <= 180; lon += 60) {{
        const x = ((lon + 180) / 360) * w;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }}

      satelliteIds.forEach((id, index) => {{
        const latSeries = latitudes[id];
        const lonSeries = longitudes[id];
        if (!latSeries || !lonSeries) return;
        const hue = (index / satelliteIds.length) * 360;
        ctx.strokeStyle = `hsl(${{hue}}, 75%, 65%)`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        latSeries.forEach((lat, idx) => {{
          const lon = lonSeries[idx];
          const x = ((lon + Math.PI) / (2 * Math.PI)) * w;
          const y = h - ((lat + Math.PI / 2) / Math.PI) * h;
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }});
        ctx.stroke();
      }});
    }}

    function renderThreeD(summary) {{
      const container = document.getElementById('three-d-view');
      if (!summary || !summary.geometry) {{
        container.innerHTML = '';
        return;
      }}
      const geometry = summary.geometry;
      const satelliteIds = geometry.satellite_ids || [];
      const positions = geometry.positions_m || {{}};
      if (!satelliteIds.length) return;

      const traces = satelliteIds.map((id, index) => {{
        const samples = positions[id] || [];
        const xs = samples.map((row) => row[0]);
        const ys = samples.map((row) => row[1]);
        const zs = samples.map((row) => row[2]);
        return {{
          type: 'scatter3d',
          mode: 'lines',
          name: id,
          x: xs,
          y: ys,
          z: zs,
          line: {{ width: 4, color: `hsl(${{(index / satelliteIds.length) * 360}}, 70%, 60%)` }},
        }};
      }});

      const sphereResolution = 32;
      const theta = [];
      const phi = [];
      for (let i = 0; i <= sphereResolution; i += 1) {{
        theta.push((i / sphereResolution) * Math.PI);
        phi.push((i / sphereResolution) * 2 * Math.PI);
      }}
      const sphereX = theta.map((t) => phi.map((p) => EARTH_RADIUS_M * Math.sin(t) * Math.cos(p)));
      const sphereY = theta.map((t) => phi.map((p) => EARTH_RADIUS_M * Math.sin(t) * Math.sin(p)));
      const sphereZ = theta.map((t) => phi.map((p) => EARTH_RADIUS_M * Math.cos(t)));
      traces.push({{
        type: 'surface',
        x: sphereX,
        y: sphereY,
        z: sphereZ,
        showscale: false,
        opacity: 0.35,
        colorscale: [[0, '#0c3b70'], [1, '#0c3b70']],
        hoverinfo: 'skip',
      }});

      const layout = {{
        margin: {{ l: 0, r: 0, b: 0, t: 0 }},
        scene: {{
          xaxis: {{ title: 'X (m)', backgroundcolor: '#0d1f38', gridcolor: '#1a3352', zerolinecolor: '#2a4671' }},
          yaxis: {{ title: 'Y (m)', backgroundcolor: '#0d1f38', gridcolor: '#1a3352', zerolinecolor: '#2a4671' }},
          zaxis: {{ title: 'Z (m)', backgroundcolor: '#0d1f38', gridcolor: '#1a3352', zerolinecolor: '#2a4671' }},
          aspectmode: 'data',
        }},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: true,
        legend: {{ orientation: 'h', x: 0, y: 1.1 }},
      }};
      Plotly.react('three-d-view', traces, layout, {{ responsive: true }});
    }}

    async function updateDebugLog() {{
      try {{
        const response = await fetch(`/debug/log/tail?offset=${{state.debugOffset}}`);
        if (!response.ok) throw new Error();
        const payload = await response.json();
        if (!payload.available) return;
        state.debugOffset = payload.offset || 0;
        if (payload.content) {{
          const view = document.getElementById('debug-log');
          view.textContent = (view.textContent === '(در انتظار به‌روزرسانی)' ? '' : view.textContent) + payload.content;
          view.scrollTop = view.scrollHeight;
        }}
      }} catch (error) {{
        // Silent failure keeps the UI responsive.
      }}
    }}

    function parseJsonField(text) {{
      if (!text || !text.trim()) return null;
      try {{
        return JSON.parse(text);
      }} catch (error) {{
        throw new Error('قالب JSON نامعتبر است.');
      }}
    }}

    function parseListField(text) {{
      if (!text || !text.trim()) return [];
      return text.split(',').map((item) => item.trim()).filter(Boolean);
    }}

    document.getElementById('triangle-form').addEventListener('submit', async (event) => {{
      event.preventDefault();
      const payload = {{
        scenario_id: document.getElementById('triangle-scenario').value || null,
        configuration: null,
        assumptions: parseListField(document.getElementById('triangle-assumptions').value),
        seed: document.getElementById('triangle-seed').value ? Number(document.getElementById('triangle-seed').value) : null,
      }};
      try {{
        payload.configuration = parseJsonField(document.getElementById('triangle-config').value);
      }} catch (error) {{
        statusMessage.textContent = error.message;
        return;
      }}
      statusMessage.textContent = 'در حال اجرا...';
      try {{
        const response = await fetch('/runs/triangle', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        if (!response.ok) throw new Error('اجرای شبیه‌سازی مثلث ناموفق بود.');
        await refreshHistory();
        statusMessage.textContent = 'اجرا با موفقیت کامل شد.';
      }} catch (error) {{
        statusMessage.textContent = error.message;
      }}
    }});

    document.getElementById('scenario-form').addEventListener('submit', async (event) => {{
      event.preventDefault();
      const payload = {{
        scenario_id: document.getElementById('scenario-id').value || null,
        configuration: null,
        metrics_specification: parseListField(document.getElementById('scenario-metrics').value),
        assumptions: parseListField(document.getElementById('scenario-assumptions').value),
        seed: document.getElementById('scenario-seed').value ? Number(document.getElementById('scenario-seed').value) : null,
      }};
      if (!payload.metrics_specification.length) delete payload.metrics_specification;
      try {{
        payload.configuration = parseJsonField(document.getElementById('scenario-config').value);
      }} catch (error) {{
        statusMessage.textContent = error.message;
        return;
      }}
      statusMessage.textContent = 'در حال اجرا...';
      try {{
        const response = await fetch('/runs/scenario', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        if (!response.ok) throw new Error('اجرای سناریو با خطا مواجه شد.');
        await refreshHistory();
        statusMessage.textContent = 'سناریو تکمیل شد.';
      }} catch (error) {{
        statusMessage.textContent = error.message;
      }}
    }});

    document.getElementById('refresh-history').addEventListener('click', refreshHistory);
    document.getElementById('debug-refresh').addEventListener('click', updateDebugLog);

    initialise();
  </script>
</body>
</html>"""


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
