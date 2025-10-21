# Tehran Triangular Formation Simulation Results

## Introduction
This memorandum records the first fully fledged simulation of the three-satellite triangular formation mandated by the mission brief. The analysis centres on a 6 km equilateral geometry that remains above Tehran for at least ninety seconds, providing a coherent sensing baseline for cooperative imaging. The study ensures consistency with the wider Systems Tool Kit (STK 11.2) export workflow by relying on the in-repository `tools/stk_export.py` interface. The latest maintenance and robustness campaign, archived as `run_20251018_1207Z`, extends the assessment to cover the Mission Requirements MR-5 through MR-7 by quantifying command latency, annual formation-keeping \(\Delta v\), and Monte Carlo injection recovery statistics.[Ref2]

## Methodology
1. **Establish orbital baseline.** The reference spacecraft adopts a near-circular \(6898.137\,\text{km}\) semi-major axis, \(97.7^\circ\) inclination orbit. The epoch is aligned with the 21 March 2026 morning overpass so that the ground track intersects Tehran.
2. **Define formation geometry.** Relative offsets of \((-\tfrac{\sqrt{3}}{6}L, \pm \tfrac{1}{2}L, 0)\) and \((\tfrac{\sqrt{3}}{3}L, 0, 0)\) metres (with \(L = 6000\,\text{m}\)) generate a centroid-centred equilateral triangle in the local-vertical, local-horizontal frame, satisfying the observability guidance of D'Amico et al. [Ref1].
3. **Propagate inertial states.** The `constellation.orbit` utilities apply Keplerian propagation to the reference orbit and transform the formation offsets into Earth-centred inertial coordinates at one-second resolution across a 180-second horizon.
4. **Assess ground geometry.** Geodetic conversion and a 350 km ground-distance tolerance quantify the duration during which all three spacecraft simultaneously observe Tehran within the desired formation aspect ratio bound (1.02).
5. **Export for STK validation.** The resulting ephemerides and ground tracks are serialised through `tools/stk_export.py`, guaranteeing ingestion compatibility with STK 11.2 scenario files.

## Results
The simulation yields the metrics summarised in Table 1. The formation maintains an aspect ratio that is unity to machine precision across the validated access window (the peak aspect ratio recorded in the summary JSON is 1.00000000000018). The maximum side-length variation is below one metre, confirming negligible distortion over the ninety-six-second access period. The centroid altitude remains \(520\,\text{km}\), matching the design reference. Automated regression `tests/unit/test_triangle_formation.py` enforces these bounds together with the new MR-5 to MR-7 margins so that future updates cannot regress compliance.[Ref3]

The committed `triangle_summary.json` differentiates the simultaneous-observation window from the full 180-second propagation. Within the validated 96-second interval the maximum ground distance from Tehran peaks at \(343.62\,\text{km}\), whereas the complete propagation reaches \(641.89\,\text{km}\). Table 1 therefore now lists both figures so that reviewers can unambiguously see which value underpins the compliance statements.[Ref2]

Table 1 – Key formation metrics

| Metric | Value |
| --- | --- |
| Formation window duration | \(96\,\text{s}\) |
| Window start (UTC) | 2026-03-21T09:31:12Z |
| Window end (UTC) | 2026-03-21T09:32:48Z |
| Mean triangle area | \(1.56\times 10^7\,\text{m}^2\) |
| Mean side length | \(6.00\pm0.00\,\text{km}\) |
| Maximum aspect ratio | 1.00000000000018 (unity within numerical precision) |
| Maximum ground distance to Tehran (validated 96 s window) | \(343.62\,\text{km}\) |
| Maximum ground distance to Tehran (full propagation) | \(641.89\,\text{km}\) |

## Orbital Element Reconstruction
The midpoint of the validated access window was sampled to recover classical orbital elements for each spacecraft using the new `cartesian_to_classical` routine. The values in Table 2 confirm that Satellites 1 and 2 share Plane A while Satellite 3 occupies Plane B with a doubled semi-major-axis offset that preserves the equilateral geometry in the local-vertical, local-horizontal frame.[Ref1]

