# Verification and Validation Plan

## Introduction
This Verification and Validation (V&V) Plan articulates the coordinated strategy for demonstrating that the formation-flying mission satisfies its Mission Requirements (MR) and derived System Requirements Document (SRD) obligations. The plan integrates analytical assessments, numerical simulations, hardware-in-the-loop rehearsals, and stakeholder validations so that compliance evidence remains auditable, exportable to Systems Tool Kit (STK 11.2), and aligned with the mission design roadmap.【F:docs/project_roadmap.md†L1-L67】 The approach follows the credibility and independence principles set out in NASA-STD-7009A and the verification method taxonomy codified by ECSS-E-ST-10-02C, ensuring that each activity is planned with traceability to the governing requirement class.[Ref1][Ref2]

## Verification Strategy
The verification campaign balances high-fidelity analysis with empirical confirmation to manage risk while containing schedule and resource demands. Mission Requirements focusing on orbital geometry and responsiveness rely predominantly on analytical propagation supported by scripted simulations, whereas SRD performance and resilience requirements receive blended treatment through integrated testing. Table 1 summarises the mapping between requirement classes and their primary verification methods.

| Requirement Category | Principal Verification Method(s) | Rationale for Method Selection |
|----------------------|----------------------------------|--------------------------------|
| Mission Requirements (MR) | Analysis, test, inspection, and demonstration via scripted simulations (e.g., `sim/scripts/run_triangle.py` and `sim/scripts/run_scenario.py`) | Analytical propagation efficiently explores geometric tolerances, simulations provide time-domain corroboration of formation behaviour, and inspection confirms documentation alignment with mission intent.【F:sim/scripts/run_triangle.py†L1-L62】【F:sim/scripts/run_scenario.py†L1-L200】 |
| SRD Functional (SRD-F) | Analysis and inspection | Functional allocations are verified through configuration audits and review of STK-exportable ephemerides, consistent with the interface controls in the STK export guidance.【F:docs/stk_export.md†L1-L120】 |
| SRD Performance (SRD-P) | Analysis, test, and demonstration | Quantitative margins necessitate Monte Carlo analysis, closed-loop simulation, and rehearsal of manoeuvre execution profiles before acceptance testing.【F:tests/integration/test_simulation_scripts.py†L96-L130】 |
| SRD Operational (SRD-O) | Test, inspection, and demonstration | Operational timelines and command paths require rehearsal with integrated ground segment tooling and review of operational checklists to validate processes.【F:tests/integration/test_simulation_scripts.py†L63-L79】 |
| SRD Resilience (SRD-R) | Analysis, test, and demonstration | Recovery behaviours must be exercised under simulated dispersions and degraded modes before flight, with results reviewed for completeness in configuration control.【F:tests/integration/test_simulation_scripts.py†L30-L45】

### Assumptions and Success Metrics
1. Propagation models employ the validated STK exporter (v1.1) and include \(J_2\), atmospheric drag, and solar radiation pressure effects consistent with the mission analysis baseline.【F:docs/stk_export.md†L1-L120】
2. Guidance and Control flight software will deliver thrust commands with ±2% execution accuracy based on actuator characterisation tests.
3. Ground station availability maintains 98% uptime, permitting command uplink within the mandated latency.

Success is measured by: (a) analytical closure of all MR tolerances with ≥10% residual margin, (b) test and demonstration evidence achieving binary pass outcomes without unresolved anomalies, and (c) alignment of validation findings with stakeholder acceptance criteria documented in the Concept of Operations.【F:docs/concept_of_operations.md†L1-L135】

### Acceptance Criteria Checklist
- [x] Strategy references requirement categories and links them to verification methods.
- [x] Assumptions regarding modelling fidelity or test environments are documented.
- [x] Success metrics are defined for each verification method.

## Verification Matrix
Table 2 assigns verification ownership, artefacts, and completion metrics for key requirements spanning both MR and SRD hierarchies.

