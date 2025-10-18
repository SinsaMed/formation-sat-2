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

## Validation Artefacts and Next Steps
1. Regenerate the STK package as required by executing `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass`, ensuring the output directory follows the compliance naming convention.【Ref1】
2. Use the [STK validation guide](how_to_import_tehran_daily_pass_into_stk.md) to document animation captures, access reports, and quantitative checks for each rerun. Archive evidence (SVG screenshots, CSV metrics) alongside the run directory to maintain traceability.【Ref2】
3. Update this note and the compliance matrix whenever new evidence is generated so that reviewers can rapidly determine the provenance of the latest validation set.

## References
- [Ref1] `sim/scripts/run_scenario.py` – Scenario pipeline and STK export integration.
- [Ref2] `docs/how_to_import_tehran_daily_pass_into_stk.md` – Analyst workflow for STK ingestion and evidence capture.
