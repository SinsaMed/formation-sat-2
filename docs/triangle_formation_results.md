# Tehran Triangular Formation Simulation Results

## Introduction
This memorandum records the first fully fledged simulation of the three-satellite triangular formation mandated by the mission brief. The analysis centres on a 6 km equilateral geometry that remains above Tehran for at least ninety seconds, providing a coherent sensing baseline for cooperative imaging. The study ensures consistency with the wider Systems Tool Kit (STK 11.2) export workflow by relying on the in-repository `tools/stk_export.py` interface. The latest maintenance and robustness campaign, archived as `artefacts/run/unnamed_run/20251018T120700Z/`, extends the assessment to cover the Mission Requirements MR-5 through MR-7 by quantifying command latency, annual formation-keeping \(\Delta v\), and Monte Carlo injection recovery statistics.[Ref2]

## Methodology
1. **Establish orbital baseline.** The reference spacecraft adopts a near-circular \(6898.137\,\text{km}\) semi-major axis, \(97.7^\circ\) inclination orbit. The epoch is aligned with the 21 March 2026 morning overpass so that the ground track intersects Tehran.
2. **Define formation geometry.** Relative offsets of \((0, -\tfrac{1}{2}L, -\tfrac{\sqrt{3}}{6}L)\), \((0, \tfrac{1}{2}L, -\tfrac{\sqrt{3}}{6}L)\), and \((0, 0, \tfrac{\sqrt{3}}{3}L)\) metres (with \(L = 50{,}000\,\text{m}\)) generate a centroid-centred equilateral triangle embedded entirely within the local horizontal plane, ensuring that all vehicles maintain comparable altitude whilst satisfying the observability guidance of D'Amico et al. [Ref1].
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

The debug export accompanying each simulation run now includes `triangle_geometry.csv`, capturing per-second area, aspect ratio, and side-length diagnostics, and the derived `triangle_geometry_timeseries.svg` plot. The automated figure overlays the ±5 per cent side-length requirement and the 1.02 aspect ratio ceiling mandated by the verification plan, demonstrating that every sample across the ninety-six-second window remains inside the authorised tolerance bands.[Ref2][Ref4]

To evidence simultaneous compliance with the \(350\,\text{km}\) ground-distance envelope and the \(2{,}200\,\text{km}\) command contact range, the artefact set now emits `ground_ranges.csv` together with the `ground_command_ranges.svg` diagnostic. The plot overlays both tolerance levels in kilometres and annotates any excursions, enabling reviewers to confirm that the Tehran target remains inside the ground track allowance while uplink opportunities continue to fall within the command antenna geometry.[Ref2]

## Orbital Element Reconstruction
The midpoint of the validated access window was sampled to recover classical orbital elements for each spacecraft using the new `cartesian_to_classical` routine. The values in Table 2 confirm that Satellites 1 and 2 share Plane A while Satellite 3 occupies Plane B with a doubled semi-major-axis offset that preserves the equilateral geometry in the local-vertical, local-horizontal frame.[Ref1]

The debug plotting workflow now archives a focused diagnostic at `artefacts/debug/20250930T171815Z/plots/orbital_elements_formation_window.svg`, filtering the orbital-element time series to the \(2026\text{-}03\text{-}21T09{:}31{:}12Z\) to \(2026\text{-}03\text{-}21T09{:}32{:}48Z\) interval declared in `triangle_summary.json`. The chart mirrors the Systems Tool Kit (STK 11.2) compatible ephemerides exported through `tools/stk_export.py`, so reviewers can interrogate the same trajectory segment in both the SVG record and STK without encountering format limitations.

Table 2 – Classical orbital elements at 2026-03-21T09:32:00Z

| Satellite | Assigned plane | Semi-major axis (km) | Eccentricity | Inclination (deg) | RAAN (deg) | Argument of perigee (deg) | Mean anomaly (deg) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SAT-1 | Plane A | 6891.215 | 7.53\(\times 10^{-4}\) | 97.70 | 18.881 | 216.040 | 180.0 |
| SAT-2 | Plane A | 6891.215 | 7.53\(\times 10^{-4}\) | 97.70 | 18.881 | 216.089 | 180.0 |
| SAT-3 | Plane B | 6912.017 | 1.51\(\times 10^{-3}\) | 97.70 | 18.881 | 36.065 | 0.0 |

