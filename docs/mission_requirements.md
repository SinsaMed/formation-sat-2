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

## References
- [Ref1] Flewelling, B., *Space Mission Analysis and Design Principles*, AIAA Press, 2020.
