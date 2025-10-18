# Tehran Daily Pass Scenario Overview

## Context
The Tehran daily pass scenario characterises a dawn-dusk imaging opportunity over the metropolitan region of Tehran to support infrastructure resilience monitoring. The configuration aligns with the wider Formation Satellite Programme baseline defined in the project configuration and preserves compatibility with the Systems Tool Kit (STK 11.2) export workflow. Operational emphasis is placed on rapid image acquisition during morning overpasses followed by evening downlink, ensuring that situational awareness products can be disseminated before the subsequent civil planning cycle.

## Configuration Linkage
The authoritative machine-readable description is maintained in the [Tehran daily pass configuration](../config/scenarios/tehran_daily_pass.json). The file records the orbital elements tied to the \(2026\) vernal equinox reference epoch, specifies the one-day repeat ground-track behaviour, and enumerates daily access windows centred on the \(09{:}24\) UTC imaging opportunity. Payload constraints capture the imaging, thermal, and data-handling limitations that must be honoured by any simulation or on-board scheduling algorithm. These entries are designed to feed directly into the simulation scaffolding exposed through `sim.scripts.scenario_execution` once that workflow is implemented.

## Assumptions
1. The spacecraft maintains a sun-synchronous altitude consistent with the programme-wide nominal value, enabling persistent morning illumination over Tehran without additional phasing manoeuvres.
2. Downlink relies on the existing high-latitude ground stations enumerated in the project configuration, with Svalbard receiving priority evening contacts for daily imagery return.
3. Thermal recovery between imaging segments is achievable within fifteen minutes provided the payload duty cycle remains below twenty-eight percent, preserving the stipulated detector temperature limits.

## STK Validation Status
The lightweight propagation pipeline exports the scenario through `tools/stk_export.py`, producing an STK 11.2 package containing ephemerides, ground-track samples, and access intervals. Validation run `run_20251018_1308Z_tehran_daily_pass` was ingested with `tools/stk_tehran_daily_pass_runner.py`, confirming that the satellite timeline matches the planned horizon, the dawn imaging and evening downlink contacts align with the documented UTC windows, and the Tehran/Svalbard facilities load with the expected geodetic coordinates.【Ref1】【Ref2】 Resultant artefacts reside under `artefacts/run_20251018_1308Z_tehran_daily_pass/`, and the configuration metadata flag `validated_against_stk_export` is set to `true` to reflect successful import testing.

## High-Fidelity Perturbation Analysis
The enhanced perturbation workflow was executed on 18 October 2025, depositing artefacts under `artefacts/run_20251018_1345Z/`. The analysis combines deterministic propagation with 200-run Monte Carlo dispersions, incorporating \(J_2\), atmospheric drag, and the programme baseline drag area-to-mass ratio. Key evaluation stages were:

1. Propagate the constellation with one-minute samples across a six-hour window, deriving both relative and absolute cross-track offsets between the leader (Plane A) and the Plane B deputy. The deterministic series reports minimum absolute offsets of 439–445 km and an intersection miss distance of \(1.81\,\text{Mm}\), demonstrating that the current orbit selection violates the ±10 km requirement even though the relative formation geometry remains tightly controlled at \(0.2095\,\text{km}\).【Ref3】
2. Execute 200 Monte Carlo trials using the dispersion set defined in `DEFAULT_MONTE_CARLO`, capturing statistics for each vehicle and the inter-plane relative motion. The \(p_{95}\) relative cross-track magnitude remains at \(0.2095\,\text{km}\), but the absolute cross-track compliance probability is 0.0 because no trial satisfies the ±10 km bound, reinforcing that MR-2 and SRD-P-001 remain open.【Ref3】
3. Archive solver settings, deterministic and Monte Carlo CSV catalogues, and refreshed STK exports alongside the run directory so that Systems Tool Kit ingestion can be re-performed without regenerating data.【Ref1】【Ref3】

The Monte Carlo catalogue and deterministic summary therefore confirm that the current evidence base does not close MR-2 or SRD-P-001. Engineering teams must either retune the orbit design to satisfy the ±10 km absolute criterion or formally modify the requirement to match the relative-plane interpretation before compliance can be claimed in the repository documentation.

## Validation Artefacts and Next Steps
1. Regenerate the STK package as required by executing `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass`, ensuring the output directory follows the compliance naming convention.【Ref1】
2. Use the [STK validation guide](how_to_import_tehran_daily_pass_into_stk.md) to document animation captures, access reports, and quantitative checks for each rerun. Archive evidence (SVG screenshots, CSV metrics) alongside the run directory to maintain traceability.【Ref2】
3. Update this note and the compliance matrix whenever new evidence is generated so that reviewers can rapidly determine the provenance of the latest validation set.

## References
- [Ref1] `sim/scripts/run_scenario.py` – Scenario pipeline and STK export integration.
- [Ref2] `docs/how_to_import_tehran_daily_pass_into_stk.md` – Analyst workflow for STK ingestion and evidence capture.
- [Ref3] `artefacts/run_20251018_1345Z` – High-fidelity Tehran daily pass perturbation analysis (deterministic summary, Monte Carlo statistics, relative cross-track catalogues, solver settings).