## STK Validation
Running `python -m cli triangle --output-dir artefacts/run/unnamed_run/20251018T120700Z/` regenerates the summary JSON, maintenance CSV, command-window CSV, Monte Carlo catalogue, and STK artefacts (`.e`, `.sat`, `.gt`, `.fac`, `.int`). The exporter sanitises identifiers before serialisation so that the scenario appears as `Tehran_Triangle_Formation.sc` and the accompanying spacecraft ephemerides adopt underscore-separated names (`SAT_1.e`, `SAT_2.e`, `SAT_3.e`). Each ephemeris is now paired with a `.sat` wrapper referencing the corresponding `.e` file, allowing STK 11.2 to bind trajectories automatically during import. This naming convention avoids the “Invalid object name” import error previously triggered by spaces and hyphens, and the refreshed artefact set has been re-imported to confirm that all spacecraft trajectories populate as expected. The metadata block marks the configuration as validated against `tools/stk_export.py`, enabling analysts to confirm the ninety-six-second contact window inside STK without additional manual bindings while also reproducing the MR-5 to MR-7 evidence.

## Maintenance and Responsiveness Assessment
Table 3 summarises the new maintenance and responsiveness metrics captured during the `artefacts/run/unnamed_run/20251018T120700Z/` run. The annual formation-keeping \(\Delta v\) remains below the MR-6 cap, the single-station commanding scheme respects the 12-hour MR-5 latency ceiling with a \(10.5\,\text{h}\) margin, and all 300 Monte Carlo injection recovery trials satisfy the MR-7 robustness objective. The underlying datasets—`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, and `injection_recovery_cdf.svg`—are version-controlled under `artefacts/run/unnamed_run/20251018T120700Z/` and validate directly against STK via the exporter workflow.[Ref2]

Table 3 – MR-5 to MR-7 maintenance and responsiveness metrics

| Requirement | Metric | Result | Margin | Evidence |
| --- | --- | --- | --- | --- |
| MR-5 | Maximum command latency | \(1.53\,\text{h}\) | \(10.47\,\text{h}\) margin versus 12-hour limit | `triangle_summary.json` (`artefacts/run/unnamed_run/20251018T120700Z/`)[Ref2] |
| MR-6 | Maximum annual formation-keeping \(\Delta v\) | \(14.04\,\text{m/s}\) | \(0.96\,\text{m/s}\) below 15 m/s budget | `maintenance_summary.csv` (`artefacts/run/unnamed_run/20251018T120700Z/`)[Ref2] |
| MR-7 | Monte Carlo recovery success rate | 100% over 300 trials; \(p_{95}\) \(\Delta v = 0.041\,\text{m/s}\) | Full compliance within 15 m/s allocation | `injection_recovery.csv` (`artefacts/run/unnamed_run/20251018T120700Z/`)[Ref2] |

## Repeatability Diagnostics
1. **Catalogue access windows.** The new `formation_windows.csv` artefact enumerates every contiguous interval satisfying the ground-distance and aspect-ratio tolerances across the fourteen-day verification horizon. Each record notes the start and end timestamps, duration, and the worst-case triangle distortion so analysts can verify that repeated opportunities occur with consistent geometry.[Ref2]
2. **Quantify recurrence statistics.** The `formation_recurrence` block inside `triangle_summary.json` reports the mean and extreme window separations alongside an orbital-period reference, enabling reviewers to confirm that the simulated constellation revisits Tehran with the expected synodic cadence.[Ref2]
3. **Monitor station-keeping demand.** An automated scheduler evaluates the maximum side-length deviation against a one-percent tolerance and records recommended corrections in `station_keeping_events.csv`. The fourteen-day campaign identified no violations, demonstrating that the equilateral geometry remains self-sustaining without invoking the manoeuvre budget, yet the logic will flag any future drift that exceeds the tolerance envelope.[Ref2]

## References
- [Ref1] D'Amico, S., et al., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
- [Ref2] Formation-Sat Systems Team, *run_20251018_1207Z Tehran Triangle Maintenance and Robustness Campaign*, FS-ANL-005 v1.0, 2025.
- [Ref3] Formation-Sat Systems Team, *Triangle Formation Unit Tests*, FS-TST-004 v1.1, 2025.
- [Ref4] Formation-Sat Systems Team, *Verification Plan*, FS-PLN-003 v1.2, 2025.
