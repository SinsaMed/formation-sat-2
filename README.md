# Conceptual Design of a Three-Satellite LEO Constellation

[![Continuous integration status](https://github.com/<owner>/formation-sat-2/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/formation-sat-2/actions/workflows/ci.yml)

This repository scaffolds the analytical workflow for designing a three-satellite low Earth orbit (LEO) constellation that forms a repeatable, transient triangular formation above a designated city-scale target. The initial research brief focuses on Tehran, but the methodology generalises to any urban objective located along the constellation's ground track.

## Project Intent
- Formulate a mission architecture comprising two satellites in one orbital plane (Plane A) and a third satellite in a second plane (Plane B).
- Engineer the orbital elements so that both planes intersect above the target city, enabling a geometrically symmetric triangular formation immediately before and after the ascending or descending node crossing.
- Guarantee a daily (or otherwise cyclic) access window of approximately 90 seconds during which the triangular formation satisfies predefined geometric tolerances.
- Quantify maintenance strategies that mitigate dominant low-Earth perturbations (\(J_2\), drag, and solar radiation pressure) to preserve the repeatability of the formation.

Further elaboration on the mission statement, objectives, and derived requirements is available in [`docs/project_overview.md`](docs/project_overview.md).
The numerical verification of the triangular formation above Tehran is documented in [`docs/triangle_formation_results.md`](docs/triangle_formation_results.md).

## Repository Layout
- `AGENTS.md` – house style and collaboration guidelines for this codebase.
- `README.md` – the document you are currently reading.
- `docs/` – detailed academic documentation, including the staged research roadmap and requirement sets.
- `tests/` – placeholder directory for forthcoming analytical or software verification assets.

## Getting Started
1. Review the staged research workflow described in [`docs/project_roadmap.md`](docs/project_roadmap.md).
2. Establish modelling assumptions and parameter baselines using the requirement tables in [`docs/mission_requirements.md`](docs/mission_requirements.md).
3. Initialise the Python tooling with `make setup`, which provisions `.venv/` using the curated `requirements.txt` list so subsequent tasks share a reproducible environment.
4. Implement analytical prototypes or simulations in your preferred environment, committing incremental progress as you validate each stage.
5. Populate the `tests/` directory with automated checks (e.g., scenario verifiers, Monte Carlo campaigns) once modelling scripts are introduced.

## Automation and Continuous Integration
The root `Makefile` offers a concise command vocabulary for recurring workflows. Invoke the targets from the repository root after completing `make setup`:

- `make lint` conducts a lightweight static analysis by byte-compiling `src/`, `sim/`, and `tools/`, surfacing syntax issues without enforcing stylistic policy.
- `make test` executes the PyTest suite with strict failure halting so regression suites can evolve alongside the mission design.
- `make simulate` generates illustrative formation plots under `artefacts/plots/` and confirms that the scenario execution entry point remains importable while the numerical core is under development.
- `make scenario` executes the sequential scenario pipeline, storing a JSON summary beneath `artefacts/scenario/` for downstream validation against Systems Tool Kit (STK) 11.2 workflows.
- `make triangle` runs the triangular formation simulation above Tehran, produces the mission summary JSON, and exports STK-compatible ephemerides beneath `artefacts/triangle/`.
- `make baselines` exercises the baseline-generation and metric-extraction scaffolding, ensuring interface compatibility is monitored even before the algorithms are implemented.
- `make docs` refreshes a timestamped documentation digest in `artefacts/docs/`, demonstrating the path that future Sphinx builds will adopt.
- `make clean` removes transient artefacts and the virtual environment when a reset is required.

The accompanying GitHub Actions workflow (`.github/workflows/ci.yml`) executes these targets on every push and pull request to `main`. Dependency installation is cached using `actions/setup-python` with the repository's `requirements.txt`, and the generated plots and documentation digests are uploaded as build artefacts for archival review. Replace `<owner>` in the status badge URL with the hosting organisation or user namespace once the remote is configured so the badge reflects live integration outcomes.

## Scenario Pipeline Usage
1. Invoke `make scenario` after `make setup` to ensure the virtual environment is initialised. The target writes `artefacts/scenario/scenario_summary.json`, documenting the nodes, mission phases, propagation summaries, and metrics calculated during the run.
2. Alternatively, call the runner directly with `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/scenario` to specify a named scenario housed under `config/scenarios/`.
3. Supply bespoke configurations via `python -m sim.scripts.run_scenario /path/to/configuration.yaml --output-dir outputs/custom` when iterating on local mission concepts. The tool logs the stage sequence (nodes, phases, two-body propagation, J2 plus drag, and metric extraction) to `stdout` so analysts can confirm that every component executed in order.

## Contributing
All contributions must preserve the academic tone and reference discipline specified in `AGENTS.md`. Each pull request should:
- Summarise the mission design progress achieved,
- Document new analyses or datasets within `docs/`, and
- Reference any added or updated tests.

## License
To be determined. Add licensing information before distributing the repository beyond the core research team.