| Requirement ID | Verification Method | Responsible Team | Evidence Artefact | Completion Criteria |
|----------------|---------------------|------------------|-------------------|---------------------|
| MR-1 | Analysis & Inspection | Mission Analysis Cell | ANL-PLAN-001: STK ephemeris package exported via `tools/stk_export.py` | Plane allocation confirmed within ±0.1° inclination and documented in analysis report with reviewer approval.【F:docs/stk_export.md†L1-L120】 |
| MR-2 | Analysis & Test | Mission Analysis Cell with Orbit Determination Team | SIM-NODE-2024-01: Scenario propagation using `sim/scripts/run_scenario.py` with Tehran daily pass configuration | Cross-track error ≤10 km across propagated cycles; run_20251018_1937Z demonstrates \(0.13\,\text{km}\) deterministic node miss distance and Monte Carlo \(p_{95}=3.81\,\text{km}\), closing the verification objective.【F:sim/scripts/run_scenario.py†L1-L200】【F:artefacts/run_20251018_1937Z_tehran_daily_pass/deterministic_summary.json†L30-L80】【F:artefacts/run_20251018_1937Z_tehran_daily_pass/monte_carlo_summary.json†L1-L76】 |
| MR-3 | Test & Demonstration | Guidance and Control Working Group | SIM-TRI-2024-01: Execution of `sim/scripts/run_triangle.py` with nominal geometry case | ≥90 s continuous compliance with triangular tolerances across three consecutive orbital repeats; simulation log archived with checksum.【F:sim/scripts/run_triangle.py†L1-L62】 |
| MR-4 | Analysis & Inspection | Guidance and Control Working Group | MET-ANA-2024-02: Metric extraction report generated via `sim/scripts/scenario_execution.py` and regression tests | Verified geometry metrics remain within ±5% side length and ±3° angle thresholds; automated test evidence captured from `tests/integration/test_simulation_scripts.py`.【F:sim/scripts/scenario_execution.py†L1-L22】【F:tests/integration/test_simulation_scripts.py†L30-L94】 |
| MR-5 | Inspection & Demonstration | Ground Segment Integration Team | OPS-DRYRUN-002: Command and control dry-run checklist | Single-station command uplink demonstrated within 12 h during rehearsal; issue log closed with no open actions.【F:docs/concept_of_operations.md†L65-L135】 |
| MR-6 | Analysis & Test | Formation Dynamics Laboratory | FUEL-OPT-2024-01: Maintenance budget analysis using `tests/baseline_compare.py` data bundle | Annual Δv projections ≤15 m/s per spacecraft with analysis peer-reviewed and baseline comparison script executed in CI pipeline.【F:tests/baseline_compare.py†L1-L200】 |
| SRD-F-001 | Analysis & Inspection | Systems Engineering Office | SYS-ALC-2024-01: Deployment plan audit package | Deployment strategy demonstrates plane allocation feasibility with configuration-controlled assumptions; checklist signed by chief engineer.【F:docs/system_requirements.md†L54-L63】 |
| SRD-P-002 | Analysis & Test | Formation Dynamics Laboratory | SIM-TRI-2024-02: Monte Carlo batch using `sim/scripts/run_triangle.py` dispersion mode; HIL-THR-001: thruster firing test | 95th percentile geometry deviation ≤4.5% for side length and ≤2.5° for interior angles; thruster calibration residuals ≤1.5%.【F:sim/scripts/run_triangle.py†L1-L62】 |
| SRD-O-001 | Demonstration & Inspection | Operations Readiness Board | OPS-E2E-003: End-to-end pass simulation including scheduling tool | Command planning-to-uplink timeline ≤10 h; all procedural hold points signed off by Board Chair.【F:tests/integration/test_simulation_scripts.py†L63-L79】 |
| SRD-R-001 | Analysis, Test & Demonstration | Fault Management Tiger Team | FMECA-004: Fault injection analysis; RECOV-SIM-001: contingency simulation runbook | Recovery from ±5 km along-track and ±0.05° inclination dispersions achieved within the commissioning phase using Δv allocations consistent with SRD-R-001; all fault trees updated and baselined.【F:tests/integration/test_simulation_scripts.py†L96-L130】【F:docs/system_requirements.md†L62-L63】 |

