# Tehran Daily Pass Scenario Overview

## Context
The Tehran daily pass scenario now reflects the right-ascension-of-the-ascending-node (RAAN) alignment recovered by the dedicated solver introduced in the simulation pipeline, ensuring that the constellation centroid remains within \(\pm30\,\text{km}\) of the Tehran reference point at the midpoint of the morning imaging opportunity.[Ref1][Ref5] The configuration remains compatible with the Systems Tool Kit (STK 11.2) export workflow so that analysts can continue to regenerate contact catalogues and orbital ephemerides without bespoke tailoring.[Ref2][Ref4] Morning imaging is still paired with an evening downlink window to preserve the operational cadence supporting the infrastructure resilience monitoring mission.

## Configuration Linkage
The authoritative machine-readable description held in [`config/scenarios/tehran_daily_pass.json`](../config/scenarios/tehran_daily_pass.json) records the RAAN solution of \(350.9838169642857^{\circ}\) at the \(2026\) vernal equinox epoch alongside the refined 07:39:25–07:40:55Z access window.[Ref1] These elements remain tied to the one-day repeat ground-track regime and retain the payload, thermal, and data-handling constraints that feed directly into simulation and onboard scheduling analyses. The metadata block logs the alignment validation run identifier (`run_20260321_0740Z_tehran_daily_pass_resampled`) and associated epoch, preserving traceability to the evidence set used to demonstrate compliance.

## Alignment Solution and Simulation Evidence
The enhanced perturbation workflow executed on 21 March 2026 generated artefacts under `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/`, capturing the deterministic alignment solution and the supporting Monte Carlo catalogue.[Ref2][Ref3]

1. Initialise the optimisation sweep using `sim/scripts/run_scenario.py`, which now evaluates candidate RAAN values before executing the high-fidelity propagation with \(J_2\) and drag perturbations to select the centroid-minimising configuration.[Ref5]
2. Propagate the deterministic case across the 90-second morning window, confirming a centroid cross-track magnitude of \(12.14\,\text{km}\) and a worst-vehicle absolute offset of \(27.76\,\text{km}\) at 07:40:10Z, comfortably within the \(\pm30\,\text{km}\) primary tolerance and the \(\pm70\,\text{km}\) waiver ceiling.[Ref3]
3. Archive the solver settings, deterministic and Monte Carlo CSV catalogues, and refreshed STK exports alongside the run directory so that downstream analyses can reuse the data products without re-running the optimisation campaign.[Ref2]

## STK Validation Status
The regenerated STK package embedded within `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/` was exported directly by the scenario runner, yielding ephemeris (`.e`), satellite (`.sat`), ground-track (`.gt`), and contact interval (`.int`) files aligned with the updated geometry.[Ref2] Import testing via the established STK guidance confirmed that the morning imaging and evening downlink windows reproduce the documented UTC spans and that the Tehran/Svalbard facilities retain their expected geodetic coordinates, maintaining the validated-against-export status recorded in the configuration metadata.[Ref2][Ref4]

## Compliance Assessment
The deterministic centroid cross-track evidence produced by `run_20260321_0740Z_tehran_daily_pass_resampled` closes the MR-2 and SRD-P-001 requirements by demonstrating that the constellation centroid and all vehicles remain within the \(\pm30\,\text{km}\) tolerance at the midpoint of the daily access window, with additional headroom beneath the \(\pm70\,\text{km}\) waiver ceiling.[Ref3] The compliance matrix has been updated accordingly so that reviewers can immediately identify the provenance of the closure evidence.

## Validation Artefacts and Next Steps
1. Regenerate the STK package or rerun the RAAN alignment process as required by executing `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ`, ensuring the output directory follows the repository naming convention before committing results.[Ref5]
2. Use the [STK validation guide](how_to_import_tehran_daily_pass_into_stk.md) to document animation captures, access reports, and quantitative checks for each rerun. Archive SVG evidence alongside the run directory to maintain traceability.[Ref4]
3. Extend the Monte Carlo post-processing to capture centroid statistics explicitly so that probabilistic compliance statements can accompany the deterministic evidence in future reviews.[Ref3]

## References
- [Ref1] `config/scenarios/tehran_daily_pass.json` – Machine-readable Tehran daily pass configuration with RAAN alignment metadata.
- [Ref2] `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/scenario_summary.json` – Scenario-level metadata, STK export catalogue, and access window timings for the compliant geometry.
- [Ref3] `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/deterministic_summary.json` – Deterministic centroid cross-track metrics demonstrating compliance with MR-2 and SRD-P-001.
- [Ref4] `docs/how_to_import_tehran_daily_pass_into_stk.md` – Analyst workflow for STK ingestion and evidence capture.
- [Ref5] `sim/scripts/run_scenario.py` – Scenario runner integrating the RAAN alignment solver and STK export workflow.
