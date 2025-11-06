# Simulation Execution Modes

## Introduction
This memorandum documents every supported mechanism for executing the Tehran formation simulations. It contrasts the web application, the development-focused debug harness, and the batch scenario pipeline so that analysts can select the correct toolchain for their objectives. Coverage includes command syntax, run-time configuration, artefact placement, and the automatic plot generation guarantees newly aligned across the project.[Ref1][Ref2][Ref3]

## Artefact Taxonomy
Simulation outputs are grouped by execution origin to preserve reproducibility and traceability:

-   `artefacts/web_runs/`: time-stamped directories produced by the FastAPI service exposed in `run.py`. Each directory is named according to the ISO-8601 `run_YYYYMMDD_HHMMZ` convention and mirrors the structure consumed by the web dashboard.[Ref1]
-   `artefacts/debug/`: archives emitted by `run_debug.py`. These are time-stamped using the UTC format `YYYYMMDDTHHMMSSZ` to facilitate chronological sorting during iterative development.[Ref2]
-   Additional analytical runs follow the same conventions and live alongside the manual studies recorded in `docs/_authoritative_runs.md`, for example `artefacts/run_20251101_0803Z/`.

Generated figures are written as Scalable Vector Graphics (SVG) files so that they remain reviewable in version control. Interactive HTML exports—for example the 3D triangle viewer—are linked from the same directory tree. Debug summaries and web responses always capture the absolute file system paths for traceability.[Ref2][Ref3]

## Web Application Runs

### Launch Procedure
1.  Install the dependencies declared in `requirements.txt` and start the FastAPI application by running `python run.py --host 0.0.0.0 --port 8000`. The optional `--reload` flag enables live code reloading for local iteration.[Ref1]
2.  Navigate to `http://localhost:8000` to load the Persian-language web client documented in `docs/web_interface.md`.

### Executing a Triangle Run
1.  Select the desired mission duration from the sidebar. The options correspond to the ground-track repeat cycle, the daily-pass planning horizon, and the manoeuvre cadence stored in the repository configuration files.[Ref1]
2.  Submit the run. The backend clones `config/scenarios/tehran_triangle.json`, applies the requested overrides, and invokes `sim.formation.triangle.simulate_triangle_formation`. Plot-ready CSVs and metrics are generated automatically and recorded in `artefacts/web_runs/run_YYYYMMDD_HHMMZ/`.[Ref1]
3.  The server emits standard diagnostic plots by calling `sim.scripts.extract_metrics.extract_metrics`, ensuring that the mission dashboard can download PNG previews alongside the canonical CSV artefacts.[Ref1]

### Executing a Scenario Pipeline Run
1.  Switch to the scenario execution form and choose a stored scenario identifier (for example `tehran_daily_pass`) or supply an inline configuration payload. The `--metrics` selector in the user interface propagates to the backend request payload.[Ref1]
2.  The server calls `sim.scripts.run_scenario.run_scenario`, which resolves the scenario configuration, propagates the constellation with two-body and \(J_2\)+drag dynamics, exports STK-compatible products, and now triggers `tools.render_scenario_plots.generate_visualisations` whenever an output directory is specified. SVG figures covering deterministic cross-track offsets, orbital-element trends, Monte Carlo dispersion statistics, and relative-plane separations are added to the run's artefact directory under `plots/`.[Ref1][Ref3]
3.  The FastAPI response records the artefact locations and appends the run metadata to `artefacts/web_runs/run_log.jsonl` for auditability.[Ref1]

## Command-Line Debug Runs (`run_debug.py`)

### Triangle Mode
1.  Execute `python run_debug.py --triangle` to run the Tehran triangle formation using the stored configuration. Use `--triangle-config PATH` to substitute a different JSON scenario file and `--output-root PATH` to change the artefact root (default `artefacts/debug`).[Ref2]
2.  The script exports time histories for positions, velocities, geodetic coordinates, triangle geometry, and orbital elements. It subsequently calls both `tools.render_debug_plots.generate_visualisations` and `tools.generate_triangle_report.main` to produce the SVG and HTML products illustrated in `artefacts/debug/20251105T193220Z/`.[Ref2]

### Scenario Mode
1.  Execute `python run_debug.py --scenario` to run the daily-pass pipeline, or append a scenario identifier such as `python run_debug.py --scenario tehran_daily_pass`. This flag is mandatory, matching the usage guidance displayed when the flag is omitted.[Ref2]
2.  The script invokes `sim.scripts.run_scenario.run_scenario` with the provided identifier and stores the JSON summary at `artefacts/debug/YYYYMMDDTHHMMSSZ/scenario_debug_summary.json`.[Ref2]
3.  The new `tools.render_scenario_plots.generate_visualisations` hook ensures that the same SVG suite created for web-triggered scenario runs is generated inside the debug artefact directory. The console summary now enumerates each plot for rapid inspection.[Ref2][Ref3]

### Artefact Checklist
Regardless of the chosen mode, `run_debug.py` writes its log to `debug.txt`. Triangle runs additionally mirror the metrics reported by the web application, while scenario runs now expose deterministic and Monte Carlo cross-track charts. Both modes therefore satisfy the repository requirement that each run archive include complete metric tables, CSVs, and SVG visualisations.[Ref2][Ref3]

## Batch Scenario Pipeline (`sim.scripts.run_scenario`)
1.  Execute `python -m sim.scripts.run_scenario --output-dir artefacts/manual_run` to process the canonical daily-pass configuration. Use `--config PATH` to reference a custom JSON scenario or `--metrics metric_id ...` to focus the metric extractor.[Ref3]
2.  When `--output-dir` is supplied the runner exports STK-ready CSV and JSON artefacts and now delegates to `tools.render_scenario_plots.generate_visualisations` to populate the `plots/` directory automatically. The aggregated summary is persisted to `scenario_summary.json` and mirrors the structure returned through the web API and debug CLIs.[Ref3]
3.  When no output directory is specified, the summary dictionary still includes the artefact map so that downstream workflows can trigger plotting on demand if desired.[Ref3]

## Plot Coverage Guarantees
All three entry points—web application, `run_debug.py`, and the module CLI—now converge on the same post-processing chain. Scenario runs produce deterministic, relative, and Monte Carlo cross-track plots alongside orbital-element trend summaries, while triangle runs continue to publish both the debug and analytical report figures. This alignment simplifies regression testing and ensures that every artefact directory contains the CSV, JSON, SVG, and HTML products required for Systems Tool Kit (STK 11.2) validation.[Ref1][Ref2][Ref3]

## References
[Ref1] `run.py` – FastAPI service exposing triangle and scenario orchestration endpoints plus the automatic metric plotter for web-driven runs.
[Ref2] `run_debug.py` – Debug CLI generating CSV artefacts and invoking the full plotting stack for triangle and scenario runs.
[Ref3] `sim/scripts/run_scenario.py`, `tools/render_scenario_plots.py` – Scenario pipeline orchestrator and SVG plot generator for deterministic and Monte Carlo outputs.
