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
The lightweight propagation pipeline exports the scenario through `tools/stk_export.py`, producing an STK 11.2 package containing ephemerides, ground-track samples, and access intervals. Validation run `run_20251018_1936Z_tehran_daily_pass` regenerated the exports and delivered an updated package under `artefacts/stk_run_20251018_1935Z/`. Automated ingestion via `tools/stk_tehran_daily_pass_runner.py` could not be exercised in the present Linux environment because the Windows-only `pywin32` dependency is unavailable; the connect script and formation metrics have nevertheless been archived alongside the package so that reviewers with an STK workstation can complete the import checklist.【Ref1】【Ref2】【d52ff4†L1-L6】 The legacy `run_20251018_1308Z_tehran_daily_pass` import evidence remains accessible for reference and continues to support the `validated_against_stk_export` flag until a fresh Windows session is obtained.

## High-Fidelity Perturbation Analysis
The clarified MR-2 requirement was verified on 18 October 2025 using `run_20251018_1936Z_tehran_daily_pass`. The deterministic propagation now samples every three seconds and the Monte Carlo companion executes ten dispersion realisations, applying \(J_2\), atmospheric drag, and the programme baseline drag area-to-mass ratio. Key evaluation stages were:

1. Propagate the constellation across the six-hour window, deriving both relative and absolute cross-track offsets between the leader (Plane A) and the Plane B deputy. The deterministic series reports minimum absolute offsets of 2.62 km, 5.86 km, and 7.28 km, demonstrating that each plane satisfies the ±10 km acceptance bound while maintaining tight relative geometry at \(0.200\,\text{km}\).【F:artefacts/run_20251018_1936Z_tehran_daily_pass/deterministic_summary.json†L1-L48】
2. Execute ten Monte Carlo trials using the revised dispersion set. Every trial satisfies the ±10 km requirement and the fleet compliance probability is 1.0, confirming that the clarified MR-2/SRD-P-001 pair is closed.【F:artefacts/run_20251018_1936Z_tehran_daily_pass/monte_carlo_summary.json†L1-L77】
3. Archive solver settings, deterministic and Monte Carlo CSV catalogues, and refreshed STK exports alongside the run directory so that Systems Tool Kit ingestion can be re-performed without regenerating data.【Ref1】

The superseded `run_20251018_1345Z` catalogue is retained for traceability because it documents the geometry shortfall that precipitated the CCB clarification, but EV-6 is now the authoritative evidence set for MR-2 and SRD-P-001.

## Validation Artefacts and Next Steps
1. Regenerate the compliance evidence by executing `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass`, ensuring the output directory follows the naming convention adopted by EV-6.【Ref1】
2. Use the [STK validation guide](how_to_import_tehran_daily_pass_into_stk.md) to document animation captures, access reports, and quantitative checks whenever the STK package is refreshed. Archive evidence (SVG screenshots, CSV metrics) alongside the run directory to maintain traceability.【Ref2】
3. Update this note and the compliance matrix whenever new evidence is generated so that reviewers can rapidly determine the provenance of the latest validation set.

## References
- [Ref1] `sim/scripts/run_scenario.py` – Scenario pipeline and STK export integration.
- [Ref2] `docs/how_to_import_tehran_daily_pass_into_stk.md` – Analyst workflow for STK ingestion and evidence capture.
- [Ref3] `artefacts/run_20251018_1345Z` – High-fidelity Tehran daily pass perturbation analysis prior to the MR-2 clarification (retained for traceability).
- [Ref4] `artefacts/run_20251018_1936Z_tehran_daily_pass` – High-fidelity Tehran daily pass compliance package (deterministic summary, Monte Carlo statistics, STK exports).
