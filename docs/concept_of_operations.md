# Concept of Operations (ConOps)

## Introduction
The Tehran Triad formation mission delivers persistent, multi-angle imaging of the Tehran metropolitan area to support rapid damage assessment, land-surface monitoring, and civil protection planning. This Concept of Operations (ConOps) consolidates the operational drivers identified in the Mission Requirements Document (MRD), with emphasis on MR-5 through MR-7, to guide control centre procedures, ground segment design, and risk management. The narrative focuses on the commissioning, sustained maintenance, and recovery manoeuvres necessary to satisfy the constellation robustness and responsiveness expectations in the crowded low-Earth orbit environment.

## Mission Overview
The mission comprises three 120 kg small satellites launched together into a 550 km sun-synchronous orbit. Two spacecraft (A1 and A2) occupy Orbital Plane A while a third (B1) is phased in Plane B such that their combined ground-tracks converge over Tehran, forming a near-equilateral triangle during daily access windows. The mission purpose is to collect tri-stereo imagery and coherent radar measurements that enable rapid structural change detection across key infrastructure corridors. The constellation will be declared operational once it demonstrates three consecutive daily passes within the ±30 km primary cross-track alignment tolerance (with excursions up to the ±70 km waiver ceiling only under approved dispensations) and delivers calibrated products to end users within four hours of downlink completion.

The launch vehicle inserts the stack into the ascending node corridor aligned with Tehran within the ±30 km primary cross-track tolerance, recognising that excursions up to ±70 km require a formally granted waiver, after which differential drag and low-thrust manoeuvres establish the MR-1 through MR-4 geometry. Success depends on sustaining the single-station commanding architecture of MR-5, reserving delta-v to respect the MR-6 annual cap, and preserving recovery options compatible with MR-7.

### Acceptance Criteria Checklist
- [x] Overview references the latest Mission Requirements and SRD documents.
- [x] Success criteria are expressed in measurable terms linked to stakeholder needs.
- [x] Assumptions about launch, deployment, and commissioning are stated explicitly.

## Operational Objectives
1. Deliver daily tri-stereo optical and radar products over Tehran with geometric fidelity sufficient for 0.5 m change detection accuracy, satisfying MR-4 performance needs of the civil protection authority.
2. Maintain a commanding and telemetry cadence compatible with a single 11 m X-band ground station in Kerman, ensuring corrective manoeuvres are uplinked within 12 hours of request as required by MR-5.
3. Constrain formation-keeping manoeuvres to an annual delta-v expenditure of ≤15 m/s per spacecraft, consistent with MR-6, while maintaining propellant reserves for end-of-life disposal.
4. Provide contingency injection and maintenance strategies capable of recovering from ±5 km along-track and ±0.05° inclination dispersions, ensuring compliance with MR-7.

### Acceptance Criteria Checklist
- [x] Objectives are prioritised and mapped to requirement identifiers where possible.
- [x] Constraints such as communication windows or resource limitations are captured.
- [x] Dependencies on external systems or partners are highlighted.

## Mission Phases
| Phase | Duration | Entry Criteria | Exit Criteria | Key Activities | Responsible Teams |
|-------|----------|----------------|---------------|----------------|-------------------|
| Launch & Early Orbit (LEOP) | L+0 to L+7 days | Successful separation, initial telemetry lock | All spacecraft detumble, power-positive state, and coarse pointing achieved | Acquisition of signal, health checks, deployment of solar arrays, activation of GPS and S-band transceivers | Spacecraft Operations Team (SCOPS) with Launch Support | 
| Formation Establishment | L+7 to L+45 days | LEOP complete, ephemeris knowledge <5 km | Triangular geometry verified over Tehran for three consecutive passes | Differential drag adjustments, along-track phasing burns, inter-satellite link calibration | Guidance, Navigation & Control (GNC), Flight Dynamics Team (FDT) |
| Nominal Imaging Operations | L+45 days to End of Life | Formation tolerance met, payload calibration complete | Mission end declared or transition to Disposal Phase | Daily pass scheduling, data acquisition, X-band downlink via Kerman Ground Station, delta-v budgeting reviews | Mission Planning Team, Payload Operations Centre |
| Contingency Recovery | As required | Geometry excursion beyond MR-4 or injection dispersions identified | Formation returned within MR-4 tolerances and MR-6 delta-v budget maintained | Execution of stored recovery manoeuvre sequences, reassessment of propellant margins, update of contingency checklists | FDT, SCOPS, Anomaly Response Board |
| Disposal | Final 6 months | Propellant margin >5 m/s and regulatory approval | Satellites in compliant disposal orbit with perigee <500 km | Controlled burn planning, passivation, regulatory reporting, final data archive | SCOPS, Compliance Office |

