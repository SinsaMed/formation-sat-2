# Verification and Validation Plan

## Introduction
This Verification and Validation (V&V) Plan articulates the coordinated strategy for demonstrating that the formation-flying mission satisfies its Mission Requirements (MR) and derived System Requirements Document (SRD) obligations. The plan integrates analytical assessments, numerical simulations, hardware-in-the-loop rehearsals, and stakeholder validations so that compliance evidence remains auditable, exportable to Systems Tool Kit (STK 11.2), and aligned with the mission design roadmap.【F:docs/project_roadmap.md†L1-L67】

## Verification Strategy
The verification campaign balances high-fidelity analysis with empirical confirmation to manage risk while containing schedule and resource demands. Mission Requirements focusing on orbital geometry and responsiveness rely predominantly on analytical propagation supported by scripted simulations, whereas SRD performance and resilience requirements receive blended treatment through integrated testing. Table 1 summarises the mapping between requirement classes and their primary verification methods.

| Requirement Category | Principal Verification Method(s) | Rationale for Method Selection |
|----------------------|----------------------------------|--------------------------------|
| Mission Requirements (MR) | Numerical analysis, scripted simulation (e.g., `sim/scripts/run_triangle.py`), and inspection of mission design artefacts | Analytical propagation efficiently explores geometric tolerances, with simulations providing time-domain corroboration of formation behaviour.【F:sim/scripts/run_triangle.py†L1-L160】 |
| SRD Functional (SRD-F) | Analysis and design inspection | Functional allocations are verified through configuration audits and review of STK-exportable ephemerides.【F:docs/stk_export.md†L1-L120】 |
| SRD Performance (SRD-P) | Monte Carlo analysis, hardware-in-the-loop test, and demonstration | Quantitative margins necessitate statistical confirmation and rehearsal of manoeuvre execution profiles. |
| SRD Operational (SRD-O) | End-to-end system test and procedural demonstration | Operational timelines and command paths require rehearsal with integrated ground segment tooling. |
| SRD Resilience (SRD-R) | Monte Carlo dispersions, fault injection test, and demonstration | Recovery behaviours must be exercised under simulated dispersions and degraded modes before flight.

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
| MR-1 | Analysis | Mission Analysis Cell | ANL-PLAN-001: STK ephemeris package exported via `tools/stk_export.py` | Plane allocation confirmed within ±0.1° inclination and documented in analysis report with reviewer approval.
| MR-3 | Simulation | Guidance and Control Working Group | SIM-TRI-2024-01: Execution of `sim/scripts/run_triangle.py` with nominal geometry case | ≥90 s continuous compliance with triangular tolerances across three consecutive orbital repeats; simulation log archived with checksum.
| MR-5 | Inspection & Demonstration | Ground Segment Integration Team | OPS-DRYRUN-002: Command and control dry-run checklist | Single-station command uplink demonstrated within 12 h during rehearsal; issue log closed with no open actions.
| SRD-P-002 | Analysis & Test | Formation Dynamics Laboratory | SIM-TRI-2024-02: Monte Carlo batch using `sim/scripts/run_triangle.py` dispersion mode; HIL-THR-001: thruster firing test | 95th percentile geometry deviation ≤4.5% for side length and ≤2.5° for interior angles; thruster calibration residuals ≤1.5%.
| SRD-O-001 | Demonstration | Operations Readiness Board | OPS-E2E-003: End-to-end pass simulation including scheduling tool | Command planning-to-uplink timeline ≤10 h; all procedural hold points signed off by Board Chair.
| SRD-R-003 | Analysis & Demonstration | Fault Management Tiger Team | FMECA-004: Fault injection analysis; RECOV-SIM-001: contingency simulation runbook | Recovery from ±5 km along-track error achieved with <12 h manoeuvre planning time and Δv ≤14 m/s; all fault trees updated and baselined.

