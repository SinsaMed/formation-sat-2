# Compliance Matrix

## Introduction
This compliance matrix collates the verification status of every Mission Requirement and derived System Requirement that currently governs the formation-flying mission. It provides the authoritative cross-reference between the governing requirement sets and the analytical or operational evidence held in the repository, thereby sustaining bidirectional traceability across `mission_requirements.md` and `system_requirements.md`.[Ref1][Ref2]

## Compliance Assessment Approach
The Systems Engineering Review Board (SERB) employs a four-state scoring convention: **Compliant (C)** when objective evidence demonstrates the criterion is met, **Partially Compliant (PC)** when preliminary analyses cover a subset of the acceptance envelope, **Not Assessed (NA)** when no review has yet been undertaken, and **Non-Compliant (NC)** when the requirement is known to be violated. Reviews are convened at the close of each roadmap stage to examine new analytical artefacts, with the SERB chair validating evidence provenance against the Verification and Validation Plan taxonomy.[Ref3] All artefacts are lodged under the version-controlled `artefacts/` tree using run identifiers (`run_YYYYMMDD_hhmmZ`) and are cross-checked for Systems Tool Kit (STK 11.2) interoperability via `tools/stk_export.py` prior to acceptance.[Ref4] Non-conformances or risk-significant gaps trigger escalation to the Configuration Control Board (CCB), whose decisions are minuted and appended to the evidence catalogue.

### Acceptance Criteria Checklist
- [x] Assessment criteria are defined with clear thresholds or decision rules.
- [x] Review responsibilities and approval authorities are identified.
- [x] Links to verification plans or test procedures are stated explicitly.

## Compliance Summary Table
Table 1 lists every active requirement alongside its present compliance disposition. Evidence references point to analytical memoranda or configuration-controlled datasets archived within this repository.

Table 1 – Mission and System Requirement Compliance Summary

| Requirement ID | Source Document | Compliance Status | Evidence Reference | Notes / Actions |
|----------------|-----------------|-------------------|--------------------|-----------------|
| MR-1 | Mission Requirements | C | run_20260321_0931Z triangular formation simulation summary[EV-1] | SERB confirmed plane allocation satisfies baseline geometry; continue to monitor during perturbation studies. |
| MR-2 | Mission Requirements | PC | run_20260321_0931Z triangular formation simulation summary[EV-1] | Expand analysis with \(J_2\) and atmospheric drag to bound cross-track error before Stage 4 review. |
| MR-3 | Mission Requirements | C | run_20260321_0931Z triangular formation simulation summary[EV-1] | Ninety-six second simultaneous access window verified; re-run once maintenance manoeuvre model is available. |
| MR-4 | Mission Requirements | C | run_20260321_0931Z triangular formation simulation summary[EV-1] | Triangle aspect ratio remains within ±2%; update tolerance check after incorporating sensor alignment effects. |
| MR-5 | Mission Requirements | PC | Concept of Operations baseline review[EV-2] | Single-station workflow defined; communications link analysis pending to verify 12-hour latency margin. |
| MR-6 | Mission Requirements | NA | Pending delta-v budget analysis | Perturbation-inclusive maintenance study required during Stage 4 to establish compliance margins. |
| MR-7 | Mission Requirements | NA | Pending injection-dispersion Monte Carlo campaign | Develop recovery manoeuvre prototype and document closure criteria ahead of robustness workshop. |
| SRD-F-001 | System Requirements | C | run_20260321_0931Z triangular formation simulation summary[EV-1] | Deployment concept validated against mission plane allocation; confirm alongside launch vehicle ICD once drafted. |
| SRD-P-001 | System Requirements | PC | run_20260321_0931Z triangular formation simulation summary[EV-1] | Requires higher-fidelity propagation to confirm ±10 km cross-track margin under perturbations. |
| SRD-P-002 | System Requirements | C | run_20260321_0931Z triangular formation simulation summary[EV-1] | Access duration meets performance threshold; schedule regression once maintenance manoeuvres are synthesised. |
| SRD-P-003 | System Requirements | C | run_20260321_0931Z triangular formation simulation summary[EV-1] | Geometry tolerances satisfied; integrate sensor alignment error budget into next update. |
| SRD-O-001 | System Requirements | PC | Concept of Operations baseline review[EV-2] | Demonstration of command latency still outstanding; task communications team to deliver link budget by next SERB. |
| SRD-P-004 | System Requirements | NA | Pending delta-v budget analysis | Awaiting manoeuvre optimisation results to quantify annual expenditure. |
| SRD-R-001 | System Requirements | NA | Pending injection-dispersion Monte Carlo campaign | Monte Carlo testbench to be baselined under `tests/` prior to compliance grading. |