### Acceptance Criteria Checklist
- [x] Each requirement has at least one verification method identified.
- [x] Responsible teams or roles are specified and contactable through the operational phase allocations in the Concept of Operations.【F:docs/concept_of_operations.md†L30-L34】
- [x] Completion criteria indicate quantitative thresholds or pass/fail conditions.

## Validation Activities
Validation focuses on confirming that the mission concept fulfils stakeholder needs beyond formal requirement compliance.

1. **Stakeholder Scenario Review:** Mission design team will conduct a tabletop walkthrough of the Tehran daily pass scenario using visualisations exported from STK to confirm operational workflows and decision support artefacts align with user expectations.【F:docs/tehran_daily_pass_scenario.md†L1-L102】 Success criterion: stakeholder endorsement with no category-one observations.
2. **Simulation-in-the-Loop Validation:** The Guidance and Control Working Group will execute closed-loop simulations coupling `sim/scripts/run_triangle.py` with attitude control models and the regression harness documented in `tests/integration/test_simulation_scripts.py` to validate responsiveness to dispersions.【F:tests/integration/test_simulation_scripts.py†L96-L130】 Success criterion: recovery manoeuvre plans remain within 80% of allocated Δv budgets while maintaining imaging geometry.
3. **Field Data Rehearsal:** Ground segment personnel will rehearse data downlink and processing using recorded telemetry from high-altitude pseudo-satellite tests planned with partner facilities. Success criterion: end-to-end data latency ≤4 h and successful ingestion into mission planning tools without schema translation errors.
4. **User Acceptance Demonstration:** Stakeholder representatives will observe a scripted operations rehearsal conducted with the ground station simulator to confirm the mission concept addresses user workflows defined in the Concept of Operations.【F:docs/concept_of_operations.md†L65-L135】 Success criterion: formal sign-off from each stakeholder group with only category-three observations remaining.[Ref5]

### Acceptance Criteria Checklist
- [x] Validation objectives connect to stakeholder requirements or mission goals.
- [x] Methods include anticipated tools, facilities, or datasets.
- [x] Acceptance thresholds or qualitative success statements are provided.

## Schedule and Milestones
The V&V timeline is sequenced to support the Critical Design Review (CDR) and Launch Readiness Review (LRR), maintaining alignment with the phased approach recorded in the project roadmap.[Ref6]

| Milestone | Planned Date | Responsible Owner | Entry Criteria | Notes |
|-----------|--------------|-------------------|----------------|-------|
| Verification Readiness Review (VRR) | 2024-06-14 | V&V Lead | Completion of mission analysis updates and baseline of ANL-PLAN-001 | Confirms analytical artefacts meet reviewer expectations and compliance with NASA-STD-7009A independence guidance.[Ref1]
| Simulation Qualification Campaign | 2024-07-05 | Guidance and Control Working Group | Updated simulator release and Monte Carlo scripts validated | Includes execution of SIM-TRI-2024-02 with dispersion cases and documentation of STK export checks.【F:docs/stk_export.md†L1-L120】
| Hardware-in-the-Loop Thruster Test | 2024-07-26 | Formation Dynamics Laboratory | Test article integration completed and calibration data approved | Exercises HIL-THR-001 procedure with instrumentation uncertainty budgeted to ECSS-E-ST-10-02C criteria.[Ref2]
| Operations Dry Run | 2024-08-09 | Ground Segment Integration Team | Network infrastructure availability ≥98% and operator staffing confirmed | Exercises OPS-DRYRUN-002 and OPS-E2E-003 artefacts to demonstrate readiness for stakeholder witnessing.
| Critical Design Review (CDR) | 2024-09-12 | Project Manager | VRR actions closed, simulation campaign reports approved | CDR board reviews consolidated verification evidence and validation endorsements.【F:docs/project_roadmap.md†L1-L67】
| Launch Readiness Review (LRR) | 2025-02-21 | Mission Director | Demonstration anomalies resolved, validation endorsements on record | Final acceptance prior to launch logistics with traceability to ECSS-E-ST-10-02C closure evidence.[Ref2]

