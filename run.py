"""Web entry points for running formation simulations and scenario pipelines."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field, root_validator

from sim.formation import simulate_triangle_formation
from sim.formation.triangle import TriangleFormationResult
from sim.scripts.configuration import resolve_scenario_path
from sim.scripts.run_scenario import run_scenario

PROJECT_ROOT = Path(__file__).resolve().parent
SCENARIO_DIR = PROJECT_ROOT / "config" / "scenarios"
WEB_ARTEFACT_DIR = PROJECT_ROOT / "artefacts" / "web_runs"
RUN_LOG_PATH = WEB_ARTEFACT_DIR / "run_log.jsonl"
DEFAULT_TRIANGLE_SCENARIO = "tehran_triangle"
DEFAULT_PIPELINE_SCENARIO = "tehran_daily_pass"

app = FastAPI(title="Formation SAT Run Service")
router = APIRouter(prefix="/runs")


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
    )

    response = {
        "run_id": run_id,
        "timestamp": timestamp,
        "summary": result,
        "artefacts": artefacts,
    }
    return response


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


app.include_router(router)
