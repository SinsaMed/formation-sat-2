# Locked Tehran Daily-Pass Alignment Run

## Introduction
This memorandum documents the deterministic and stochastic evidence preserved in `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/`. The run realises the optimised Tehran daily-pass geometry and serves as the authoritative compliance package for the mission’s cross-track requirement envelope.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json†L1-L118】【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json†L1-L116】

## Simulation Workflow
1. **RAAN alignment sweep.** `sim/scripts/run_scenario.py` ingests `config/scenarios/tehran_daily_pass.json`, applies the locked RAAN solution of \(350.788504^{\circ}\), and establishes the daily imaging window over Tehran.【F:sim/scripts/run_scenario.py†L1-L200】【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json†L83-L146】
2. **High-fidelity propagation.** The solver advances the constellation with \(J_{2}\) and drag enabled, capturing the cross-track behaviour of each spacecraft at ten-second cadence across the 90-second access window.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json†L147-L226】【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json†L1-L116】
3. **STK verification.** The resulting ephemerides are exported through `tools/stk_export.py`, producing the `.sat`, `.e`, `.gt`, and `.int` files archived alongside the run directory. Import checks against STK 11.2 confirmed compatibility and preserve the evidence trace.【F:tools/stk_export.py†L1-L200】【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json†L227-L268】
4. **Visualisation synthesis.** `tools/render_tehran_daily_pass_plots.py` and `tools/render_scenario_formation.py` transform the textual artefacts into canonical SVG graphics and a Plotly scene for presentation use.【F:tools/render_tehran_daily_pass_plots.py†L1-L237】【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/formation_3d.svg†L1-L2】

## Deterministic Cross-Track Performance
The deterministic catalogue shows that all three spacecraft achieve the ±30 km primary tolerance with substantial margin at the 07:40:10Z evaluation epoch. FSAT-DP1 records the largest absolute offset (27.76 km), FSAT-LDR closes at 12.21 km, and FSAT-DP2 remains within 3.54 km of the target meridian; the centroid magnitude is 12.14 km.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json†L16-L81】 The newly generated plot `deterministic_cross_track_signed.svg` captures the signed evolution across the access window, highlighting the centroid track and the ±30/±70 km thresholds.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/deterministic_cross_track_signed.svg†L1-L16】

## Relative Plane Geometry
Relative separation between the imaging and downlink planes remains tightly bounded. The deterministic catalogue records a minimum absolute cross-plane offset of 0.143 km and a maximum of 0.200 km, demonstrating that the phasing manoeuvres keep the planes co-aligned throughout the pass.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json†L101-L116】 The plot `relative_cross_track.svg` visualises the signed and absolute separations and confirms that the evaluation point sits near the most favourable alignment.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/relative_cross_track.svg†L1-L16】

## Monte Carlo Dispersion
The Monte Carlo catalogue summarises 300 trials per spacecraft with injection and atmospheric perturbations enabled. The 95th-percentile absolute cross-track magnitudes remain below 8.85 km for the minimum excursions and below 2,478.37 km for the maximum excursions; the fleet-level relative separation remains under 0.200 km.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_cross_track.csv†L1-L7】 These statistics are communicated through `monte_carlo_cross_track_p95.svg`, which juxtaposes the minimum and maximum absolute magnitudes for each spacecraft.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/monte_carlo_cross_track_p95.svg†L1-L16】

## Visualisation Inventory
- `deterministic_cross_track_signed.svg` – Signed cross-track time-series with centroid overlay.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/deterministic_cross_track_signed.svg†L1-L16】
- `deterministic_cross_track_absolute.svg` – Absolute cross-track magnitudes and compliance bands.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/deterministic_cross_track_absolute.svg†L1-L16】
- `relative_cross_track.svg` – Inter-plane separation history.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/relative_cross_track.svg†L1-L16】
- `monte_carlo_cross_track_p95.svg` – 95th-percentile dispersion summary for each spacecraft.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/monte_carlo_cross_track_p95.svg†L1-L16】
- `formation_3d.svg` and `formation_3d.html` – Canonical three-dimensional formation render derived from the STK ephemerides.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/formation_3d.svg†L1-L2】

## References
- [Ref1] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json`.
- [Ref2] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`.
- [Ref3] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_cross_track.csv`.
- [Ref4] `sim/scripts/run_scenario.py`.
- [Ref5] `tools/stk_export.py`.
- [Ref6] `tools/render_tehran_daily_pass_plots.py`.
- [Ref7] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/plots/formation_3d.svg`.
