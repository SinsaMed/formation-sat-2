# Tehran Triangular Formation Simulation Results

## Introduction
This memorandum documents the refreshed 1 November 2025 rerun of the three-satellite triangular formation mandated by the mission brief. The new analytics campaign—archived as `run_20251101_0803Z_tehran_triangle`—maintains the 6 km equilateral geometry above Tehran while enriching the evidence base with the requested visual diagnostics and sensitivity studies.[Ref2] The workflow remains anchored on the in-repository STK exporter and now chains the dedicated plotting utility `sim/scripts/generate_triangle_products.py` to produce the publication-ready SVG suite for documentation and thesis use.[Ref3]

## Methodology
1. **Establish orbital baseline.** The reference spacecraft adopts a near-circular \(6898.137\,\text{km}\) semi-major axis, \(97.7^\circ\) inclination orbit. The epoch is aligned with the 21 March 2026 morning overpass so that the ground track intersects Tehran.
2. **Define formation geometry.** Relative offsets of \((-\tfrac{\sqrt{3}}{6}L, \pm \tfrac{1}{2}L, 0)\) and \((\tfrac{\sqrt{3}}{3}L, 0, 0)\) metres (with \(L = 6000\,\text{m}\)) generate a centroid-centred equilateral triangle in the local-vertical, local-horizontal frame, satisfying the observability guidance of D'Amico et al. [Ref1].
3. **Propagate inertial states.** The `constellation.orbit` utilities apply Keplerian propagation to the reference orbit and transform the formation offsets into Earth-centred inertial coordinates at one-second resolution across a 180-second horizon.
4. **Assess ground geometry.** Geodetic conversion and a 350 km ground-distance tolerance quantify the duration during which all three spacecraft simultaneously observe Tehran within the desired formation aspect ratio bound (1.02).
5. **Export for STK validation.** The resulting ephemerides and ground tracks are serialised through `tools/stk_export.py`, guaranteeing ingestion compatibility with STK 11.2 scenario files.
6. **Generate analytical figures.** `python -m sim.scripts.generate_triangle_products` ingests the `run_20251101_0803Z_tehran_triangle` artefacts and emits the SVG plots requested for thesis documentation (ground tracks, orbital planes, maintenance budgets, Monte Carlo sensitivity, and parameter sweeps).[Ref3]

## Results
The simulation yields the metrics summarised in Table 1. The formation retains unity aspect ratio (maximum 1.00000000000021) and metre-level side-length constancy throughout the ninety-six-second access interval, confirming that the equilateral geometry remains undistorted during the imaging opportunity.【F:artefacts/run_20251101_0803Z_tehran_triangle/triangle_summary.json†L3-L18】 Automated regression `tests/unit/test_triangle_formation.py` continues to guard these tolerances alongside the MR-5 to MR-7 performance limits.[Ref4]

The committed `triangle_summary.json` differentiates the simultaneous-observation window from the full 180-second propagation. Within the validated interval the maximum ground distance from Tehran is \(345.91\,\text{km}\), whereas the complete propagation peaks at \(658.41\,\text{km}\).【F:artefacts/run_20251101_0803Z_tehran_triangle/triangle_summary.json†L21-L24】【F:artefacts/run_20251101_0803Z_tehran_triangle/triangle_summary.json†L11135-L11140】 Table 1 records both figures so reviewers can unambiguously see which value underpins the compliance statements.

Table 1 – Key formation metrics

| Metric | Value |
| --- | --- |
| Formation window duration | \(96\,\text{s}\) |
| Window start (UTC) | 2026-03-21T07:39:20Z |
| Window end (UTC) | 2026-03-21T07:40:56Z |
| Mean triangle area | \(1.56\times 10^7\,\text{m}^2\) |
| Mean side length | \(6.00\pm0.00\,\text{km}\) |
| Maximum aspect ratio | 1.00000000000021 (unity within numerical precision) |
| Maximum ground distance to Tehran (validated 96 s window) | \(345.91\,\text{km}\) |
| Maximum ground distance to Tehran (full propagation) | \(658.41\,\text{km}\) |

The refreshed artefact set now bundles the requested SVG suite under `artefacts/run_20251101_0803Z_tehran_triangle/plots/`, covering: (a) 24-hour ground tracks with the ninety-second window highlighted; (b) a three-dimensional rendering of the dual orbital planes; (c) classical orbital-element timelines; (d) Hill-frame snapshots and pairwise separation traces; (e) maintenance and Monte Carlo sensitivity charts; (f) perturbation effects over a 30-day horizon; (g) an access-window recurrence timeline; (h) an STK versus Python ground-track overlay; and (i) an access-duration sensitivity contour. These figures are generated deterministically by `sim/scripts/generate_triangle_products.py` so they can be refreshed whenever the scenario is re-run without manual intervention.[Ref3][Ref2]