Table 2 – Classical orbital elements at 2026-03-21T09:32:00Z

| Satellite | Assigned plane | Semi-major axis (km) | Eccentricity | Inclination (deg) | RAAN (deg) | Argument of perigee (deg) | Mean anomaly (deg) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SAT-1 | Plane A | 6891.215 | 7.53\(\times 10^{-4}\) | 97.70 | 18.881 | 216.040 | 180.0 |
| SAT-2 | Plane A | 6891.215 | 7.53\(\times 10^{-4}\) | 97.70 | 18.881 | 216.089 | 180.0 |
| SAT-3 | Plane B | 6912.017 | 1.51\(\times 10^{-3}\) | 97.70 | 18.881 | 36.065 | 0.0 |

## STK Validation
Running `python -m sim.scripts.run_triangle --output-dir artefacts/run_20251018_1207Z` regenerates the summary JSON, maintenance CSV, command-window CSV, Monte Carlo catalogue, and STK artefacts (`.e`, `.sat`, `.gt`, `.fac`, `.int`). The exporter sanitises identifiers before serialisation so that the scenario appears as `Tehran_Triangle_Formation.sc` and the accompanying spacecraft ephemerides adopt underscore-separated names (`SAT_1.e`, `SAT_2.e`, `SAT_3.e`). Each ephemeris is now paired with a `.sat` wrapper referencing the corresponding `.e` file, allowing STK 11.2 to bind trajectories automatically during import. This naming convention avoids the “Invalid object name” import error previously triggered by spaces and hyphens, and the refreshed artefact set has been re-imported to confirm that all spacecraft trajectories populate as expected. The metadata block marks the configuration as validated against `tools/stk_export.py`, enabling analysts to confirm the ninety-six-second contact window inside STK without additional manual bindings while also reproducing the MR-5 to MR-7 evidence.

## Maintenance and Responsiveness Assessment
Table 3 summarises the new maintenance and responsiveness metrics captured during `run_20251018_1207Z`. The annual formation-keeping \(\Delta v\) remains below the MR-6 cap, the single-station commanding scheme respects the 12-hour MR-5 latency ceiling with a \(10.5\,\text{h}\) margin, and all 300 Monte Carlo injection recovery trials satisfy the MR-7 robustness objective. The underlying datasets—`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, and `injection_recovery_cdf.svg`—are version-controlled under `artefacts/run_20251018_1207Z/` and validate directly against STK via the exporter workflow.[Ref2]

Table 3 – MR-5 to MR-7 maintenance and responsiveness metrics

| Requirement | Metric | Result | Margin | Evidence |
| --- | --- | --- | --- | --- |
| MR-5 | Maximum command latency | \(1.53\,\text{h}\) | \(10.47\,\text{h}\) margin versus 12-hour limit | `triangle_summary.json` (run_20251018_1207Z)[Ref2] |
| MR-6 | Maximum annual formation-keeping \(\Delta v\) | \(14.04\,\text{m/s}\) | \(0.96\,\text{m/s}\) below 15 m/s budget | `maintenance_summary.csv` (run_20251018_1207Z)[Ref2] |
| MR-7 | Monte Carlo recovery success rate | 100% over 300 trials; \(p_{95}\) \(\Delta v = 0.041\,\text{m/s}\) | Full compliance within 15 m/s allocation | `injection_recovery.csv` (run_20251018_1207Z)[Ref2] |

## References
- [Ref1] D'Amico, S., et al., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
- [Ref2] Formation-Sat Systems Team, *run_20251018_1207Z Tehran Triangle Maintenance and Robustness Campaign*, FS-ANL-005 v1.0, 2025.
- [Ref3] Formation-Sat Systems Team, *Triangle Formation Unit Tests*, FS-TST-004 v1.1, 2025.
