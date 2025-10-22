# Project Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Preface
This project prompt codifies the expectations, evidence pathways, and research scaffolding necessary to expand the "Formation Satellite Programme Phase 2" dossier into a comprehensive scholarly manuscript. It harmonises the repository's configuration-controlled artefacts, simulation stack, and verification doctrine so that subsequent writing, analysis, and literature synthesis remain traceable to the Tehran-centred triangular formation case study while generalising to other mid-latitude targets.[Ref1][Ref2][Ref10]

### Purpose of This Prompt
- Provide a single reference blueprint for authoring chapters that interleave literature review, analytical derivations, simulation evidence, and operational doctrine.
- Enumerate explicit research prompts covering theoretical groundwork, applied modelling, validation against Systems Tool Kit (STK) 11.2, and post-analysis reflection.
- Embed mission assurance artefacts (run identifiers, configuration files, tests) within the writing workflow so that every claim cites reproducible data products.[Ref5][Ref7][Ref9]
- Maintain alignment with the Systems Engineering Review Board (SERB) governance model, ensuring compliance statements, maintenance metrics, and robustness margins draw from the curated run ledger.[Ref5][Ref20]

### Using This Document
1. Treat each chapter as a mandatory deliverable. Do not omit sections even if certain evidence requires future work; instead, articulate outstanding tasks using the provided prompts.
2. For literature review expansions, prefer peer-reviewed sources (2019–2025) unless foundational texts pre-date this window. Cite standards (NASA-STD-7009A, ECSS-E-ST-10-02C), mission design treatises, and authoritative agency handbooks when bridging simulation outputs to operational doctrine.[Ref20]
3. When referencing repository artefacts, state the run identifier, file path, and relevant metric; confirm that the artefact resides in the authoritative ledger (`docs/_authoritative_runs.md`).[Ref9]
4. Maintain British English spelling and adopt an academic yet accessible tone. Interleave narrative exposition with numbered procedures, prompts, and data tables as instructed in `AGENTS.md`.
5. Update the References section if new artefacts or external works are introduced. Preserve numbering consistency across editions to avoid ambiguity for reviewers.

### Document Navigation
- **Chapter 1**: Mission framing, requirement lineage, and literature prompts.
- **Chapter 2**: Configuration baselines and geometric design constructs.
- **Chapter 3**: Simulation pipeline, toolchain narrative, and data engineering workflows.
- **Chapter 4**: Authoritative run evidence, maintenance analytics, and robustness catalogues.
- **Chapter 5**: Results interpretation, cross-target adaptation, and discussion triggers.
- **Chapter 6**: Conclusions, strategic recommendations, and future research arcs.
- **Chapter 7**: Appendices covering reproduction procedures, data governance, and writing templates.

Use the embedded "Prompt" blocks within each section to direct writing tasks. Each prompt may be executed multiple times as evidence deepens; record completion dates within your working log for configuration control.

---

## Chapter 1 – Mission Framing and Literature Review Foundations

### 1.1 Mission Context Recapitulation
Summarise the mission intent as presented in the repository README and Project Overview, emphasising the dual-plane constellation architecture, the daily 90-second equilateral formation above Tehran, and the requirement for repeatability under low Earth orbit perturbations.[Ref1][Ref2]

**Prompt 1.1A – Executive Synopsis**
Produce a 500-word narrative that contextualises the Tehran use case within wider mid-latitude resilience missions, explicitly connecting stakeholder objectives, formation geometry, and the 90-second access requirement. Anchor statements to MR-1 through MR-4 and SRD performance clauses.[Ref3][Ref4]

**Prompt 1.1B – Stakeholder Mapping Table**
Create a table mapping primary stakeholders (civil protection authority, formation dynamics laboratory, ground segment integration team) to mission objectives, requirement identifiers, and operational needs. Reference the Concept of Operations and Compliance Matrix to substantiate responsibility assignments.[Ref5][Ref21]

### 1.2 Historical and Contemporary Literature Themes
Develop a literature review strategy that weaves together formation flying theory, multi-plane constellation management, and responsive ground operations. Use the following thematic clusters as anchors:

