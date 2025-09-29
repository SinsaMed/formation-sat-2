# Final Delivery Manifest

## Introduction
This manifest consolidates the artefacts that deliver the Tehran triangular-formation demonstration. The repository now provides a reproducible simulation pipeline, documented evidence of the ninety-six-second access window above Tehran, and Systems Tool Kit (STK 11.2) exports validated through the in-repository tooling. The material enumerated below forms the baseline package for handover to downstream mission analysis and operations teams.

## Executive Summary
1. The equilateral formation maintains \(6\,\text{km}\) side lengths while overflying Tehran for \(96\,\text{s}\), exceeding the \(90\,\text{s}\) requirement with margin.[Ref1]
2. Orbital element reconstruction confirms two spacecraft remain in Plane A while the third occupies Plane B, preserving the mission geometry assumptions used for manoeuvre planning.[Ref1]
3. The STK export pathway has been exercised end-to-end via `tools/stk_export.py`, ensuring interoperability with STK 11.2 scenario ingestion workflows.[Ref2]

## Deliverable Register
| Item | Description | Location |
| --- | --- | --- |
| Scenario configuration | JSON definition of the Tehran triangular formation, including plane assignments and geometric tolerances. | `config/scenarios/tehran_triangle.json` |
| Simulation engine | Python module implementing the Keplerian propagation, geometric assessment, and STK export orchestration. | `sim/formation/triangle.py` |
| Analytical report | Documented simulation outcomes, formation metrics, and orbital element reconstruction tables. | `docs/triangle_formation_results.md` |
| Automation entry point | Command-line tool that triggers the simulation and produces the STK-compatible artefacts. | `sim/scripts/run_triangle.py` |
| Verification test | PyTest case that enforces the \(\geq 90\,\text{s}\) access window and plane-allocation logic. | `tests/unit/test_triangle_formation.py` |

## Reproduction Procedure
1. Execute `make setup` followed by `make triangle` from the repository root to generate the summary JSON and STK directory under `artefacts/triangle/`.
2. Inspect `artefacts/triangle/triangle_summary.json` to confirm the recorded formation window and orbital element metrics.
3. Launch STK 11.2 and import the exported ephemerides, ground tracks, and interval lists located in `artefacts/triangle/stk/` to visualise the Tehran pass.
4. Run `pytest tests/unit/test_triangle_formation.py` to verify that future modifications preserve the \(\geq 90\,\text{s}\) requirement and plane allocation schema.

## References
- [Ref1] `docs/triangle_formation_results.md`.
- [Ref2] `docs/stk_export.md`.
