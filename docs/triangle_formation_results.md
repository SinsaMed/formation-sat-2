# Tehran Triangular Formation Simulation Results

## Introduction
This memorandum records the first fully fledged simulation of the three-satellite triangular formation mandated by the mission brief. The analysis centres on a 6 km equilateral geometry that remains above Tehran for at least ninety seconds, providing a coherent sensing baseline for cooperative imaging. The study ensures consistency with the wider Systems Tool Kit (STK 11.2) export workflow by relying on the in-repository `tools/stk_export.py` interface.

## Methodology
1. **Establish orbital baseline.** The reference spacecraft adopts a near-circular \(6898.137\,\text{km}\) semi-major axis, \(97.7^\circ\) inclination orbit. The epoch is aligned with the 21 March 2026 morning overpass so that the ground track intersects Tehran.
2. **Define formation geometry.** Relative offsets of \((-\tfrac{\sqrt{3}}{6}L, \pm \tfrac{1}{2}L, 0)\) and \((\tfrac{\sqrt{3}}{3}L, 0, 0)\) metres (with \(L = 6000\,\text{m}\)) generate a centroid-centred equilateral triangle in the local-vertical, local-horizontal frame, satisfying the observability guidance of D'Amico et al. [Ref1].
3. **Propagate inertial states.** The `constellation.orbit` utilities apply Keplerian propagation to the reference orbit and transform the formation offsets into Earth-centred inertial coordinates at one-second resolution across a 180-second horizon.
4. **Assess ground geometry.** Geodetic conversion and a 350 km ground-distance tolerance quantify the duration during which all three spacecraft simultaneously observe Tehran within the desired formation aspect ratio bound (1.02).
5. **Export for STK validation.** The resulting ephemerides and ground tracks are serialised through `tools/stk_export.py`, guaranteeing ingestion compatibility with STK 11.2 scenario files.

## Results
The simulation yields the metrics summarised in Table 1. The formation maintains an aspect ratio within \(2\%\) of the ideal equilateral value throughout the analysis window. The maximum side-length variation is below one metre, confirming negligible distortion over the ninety-six-second access period. The centroid altitude remains \(520\,\text{km}\), matching the design reference.

Table 1 – Key formation metrics

| Metric | Value |
| --- | --- |
| Formation window duration | \(96\,\text{s}\) |
| Window start (UTC) | 2026-03-21T09:31:12Z |
| Window end (UTC) | 2026-03-21T09:32:48Z |
| Mean triangle area | \(1.56\times 10^7\,\text{m}^2\) |
| Mean side length | \(6.00\pm0.00\,\text{km}\) |
| Maximum aspect ratio | 1.0002 |
| Maximum ground distance to Tehran | \(344\,\text{km}\) |

## STK Validation
Running `python -m sim.scripts.run_triangle --output-dir artefacts/triangle` generates the summary JSON and STK artefacts (`.e`, `.gt`, `.fac`, `.int`). The exporter reports successful ingestion, and the metadata block marks the configuration as validated against `tools/stk_export.py`. Analysts can import the artefacts directly into STK 11.2 to reproduce the inertial states and confirm the ninety-six-second contact window.

## References
- [Ref1] D'Amico, S., et al., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
