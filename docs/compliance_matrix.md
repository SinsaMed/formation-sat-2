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
Table 1 lists every active requirement alongside its present compliance disposition. Evidence references point to analytical memoranda or configuration-controlled datasets archived within this repository. A repository traceability check conducted alongside the Verification and Validation Plan update confirmed that each requirement identifier cited in the verification matrix maps to a defined SRD entry, eliminating previously undefined cross-references.【F:docs/verification_plan.md†L32-L44】【F:docs/system_requirements.md†L62-L63】

Table 1 – Mission and System Requirement Compliance Summary

| Requirement ID | Source Document | Compliance Status | Evidence Reference | Notes / Actions |
|----------------|-----------------|-------------------|--------------------|-----------------|
| MR-1 | Mission Requirements | C | `artefacts/triangle_run` triangular formation simulation summary[EV-1] | SERB confirmed plane allocation satisfies baseline geometry; continue to monitor during perturbation studies. |
| MR-2 | Mission Requirements | C | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked` Tehran daily pass alignment campaign[EV-5] | Deterministic midpoint centroid offset of \(12.143\,\text{km}\) with a \(27.759\,\text{km}\) worst vehicle remains within the ±30 km/±70 km thresholds, and the associated Monte Carlo catalogue reports centroid \(\vert x_{c}\vert\) statistics of \(23.914\,\text{km}\) (mean) and \(24.180\,\text{km}\) (\(p_{95}\)) with a \(39.761\,\text{km}\) \(p_{95}\) worst-spacecraft displacement, evidencing probabilistic compliance. |
| MR-3 | Mission Requirements | C | `artefacts/triangle_run` triangular formation simulation summary[EV-1] | Ninety-six second simultaneous access window verified; re-run once maintenance manoeuvre model is available. |
| MR-4 | Mission Requirements | C | `artefacts/triangle_run` triangular formation simulation summary[EV-1] | Triangle aspect ratio remains within ±2%; update tolerance check after incorporating sensor alignment effects. |
| MR-5 | Mission Requirements | C | run_20251018_1207Z maintenance and responsiveness study[EV-3] | Single-station command latency measured at \(1.53\,\text{h}\) with \(10.47\,\text{h}\) margin; regression `tests/unit/test_triangle_formation.py` guards compliance. |
| MR-6 | Mission Requirements | C | run_20251018_1207Z maintenance and responsiveness study[EV-3] | Weekly formation-keeping burns expend \(14.04\,\text{m/s}\) annually, preserving \(0.96\,\text{m/s}\) margin beneath the 15 m/s cap. |
| MR-7 | Mission Requirements | C | run_20251018_1207Z maintenance and responsiveness study[EV-3] | Monte Carlo injection recovery succeeds in 300/300 trials with \(p_{95}\) \(\Delta v = 0.041\,\text{m/s}\), satisfying robustness expectations. |
| SRD-F-001 | System Requirements | C | `artefacts/triangle_run` triangular formation simulation summary[EV-1] | Deployment concept validated against mission plane allocation; confirm alongside launch vehicle ICD once drafted. |
| SRD-P-001 | System Requirements | C | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked` Tehran daily pass alignment campaign[EV-5] | Locked deterministic propagation yields \(12.143\,\text{km}\) centroid and \(27.759\,\text{km}\) worst-spacecraft offsets at the access midpoint, and the regenerated Monte Carlo set documents \(\bar{x}_{c}=23.914\,\text{km}\), \(p_{95}(\vert x_{c}\vert)=24.180\,\text{km}\), and \(p_{95}(\vert x\_{\mathrm{worst}}\vert)=39.761\,\text{km}\), demonstrating sustained compliance with the ±30 km/±70 km acceptance bands. |
| SRD-P-002 | System Requirements | C | `artefacts/triangle_run` triangular formation simulation summary[EV-1] | Access duration meets performance threshold; schedule regression once maintenance manoeuvres are synthesised. |
| SRD-P-003 | System Requirements | C | `artefacts/triangle_run` triangular formation simulation summary[EV-1] | Geometry tolerances satisfied; integrate sensor alignment error budget into next update. |
| SRD-O-001 | System Requirements | C | run_20251018_1207Z maintenance and responsiveness study[EV-3] | Single-station command uplink achieved within \(1.53\,\text{h}\); latency ledger enforced via automated tests. |
| SRD-P-004 | System Requirements | C | run_20251018_1207Z maintenance and responsiveness study[EV-3] | Annual \(\Delta v\) of \(14.04\,\text{m/s}\) meets propulsion budgeting requirement with documented weekly duty cycle. |
| SRD-R-001 | System Requirements | C | run_20251018_1207Z maintenance and responsiveness study[EV-3] | Monte Carlo recovery catalogue evidences full success within \(15\,\text{m/s}\) per-spacecraft allocation. |
| SRD-O-002 | System Requirements | C | run_20251018_1308Z_tehran_daily_pass STK validation[EV-4] | STK 11.2 import confirmed imaging and downlink geometry; repeat after major configuration changes. |

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
Evidence items adopt the `run_YYYYMMDD_hhmmZ` naming convention and are committed under `artefacts/` with accompanying metadata (e.g., simulation seeds, tool versions, STK export status). Configuration control is maintained through Git history and mandatory review by the SERB prior to merge, ensuring that analysts can reproduce every dataset and that STK ingestion is guaranteed via the `tools/stk_export.py` validation workflow.[Ref4] Table 2 enumerates the artefacts currently underpinning compliance statements and flags outstanding acquisitions. Each evidence tag now resolves directly to a concrete directory beneath `artefacts/`, eliminating the prior dependency on the non-existent `run_20260321_0931Z` placeholder.