### Acceptance Criteria Checklist
- [x] Each phase includes entry and exit criteria with measurable indicators.
- [x] Critical activities and responsible teams are identified for every phase.
- [x] Contingency triggers and fall-back procedures are noted where applicable.

## Operational Scenarios
### Scenario 1: Daily Tehran Imaging Pass
- **Preconditions:** Formation geometry within MR-4 tolerances; payload thermal conditioning complete; communication windows loaded in Mission Planning System (MPS).
- **Actions:**
  1. Mission Planner generates 24-hour command loads with imaging timelines and downlink allocations.
  2. SCOPS validates command loads against delta-v budget ledger to ensure MR-6 compliance.
  3. Automated uplink executed via Kerman station during morning visibility; confirmation receipt logged within 15 minutes.
  4. Satellites capture synchronised optical and radar data over Tehran access window; onboard processors compress products.
  5. Evening pass downlinks data to Kerman; Ground Data System pushes Level-1B products to Civil Protection Portal within four hours.
- **Expected Outcomes:** Daily situational awareness products archived, operator logbook updated with fuel usage, stakeholders notified of data availability.

### Scenario 2: Formation Excursion Recovery
- **Preconditions:** Relative navigation solution indicates along-track separation drift exceeding MR-4 threshold and trending toward MR-7 limit; propellant margin above 8 m/s.
- **Actions:**
  1. FDT runs Monte Carlo recovery plan leveraging ±5 km robustness envelope described in MR-7.
  2. SCOPS requests approval from Anomaly Response Board; decision recorded within six hours.
  3. Recovery command sequence uploaded during next visibility pass; burn executed autonomously with thrust vector tracking.
  4. Post-manoeuvre assessment compares reconstructed orbit to MR-4 tolerances; additional trim burn scheduled if required.
- **Expected Outcomes:** Formation geometry restored within 24 hours, MR-6 budget updated, lessons learned fed into contingency playbook.

### Scenario 3: Ground Station Outage
- **Preconditions:** Kerman station offline due to scheduled maintenance; predicted to exceed 12-hour commanding window defined by MR-5.
- **Actions:**
  1. Operations Duty Manager triggers backup service agreement with ESA Redu site within 30 minutes of outage notification.
  2. Alternative link budget verified; uplink and downlink windows rescheduled through Network Coordination System.
  3. Command loads re-routed to Redu; spacecraft contact re-established within eight hours.
  4. Post-outage audit reconciles telemetry continuity and verifies no missed delta-v actions.
- **Expected Outcomes:** Commanding latency remains below MR-5 limit, service-level agreement obligations documented, stakeholders informed of restored operations.

### Acceptance Criteria Checklist
- [x] Scenarios include preconditions, step-by-step actions, and expected outcomes.
- [x] Interfaces with ground systems, payload teams, and external stakeholders are described.
- [x] Scenario coverage addresses both nominal and off-nominal situations.

## Ground Segment and Support Infrastructure
The ground segment is anchored by the Tehran Mission Operations Centre (TMOC) and the Kerman X-band station. TMOC hosts the Mission Planning System, Flight Dynamics Facility, and Payload Data Processing Centre. Operator consoles employ role-based access control and integrate cyber monitoring aligned with ISO/IEC 27001 controls. The Kerman station provides dual X-/S-band links with 9.6 Mbps downlink throughput and 100 kbps uplink, ensuring 10-minute daily contact windows satisfy the MR-5 responsiveness metric.

