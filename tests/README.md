# Test Suite Guide

## Overview

The automated tests exercise the analytical utilities in `src/constellation` and
confirm that the current simulation script scaffolding continues to signal its
placeholder status. The suite runs under `pytest` and is designed for rapid
feedback during development and regression analysis.

## Running the Tests

1. Create and activate a virtual environment using Python 3.10 or later.
2. Install the development dependencies: `pip install -r requirements.txt`.
3. Execute the full test campaign from the repository root with `pytest`.

For targeted debugging you may append selectors such as `-k roe` to focus on a
single module, or `tests/integration` to run the simulation interface checks in
isolation.

## Analysing Results

Pytest reports `PASSED` for successful checks, `FAILED` when an assertion does
not hold, and `ERROR` if the test code itself raises an unexpected exception. A
summary section at the end of the run enumerates outcomes by category. When
failures occur, review the stack trace and compare the observed values with the
mission design expectations described in `docs/mission_requirements.md`.

## Available Fixtures

Common fixtures live in `tests/conftest.py` and provide reusable scenario
configurations together with reference output placeholders. Use
`scenario_configuration` when invoking constellation or simulation routines that
require mission inputs, and `reference_outputs` when crafting regression guards
for exported artefacts.
