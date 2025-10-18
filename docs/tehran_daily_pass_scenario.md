# Tehran Daily Pass Scenario Overview

## Context
The Tehran daily pass scenario characterises a dawn-dusk imaging opportunity over the metropolitan region of Tehran to support infrastructure resilience monitoring. The configuration aligns with the wider Formation Satellite Programme baseline defined in the project configuration and preserves compatibility with the Systems Tool Kit (STK 11.2) export workflow. Operational emphasis is placed on rapid image acquisition during morning overpasses followed by evening downlink, ensuring that situational awareness products can be disseminated before the subsequent civil planning cycle.

## Configuration Linkage
The authoritative machine-readable description is maintained in the [Tehran daily pass configuration](../config/scenarios/tehran_daily_pass.json). The file records the orbital elements tied to the \(2026\) vernal equinox reference epoch, specifies the one-day repeat ground-track behaviour, and enumerates daily access windows centred on the \(09{:}24\) UTC imaging opportunity. Payload constraints capture the imaging, thermal, and data-handling limitations that must be honoured by any simulation or on-board scheduling algorithm. These entries are designed to feed directly into the simulation scaffolding exposed through `sim.scripts.scenario_execution` once that workflow is implemented.

## Scenario Pipeline Implementation
The lightweight propagation chain has now been implemented within [`sim/scripts/run_scenario.py`](../sim/scripts/run_scenario.py). Executing `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir <run_dir>` generates a mission summary together with Systems Tool Kit (STK 11.2) compliant ephemeris, ground-track, and contact interval artefacts under `<run_dir>/stk_export`. The exporter leverages the `tools/stk_export.py` primitives to ensure naming hygiene, monotonic sampling, and coordinate-frame assumptions are consistent with the validation workflow. Analysts should retain the default directory structure so that downstream documentation can cite the run via an ISO-8601 `run_YYYYMMDD_hhmmZ` identifier, with provenance captured alongside the JSON summary.

## Assumptions
1. The spacecraft maintains a sun-synchronous altitude consistent with the programme-wide nominal value, enabling persistent morning illumination over Tehran without additional phasing manoeuvres.
2. Downlink relies on the existing high-latitude ground stations enumerated in the project configuration, with Svalbard receiving priority evening contacts for daily imagery return.
3. Thermal recovery between imaging segments is achievable within fifteen minutes provided the payload duty cycle remains below twenty-eight percent, preserving the stipulated detector temperature limits.

## STK Validation Status
`sim/scripts/run_scenario.py` now produces a complete STK export package for the scenario, comprising the external ephemeris (`.e`), satellite definition (`.sat`), ground-track (`.gt`), facility (`.fac`), and interval (`.int`) files required for ingestion. Validation against a live STK 11.2 environment remains outstanding; once analysts import the artefacts they should follow the steps in [`how_to_validate_tehran_stk.md`](how_to_validate_tehran_stk.md) to verify geometry, capture evidence, and toggle the `"validated_against_stk_export"` flag within the configuration. Compliance artefacts and the repository documentation must be updated immediately after successful validation to preserve auditability.

## References
No external references were required for this scenario summary.
