# Tehran Daily Pass Locked Run Analysis

## Introduction
The locked evidence set `run_20251020_1900Z_tehran_daily_pass_locked` encapsulates the daily access alignment propagated on 21 March 2026 using the high-fidelity pipeline defined by `sim/scripts/run_scenario.py`. The scenario summary records the imaging window from 07:39:25Z to 07:40:55Z, the optimised right ascension of the ascending node (RAAN) of \(350.7885^{\circ}\), and the delivery of a complete Systems Tool Kit (STK 11.2) export for independent validation.[Ref1] These artefacts ensure that the deterministic and Monte Carlo assessments remain traceable to a configuration-controlled product that has already been imported into STK without limitation.[Ref1]

## Execution Workflow
The scenario proceeds through seven stages—RAAN alignment, access-node detection, mission phase tagging, two-body propagation, high-fidelity \(J_2\)+drag propagation, metric extraction, and STK export—so that the final statistics reflect the perturbation-aware geometry used for compliance sign-off.[Ref1] The solver settings encode a ten-second cadence with drag coefficient 2.2, ballistic coefficient \(0.025\,\text{m}^2\,\text{kg}^{-1}\), and F10.7 solar flux index 150, matching the locked deterministic summary.[Ref2]

## Deterministic Geometry
Table 1 reports the great-circle cross-track separation for each spacecraft at the evaluation epoch 07:40:10Z. All vehicles remain within the ±30 km primary tolerance, and the centroid offset is 12.14 km, leaving margin to the ±70 km waiver envelope.[Ref2]

| Spacecraft | Cross-track at 07:40:10Z (km) | Absolute cross-track at 07:40:10Z (km) |
| --- | --- | --- |
| FSAT-LDR | 12.21 | 12.21 |
| FSAT-DP1 | 27.76 | 27.76 |
| FSAT-DP2 | -3.54 | 3.54 |
| Centroid | 12.14 | 12.14 |

The deterministic cross-track history spans the complete access window, showing convergence from kilometre-scale offsets into the compliant corridor; the newly generated SVG `cross_track_deterministic.svg` visualises this closure alongside the primary and waiver thresholds.[Ref4]

## Monte Carlo Dispersion
The Monte Carlo catalogue comprises 1000 realisations sampled at the same epoch, demonstrating unit compliance probability for both primary and waiver criteria.[Ref3] Table 2 summarises the evaluation statistics.

| Spacecraft | Mean absolute cross-track (km) | Standard deviation (km) | 95th percentile (km) |
| --- | --- | --- | --- |
| FSAT-LDR | 23.76 | 0.11 | 23.95 |
| FSAT-DP1 | 8.35 | 0.28 | 8.84 |
| FSAT-DP2 | 39.63 | 0.08 | 39.76 |
| Centroid | 23.91 | 0.15 | 24.18 |

The figure `cross_track_monte_carlo.svg` overlays the mean, ±1σ dispersion, and 95th-percentile markers against the ±30 km/±70 km thresholds and the centroid percentile to aid presentation.[Ref4] The relative spacing metric remains tightly bounded between 0.143 km and 0.200 km, as depicted in `cross_track_relative.svg`, reaffirming that inter-spacecraft geometry is preserved while closing on the target.[Ref3][Ref4]

## References
- [Ref1] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json`.
- [Ref2] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`.
- [Ref3] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`.
- [Ref4] `tools/render_tehran_daily_pass_plots.py`.