Data handling follows a four-step workflow: acquisition of raw packets at Kerman, Level-0 formatting validated against `tools/stk_export.py` compatibility checklists, Level-1B image generation at TMOC, and dissemination to civil protection partners through the Secure Data Hub. Latency performance is monitored using automated dashboards that flag deviations from the four-hour delivery objective. Support infrastructure includes a 24/7 Duty Console staffed by certified operators, a resilience-tested power and cooling system with N+1 redundancy, and a secure VPN tunnel for remote payload scientist access. Memoranda of understanding with ESA’s Redu station and the Mohammed Bin Rashid Space Centre (MBRSC) provide surge capacity for contingency passes.

### Acceptance Criteria Checklist
- [x] Communication links are characterised with frequency bands, latencies, and availability expectations.
- [x] Data handling workflows describe acquisition, processing, storage, and dissemination steps.
- [x] Support infrastructure requirements (personnel, tools, facilities) are enumerated.

## Risk and Contingency Considerations
Risk governance follows the agency’s three-tier review cycle with weekly monitoring during operations. Table 1 summarises the current operational risk register.

| Risk ID | Description | Cause | Consequence | Probability | Impact | Mitigation | Owner |
|---------|-------------|-------|-------------|-------------|--------|------------|-------|
| R-01 | Loss of single-station commanding capability | Hardware failure at Kerman | Violates MR-5 commanding latency | Medium | High | Maintain Redu and MBRSC cross-support agreements, execute quarterly end-to-end tests | Ground Segment Lead |
| R-02 | Excessive delta-v consumption during recovery | Inaccurate manoeuvre execution | Breach of MR-6 annual budget | Low | High | Implement closed-loop burn calibration and monthly propellant trending reviews | Flight Dynamics Lead |
| R-03 | Injection dispersions beyond planned envelope | Launch vehicle performance variability | Extended formation recovery timeline challenging MR-7 robustness | Medium | Medium | Pre-load extended recovery sequences, retain 20% propellant margin, rehearse dispersions in high-fidelity simulator | Mission Manager |
| R-04 | Cyber intrusion on TMOC network | Sophisticated phishing campaign | Loss of command authority, data integrity risk | Low | High | Enforce ISO/IEC 27001 controls, conduct quarterly penetration tests, maintain incident response playbooks | Cybersecurity Officer |
| R-05 | STK export incompatibility of processed ephemerides | Software regression in data pipeline | Delayed handover to analysis teams | Low | Medium | Run nightly validation against `tools/stk_export.py`, maintain change control board approvals | Data Systems Lead |

Contingency strategies prioritise maintaining MR-5 to MR-7 compliance. Recovery playbooks define decision thresholds: if predicted commanding latency exceeds 10 hours, backup stations are activated; if propellant margins fall below 6 m/s, payload duty cycles are reduced to conserve delta-v; if formation angle deviations exceed MR-4 limits for more than two passes, the Anomaly Response Board convenes to authorise recovery burns. Disposal contingencies include passive aerodynamic drag augmentation should active propulsion become unavailable, ensuring regulatory deorbit timelines remain satisfied.

### Acceptance Criteria Checklist
- [x] Risks are ranked using a qualitative or quantitative scale.
- [x] Mitigation actions are tied to responsible owners and decision timelines.
- [x] Contingency plans reference relevant procedures, checklists, or external support agreements.

## References
- [Ref1] NASA, *Systems Engineering Handbook*, NASA/SP-2016-6105 Rev2, 2016.
- [Ref2] Wertz, J. R., Everett, D. F., Puschell, J. J. (eds.), *Space Mission Engineering: The New SMAD*, Microcosm Press, 2011.
- [Ref3] European Space Agency, *Ground Station Operations Manual*, ESA-GSOP-OPS-MAN-001, 2021.
- [Ref4] International Organisation for Standardisation, *ISO/IEC 27001:2022 Information security, cybersecurity and privacy protection — Information security management systems*, ISO, 2022.