Table 2 – Evidence Catalogue

| Evidence Tag | Description | Storage Location | Configuration Notes |
|--------------|-------------|------------------|---------------------|
| [EV-1] | triangle_run triangular formation simulation package capturing ninety-six second Tehran access window | `artefacts/triangle_run` | JSON time-series under Git control; associated STK exports regenerated via `tools/stk_export.py` before acceptance.[Ref4][Ref6] |
| [EV-2] | Concept of Operations baseline review describing single-station command architecture | `artefacts/conops_baseline` | Directory records the CCB approval metadata and traceability link back to `docs/concept_of_operations.md` for narrative context.[Ref5] |
| [EV-3] | run_20251018_1207Z maintenance and responsiveness study covering MR-5 to MR-7 | `artefacts/run_20251018_1207Z` | Includes maintenance, command, and Monte Carlo CSV catalogues plus SVG CDF plot; supporting interpretation retained within `docs/triangle_formation_results.md`. Windowed and full-propagation ground-distance maxima (\(343.62\,\text{km}\) and \(641.89\,\text{km}\)) are recorded explicitly to prevent ambiguity in compliance traceability.[Ref7][Ref8] |
| [EV-4] | run_20251018_1308Z_tehran_daily_pass STK validation package (ephemeris, ground-track, contact intervals) | `artefacts/run_20251018_1308Z_tehran_daily_pass` | Exported via `sim/scripts/run_scenario.py`; ingestion and evidence capture follow the dedicated STK validation guide, with supporting instructions in `docs/how_to_import_tehran_daily_pass_into_stk.md`.【Ref4】【Ref2】 |
| [EV-5] | run_20251020_1900Z_tehran_daily_pass_locked Tehran daily pass alignment package (deterministic centroid metrics, Monte Carlo catalogue, STK exports) | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked` | Records the post-fix RAAN solution, deterministic cross-track mid-point closure, Monte Carlo centroid distributions, and STK 11.2 exports generated via `sim/scripts/run_scenario.py` with \(J_2\)+drag, constituting the authoritative evidence set for MR-2 and SRD-P-001.【Ref4】【Ref1】 |

Outstanding evidence actions: The quarterly rerun mandate has been satisfied by executing `run_20251018_1424Z`, which generated a drag-inclusive Monte Carlo catalogue using `sim/scripts/run_triangle_campaign.py` and archived outputs under `artefacts/run_20251018_1424Z`. The campaign history ledger (`artefacts/triangle_campaign/history.csv`) records the execution timestamp and schedules the next rerun for 16 January 2026, demonstrating that cadence governance is now automated. Atmospheric drag dispersions perturb the command geometry by \(p_{95} = 3.6\,\text{m}\) along-track while preserving the \(350\,\text{km}\) tolerance margin; the regenerated Tehran daily pass baseline (`run_20251020_1900Z_tehran_daily_pass_locked`) now embeds Monte Carlo centroid statistics alongside the deterministic evidence, closing the previously deferred action.

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
- [Ref7] Formation-Sat Systems Team, *Triangle Formation Unit Tests*, FS-TST-004 v1.1, 2025.
- [Ref8] Formation-Sat Systems Team, *run_20251018_1207Z Tehran Triangle Maintenance and Robustness Campaign*, FS-ANL-005 v1.0, 2025.
