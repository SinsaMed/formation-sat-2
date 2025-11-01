# Tehran Triangle Simulation Walkthrough

## Introduction
This memorandum collates the procedural knowledge required to reproduce the Tehran triangular-formation demonstration using the repository toolchain. The intent is to guide analysts from environment preparation through to Systems Tool Kit (STK 11.2) validation, ensuring the verified ninety-second access window can be regenerated without ambiguity.[Ref1]

## Prerequisites
1. **Establish the Python environment.** Execute `make setup` from the repository root to create the managed virtual environment and install the pinned dependency set declared in `requirements.txt`.
2. **Review configuration artefacts.** Inspect `config/scenarios/tehran_triangle.json` to confirm the mission epoch, geometric tolerances, and plane assignments align with the intended analysis case.[Ref1]
3. **Confirm exporter compatibility.** Familiarise yourself with `tools/stk_export.py` to understand the file formats and metadata required by STK 11.2 ingestion workflows.[Ref2]

## Execution Procedure
1. **Inspect the archived run.** Review the curated `artefacts/triangle_run/` snapshot—mirroring the drag-inclusive rerun `run_20251018_1424Z`—so that `triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, `injection_recovery_cdf.svg`, and the accompanying `run_metadata.json` ledger refresh the baseline before initiating a fresh propagation.[Ref1]
2. **Launch the formation runner.** Invoke `python -m sim.scripts.run_triangle --output-dir artefacts/triangle` to propagate the formation, compute geometry metrics, and serialise the results into a new `artefacts/triangle/` directory that mirrors the archived structure.
3. **Observe command output.** Verify that the terminal log reports a formation window of at least ninety seconds alongside the UTC start and end timestamps for the Tehran overflight.
4. **Inspect generated artefacts.** Examine the regenerated `artefacts/triangle/triangle_summary.json` (or the committed `artefacts/triangle_run/triangle_summary.json`) together with the curated CSV analytics to confirm the recorded triangle metrics, centroid behaviour, maintenance \(\Delta v\), command latency, injection recovery statistics, and drag dispersion margins remain within the documented tolerances.[Ref1]

## Output Interpretation
1. **Validate temporal coverage.** Within either the archived or regenerated summary JSON, ensure the `formation_window.duration_s` field exceeds the ninety-second threshold mandated by the mission requirement set.[Ref1]
2. **Check geometric fidelity.** Review the `triangle.aspect_ratio_max` and `triangle.mean_side_lengths_m` entries to confirm the equilateral geometry is preserved across the access interval.[Ref1]
3. **Review ground-track alignment.** Inspect the `samples` entries within `triangle_summary.json` whose timestamps fall between the `metrics.formation_window.start` and `metrics.formation_window.end` markers. Confirm that the maximum of those windowed `max_ground_distance_km` values remains below the \(350\,\text{km}\) tolerance, demonstrating that all three spacecraft remain within the observation corridor above Tehran. The global propagation also exposes a \(658.41\,\text{km}\) maximum outside the validated window, so capturing the filtered figure in compliance reports prevents ambiguity.[Ref1]

## STK Verification
1. **Prepare the STK workspace.** Open STK 11.2 and create a new scenario matching the start and stop epochs reported in the JSON summary.
2. **Import ephemerides and ground tracks.** Load the `.e` and `_groundtrack.gt` files located under `artefacts/triangle_run/stk_export/` (or from the regenerated `artefacts/triangle/stk_export/` directory) for each spacecraft, ensuring the assets are referenced to the TEME frame as documented in the exporter guide.[Ref2]
3. **Load facilities and contact intervals.** Add the generated `.fac` and `.int` files to visualise the Tehran ground facility and the simultaneous contact window. The interval should match the ninety-second duration established by the Python simulation.[Ref1]
4. **Cross-check metrics.** Use STK's built-in measurement tools to confirm that the triangle side lengths and centroid altitude match the analytical results to within numerical tolerance.[Ref1]

## RAAN Provenance and Traceability
The \(350.983817^{\circ}\) right-ascension-of-the-ascending-node value that surfaces in the triangle artefacts belongs to the validated ninety-six-second window generated on 21 March 2026 between 07:39:20Z and 07:40:56Z, as archived in both `artefacts/triangle_run/triangle_summary.json` and the refreshed `run_20251101_0803Z_tehran_triangle` catalogue.[Ref1][Ref3] These files retain the equilateral-formation solution that satisfied the Tehran access and geometry constraints during the dedicated triangle campaign, so the RAAN figure is deliberately preserved for historical replay and Systems Tool Kit ingestion.

By contrast, the daily pass scenario file `config/scenarios/tehran_daily_pass.json` and its locked alignment artefact `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json` document the \(350.788504^{\circ}\) RAAN derived from the repeat-ground-track optimisation conducted later in the programme.[Ref4][Ref5] Keeping both data sets in the repository clarifies that the triangle demonstration remained successful while the daily operations baseline migrated to the refined nodal alignment; analysts selecting inputs for renewed studies should therefore choose the RAAN that matches the mission thread they are reproducing rather than assuming the \(18.880656^{\circ}\) entry represents a failure case.

## References
- [Ref1] `docs/triangle_formation_results.md`.
- [Ref2] `docs/stk_export.md`.
- [Ref3] `artefacts/run_20251101_0803Z_tehran_triangle/triangle_summary.json` – Triangle run catalogue confirming the 96 s formation window and \(18.880656^{\circ}\) RAAN.
- [Ref4] `config/scenarios/tehran_daily_pass.json` – Daily pass configuration capturing the \(350.788504^{\circ}\) RAAN used for routine operations.
- [Ref5] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json` – Locked alignment ledger documenting the optimised RAAN lineage and solver sweep.