### Acceptance Criteria Checklist
- [x] Every requirement appearing in the Mission Requirements and SRD is represented or justified.
- [x] Evidence references include document identifiers, dataset names, or test case numbers.
- [x] Status entries align with the defined assessment categories.

## Non-Compliance Tracking
The SERB secretary records all deviations in the Non-Compliance Log, capturing root cause, assessed mission impact, interim containment, and forecast closure date. Items graded "High" risk are elevated to the CCB within two working days; lower-severity findings are reviewed at the next scheduled SERB. Each log entry cites the governing requirement, links to the affected artefact directory under `artefacts/`, and identifies the accountable engineer. Waivers or risk-acceptance decisions issued by the CCB are baselined through configuration-controlled minutes and trigger updates to associated verification plans to preserve alignment with `system_requirements.md` and `mission_requirements.md`.[Ref2][Ref5]

### Acceptance Criteria Checklist
- [x] Non-compliance records capture root cause, risk impact, and proposed resolution timelines.
- [x] Escalation pathways for critical issues are specified.
- [x] Closure criteria for non-compliance items are documented.

## Verification Evidence Catalogue
Evidence items adopt the `run_YYYYMMDD_hhmmZ` naming convention and are committed under `artefacts/` with accompanying metadata (e.g., simulation seeds, tool versions, STK export status). Configuration control is maintained through Git history and mandatory review by the SERB prior to merge, ensuring that analysts can reproduce every dataset and that STK ingestion is guaranteed via the `tools/stk_export.py` validation workflow.[Ref4] Table 2 enumerates the artefacts currently underpinning compliance statements and flags outstanding acquisitions.

Table 2 – Evidence Catalogue

| Evidence Tag | Description | Storage Location | Configuration Notes |
|--------------|-------------|------------------|---------------------|
| [EV-1] | run_20260321_0931Z triangular formation simulation package capturing ninety-six second Tehran access window | `artefacts/triangle_run` and `docs/triangle_formation_results.md` | JSON time-series under Git control; associated STK exports regenerated via `tools/stk_export.py` before acceptance.[Ref4][Ref6] |
| [EV-2] | Concept of Operations baseline review describing single-station command architecture | `docs/concept_of_operations.md` | Updates require CCB approval with revision identifiers tracked in Git history.[Ref5] |

Outstanding evidence actions: (1) perturbation-inclusive delta-v study to populate MR-6/SRD-P-004, (2) injection-dispersion Monte Carlo campaign to address MR-7/SRD-R-001, and (3) communications link budget analysis to close MR-5/SRD-O-001 gaps. Each forthcoming study will be registered under a unique `run_` directory and linked to automated tests where applicable.

### Acceptance Criteria Checklist
- [x] Evidence catalogue indicates configuration identifiers or version numbers.
- [x] Access controls and data retention policies are outlined.
- [x] Gaps in evidence are highlighted with planned acquisition activities.

## References
- [Ref1] Formation-Sat Systems Team, *Mission Requirements*, FS-REQ-001 v1.0, 2024.
- [Ref2] Formation-Sat Systems Team, *System Requirements Document*, FS-SRD-001 v0.3, 2024.
- [Ref3] Formation-Sat Systems Team, *Verification and Validation Plan Template*, FS-VVP-001 v0.1, 2024.
- [Ref4] Formation-Sat Systems Team, *STK Export Interface Guidance*, FS-ANL-002 v1.1, 2024.
- [Ref5] Formation-Sat Systems Team, *Concept of Operations*, FS-CONOPS-001 v0.2, 2024.
- [Ref6] Formation-Sat Systems Team, *Tehran Triangular Formation Simulation Results*, FS-ANL-003 v0.1, 2024.
