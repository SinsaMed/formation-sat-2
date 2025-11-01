# Tehran Triangle Run `run_20251101_0803Z` Analytical Report

## Introduction
This memorandum documents the freshly generated triangular-formation dataset `run_20251101_0803Z`, executed against the baseline Tehran scenario in `config/scenarios/tehran_triangle.json` and capturing a verified \(96\,\text{s}\) simultaneous access window.[Ref1][Ref2] The run supplements the authoritative catalogue with a comprehensive suite of visual analytics that render the mission geometry, perturbation environment, and validation cross-checks in publication-ready form. All plots are archived as scalable vector graphics to remain compliant with the repository’s reviewability constraints.[Ref3]

## Methodology
1. **Propagation.** The run was produced by executing `python -m sim.scripts.run_triangle --config config/scenarios/tehran_triangle.json --output-dir artefacts/run_20251101_0803Z`, yielding the canonical JSON summary, CSV diagnostics, and STK export bundle.[Ref4][Ref2]
2. **Post-processing.** The bespoke `tools/generate_triangle_report.py` utility ingested the simulation outputs, performed supplementary one-day Keplerian propagation, and generated twelve SVG figures spanning mission design, formation kinematics, perturbation budgets, and validation overlays.[Ref5]
3. **Archiving.** A structured `run_metadata.json` ledger records the scenario provenance, file locations, and summary metrics to ease traceability and downstream audit.[Ref6]

## Data Products
| Artefact | Purpose |
| --- | --- |
| `triangle_summary.json` | Primary metrics including triangle geometry, formation window timestamps, maintenance estimates, and Monte Carlo statistics.[Ref2] |
| `maintenance_summary.csv` | Differential-acceleration statistics and annualised Δv requirements per spacecraft.[Ref7] |
| `command_windows.csv` | Consolidated command-station visibility intervals derived from the Tehran uplink geometry.[Ref8] |
| `drag_dispersion.csv` | Atmospheric drag Monte Carlo outcomes over a twelve-orbit horizon with tolerance checks.[Ref9] |
| `orbital_elements.csv` | Time-resolved classical orbital elements for all spacecraft during the access interval.[Ref10] |
| `stk/` suite | STK 11.2 compatible ephemerides, ground tracks, and facility definitions for independent validation.[Ref11] |
| `plots/` directory | Mission design, formation kinematics, perturbation, and validation figures described in the following sections.[Ref3] |

## Mission Design Visualisations
1. **Twenty-four-hour ground tracks.** Figure `ground_tracks.svg` overlays the daily repeating equatorial crossings with the ninety-second Tehran window, evidencing the repeat-ground-track alignment and centroid convergence.[Ref3]
2. **Orbital plane geometry.** Figure `orbital_planes_3d.svg` renders the two assigned orbital planes, their intersection above Tehran, and the equilateral spacing at the window midpoint, aiding qualitative explanation of the formation architecture.[Ref3]
3. **Orbital element stability.** Figure `orbital_elements_timeseries.svg` charts semi-major axis, inclination, RAAN, and argument of perigee across the simulated window, demonstrating negligible drift during the access interval.[Ref3][Ref10]

## Triangle Formation Window Analysis
1. **Relative LVLH positions.** Figure `relative_positions.svg` samples three instants bracketing the window, showing the deputies’ along-track symmetry and centroid placement within the \(\pm 30\,\text{km}\) tolerance corridor.[Ref3][Ref2]
2. **Pairwise separations.** Figure `pairwise_distances.svg` confirms all sides remain within centimetres of the commanded \(6\,\text{km}\) length throughout the access, with a reference line marking the specification value.[Ref3]
3. **Daily access recurrence.** Figure `access_timeline.svg` expresses the recurring ninety-second window over a seven-day horizon, underpinning the mission-level coverage narrative.[Ref3][Ref2]

## Perturbations and Maintenance
1. **Perturbation trends.** Figure `perturbation_effects.svg` estimates RAAN drift under \(J_2\), altitude loss under drag, and along-track displacement under solar radiation pressure for a maintenance-free month, contextualising the manoeuvre cadence.[Ref3][Ref2][Ref9]
2. **Maintenance budget.** Figure `maintenance_delta_v.svg` visualises the annual Δv allocation drawn from the differential acceleration statistics, supporting compliance with MR-5 fuel limits.[Ref3][Ref7]
3. **Monte Carlo recovery envelope.** Figure `monte_carlo_sensitivity.svg` scatters the injection-recovery samples, illustrating the modest Δv demand required to re-establish geometry under dispersed initial errors.[Ref3][Ref12]

## Validation and Sensitivity Studies
1. **Analytical versus STK comparison.** Figure `analytical_vs_stk_groundtrack.svg` overlays the Python propagation against the STK ground tracks, demonstrating sub-arcminute agreement in latitude and longitude.[Ref3][Ref11]
2. **Performance metrics synopsis.** Figure `performance_metrics.svg` juxtaposes the measured aspect ratio, side length, ground-distance peak, and window duration against mission thresholds, reaffirming MR-3 compliance.[Ref3][Ref2]
3. **Access sensitivity contour.** Figure `access_sensitivity_contour.svg` maps window duration as a function of semi-major axis and inclination perturbations, highlighting the robustness of the chosen operating point.[Ref3][Ref1]

## References
- [Ref1] `config/scenarios/tehran_triangle.json` – Scenario baseline defining orbital elements, formation geometry, and tolerances.
- [Ref2] `artefacts/run_20251101_0803Z/triangle_summary.json` – Simulation metrics and window timestamps for `run_20251101_0803Z`.
- [Ref3] `artefacts/run_20251101_0803Z/plots/` – SVG figure directory generated for this run.
- [Ref4] `sim/scripts/run_triangle.py` – Command-line driver for the Tehran triangular-formation propagator.
- [Ref5] `tools/generate_triangle_report.py` – Plotting utility producing the analytical figures listed above.
- [Ref6] `artefacts/run_20251101_0803Z/run_metadata.json` – Run ledger capturing provenance and artefact locations.
- [Ref7] `artefacts/run_20251101_0803Z/maintenance_summary.csv` – Differential acceleration and Δv statistics.
- [Ref8] `artefacts/run_20251101_0803Z/command_windows.csv` – Command-station visibility intervals.
- [Ref9] `artefacts/run_20251101_0803Z/drag_dispersion.csv` – Atmospheric drag Monte Carlo sample set.
- [Ref10] `artefacts/run_20251101_0803Z/orbital_elements.csv` – Classical orbital-element time series.
- [Ref11] `artefacts/run_20251101_0803Z/stk/` – STK 11.2 ephemeris and facility export suite.
- [Ref12] `artefacts/run_20251101_0803Z/injection_recovery.csv` – Injection recovery Monte Carlo statistics.
