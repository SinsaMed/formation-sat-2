# Tehran Daily Pass Scenario Overview

## Context
The Tehran daily pass scenario now reflects the right-ascension-of-the-ascending-node (RAAN) alignment recovered by the dedicated solver introduced in the simulation pipeline, ensuring that the constellation centroid remains within \(\pm30\,\text{km}\) of the Tehran reference point at the midpoint of the morning imaging opportunity.[Ref1][Ref6] The configuration remains compatible with the Systems Tool Kit (STK 11.2) export workflow so that analysts can continue to regenerate contact catalogues and orbital ephemerides without bespoke tailoring.[Ref2][Ref5] Morning imaging is still paired with an evening downlink window to preserve the operational cadence supporting the infrastructure resilience monitoring mission.

## Configuration Linkage
The authoritative machine-readable description held in [`config/scenarios/tehran_daily_pass.json`](../config/scenarios/tehran_daily_pass.json) records the RAAN solution of \(350.9838169642857^{\circ}\) at the \(2026\) vernal equinox epoch alongside the refined 07:39:25–07:40:55Z access window.[Ref1] These elements remain tied to the one-day repeat ground-track regime and retain the payload, thermal, and data-handling constraints that feed directly into simulation and onboard scheduling analyses. The metadata block logs the alignment validation run identifier (`run_20251020_1900Z_tehran_daily_pass_locked`) and associated epoch, preserving traceability to the evidence set baselined for compliance oversight.[Ref1][Ref7]

## Alignment Solution and Simulation Evidence
The locked alignment campaign is archived under `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/`, capturing the deterministic alignment solution and the supporting Monte Carlo catalogue.[Ref2][Ref3][Ref4]

1. Initialise the optimisation sweep using `sim/scripts/run_scenario.py`, which now evaluates candidate RAAN values before executing the high-fidelity propagation with \(J_2\) and drag perturbations to select the centroid-minimising configuration.[Ref6]
2. Propagate the deterministic case across the 90-second morning window, confirming a centroid cross-track magnitude of \(12.14\,\text{km}\) and a worst-vehicle absolute offset of \(27.76\,\text{km}\) at 07:40:10Z, comfortably within the \(\pm30\,\text{km}\) primary tolerance and the \(\pm70\,\text{km}\) waiver ceiling.[Ref3]
3. Archive the solver settings, deterministic and Monte Carlo CSV catalogues, and refreshed STK exports alongside the run directory so that downstream analyses can reuse the data products without re-running the optimisation campaign.[Ref2]

*Note:* `run_20260321_0740Z_tehran_daily_pass_resampled` remains available as an exploratory rerun that exercised the resampling workflow while reproducing the locked geometry, export set, and Monte Carlo statistics for comparison studies rather than baseline compliance.[Ref8][Ref9]

## STK Validation Status
The regenerated STK package embedded within `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` was exported directly by the scenario runner, yielding ephemeris (`.e`), satellite (`.sat`), ground-track (`.gt`), and contact interval (`.int`) files aligned with the updated geometry.[Ref2] Import testing via the established STK guidance confirmed that the morning imaging and evening downlink windows reproduce the documented UTC spans and that the Tehran/Svalbard facilities retain their expected geodetic coordinates, maintaining the validated-against-export status recorded in the configuration metadata.[Ref2][Ref5]

## Compliance Assessment
The deterministic centroid cross-track evidence produced by `run_20251020_1900Z_tehran_daily_pass_locked` closes the MR-2 and SRD-P-001 requirements by demonstrating that the constellation centroid and all vehicles remain within the \(\pm30\,\text{km}\) tolerance at the midpoint of the daily access window, with additional headroom beneath the \(\pm70\,\text{km}\) waiver ceiling.[Ref3] The accompanying Monte Carlo catalogue sustains 100% primary and waiver compliance while holding the centroid \(p_{95}\) magnitude to \(24.18\,\text{km}\), reinforcing the robustness margin.[Ref4] The compliance matrix now identifies this run as the authoritative evidence set so that reviewers can immediately confirm provenance during audits.[Ref7]

## Validation Artefacts and Next Steps
1. Regenerate the STK package or rerun the RAAN alignment process as required by executing `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ`, ensuring the output directory follows the repository naming convention before committing results.[Ref6]
2. Use the [STK validation guide](how_to_import_tehran_daily_pass_into_stk.md) to document animation captures, access reports, and quantitative checks for each rerun. Archive SVG evidence alongside the run directory to maintain traceability.[Ref5]
3. Extend the Monte Carlo post-processing to capture centroid statistics explicitly so that probabilistic compliance statements can accompany the deterministic evidence in future reviews.[Ref4]

## References
- [Ref1] `config/scenarios/tehran_daily_pass.json` – Machine-readable Tehran daily pass configuration with RAAN alignment metadata.
- [Ref2] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json` – Scenario-level metadata, STK export catalogue, and access window timings for the compliant geometry.
- [Ref3] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json` – Deterministic centroid cross-track metrics demonstrating compliance with MR-2 and SRD-P-001.
- [Ref4] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json` – Monte Carlo statistics quantifying centroid and worst-spacecraft dispersion for the locked geometry.
- [Ref5] `docs/how_to_import_tehran_daily_pass_into_stk.md` – Analyst workflow for STK ingestion and evidence capture.
- [Ref6] `sim/scripts/run_scenario.py` – Scenario runner integrating the RAAN alignment solver and STK export workflow.
- [Ref7] `docs/compliance_matrix.md` – Repository compliance ledger designating the authoritative evidence set for MR-2 and SRD-P-001.
- [Ref8] `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/scenario_summary.json` – Exploratory rerun capturing the resampled scenario metadata, export catalogue, and access timings.
- [Ref9] `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/monte_carlo_summary.json` – Monte Carlo statistics retained for the exploratory resampled dataset.
