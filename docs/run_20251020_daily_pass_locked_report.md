# Tehran daily pass locked formation evidence

## Overview
The archived run `run_20251020_1900Z_tehran_daily_pass_locked` captures the authoritative Tehran daily-pass alignment propagated with \(J_2\)+drag and exported through the Systems Tool Kit (STK) interface. The scenario log records the 07:39:25–07:40:55Z morning imaging window with a midpoint at 07:40:10Z alongside the evening Svalbard downlink opportunity, anchoring the compliance evidence set for mission requirement MR-2.[Ref1][Ref5]

## Propagation set-up
1. The deterministic propagation archived in the run ledger emits the alignment catalogue (`deterministic_cross_track.csv`) together with the supporting metadata listed under `artefacts`.[Ref1]
2. Trigger the Monte Carlo dispersions embedded in the pipeline to regenerate the stochastic catalogue and compliance statistics archived in `monte_carlo_summary.json`, ensuring consistent drag and solar-flux assumptions across all samples.[Ref3]
3. Export the STK package (`stk_export/`) directly from the runner so that subsequent visualisation reuses the ephemeris, ground-track, facility, and contact assets without manual intervention.[Ref1]

## Deterministic cross-track closure
The deterministic summary demonstrates that all three spacecraft close the access midpoint well inside the ±30 km primary limit while retaining margin to the ±70 km waiver ceiling. The evaluation metrics at 07:40:10Z report the following offsets relative to Tehran:[Ref2]

| Spacecraft | Cross-track offset (km) | Absolute offset (km) |
|------------|------------------------|----------------------|
| FSAT-LDR   | 12.207                 | 12.207               |
| FSAT-DP1   | 27.759                 | 27.759               |
| FSAT-DP2   | -3.538                 | 3.538                |

The centroid cross-track magnitude remains at 12.143 km, confirming compliance with both the primary and waiver thresholds.[Ref2]

## Monte Carlo dispersion assessment
The 1000-sample dispersion study preserves full compliance probability: the centroid absolute offset exhibits a mean of 23.914 km with a 95th percentile of 24.180 km, while the worst-spacecraft absolute offset holds a mean of 39.631 km and a 95th percentile of 39.761 km.[Ref3] The fleet-level relative separation maintains a 95th-percentile span of 0.200 km, evidencing negligible in-plane distortion across the ensemble.[Ref3]

## Visual analytics package
Running `python -m tools.render_scenario_formation artefacts/run_20251020_1900Z_tehran_daily_pass_locked` now yields an expanded SVG suite in addition to the canonical three-dimensional render:

- `plots/cross_track_timeseries.svg` – spacecraft cross-track offsets with ±30 km/±70 km envelopes and imaging-window shading.[Ref4]
- `plots/centroid_cross_track.svg` – centroid closure trace across the simulated access interval.[Ref4]
- `plots/relative_cross_track.svg` – absolute pairwise separation history derived from the deterministic catalogue.[Ref4]
- `plots/monte_carlo_statistics.svg` – bar chart summarising mean and 95th-percentile absolute offsets for each spacecraft at the access midpoint, annotated with centroid and worst-spacecraft statistics.[Ref4]
- `plots/formation_3d.svg` – canonical STK-aligned three-dimensional overview with facilities and access cones, unchanged from the previous release.[Ref4]

## References
- [Ref1] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json`.
- [Ref2] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`.
- [Ref3] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`.
- [Ref4] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/`.
- [Ref5] `docs/compliance_matrix.md`.
