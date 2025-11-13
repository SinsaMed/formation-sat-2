# Project Overview

This repository contains a Python-based simulation and analysis tool for designing a three-satellite low Earth orbit (LEO) constellation. The primary goal is to model a repeatable, transient triangular formation above a designated city-scale target, with an initial focus on Tehran.

The project is structured as a scientific computing workflow, with a clear separation of concerns:
- **`sim/`**: Core simulation logic, including orbital mechanics and formation dynamics.
- **`tools/`**: Scripts for running simulations, generating reports, and exporting data.
- **`config/`**: Configuration files for different simulation scenarios.
- **`artefacts/`**: Output directory for simulation results, plots, and reports.
- **`docs/`**: Detailed project documentation, including `formation_analysis_report.md`, `satellite_formation_control_methods.md`, `active_station_keeping_plan.md`.
- **`tests/`**: Automated tests for the simulation code.

The project also includes a FastAPI web server (`run.py`) that provides a web interface for running simulations and viewing results.

# Building and Running

## Setup

To set up the development environment, run the following command:

```bash
make setup
```

This will create a Python virtual environment in `.venv/` and install the required dependencies from `requirements.txt`.

## Running Simulations

The project provides several `make` targets for running different simulation scenarios:

- **`make simulate`**: Runs a stub simulation to generate placeholder plots and verify interfaces.
- **`make scenario`**: Runs the "Tehran Daily Pass" scenario, which is based on a repeating ground track (RGT) orbit.
- **`make triangle`**: Runs the "Tehran Triangle" formation scenario, which is based on a repeating ground track (RGT) orbit and configured by `config/scenarios/tehran_triangle.json`.

You can also run the simulations directly using the Python scripts in `sim/scripts/` and `tools/`. For example, to run the "Tehran Daily Pass" scenario:

```bash
python -m sim.scripts.run_scenario tehran_triangle --output-dir artefacts/scenario
```

## Running the Web Server

To run the FastAPI web server, use the following command:

```bash
python run.py
```

This will start the server on `http://127.0.0.1:8000`. The web interface allows you to run simulations, view results, and explore the configuration options.

## Testing

To run the test suite, use the following command:

```bash
make test
```

This will execute the PyTest tests in the `tests/` directory.

# Development Conventions

- **Code Style**: The project uses `black` for code formatting and `flake8` for linting.
- **Testing**: The project uses `pytest` for testing. All new code should be accompanied by tests.
- **Documentation**: The project uses Sphinx for documentation. The documentation is located in the `docs/` directory.
- **Continuous Integration**: The project uses GitHub Actions for continuous integration. The CI pipeline is defined in `.github/workflows/ci.yml`.
