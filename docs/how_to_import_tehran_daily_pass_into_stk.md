# STK 11.2 Validation Guide for the Tehran Daily Pass Scenario

## Purpose
This guide explains how to ingest the exported Tehran daily pass artefacts into Systems Tool Kit (STK) 11.2, verify that the propagated formation geometry conforms to the scenario assumptions, and capture a complete validation record suitable for compliance reporting. The workflow links the lightweight propagation pipeline to analyst-facing tooling so that the configuration documented in the scenario overview remains traceable to STK evidence packages.【Ref1】【Ref2】

## Prerequisites
1. Install STK 11.2 with a valid licence and ensure the Connect module is available.
2. Export the scenario by running `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir <RUN_DIR>` so that `scenario_summary.json` and the `stk_export/` sub-directory are populated with ephemeris, ground-track, and interval files.【Ref1】
3. Confirm that Python can access the STK COM interface (`comtypes`), enabling automation through the provided helper script.【Ref3】

## Import Procedure
1. Launch the helper script: `python tools/stk_tehran_daily_pass_runner.py <RUN_DIR>`. The command loads the generated `.sc`, `.sat`, `.fac`, `.gt`, and `.int` files, applies the planning-horizon bounds, and activates ground-track visualisation for the exported satellite.【Ref3】
2. Open the 3D Graphics window in STK and verify that the satellite timeline matches the start and stop epochs in `scenario_summary.json`. The camera automatically frames the Tehran facility, but analysts may adjust the view to inspect formation geometry and revisit the animation timeline.
3. In the 2D Graphics window, confirm that the imported ground-track overlays the Tehran metropolitan area and that the Svalbard downlink contact appears at the scheduled epoch.

## Geometry and Operations Verification
1. Run the animation from the planning-horizon start to end while monitoring the satellite’s altitude, inclination, and ground-track coverage. Compare the observed orbital period and repeat-ground-track cadence against the metrics recorded in the scenario summary (`orbital_period_nominal_s`, `orbital_period_perturbed_s`).【Ref1】
2. Inspect the imported interval lists (`Contacts_*.int`) to ensure imaging and downlink windows align with the metadata expectations (09:24 UTC imaging and 20:55 UTC downlink). Confirm that minimum elevation constraints are satisfied by querying access reports in STK.
3. Validate that facility geometry (Tehran area of interest, Svalbard ground station) matches the documented latitudes and longitudes. Any discrepancies should trigger a rerun of the export pipeline after correcting the configuration.

## Evidence Capture and Reporting
1. Capture annotated screenshots of the 3D orbit depiction, 2D ground-track coverage, and access report plots demonstrating compliance with imaging and downlink assumptions. Store the images within the run directory using descriptive filenames (e.g., `run_YYYYMMDD_hhmmZ_tehran_groundtrack.svg`).
2. Record quantitative metrics (orbital period, access start/stop times, peak elevation) directly from STK and compare them with the JSON summary. Document deviations greater than 1% in `docs/tehran_daily_pass_scenario.md` and raise a configuration review if necessary.【Ref2】
3. Once the evidence aligns with expectations, confirm that `validated_against_stk_export` is set to `true` in `config/scenarios/tehran_daily_pass.json`, update `docs/tehran_daily_pass_scenario.md` with a concise validation statement, and log the run identifier in the compliance matrix (`docs/compliance_matrix.md`) together with the captured artefacts.【Ref2】

## References
- [Ref1] `sim/scripts/run_scenario.py` – Scenario propagation and export workflow linking mission configuration to STK-ready artefacts.
- [Ref2] `docs/tehran_daily_pass_scenario.md` – Authoritative scenario description and validation status log.
- [Ref3] `tools/stk_tehran_daily_pass_runner.py` – Automation script for importing and animating the exported scenario within STK 11.2.