### Acceptance Criteria Checklist
- [x] Each requirement has at least one verification method identified.
- [x] Responsible teams or roles are specified and contactable through the operational phase allocations in the Concept of Operations.【F:docs/concept_of_operations.md†L30-L34】
- [x] Completion criteria indicate quantitative thresholds or pass/fail conditions.

## Validation Activities
Validation focuses on confirming that the mission concept fulfils stakeholder needs beyond formal requirement compliance.

1. **Stakeholder Scenario Review:** Mission design team will conduct a tabletop walkthrough of the Tehran daily pass scenario using visualisations exported from STK to confirm operational workflows and decision support artefacts align with user expectations.【F:docs/tehran_daily_pass_scenario.md†L1-L102】 Success criterion: stakeholder endorsement with no category-one observations.
2. **Simulation-in-the-Loop Validation:** The Guidance and Control Working Group will execute closed-loop simulations coupling `sim/scripts/run_triangle.py` with attitude control models to validate responsiveness to dispersions. Success criterion: recovery manoeuvre plans remain within 80% of allocated Δv budgets while maintaining imaging geometry.
3. **Field Data Rehearsal:** Ground segment personnel will rehearse data downlink and processing using recorded telemetry from high-altitude pseudo-satellite tests planned with partner facilities. Success criterion: end-to-end data latency ≤4 h and successful ingestion into mission planning tools without schema translation errors.

### Acceptance Criteria Checklist
- [x] Validation objectives connect to stakeholder requirements or mission goals.
- [x] Methods include anticipated tools, facilities, or datasets.
- [x] Acceptance thresholds or qualitative success statements are provided.

## Schedule and Milestones
The V&V timeline is sequenced to support the Critical Design Review (CDR) and Launch Readiness Review (LRR).

| Milestone | Planned Date | Responsible Owner | Entry Criteria | Notes |
|-----------|--------------|-------------------|----------------|-------|
| Verification Readiness Review (VRR) | 2024-06-14 | V&V Lead | Completion of mission analysis updates and baseline of ANL-PLAN-001 | Confirms analytical artefacts meet reviewer expectations.
| Simulation Qualification Campaign | 2024-07-05 | Guidance and Control Working Group | Updated simulator release and Monte Carlo scripts validated | Includes execution of SIM-TRI-2024-02 with dispersion cases.
| Operations Dry Run | 2024-08-09 | Ground Segment Integration Team | Network infrastructure availability ≥98% and operator staffing confirmed | Exercises OPS-DRYRUN-002 and OPS-E2E-003 artefacts.
| Critical Design Review (CDR) | 2024-09-12 | Project Manager | VRR actions closed, simulation campaign reports approved | CDR board reviews consolidated verification evidence.
| Launch Readiness Review (LRR) | 2025-02-21 | Mission Director | Demonstration anomalies resolved, validation endorsements on record | Final acceptance prior to launch logistics.

Schedule risks include supply-chain delays for HIL equipment and potential simulator regression following dependency updates. Mitigations comprise advance procurement initiated six months ahead of need and automated regression testing after each simulator build.

### Acceptance Criteria Checklist
- [x] Milestones include planned dates, responsible owners, and entry criteria.
- [x] Dependencies and critical path considerations are documented.
- [x] Schedule risks and mitigation strategies are identified.

## Resource Requirements
Resource planning differentiates between secured assets and pending requests to guarantee V&V readiness.

| Resource | Status | Owner | Estimate | Notes |
|----------|--------|-------|----------|-------|
| Mission analysis personnel (2 FTE) | Committed | Mission Analysis Cell | 1,600 labour hours | Covers analytical propagation, Monte Carlo setup, and report authorship.
| Hardware-in-the-loop facility time | Requested | Formation Dynamics Laboratory | £120,000 | Includes thruster characterisation campaigns and simulator coupling.
| Ground station simulator licence | Committed | Ground Segment Integration Team | £35,000 | Annual maintenance already budgeted for OPS-E2E rehearsals.
| Stakeholder review workshops | Requested | Project Manager | £18,500 | Funds travel and facilitation for scenario validation sessions.

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
