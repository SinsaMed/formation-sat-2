# Formation SAT Interactive Execution Guide

## 1. Introduction
This guide explains how to operate the Formation SAT interactive execution capabilities delivered through the FastAPI web service and the command-line debugging companion. The objective is to ensure mission analysts can reproduce Tehran-focused formation runs, inspect artefacts, and maintain compatibility with Systems Tool Kit (STK) ingest workflows without consulting the source code. The material consolidates the main behaviours exposed in the web runner and the debug instrumentation so that operations remain auditable and deterministic across environments.[Ref1][Ref2]

## 2. Prerequisites
- Python 3.10 or later with the project dependencies installed via `pip install -r requirements.txt`.
- A workstation capable of hosting Uvicorn locally on TCP port 6000.
- Access to the repository artefact directories so run histories and debug exports can be persisted between sessions.

## 3. Launching the Web Run Service
1. Activate the virtual environment that contains the project dependencies.
2. Navigate to the repository root and execute `uvicorn run:app --host 127.0.0.1 --port 6000` to start the FastAPI service.[Ref1]
3. Confirm that the terminal reports the service as listening, then open `http://127.0.0.1:6000/` in a web browser to load the single-page interface.
4. Leave the terminal session active while interacting with the interface so that artefacts continue to stream into `artefacts/web_runs` and the run log remains current.[Ref1]

## 4. Web Interface Overview
### 4.1 Scenario Catalogue
The left-hand column enumerates every JSON scenario stored in `config/scenarios`. Selecting a scenario reveals its metadata, including mission description, stored keys, and any inline documentation. The default entries include the Tehran triangle and Tehran daily pass scenarios to support the ground-track analysis requested by the mission stakeholders.[Ref1]

### 4.2 Run Orchestration
The central pane coordinates new executions. Initiating a triangle run produces a timestamped directory `artefacts/web_runs/run_YYYYMMDD_hhmmZ` that captures metrics, tabular outputs, and a consolidated JSON log. Each run records the assumptions list and random seed so downstream analyses remain reproducible. Scenario pipeline runs accept optional metric subsets to prioritise specific figures of merit during summarisation.[Ref1]

### 4.3 Visualisation and Telemetry
The right-hand column renders two complementary visual layers. A two-dimensional canvas presents the Tehran ground track with the red trace highlighting the terrestrial footprint of the overpass. A Plotly-powered three-dimensional panel simultaneously displays the Earth as a translucent sphere with the trio of formation satellites traced in distinct colours. Selecting a run refreshes both panels and updates the metrics table to report formation window timing, triangle aspect ratio, and contact opportunities without reloading the page.[Ref1]

### 4.4 Debug Log Streaming
The interface polls the `/debug/log/tail` endpoint to surface the `debug.txt` file as it is written. Analysts can therefore monitor the stage-by-stage progress of long-running simulations, or download the full log via `/debug/log/download` when a permanent record is required. These endpoints complement the command-line tooling described later in this document.[Ref1]

## 5. Managing Run Artefacts
1. After each execution, review the `run_log.jsonl` file stored in `artefacts/web_runs` to confirm metadata capture succeeded.[Ref1]
2. Archive SVG figures, CSV tables, and JSON summaries from the relevant `run_YYYYMMDD_hhmmZ` directory into mission data stores while retaining the original timestamped structure.
3. When a run must be repeated, copy the recorded assumptions, seed, and configuration notes to the new request to preserve traceability between iterations.

## 6. Debug Workflow
1. Execute `python run_debug.py --triangle` to replay the Tehran triangle scenario with verbose logging. The command regenerates `debug.txt` and emits CSV files for positions, velocities, latitudes, and longitudes under `artefacts/debug/<timestamp>`. Each CSV encodes satellites as column groups and timestamps in ISO 8601 form to simplify ingestion into analysis notebooks.[Ref2]
2. Execute `python run_debug.py --scenario tehran_daily_pass` when investigating the general mission pipeline. The tool writes a structured JSON summary, logs the ordered stage sequence at DEBUG level, and reports mission node, phase, and contact metrics to the console for quick inspection.[Ref2]
3. Inspect `debug.txt` to trace stepwise progress. Because the file is rewritten on each invocation, archive copies after significant investigations to maintain a permanent audit trail.

## 7. STK Validation Procedure
1. Once artefacts are generated, invoke `python tools/stk_export.py --help` to review exporter options and verify the expected TEME frame inputs. The exporter ensures STK 11.2 compatibility by enforcing monotonically increasing epochs and consistent inertial coordinates.[Ref3]
2. Prepare `StateSample` series for each spacecraft using the CSV outputs from the debug workflow or the JSON artefacts from the web interface. Convert units to kilometres and kilometres per second before export if necessary.[Ref2][Ref3]
3. Run the exporter with the prepared state histories to produce STK text ephemerides. Record any deviations or limitations in the mission log so downstream consumers understand the conversion assumptions.[Ref3]

## References
[Ref1] `run.py`, Formation SAT Web Run Service implementation, 2023.
[Ref2] `run_debug.py`, Formation SAT Debugging CLI, 2023.
[Ref3] `tools/stk_export.py`, Formation SAT STK Export Utilities, 2023.
