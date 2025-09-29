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
The scenario has not yet been exported through `tools/stk_export.py`; therefore, validation against STK 11.2 remains outstanding. Once the simulation pipeline is implemented, the configuration should be propagated and checked against the exporter to confirm facility and orbit definitions remain interoperable with the STK environment.

## References
No external references were required for this scenario summary.