## Orbital Element Reconstruction
The midpoint of the validated access window (2026-03-21T07:40:08Z) was sampled to recover classical orbital elements for each spacecraft using the `cartesian_to_classical` routine. Table 2 confirms that Satellites 1 and 2 occupy Plane A while Satellite 3 flies the displaced Plane B solution that preserves the equilateral geometry in the local-vertical, local-horizontal frame.[Ref1] The accompanying `orbital_elements_timeseries.svg` figure in the plots directory visualises the per-second evolution of semi-major axis, inclination, right ascension of the ascending node, and argument of perigee across the full propagation, mirroring the Systems Tool Kit data products generated by the exporter.[Ref3][Ref2]

Table 2 – Classical orbital elements at 2026-03-21T07:40:08Z

| Satellite | Assigned plane | Semi-major axis (km) | Eccentricity | Inclination (deg) | RAAN (deg) | Argument of perigee (deg) | Mean anomaly (deg) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SAT-1 | Plane A | 6891.215 | 7.53\(	imes 10^{-4}\) | 97.70 | 350.984 | 215.913 | 180.0 |
| SAT-2 | Plane A | 6891.215 | 7.53\(	imes 10^{-4}\) | 97.70 | 350.984 | 215.963 | 180.0 |
| SAT-3 | Plane B | 6912.017 | 1.51\(	imes 10^{-3}\) | 97.70 | 350.984 | 35.938 | 0.0 |

## STK Validation
Running `python -m sim.scripts.run_triangle --output-dir artefacts/run_20251101_0803Z_tehran_triangle` regenerates the summary JSON, maintenance CSV, command-window CSV, Monte Carlo catalogue, orbital-element exports, and STK artefacts (`.e`, `.sat`, `.gt`, `.fac`, `.int`). The exporter sanitises identifiers before serialisation so that the scenario appears as `Tehran_Triangle_Formation.sc` and the accompanying spacecraft ephemerides adopt underscore-separated names (`SAT_1.e`, `SAT_2.e`, `SAT_3.e`), avoiding historical import issues. Invoking `python -m sim.scripts.generate_triangle_products artefacts/run_20251101_0803Z_tehran_triangle` immediately refreshes the SVG diagnostics described above, ensuring the STK validation and analytical figure set remain synchronised without manual post-processing.[Ref2][Ref3]

## Maintenance and Responsiveness Assessment
Table 3 summarises the maintenance and responsiveness metrics captured during `run_20251101_0803Z_tehran_triangle`. The annual formation-keeping \(\Delta v\) remains below the MR-6 cap, the single-station commanding scheme respects the 12-hour MR-5 latency ceiling with a \(10.47\,\text{h}\) margin, and all 300 Monte Carlo injection recovery trials satisfy the MR-7 robustness objective. The underlying datasets—`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, and the refreshed SVG plots—are version-controlled under `artefacts/run_20251101_0803Z_tehran_triangle/` and validate directly against STK via the exporter workflow.[Ref2][Ref3]

Table 3 – MR-5 to MR-7 maintenance and responsiveness metrics

| Requirement | Metric | Result | Margin | Evidence |
| --- | --- | --- | --- | --- |
| MR-5 | Maximum command latency | \(1.53\,\text{h}\) | \(10.47\,\text{h}\) margin versus 12-hour limit | `triangle_summary.json` (run_20251101_0803Z_tehran_triangle)[Ref2] |
| MR-6 | Maximum annual formation-keeping \(\Delta v\) | \(14.04\,\text{m/s}\) | \(0.96\,\text{m/s}\) below 15 m/s budget | `maintenance_summary.csv` (run_20251101_0803Z_tehran_triangle)[Ref2] |
| MR-7 | Monte Carlo recovery success rate | 100% over 300 trials; \(p_{95}\) \(\Delta v = 0.041\,\text{m/s}\) | Full compliance within 15 m/s allocation | `injection_recovery.csv` (run_20251101_0803Z_tehran_triangle)[Ref2] |

## References
- [Ref1] D'Amico, S., et al., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
- [Ref2] Formation-Sat Systems Team, *run_20251101_0803Z Tehran Triangle Analytics Campaign*, FS-ANL-006 v1.0, 2025.
- [Ref3] Formation-Sat Systems Team, *Triangle Analytics Plotting Workflow*, FS-ANL-006 App. A, 2025.
- [Ref4] Formation-Sat Systems Team, *Triangle Formation Unit Tests*, FS-TST-004 v1.1, 2025.
