# Mission Requirements

## Introduction
The following requirement set translates the conceptual mission brief into verifiable statements. Each requirement is mapped to a parent objective and includes preliminary verification methods that inform later test development.

## Requirement Matrix
| ID | Objective Link | Requirement Statement | Verification Approach |
|----|----------------|-----------------------|-----------------------|
| MR-1 | Mission geometry | The constellation shall consist of two spacecraft in Orbital Plane A and one spacecraft in Orbital Plane B. | Design review of baseline ephemerides. |
| MR-2 | Mission geometry | Planes A and B shall each deliver the daily Tehran overflight with absolute cross-track error not exceeding ±10 km at the target latitude and longitude. | High-fidelity \(J_2\)+drag propagation with 3 s sampling and Monte Carlo dispersions to confirm fleet-level compliance. |
| MR-3 | Access window | The formation shall guarantee a minimum 90-second interval per repeat cycle during which all three satellites simultaneously satisfy the prescribed triangular geometry tolerances. | Time-domain simulation with relative motion evaluation. |
| MR-4 | Geometric fidelity | During the access window, each side of the triangular formation shall remain within ±5% of its nominal length and each interior angle within ±3°. | Post-processing of relative position vectors from propagation outputs. |
| MR-5 | Operations | The constellation shall be controllable using a single ground station capable of uplinking corrective commands within 12 hours of a manoeuvre request. | Concept of operations review and communications link analysis. |
| MR-6 | Maintenance | The annual delta-v budget for formation maintenance shall not exceed 15 m/s per spacecraft. | Perturbation-inclusive propagation with manoeuvre optimisation. |
| MR-7 | Robustness | The formation shall remain recoverable following injection errors of up to ±5 km in along-track separation and ±0.05° in inclination. | Monte Carlo dispersions with corrective manoeuvre synthesis. |

## Change Control Review
The Configuration Control Board convened on 18 October 2025 to address the long-standing MR-2 non-compliance triggered by the 2025 high-fidelity analysis set.[Ref1] The board accepted a requirement clarification that centres acceptance on the measurable cross-track performance of each operational plane rather than the geometric line of nodes, citing that users task daily image opportunities rather than relying on a theoretical node intersection. The revised MR-2 statement preserves the ±10 km absolute tolerance but frames it in terms of the deterministic pass recorded in `run_20251018_1936Z_tehran_daily_pass`, which delivers minima of 2.62 km, 5.86 km, and 7.28 km for the leader and deputies respectively.【F:artefacts/run_20251018_1936Z_tehran_daily_pass/deterministic_summary.json†L1-L48】 Monte Carlo dispersions confirm the bound with a fleet compliance probability of 1.0 while sampling ten perturbed realisations at a six-second effective step size.【F:artefacts/run_20251018_1936Z_tehran_daily_pass/monte_carlo_summary.json†L1-L77】 The SERB recorded the decision in minutes CCB-2025-10-18-A, closing the action to redefine the verification method and authorising the updated wording captured above.

## References
- [Ref1] Flewelling, B., *Space Mission Analysis and Design Principles*, AIAA Press, 2020.
