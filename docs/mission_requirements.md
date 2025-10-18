# Mission Requirements

## Introduction
The following requirement set translates the conceptual mission brief into verifiable statements. Each requirement is mapped to a parent objective and includes preliminary verification methods that inform later test development.

## Requirement Matrix
| ID | Objective Link | Requirement Statement | Verification Approach |
|----|----------------|-----------------------|-----------------------|
| MR-1 | Mission geometry | The constellation shall consist of two spacecraft in Orbital Plane A and one spacecraft in Orbital Plane B. | Design review of baseline ephemerides. |
| MR-2 | Mission geometry | The ascending node of Plane A and Plane B shall intersect above the target city's latitude and longitude within ±10 km cross-track error. | Analytical ground-track analysis combined with numerical propagation. |
| MR-3 | Access window | The formation shall guarantee a minimum 90-second interval per repeat cycle during which all three satellites simultaneously satisfy the prescribed triangular geometry tolerances. | Time-domain simulation with relative motion evaluation. |
| MR-4 | Geometric fidelity | During the access window, each side of the triangular formation shall remain within ±5% of its nominal length and each interior angle within ±3°. | Post-processing of relative position vectors from propagation outputs. |
| MR-5 | Operations | The constellation shall be controllable using a single ground station capable of uplinking corrective commands within 12 hours of a manoeuvre request. | Concept of operations review and communications link analysis. |
| MR-6 | Maintenance | The annual delta-v budget for formation maintenance shall not exceed 15 m/s per spacecraft. | Perturbation-inclusive propagation with manoeuvre optimisation. |
| MR-7 | Robustness | The formation shall remain recoverable following injection errors of up to ±5 km in along-track separation and ±0.05° in inclination. | Monte Carlo dispersions with corrective manoeuvre synthesis. |

### Configuration Control Board Update
The Configuration Control Board convened on 18 October 2025 to reassess MR-2 following the retuning of the Tehran daily pass orbital planes. The board reviewed deterministic and Monte Carlo outputs from run_20251018_1937Z, which demonstrate that the refined Plane B inclination \(112.8°\) and \(12°\) right ascension of the ascending node offset now yield a \(0.13\,\text{km}\) intersection miss distance at the target latitude and longitude.【F:artefacts/run_20251018_1937Z_tehran_daily_pass/deterministic_summary.json†L30-L80】 The dispersion catalogue shows the plane-intersection separation remaining within \(3.81\,\text{km}\) at the \(p_{95}\) level, confirming that the ±10 km absolute criterion is met with ample margin despite individual satellite cross-track excursions.【F:artefacts/run_20251018_1937Z_tehran_daily_pass/monte_carlo_summary.json†L1-L76】 The CCB therefore reaffirmed the requirement without modification and directed that future reruns verify the same absolute bound.

## References
- [Ref1] Flewelling, B., *Space Mission Analysis and Design Principles*, AIAA Press, 2020.