1. **Relative Orbital Elements (ROE) and Formation Geometry** – highlight core papers (e.g., D'Amico et al. 2005) and recent advances in transient LVLH triangle shaping. Analyse how ROE-based control laws support the near-equilateral design described in the simulation outputs.[Ref7]
2. **Mid-Latitude Disaster Response Constellations** – survey missions employing multi-angle imaging for infrastructure resilience, emphasising revisit strategies and cross-track tolerance management comparable to the ±30 km/±70 km envelope.[Ref8]
3. **Single-Station Command Architectures** – examine ground segment reliability literature, focusing on command latency guarantees within 12 hours and contingency agreements (e.g., ESA Redu). Relate findings to MR-5 and SRD-O-001 compliance evidence.[Ref5][Ref21]
4. **Maintenance and Robustness Under Perturbations** – assess delta-v budgeting methodologies, drag modulation techniques, and Monte Carlo dispersion recovery frameworks that parallel the repository's maintenance and robustness study.[Ref7][Ref23]

**Prompt 1.2A – Literature Matrix**
Construct a literature matrix listing at least ten sources per thematic cluster. For each entry, document publication year, method type (analytical, experimental, operational), relevance to mission requirements, and anticipated chapter integration point. Note any standards (NASA-STD-7009A, ECSS-E-ST-10-02C) or agency manuals that must be cited when discussing verification credibility.[Ref20]

**Prompt 1.2B – Gap Identification Essay**
Write a 700-word essay isolating knowledge gaps the existing repository evidence does not yet close (e.g., long-term drag modelling beyond 12 orbits, integration of optical payload calibration into geometry tolerances). Justify why these gaps necessitate further literature review or new simulation campaigns, and propose how upcoming roadmap milestones might address them.[Ref6][Ref20]

### 1.3 Requirement Traceability Narrative
Trace each Mission Requirement (MR-1 to MR-7) to its supporting System Requirements and evidence artefacts.

**Prompt 1.3A – Traceability Diagram Description**
Describe (500 words) a SysML-style requirement diagram linking mission objectives, MR identifiers, SRD derivatives, and evidence tags [EV-*] from the Compliance Matrix.[Ref5] Emphasise how configuration control ensures the ledger remains synchronised with analytical outputs.

**Prompt 1.3B – Requirement Compliance Commentary**
For each MR, provide a 250-word commentary summarising current compliance status, evidence source (run identifier and artefact), residual risk, and future verification tasks. Reference the Verification Plan for planned validation activities or outstanding hardware-in-the-loop exercises.[Ref5][Ref20]

### 1.4 Research Ethics and Data Governance Considerations
Discuss ethical, regulatory, and data governance constraints relevant to publishing mission analysis content, including export control sensitivities, data retention policies, and configuration management responsibilities documented in the roadmap and verification plan.[Ref6][Ref20]

**Prompt 1.4A – Ethics Statement Draft**
Draft a 300-word ethics statement outlining how data (ephemerides, contact logs, Monte Carlo outputs) will be handled to protect mission integrity while enabling academic dissemination. Reference the data retention periods and checksum policies specified in `config/project.yaml` and `docs/compliance_matrix.md`.

**Prompt 1.4B – Configuration Management Checklist**
Create a numbered checklist for authors to confirm prior to publication, ensuring run identifiers are registered, STK validation status is documented, and evidence conforms to repository naming conventions.[Ref9][Ref17]

---

## Chapter 2 – Configuration Baselines and Geometric Design Constructs

### 2.1 Programme Configuration Snapshot
Summarise the project-wide constants recorded in `config/project.yaml`, including gravitational parameters, nominal altitude, window targets, and propulsion characteristics. Explain how these constants constrain scenario design and maintenance modelling.[Ref10]

**Prompt 2.1A – Configuration Exegesis**
Write a detailed exposition (600 words) explaining how each global constant (Earth model, nominal altitude, transponder band, propulsion budget) influences simulation parameterisation and requirement satisfaction. Connect propulsion reserves to the annual delta-v ceilings evidenced by `run_20251018_1207Z`.

**Prompt 2.1B – Configuration Change Impact Table**
Construct a table evaluating hypothetical updates to `config/project.yaml` (e.g., enabling solar radiation pressure modelling, modifying Monte Carlo sample count). For each change, predict its effect on formation geometry, maintenance budgets, and verification scope.

### 2.2 Scenario Definitions and Geometric Parameters
Detail the machine-readable scenarios for the Tehran triangle (`config/scenarios/tehran_triangle.json`) and Tehran daily pass (`config/scenarios/tehran_daily_pass.json`), emphasising epoch selection, plane allocations, target coordinates, and Monte Carlo settings.[Ref11][Ref12]

**Prompt 2.2A – Scenario Narrative**
Compose a narrative comparing the triangle and daily pass scenarios, highlighting how the LVLH offsets translate into classical elements, how the RAAN alignment solver locks the centroid within ±30 km, and how command geometry is parameterised for the Kerman station.

**Prompt 2.2B – Parameter Sensitivity Analysis**
Identify the parameters within the scenario files that most strongly affect access window duration and centroid compliance (e.g., `time_step_s`, `ground_tolerance_km`, `contact_range_km`). Outline an experimental plan to vary each parameter, referencing the simulation scripts that must be exercised to observe impacts.[Ref13][Ref14]

### 2.3 Geometric Foundations and Relative Motion Constructs
Explain the mathematical formulation of the equilateral LVLH triangle, referencing the transformation pipeline from relative offsets to inertial states implemented in `sim/formation/triangle.py` and `src/constellation/orbit.py`.[Ref13][Ref24]

**Prompt 2.3A – Derivation Essay**
Derive the conversion from the LVLH offsets \((-\tfrac{\sqrt{3}}{6}L, \pm \tfrac{1}{2}L, 0)\) to Earth-centred inertial positions, detailing how `_lvlh_frame` establishes the basis and how Keplerian propagation maintains geometry across the 180-second horizon. Integrate references to `mean_to_true_anomaly`, `propagate_kepler`, and `cartesian_to_classical` routines.[Ref13]

**Prompt 2.3B – Geometry Validation Plan**
Outline a validation plan using `tests/unit/test_triangle_formation.py` to ensure future modifications preserve triangle integrity. Discuss additional metrics (e.g., area variance, centroid altitude stability) that may warrant new regression tests.

### 2.4 Command and Communications Geometry
Interpret the command latency model derived from Kerman station geometry (latitude 30.283° N, longitude 57.083° E, 2200 km contact range). Explain how `_analyse_command_latency` translates ground station geometry into latency metrics and how the single-station architecture influences operations.[Ref13][Ref23]

**Prompt 2.4A – Communications Analysis**
Produce a 400-word analysis connecting the computed contact probability (≈0.0316) and maximum latency (1.53 h) to MR-5 compliance, including discussion of fallback arrangements documented in the Concept of Operations.[Ref21][Ref23]

**Prompt 2.4B – Contingency Scenario Proposal**
Design a contingency scenario where the primary station is unavailable for 18 hours. Detail which configuration parameters must change, how to document the deviation in the Compliance Matrix, and which literature sources should be consulted to justify backup station engagement.

---

## Chapter 3 – Simulation Pipeline, Toolchain, and Data Engineering

### 3.1 Simulation Architecture Overview
Summarise the simulation architecture covering `sim/scripts/run_triangle.py`, `sim/scripts/run_scenario.py`, `run.py`, and `run_debug.py`. Clarify how the command-line tools, FastAPI service, and debug utilities interact with the artefact directories (`artefacts/triangle`, `artefacts/web_runs`).[Ref13][Ref14]

**Prompt 3.1A – Pipeline Narrative**
Draft a 700-word narrative describing the end-to-end pipeline from scenario configuration through to STK export, referencing each script's role, the stage sequence logged in scenario runs, and the debug instrumentation available for analysts.

**Prompt 3.1B – Stage Sequence Table**
Construct a table enumerating each pipeline stage (configuration load, RAAN sweep, propagation, metric extraction, STK export), the responsible script/module, key inputs/outputs, and validation hooks (unit tests, integration tests, manual review checkpoints).

### 3.2 Artefact Management and Naming Conventions
Explain the `run_YYYYMMDD_hhmmZ` naming pattern, artefact directory structures, and metadata captured in summary JSON files. Reference the Final Delivery Manifest for reproduction procedure expectations.[Ref9][Ref19]

**Prompt 3.2A – Artefact Ledger Commentary**
Write a commentary linking each artefact type (summary JSON, maintenance CSV, STK directory, Monte Carlo catalogue) to its downstream use (compliance evidence, figure generation, STK validation). Highlight how the ledger prevents inadvertent citation of non-baseline runs.

**Prompt 3.2B – Metadata Quality Checklist**
Develop a checklist to verify metadata completeness after each run, including presence of epoch timestamps, solver settings, STK export flags, and references to configuration sources.

### 3.3 STK Export Workflow
Detail the exporter interface defined in `tools/stk_export.py`, the expected TEME frame inputs, file outputs (`.e`, `.sat`, `.gt`, `.fac`, `.int`, `.evt`), and sanitisation of object names.[Ref15][Ref17]

**Prompt 3.3A – Export Procedure Description**
Describe step-by-step how simulation outputs are converted into STK-compatible artefacts, referencing the exporter data classes (`StateSample`, `PropagatedStateHistory`, `GroundTrack`, etc.) and the integration tests safeguarding file structure.[Ref15][Ref17]

**Prompt 3.3B – Validation Log Template**
Draft a template for logging STK validation sessions, capturing import steps, anomalies, corrective actions, and screenshots. Ensure the template references the STK validation guide and emphasises storage of SVG evidence within run directories.[Ref17][Ref22]

### 3.4 Testing and Continuous Integration Coverage
Summarise the existing tests (`tests/unit/test_triangle_formation.py`, `tests/test_stk_export.py`, integration scripts) and describe how they enforce compliance with mission metrics and exporter integrity.[Ref16][Ref17]

**Prompt 3.4A – Regression Coverage Report**
Compose a 600-word report assessing current regression coverage, identifying scenarios not yet captured by automated tests (e.g., drag dispersion validation, RAAN optimiser regression). Recommend new test cases and specify their intended location within the `tests/` hierarchy.

**Prompt 3.4B – Continuous Integration Narrative**
Explain how the Makefile targets (`make simulate`, `make triangle`, `make scenario`, `make docs`) align with GitHub Actions workflows. Suggest enhancements to the CI pipeline to include Monte Carlo distribution checks or STK export diffing.

### 3.5 Interactive Execution Interface
Describe the FastAPI-based interactive runner, job management, and artefact streaming (logs, metrics, visualisations) documented in `docs/interactive_execution_guide.md` and implemented in `run.py`.[Ref18][Ref21]

**Prompt 3.5A – User Guide Expansion**
Extend the interactive execution guide with detailed instructions for remote analysts, including VPN considerations, concurrent job handling, and archive rotation policies for `artefacts/web_runs`.

**Prompt 3.5B – Telemetry Audit Plan**
Design an audit plan ensuring telemetry outputs (debug logs, JSONL run logs, Plotly exports) remain consistent with configuration-controlled datasets. Specify when to snapshot `run_log.jsonl` into the compliance evidence chain.

---

## Chapter 4 – Authoritative Runs and Quantitative Evidence Synthesis

### 4.1 Run Ledger Interpretation
Analyse the authoritative runs recorded in `docs/_authoritative_runs.md`, focusing on `run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`, and associated exploratory reruns. Explain how each run underpins specific compliance statements.[Ref7][Ref8][Ref9]

**Prompt 4.1A – Run Dossier Summaries**
Prepare one-page summaries for each authoritative run, detailing objectives, key metrics (duration, centroid offsets, maintenance budgets, success rates), and STK validation status. Use bullet points to list artefact paths and highlight any unique considerations (e.g., windowed vs full-propagation maxima).

**Prompt 4.1B – Evidence Trace Table**
Create a table linking Mission/System Requirements to run identifiers, metrics, and regression tests. Include columns for metric values, compliance margins, and references to relevant documentation sections (e.g., `docs/triangle_formation_results.md`).

### 4.2 Tehran Triangle Maintenance and Robustness Campaign (`run_20251018_1207Z`)
Document the metrics captured in `triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, and `injection_recovery_cdf.svg`.

**Prompt 4.2A – Metrics Interpretation Essay**
Analyse the 96-second window, maximum aspect ratio (≈1.00000000000018), command latency (1.53 h), and aggregate delta-v statistics (mean 0.0263 m/s, p95 0.0412 m/s). Discuss how these values satisfy MR-3 through MR-7 and inform maintenance doctrine.[Ref7][Ref23]

**Prompt 4.2B – Figure Development Plan**
Plan figures illustrating (a) centroid ground-distance profile (highlighting 343.62 km within the 96 s window vs 641.89 km full propagation), (b) delta-v cumulative distribution, and (c) command latency histogram. Specify data sources and intended chapter placements.

### 4.3 Tehran Daily Pass Alignment Campaign (`run_20251020_1900Z_tehran_daily_pass_locked`)
Summarise deterministic and Monte Carlo outputs ensuring centroid cross-track alignment and waiver compliance.

**Prompt 4.3A – Deterministic Geometry Commentary**
Interpret the deterministic midpoint metrics (centroid 12.1428 km, worst vehicle 27.7595 km) relative to the ±30 km/±70 km tolerances. Explain how node/phases metadata, orbital period (5679.47 s), and access windows feed into operations planning.[Ref8][Ref24]

**Prompt 4.3B – Monte Carlo Dispersion Analysis**
Evaluate the Monte Carlo summary (centroid mean 23.914 km, p95 24.180 km; worst vehicle p95 39.761 km) and its implications for requirement robustness, contingency planning, and reporting in the Compliance Matrix.[Ref8][Ref25]

### 4.4 Exploratory Reruns and Drag Dispersion Campaigns
Discuss the role of exploratory runs (`run_20260321_0740Z_tehran_daily_pass_resampled`, `artefacts/triangle_campaign`) in validating methodological updates and drag dispersion effects.

**Prompt 4.4A – Methodology Comparison Essay**
Compare baseline runs with exploratory reruns, focusing on parameter adjustments, resampling strategies, and drag dispersion outcomes (e.g., p95 along-track shift 3.6 m). Explain how these datasets should be cited as non-baseline supporting evidence.[Ref9]

**Prompt 4.4B – Future Campaign Proposal**
Propose a future analysis campaign targeting solar radiation pressure effects or extended planning horizons. Detail required configuration changes, anticipated metrics, and documentation updates.

### 4.5 Data Integrity and Cross-Validation
Outline procedures for verifying data integrity across artefacts, including checksum verification, metadata consistency, and cross-checks against STK imports.

**Prompt 4.5A – Integrity Audit Checklist**
Create a checklist ensuring triangle and daily pass artefacts remain internally consistent (matching epochs, plane allocations, metric reproducibility). Include STK ingestion checks and regression test confirmations.

**Prompt 4.5B – Cross-Validation Narrative**
Write a narrative describing how to cross-validate Python-derived metrics with STK analyses, emphasising the need to reconcile frame assumptions (TEME) and to document any discrepancies.

---

## Chapter 5 – Results Interpretation, Discussion, and Cross-Target Adaptation

### 5.1 Formation Performance Discussion
Interpret the simulation results in light of mission objectives, focusing on geometric fidelity, access duration, and centroid control.

**Prompt 5.1A – Performance Narrative**
Compose a 900-word discussion linking triangle stability, centroid ground distance, and maintenance margins to stakeholder outcomes (e.g., tri-stereo imaging quality). Reference the Concept of Operations to tie performance metrics to data product delivery timelines.[Ref7][Ref21]

**Prompt 5.1B – Comparative Analysis Prompt**
Propose a comparative analysis with alternative formation geometries (e.g., isosceles, linear string-of-pearls), outlining expected benefits/drawbacks and necessary simulation modifications.

### 5.2 Ground Segment and Operational Resilience
Discuss command latency, ground station availability, and contingency plans, referencing operational scenarios and risk registers.[Ref21]

**Prompt 5.2A – Operations Commentary**
Provide a 600-word commentary linking command latency margins (10.47 h) to risk mitigation strategies (Redu/MBRSC agreements) and to MR-5 compliance. Include references to operational scenarios in the Concept of Operations and Compliance Matrix risk entries.

**Prompt 5.2B – Risk Mitigation Table**
Develop a table summarising key operational risks (R-01 to R-05), current mitigation status, residual exposure, and evidence sources.

### 5.3 Robustness to Perturbations
Evaluate the Monte Carlo recovery statistics and drag dispersion findings.

**Prompt 5.3A – Robustness Essay**
Write an 800-word essay interpreting 100% recovery success, p95 delta-v 0.041 m/s, and drag-induced ground-distance deltas. Discuss implications for propellant management, timeline planning, and future sensor alignment studies.

**Prompt 5.3B – Sensitivity Analysis Plan**
Design a sensitivity analysis plan exploring variations in drag coefficient, recovery time, and contact range. Specify simulation scripts, parameter sweeps, and anticipated outputs.

### 5.4 Cross-Target Adaptation Strategy
Explain how the Tehran-focused methodology adapts to other mid-latitude targets (e.g., AuroraScience, EquatorialEnergy window targets in `config/project.yaml`).[Ref10]

**Prompt 5.4A – Adaptation Narrative**
Draft a narrative describing the steps to retarget the formation to a different city, including configuration changes, RAAN optimisation reruns, and compliance documentation updates.

**Prompt 5.4B – Comparative Metrics Table**
Plan a table comparing Tehran metrics with hypothetical AuroraScience/Ecuadorian targets, noting anticipated changes in access duration, centroid tolerance, and maintenance budgets.

### 5.5 Integration with Verification and Validation Plan
Connect results interpretation to planned verification activities (VRR, Simulation Qualification Campaign, HIL tests) documented in the V&V Plan.[Ref20]

**Prompt 5.5A – Verification Alignment Commentary**
Explain how existing evidence supports upcoming milestones (VRR, CDR), identifying which artefacts should be presented and which additional tests are required.

**Prompt 5.5B – Validation Roadmap Update**
Draft an update summarising validation progress (stakeholder reviews, simulation-in-the-loop, field rehearsals), referencing outstanding actions and resource allocations.

---

## Chapter 6 – Conclusions, Recommendations, and Future Research Directions

### 6.1 Key Findings Synthesis
Summarise the primary findings derived from simulation evidence, compliance reviews, and operations analyses. Emphasise the readiness level of the triangular formation concept.

**Prompt 6.1A – Findings Bullet Summary**
List at least ten bullet points capturing key results (formation duration, centroid control, delta-v margins, command latency). Each bullet should cite the corresponding artefact and requirement identifier.

**Prompt 6.1B – Impact Statement**
Compose a 400-word impact statement explaining how the mission concept advances mid-latitude resilience capabilities and what strategic advantages the formation offers compared with existing constellations.

### 6.2 Recommendations for Implementation
Provide actionable recommendations for mission planners, simulation engineers, and operations teams.

**Prompt 6.2A – Recommendations List**
Enumerate recommendations grouped by domain (Orbital Design, Maintenance Strategy, Ground Operations, Verification). For each recommendation, cite supporting evidence and outline next steps.

**Prompt 6.2B – Decision Gate Preparation**
Draft guidance for preparing for Critical Design Review (CDR) and Launch Readiness Review (LRR), mapping required artefacts, analyses, and risk mitigations to milestone entry criteria.[Ref20]

### 6.3 Future Research Agenda
Identify future work streams, including extended perturbation modelling, sensor integration, and autonomous operations.

**Prompt 6.3A – Research Roadmap**
Develop a roadmap of future studies aligned with `docs/project_roadmap.md`, specifying objectives, required tooling, and success criteria.[Ref6]

**Prompt 6.3B – Literature Outlook Summary**
Summarise emerging research avenues (autonomous formation control, machine-learning-based maintenance) that should be monitored. Suggest key conferences and journals for dissemination.

---

## Chapter 7 – Appendices and Authoring Toolkit

### 7.1 Reproduction Procedures
Compile reproduction steps from the Final Delivery Manifest and Tehran Triangle Walkthrough, ensuring analysts can regenerate artefacts and STK exports.[Ref18][Ref19]

**Prompt 7.1A – Step-by-Step Procedure**
List numbered steps (minimum twelve) covering environment setup, scenario execution, artefact comparison, STK import, and regression testing. Indicate where to capture logs and how to document outcomes.

**Prompt 7.1B – Troubleshooting Guide**
Develop a troubleshooting table mapping common issues (missing dependencies, STK import errors, metadata mismatches) to remediation actions and references.

### 7.2 Data Governance and Archiving
Reiterate data retention, checksum policies, and archival expectations from the Compliance Matrix and Verification Plan.[Ref5][Ref20]

**Prompt 7.2A – Archiving Policy Summary**
Summarise archiving rules for raw outputs, processed artefacts, and documentation. Specify directory structures, version control practices, and review cadence.

**Prompt 7.2B – Data Integrity Procedure**
Outline procedures for verifying checksums, validating JSON schemas, and logging integrity checks. Include instructions for reporting discrepancies to the SERB.

### 7.3 Writing Templates and Style Guidance
Provide writing templates for sections within each chapter, ensuring consistent tone and citation practice.

**Prompt 7.3A – Chapter Template**
Draft a reusable outline for chapter sections, including standard headings (Introduction, Methods, Results, Discussion, References) and annotation prompts for evidence citation.

**Prompt 7.3B – Citation Checklist**
Create a checklist to ensure each claim references a configuration-controlled artefact or external source, aligning with repository citation standards.

### 7.4 Visualisation and Figure Standards
Define expectations for figures (SVG format, annotation standards), referencing the Compliance Matrix and STK export guidance.[Ref5][Ref17]

**Prompt 7.4A – Figure Specification Sheet**
Specify resolution, colour palettes, annotation conventions, and file naming for figures derived from simulation outputs or STK captures.

**Prompt 7.4B – Visual Validation Workflow**
Describe the workflow for generating, reviewing, and archiving figures, including peer review steps and integration into documentation.

### 7.5 Glossary and Acronym Register
Compile a glossary of mission-specific terminology and acronyms to ensure consistent usage.

**Prompt 7.5A – Glossary Compilation**
List key terms (e.g., ROE, LVLH, RAAN, MR, SRD, STK, TEME) with concise definitions grounded in repository context.

**Prompt 7.5B – Acronym Validation Process**
Outline a process for validating new acronyms against existing documentation, preventing duplication or ambiguity.

---

### 3.5B – Telemetry Audit Plan
Design an audit plan ensuring telemetry outputs (debug logs, JSONL run logs, Plotly exports) remain consistent with configuration-controlled datasets. Specify when to snapshot `run_log.jsonl` into the compliance evidence chain.

### 3.6 Data Analytics and Visualisation Workbench
Document expectations for data analytics workflows (e.g., Jupyter notebooks, Pandas pipelines) that consume artefact CSV/JSON outputs to produce analytical figures and tables.

**Prompt 3.6A – Notebook Standards**
Define standards for analytical notebooks, including metadata headers (run identifier, scenario, seed), reproducibility notes, and export requirements (SVG, CSV) for derived products. Reference repository policies prohibiting binary artefacts.[Ref5]

**Prompt 3.6B – Data Pipeline Checklist**
List checklist items for validating data pipelines: schema validation, unit conversions, rounding protocols, outlier handling, and cross-verification with raw artefacts.

### 3.7 External Tool Integration
Outline procedures for integrating third-party tools (e.g., STK Connect automation, MATLAB prototypes) while maintaining configuration control.

**Prompt 3.7A – Toolchain Integration Plan**
Develop a plan for incorporating external analyses, specifying interfaces, data interchange formats, and documentation expectations.

**Prompt 3.7B – Compliance Safeguards**
Describe safeguards (version control, checksum validation, review gates) to ensure external tool outputs remain traceable and auditable.

---

## Chapter 4 – Authoritative Runs and Quantitative Evidence Synthesis (continued)

### 4.5B – Cross-Validation Narrative
Write a narrative describing how to cross-validate Python-derived metrics with STK analyses, emphasising the need to reconcile frame assumptions (TEME) and to document any discrepancies.

### 4.6 Extended Metrics Catalogue
Catalogue secondary metrics (e.g., centroid altitude drift, triangle area variance, command window phasing) captured in artefacts or derivable from existing data.

**Prompt 4.6A – Secondary Metric Extraction Guide**
Explain how to compute additional metrics from `triangle_summary.json` and `deterministic_cross_track.csv`, including formulas, tools, and validation steps.

**Prompt 4.6B – Metric Prioritisation Table**
Prioritise secondary metrics by mission relevance, indicating which should appear in the manuscript body, appendices, or supplementary material.

### 4.7 Evidence Gap Log
Establish a log for tracking missing or outdated evidence, mapping each gap to planned campaigns or literature tasks.

**Prompt 4.7A – Gap Register Template**
Draft a template capturing gap description, affected requirement, interim mitigation, and planned closure action.

**Prompt 4.7B – Quarterly Review Checklist**
Create a checklist for quarterly evidence reviews, ensuring the ledger stays current and exploratory runs are clearly demarcated.

---

## Chapter 5 – Results Interpretation, Discussion, and Cross-Target Adaptation (continued)

### 5.1B – Comparative Analysis Prompt
Propose a comparative analysis with alternative formation geometries (e.g., isosceles, linear string-of-pearls), outlining expected benefits/drawbacks and necessary simulation modifications.

### 5.6 Uncertainty Quantification
Discuss approaches for quantifying uncertainties beyond current Monte Carlo statistics, including parameter estimation, covariance propagation, and Bayesian updating.

**Prompt 5.6A – Uncertainty Method Survey**
Survey methods (e.g., Unscented Transform, Polynomial Chaos) applicable to formation flying analysis, summarising computational demands and integration considerations.

**Prompt 5.6B – Implementation Roadmap**
Draft a roadmap for introducing advanced uncertainty techniques into the simulation pipeline, specifying tooling, validation, and reporting requirements.

### 5.7 Stakeholder Communication Strategy
Outline strategies for communicating results to stakeholders with varying technical backgrounds (policy makers, operations staff, academic reviewers).

**Prompt 5.7A – Communication Plan**
Develop a plan detailing communication artefacts (executive summaries, technical briefs, dashboards), delivery cadence, and responsible teams.

**Prompt 5.7B – Feedback Integration Checklist**
List steps for capturing stakeholder feedback and incorporating it into subsequent analyses or documentation revisions.

---

## Chapter 6 – Conclusions, Recommendations, and Future Research Directions (continued)

### 6.3B – Literature Outlook Summary
Summarise emerging research avenues (autonomous formation control, machine-learning-based maintenance) that should be monitored. Suggest key conferences and journals for dissemination.

### 6.4 Implementation Readiness Assessment
Introduce an implementation readiness assessment aligning analytical maturity, documentation completeness, and operational readiness.

**Prompt 6.4A – Readiness Matrix**
Construct a matrix evaluating readiness across domains (Orbit Design, Ground Operations, Verification, Risk Management), grading each on evidence maturity and listing outstanding actions.

**Prompt 6.4B – Decision Support Narrative**
Write a narrative guiding decision-makers on interpreting the readiness matrix, highlighting thresholds for advancing to integration or flight phases.

---

## Chapter 7 – Appendices and Authoring Toolkit (continued)

### 7.3B – Citation Checklist
Create a checklist to ensure each claim references a configuration-controlled artefact or external source, aligning with repository citation standards.

### 7.6 Collaboration and Review Workflow
Detail collaboration workflows for drafting, reviewing, and approving manuscript sections.

**Prompt 7.6A – Review Cycle Plan**
Describe review cycles (author drafting, peer review, SERB endorsement), including timelines, required artefacts, and approval gates.

**Prompt 7.6B – Version Control Policy**
Outline version control policies for documentation drafts, including branching strategy, pull request expectations, and merge criteria.

### 7.7 Accessibility and Knowledge Transfer
Highlight practices ensuring documentation is accessible and transferable to new team members or partner organisations.

**Prompt 7.7A – Onboarding Guide Outline**
Create an outline for onboarding materials covering repository orientation, key documents, and essential scripts.

**Prompt 7.7B – Training Exercise Catalogue**
Catalogue suggested training exercises (e.g., reproducing `run_20251018_1207Z`, executing STK imports) with estimated effort and learning objectives.

---

## Chapter 8 – Writing Schedule and Progress Tracking
Introduce a schedule management framework to coordinate literature review, analysis updates, and manuscript drafting.

### 8.1 Milestone Calendar
Define a calendar aligning writing tasks with mission milestones (VRR, CDR, LRR) and evidence refresh cycles.

**Prompt 8.1A – Calendar Draft**
Draft a calendar showing monthly objectives, responsible authors, and dependency notes.

**Prompt 8.1B – Slippage Mitigation Plan**
Outline mitigation strategies for schedule slips, including resource reallocation and interim deliverables.

### 8.2 Progress Metrics
Specify metrics for tracking writing progress (chapters drafted, prompts completed, references integrated).

**Prompt 8.2A – Progress Dashboard Specification**
Define key performance indicators, data collection methods, and reporting cadence for a writing progress dashboard.

**Prompt 8.2B – Retrospective Template**
Create a retrospective template for monthly reviews, capturing achievements, blockers, and next actions.

### 8.3 Quality Assurance Gates
Establish quality assurance gates (content completeness, citation integrity, technical accuracy) before final submission.

**Prompt 8.3A – QA Checklist**
Develop a checklist for each gate, specifying verification activities and sign-off authorities.

**Prompt 8.3B – Issue Escalation Workflow**
Describe how to escalate and resolve issues identified during QA reviews, referencing configuration management practices.

---

## Chapter 9 – Supplementary Research Prompts
Provide an extended prompt bank supporting specialised investigations and cross-disciplinary insights.

### 9.1 Atmospheric and Environmental Effects

**Prompt 9.1A – Space Weather Literature Review**
Investigate space weather impacts (solar storms, geomagnetic activity) on atmospheric density models relevant to drag dispersion studies. Summarise mitigation strategies for formation-keeping.

**Prompt 9.1B – Thermospheric Modelling Plan**
Outline a plan for integrating updated thermospheric models (e.g., JB2008) into the simulation pipeline, noting data sources and validation requirements.

### 9.2 Payload and Sensor Integration

**Prompt 9.2A – Sensor Alignment Study**
Design a study to quantify how payload pointing errors influence formation geometry tolerances and data product quality.

**Prompt 9.2B – Calibration Workflow Proposal**
Propose a calibration workflow linking on-orbit calibration passes to formation control updates, referencing ground station resources.

### 9.3 Autonomy and Onboard Processing

**Prompt 9.3A – Autonomy Literature Review**
Survey recent developments in onboard autonomy for formation flying, including distributed control and onboard navigation filters.

**Prompt 9.3B – Prototype Algorithm Plan**
Develop a plan for prototyping an onboard maintenance algorithm, indicating simulation hooks and validation datasets.

### 9.4 Policy, Legal, and Socio-Technical Considerations

**Prompt 9.4A – Regulatory Assessment**
Assess regulatory considerations (frequency allocation, debris mitigation, data privacy) influencing mission deployment.

**Prompt 9.4B – Socio-Technical Impact Essay**
Write an essay reflecting on societal impacts, stakeholder engagement, and ethical deployment of persistent imaging constellations.

### 9.5 Interdisciplinary Collaboration Opportunities

**Prompt 9.5A – Partner Mapping**
Map potential academic, industry, and agency partners who could contribute expertise (aeronomy, AI, ground systems) to future increments.

**Prompt 9.5B – Joint Study Concept Note**
Draft a concept note for a joint study exploring cross-domain opportunities (e.g., integrating GNSS radio occultation data).

---

## References (supplemental note)
The reference list in Section "References" remains authoritative. Update numbering if additional sources are introduced during future revisions.

## Chapter 1 – Mission Framing and Literature Review Foundations (supplemental prompts)

### 1.5 Contextual Data Inventory
Enumerate all configuration-controlled datasets referenced in the mission dossier, clarifying their roles in literature contextualisation and evidence synthesis.

**Prompt 1.5A – Data Inventory Table**
Produce a table listing each dataset (scenario JSON, summary JSON, CSV catalogues, SVG plots), associated run identifier, storage path, and descriptive tags for literature linkage.

**Prompt 1.5B – Data Provenance Narrative**
Write a narrative explaining how provenance is maintained from simulation output to literature discussion, including citation practices and change-control notes.

### 1.6 Literature Output Formatting Guidelines
Specify formatting requirements for literature review outputs (citation style, table structure, figure references) to ensure consistency across chapters.

**Prompt 1.6A – Citation Style Guide**
Draft a mini style guide defining in-text citation formats, bibliography structure, and handling of standards or institutional documents.

**Prompt 1.6B – Summary Template**
Create a template for literature review summaries, including sections for methodology, key findings, applicability to mission, and gaps identified.

---

## Chapter 2 – Configuration Baselines and Geometric Design Constructs (supplemental prompts)

### 2.5 Assumption Management
Document modelling assumptions embedded in scenario and configuration files, linking each assumption to validation evidence or planned verification activity.

**Prompt 2.5A – Assumption Ledger**
Compile a ledger of assumptions (e.g., drag coefficient, uniform request distribution) with justification and impact assessment.

**Prompt 2.5B – Sensitivity Trigger Matrix**
Develop a matrix mapping assumption deviations to required re-analysis or documentation updates.

### 2.6 Coordinate Frames and Transformations
Detail the coordinate frames used throughout the simulation pipeline (TEME, LVLH, ECEF) and their transformation pathways.

**Prompt 2.6A – Frame Conversion Guide**
Explain step-by-step how positions flow from inertial propagation to geodetic reporting, referencing `inertial_to_ecef` and `geodetic_coordinates` routines.[Ref13]

**Prompt 2.6B – Consistency Checklist**
List checks to ensure frame consistency across artefacts and STK imports (e.g., verifying TEME assumptions, epoch synchronisation).

---

## Chapter 3 – Simulation Pipeline, Toolchain, and Data Engineering (supplemental prompts)

### 3.8 Documentation Automation
Plan for automating documentation refresh (e.g., generating summary digests via `make docs`, integrating metrics into Sphinx or Markdown dashboards).

**Prompt 3.8A – Automation Workflow Sketch**
Sketch a workflow automating extraction of key metrics into documentation, ensuring traceability and review points.

**Prompt 3.8B – Tool Evaluation List**
List potential tools (MkDocs, Sphinx, Pandoc) for integrating simulation outputs into documentation, noting advantages and integration steps.

---

## Chapter 4 – Authoritative Runs and Quantitative Evidence Synthesis (supplemental prompts)

### 4.8 Visual Evidence Repository
Define a repository structure for storing SVG plots, annotated screenshots, and visual summaries associated with each run.

**Prompt 4.8A – Visual Catalogue Template**
Create a template cataloguing visual artefacts with metadata (description, source data, reviewer sign-off).

**Prompt 4.8B – Quality Criteria List**
Enumerate quality criteria for visual artefacts (resolution, annotation clarity, colour accessibility) and review procedures.

---

## Chapter 5 – Results Interpretation, Discussion, and Cross-Target Adaptation (supplemental prompts)

### 5.8 Comparative Mission Case Studies
Encourage comparative analysis with existing or proposed missions (e.g., TanDEM-X, COSMO-SkyMed) to contextualise the Tehran formation.

**Prompt 5.8A – Case Study Outline**
Outline a case study comparing mission architectures, highlighting differences in formation design, revisit, and operations.

**Prompt 5.8B – Benchmark Metrics Table**
Assemble a table benchmarking key metrics (baseline length, access duration, delta-v budgets) against comparator missions.

---

## Chapter 6 – Conclusions, Recommendations, and Future Research Directions (supplemental prompts)

### 6.5 Technology Readiness Discussion
Discuss technology readiness levels (TRL) for key subsystems (formation control algorithms, ground automation, STK export tooling).

**Prompt 6.5A – TRL Assessment Table**
Create a table assigning TRLs, evidence sources, and advancement actions.

**Prompt 6.5B – Risk-Adjusted Recommendation**
Write recommendations considering TRL and risk appetite, guiding investment priorities.

---

## Chapter 7 – Appendices and Authoring Toolkit (supplemental prompts)

### 7.8 Style and Language Consistency Checks
Define proofreading and language consistency checks to preserve British English usage and tone.

**Prompt 7.8A – Proofreading Checklist**
List proofreading checks (terminology consistency, reference accuracy, figure/table captions) and assign review responsibility.

**Prompt 7.8B – Terminology Watchlist**
Create a watchlist of terms with preferred spellings or usage notes (e.g., "organisation" vs "organization").

---

## Chapter 10 – Publication and Dissemination Strategy
Outline plans for disseminating the final dossier, including academic publications, conference presentations, and stakeholder briefings.

### 10.1 Target Venues
Identify journals, conferences, and workshops aligned with mission themes (formation flying, mission analysis, civil protection).

**Prompt 10.1A – Venue Ranking Table**
Rank target venues by relevance, submission windows, and required adaptations.

**Prompt 10.1B – Abstract Drafting Template**
Provide a template for drafting abstracts tailored to different venues.

### 10.2 Publication Timeline
Integrate dissemination activities into the mission schedule, ensuring alignment with evidence availability and review cycles.

**Prompt 10.2A – Timeline Chart**
Develop a timeline aligning manuscript preparation, review, submission, and presentation milestones.

**Prompt 10.2B – Resource Allocation Plan**
Plan resource allocation (authors, reviewers, graphics support) for publication efforts.

### 10.3 Open Science and Data Sharing Considerations
Discuss policies for sharing data, code, and artefacts while respecting export controls and proprietary constraints.

**Prompt 10.3A – Data Sharing Policy Draft**
Draft a policy outlining what can be shared publicly, under what licences, and with what redactions.

**Prompt 10.3B – Repository Integration Plan**
Plan how public releases (e.g., anonymised datasets, scripts) will be integrated into open repositories while maintaining configuration control internally.

---

## Chapter 11 – Continuous Improvement and Lessons Learned
Establish a framework for capturing lessons learned throughout the mission analysis and documentation process.

### 11.1 Lessons Learned Log
Design a log capturing observations, corrective actions, and knowledge transfer notes.

**Prompt 11.1A – Log Template**
Draft a template with fields for context, issue, resolution, and follow-up actions.

**Prompt 11.1B – Review Cadence Plan**
Set a cadence for reviewing and disseminating lessons learned within the team.

### 11.2 Process Improvement Backlog
Maintain a backlog of process improvement opportunities (tooling, documentation, communication) with prioritisation.

**Prompt 11.2A – Backlog Board Setup**
Describe how to structure the backlog (Kanban board, prioritisation criteria) and integrate it with sprint cycles.

**Prompt 11.2B – Success Metrics Definition**
Define metrics for evaluating improvement initiatives (cycle time reduction, defect rates, reviewer satisfaction).

---

## Chapter 12 – Appendices Expansion Guidelines
Provide guidance for creating supplementary appendices (e.g., mathematical derivations, extended tables, code listings).

### 12.1 Derivation Appendices

**Prompt 12.1A – Derivation Structure Guide**
Outline how to present extended derivations (assumptions, step-by-step equations, validation checks).

**Prompt 12.1B – Cross-Reference Checklist**
Ensure derivations reference main text sections, figures, and datasets appropriately.

### 12.2 Extended Tables and Data Listings

**Prompt 12.2A – Table Formatting Rules**
Specify formatting rules for large tables (caption placement, footnotes, pagination).

**Prompt 12.2B – Data Listing Integrity Check**
Define integrity checks for extensive data listings (checksum verification, sampling validation).

### 12.3 Code and Algorithm Appendices

**Prompt 12.3A – Code Inclusion Policy**
Set policies for including code snippets or algorithm pseudo-code, balancing clarity and intellectual property considerations.

**Prompt 12.3B – Reproducibility Note Template**
Provide a template for reproducibility notes accompanying code listings (dependencies, execution steps, expected outputs).

---
## References
- [Ref1] `README.md` – Repository overview and mission intent statement.【F:README.md†L1-L83】
- [Ref2] `docs/project_overview.md` – Mission problem statement, objectives, and deliverables.【F:docs/project_overview.md†L1-L52】
- [Ref3] `docs/mission_requirements.md` – Mission requirement matrix and verification approaches.【F:docs/mission_requirements.md†L1-L24】
- [Ref4] `docs/system_requirements.md` – System requirement derivations and compliance linkage.【F:docs/system_requirements.md†L1-L166】
- [Ref5] `docs/compliance_matrix.md` – Compliance status, evidence catalogue, and risk governance.【F:docs/compliance_matrix.md†L1-L210】
- [Ref6] `docs/project_roadmap.md` – Stage-wise roadmap for mission analysis progression.【F:docs/project_roadmap.md†L1-L67】
- [Ref7] `docs/triangle_formation_results.md` – Detailed analysis of the Tehran triangular formation simulation.【F:docs/triangle_formation_results.md†L1-L165】
- [Ref8] `docs/tehran_daily_pass_scenario.md` – Tehran daily pass configuration and validation narrative.【F:docs/tehran_daily_pass_scenario.md†L1-L164】
- [Ref9] `docs/_authoritative_runs.md` – Ledger of configuration-controlled simulation runs.【F:docs/_authoritative_runs.md†L1-L83】
- [Ref10] `config/project.yaml` – Programme-wide configuration constants and simulation controls.【F:config/project.yaml†L1-L160】
- [Ref11] `config/scenarios/tehran_triangle.json` – Authoritative triangle scenario definition.【F:config/scenarios/tehran_triangle.json†L1-L52】
- [Ref12] `config/scenarios/tehran_daily_pass.json` – Authoritative daily pass scenario configuration.【F:config/scenarios/tehran_daily_pass.json†L1-L71】
- [Ref13] `sim/formation/triangle.py` – Triangle formation simulation implementation and metric extraction.【F:sim/formation/triangle.py†L1-L423】
- [Ref14] `sim/scripts/run_scenario.py` – Scenario orchestration pipeline with RAAN alignment and export hooks.【F:docs/tehran_daily_pass_scenario.md†L53-L111】
- [Ref15] `tools/stk_export.py` – STK exporter utilities and data classes.【F:tools/stk_export.py†L1-L160】
- [Ref16] `tests/unit/test_triangle_formation.py` – Regression test enforcing formation requirements.【F:tests/unit/test_triangle_formation.py†L1-L48】
- [Ref17] `docs/stk_export.md` – STK export usage guide and file descriptions.【F:docs/stk_export.md†L1-L64】
- [Ref18] `docs/tehran_triangle_walkthrough.md` – Step-by-step walkthrough for reproducing triangle artefacts.【F:docs/tehran_triangle_walkthrough.md†L1-L102】
- [Ref19] `docs/final_delivery_manifest.md` – Delivery manifest and reproduction procedure summary.【F:docs/final_delivery_manifest.md†L1-L79】
- [Ref20] `docs/verification_plan.md` – Verification and validation strategy, milestones, and resource planning.【F:docs/verification_plan.md†L1-L196】
- [Ref21] `docs/concept_of_operations.md` – Operational scenarios, mission phases, and risk management constructs.【F:docs/concept_of_operations.md†L1-L210】
- [Ref22] `docs/how_to_import_tehran_daily_pass_into_stk.md` – STK validation workflow for the daily pass scenario.【F:docs/how_to_import_tehran_daily_pass_into_stk.md†L1-L91】
- [Ref23] `artefacts/run_20251018_1207Z/triangle_summary.json` – Triangle maintenance and robustness metrics.【F:artefacts/run_20251018_1207Z/triangle_summary.json†L1-L137】
- [Ref24] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json` – Deterministic centroid and cross-track metrics.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json†L1-L157】
- [Ref25] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json` – Monte Carlo centroid and worst-vehicle statistics.【F:artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json†L1-L57】