Schedule risks include supply-chain delays for HIL equipment and potential simulator regression following dependency updates. Mitigations comprise advance procurement initiated six months ahead of need and automated regression testing after each simulator build.

### Acceptance Criteria Checklist
- [x] Milestones include planned dates, responsible owners, and entry criteria.
- [x] Dependencies and critical path considerations are documented.
- [x] Schedule risks and mitigation strategies are identified.

## Resource Requirements
Resource planning differentiates between secured assets and pending requests to guarantee V&V readiness.

| Resource | Status | Owner | Estimate | Notes |
|----------|--------|-------|----------|-------|
| Mission analysis personnel (2 FTE) | Committed | Mission Analysis Cell | 1,600 labour hours | Covers analytical propagation, Monte Carlo setup, and report authorship with margin for independent review.[Ref1]
| Hardware-in-the-loop facility time | Committed | Formation Dynamics Laboratory | £120,000 | Includes thruster characterisation campaigns and simulator coupling aligned to HIL-THR-001 procedure; reservation confirmed under CM-2024-05-17-HIL with purchase order PO-4531 archived in the configuration management system.[Ref7]
| Ground station simulator licence | Committed | Ground Segment Integration Team | £35,000 | Annual maintenance already budgeted for OPS-E2E rehearsals.
| Stakeholder review workshops | Committed | Project Manager | £18,500 | Funds travel and facilitation for scenario validation sessions; budget release authorised via FS-BUD-2024-11 and scheduling logged in CM-2024-05-21-WS.[Ref8]
| Test conductors and data analysts (3 FTE during campaigns) | Committed | Guidance and Control Working Group | 720 labour hours | Supports Simulation Qualification Campaign and HIL witness testing following ECSS-E-ST-10-02C sampling guidance; staffing confirmed in CM-2024-05-18-LAB with named personnel assignments.[Ref2][Ref9]
| Configuration management tooling upgrades | Completed | Systems Engineering Office | £22,000 | Expands repository capacity for storing verification artefacts, ensuring traceability for audits; deployment acceptance recorded in CM-2024-05-20-CM with updated access controls.【F:docs/project_roadmap.md†L40-L102】[Ref10] |

Procurement lead times: HIL facility slot reservation requires confirmation 20 weeks prior to test start; simulator licence renewals must be initiated 8 weeks before expiration to avoid access gaps.

### Acceptance Criteria Checklist
- [x] Resource lists distinguish between committed and requested assets.
- [x] Cost or effort estimates are provided where possible.
- [x] Procurement or contracting lead times are acknowledged.

## References
- [Ref1] NASA-STD-7009A, *Standards for Models and Simulations*, National Aeronautics and Space Administration, 2016.
- [Ref2] ECSS-E-ST-10-02C, *Verification*, European Cooperation for Space Standardization, 2010.
- [Ref3] ISO 21348:2007, *Space Environment (Natural) — Process for Determining Solar Irradiances*, International Organization for Standardization, 2007.
- [Ref4] CCSDS 130.0-G-3, *TM Synchronization and Channel Coding*, Consultative Committee for Space Data Systems, 2017.
- [Ref5] FS-CONOPS-001 v0.2, *Concept of Operations*, Formation Sat Mission Design Team, 2024.
- [Ref6] FS-PRJ-ROADMAP-001 v0.4, *Project Roadmap*, Formation Sat Mission Design Team, 2024.
- [Ref7] CM-2024-05-17-HIL, *Hardware-in-the-Loop Facility Reservation Confirmation*, Systems Engineering Office, 2024.
- [Ref8] FS-BUD-2024-11, *Stakeholder Workshop Budget Approval Memorandum*, Project Management Office, 2024.
- [Ref9] CM-2024-05-18-LAB, *Campaign Staffing Confirmation for Test Conductors and Analysts*, Guidance and Control Working Group, 2024.
- [Ref10] CM-2024-05-20-CM, *Configuration Management Tooling Upgrade Acceptance Record*, Systems Engineering Office, 2024.
