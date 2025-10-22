# Project Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Global Output Expectations
- Produce a comprehensive "Mission Research & Evidence Brief" spanning **six fully developed chapters** and supporting appendices. Each chapter must exceed 1,000 words and present academically reasoned arguments grounded in repository artefacts, simulation outputs, and Systems Tool Kit (STK 11.2) validation practices.
- Adopt a British English narrative voice that balances academic rigour with operational clarity. Maintain a neutral, analytical tone that foregrounds traceability, reproducibility, and mission assurance considerations.
- Anchor every factual assertion to configuration-controlled evidence. Reference run identifiers (e.g., `run_20251018_1207Z`) and specific datasets (`triangle_summary.json`, `deterministic_summary.json`) alongside documentation sources (`docs/triangle_formation_results.md`). Use inline numbered citations `[RefX]` and collate them into a chapter-level reference list.
- Integrate quantitative metrics with qualitative context. When quoting results (e.g., \(\Delta v\) budgets, centroid cross-track offsets, triangle aspect ratios), reproduce exact figures and tolerance envelopes as captured in the repository artefacts.[Ref3][Ref4]
- Preserve interoperability guidance for STK 11.2 exports. Explicitly note exporter versioning, file naming conventions, and validation workflows described in `tools/stk_export.py`, `docs/stk_export.md`, and `docs/how_to_import_tehran_daily_pass_into_stk.md` whenever simulation outputs feed downstream visualisation or assurance tasks.[Ref5][Ref6][Ref7]
- Document modelling assumptions, seeds, and configuration contexts exactly as recorded in the JSON artefacts so subsequent reruns remain reproducible. Highlight the `seed` entries, perturbation spreads, and maintenance cadence information stored under the Monte Carlo and maintenance sections of the summary files.[Ref3][Ref4]
- Cross-reference mission requirements (MR-1 to MR-7) and derived system requirements (SRD-###) using the compliance matrix so that compliance narratives remain synchronised with the Systems Engineering Review Board (SERB) ledger.[Ref2][Ref8]
- Incorporate forward-looking recommendations that build upon the `docs/project_roadmap.md` stages, the verification plan milestones, and the automation tooling maintained under `tests/` and `tools/`. Position each recommendation within the programme governance framework (Configuration Control Board, SERB, V&V milestones).[Ref1][Ref9]
- Ensure each chapter contains:
  1. **Key Artefact Digest:** A bulleted list summarising the repository evidence that underpins the chapter. Include directories, filenames, and metrics.
  2. **Literature & Standards Prompt:** Detailed instructions for sourcing peer-reviewed literature (2019–2025 preferred) and applicable standards. Map references to specific analytical gaps identified in the repository.
  3. **Analytical Narrative Outline:** A sequential plan describing how to weave evidence, models, and literature into a coherent chapter.
  4. **Data Tables & Figures Brief:** Guidance on reproducing or adapting figures, tables, and equations with explicit citations.
  5. **Validation & Assurance Hooks:** Notes on how the chapter contributes to mission assurance, including test coverage, STK validation steps, and compliance checkpoints.
  6. **Future Work & Risk Register Inputs:** Prompts for articulating unresolved questions, risk items, or backlog tasks, referencing `docs/verification_plan.md` and `docs/compliance_matrix.md` entries.
- Close the document with appendices that consolidate reusable prompts (e.g., literature search keywords, STK validation checklists, Monte Carlo scenario templates) and a repository-specific reference list following the `[RefX]` convention.

### Repository Evidence Map
| Evidence Domain | Artefact | Location | Key Notes |
|-----------------|----------|----------|-----------|
| Mission framing | Project overview | `docs/project_overview.md` | Mission objectives, deliverables, recent verification evidence summarising MR-5 to MR-7 coverage.[Ref1]
| Requirements | Mission requirements | `docs/mission_requirements.md` | Defines MR-1 to MR-7 with verification approaches and tolerance statements.[Ref2]
| Orbital configuration | Programme configuration | `config/project.yaml` | Captures global constants, platform data, orbital elements, Monte Carlo dispersion settings, and STK export policies.[Ref3]
| Scenario baselines | Tehran triangle configuration | `config/scenarios/tehran_triangle.json` | Declares formation geometry, maintenance cadence, Monte Carlo dispersions, drag sampling settings, and STK validation flag.[Ref4]
| Scenario baselines | Tehran daily pass configuration | `config/scenarios/tehran_daily_pass.json` | Records RAAN solution (350.7885044642857°), access window timings, payload constraints, and Monte Carlo catalogue metadata.[Ref5]
| Authoritative runs | Triangular formation maintenance | `artefacts/run_20251018_1207Z/` | Stores `triangle_summary.json`, maintenance and command CSVs, injection recovery catalogue, drag dispersion CSV, STK exports, and CDF plot.[Ref6]
| Authoritative runs | Tehran daily pass locked geometry | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` | Houses deterministic and Monte Carlo summaries with centroid \(p_{95}\) \(24.18\,\text{km}\), STK exports, and RAAN optimiser metadata.[Ref7]
| Documentation | Simulation results memorandum | `docs/triangle_formation_results.md` | Explains methodology, key metrics (96 s window, \(343.62\,\text{km}\) windowed maximum, \(641.89\,\text{km}\) full propagation), and MR-5 to MR-7 evidence alignment.[Ref3]
| Documentation | Tehran daily pass scenario overview | `docs/tehran_daily_pass_scenario.md` | Links RAAN solver evidence, deterministic metrics (centroid 12.142754610722838 km), Monte Carlo statistics, and STK validation procedures.[Ref5]
| Compliance | Compliance matrix | `docs/compliance_matrix.md` | Records SERB dispositions, evidence tags [EV-1] to [EV-5], and outstanding actions.[Ref8]
| Verification | V&V plan | `docs/verification_plan.md` | Articulates verification taxonomy, schedule, milestone responsibilities, and resource allocations.[Ref9]
| Tooling | STK exporter | `tools/stk_export.py` | Defines export data structures, interpolation logic, naming sanitisation, and scenario metadata requirements.[Ref6]
| Testing | Regression guardrails | `tests/` | Enforces geometry compliance, exporter integrity, scenario pipeline sequencing, and CLI smoke tests.[Ref10]

---

## Chapter 1 – Mission Framing, Stakeholder Drivers, and Requirements Baseline

### 1.1 Research Orientation
- Explain the mission problem statement using the dual-plane architecture with a transient triangular formation over Tehran (or analogous mid-latitude targets). Connect stakeholder priorities (civil protection, rapid imaging) to MR-1 through MR-4 definitions and ConOps objectives.[Ref1][Ref2][Ref11]
- Detail the operational success criteria: sustained 96-second equilateral geometry, ±30 km centroid cross-track tolerance at the daily pass midpoint (with ±70 km waiver bracket), single ground-station responsiveness within 12 hours, ≤15 m/s annual maintenance \(\Delta v\), and robustness to ±5 km/±0.05° dispersions.[Ref2]
- Identify stakeholder groups (Mission Planning Cell, Guidance and Control Working Group, Ground Segment Integration Team) and describe their evidence needs using the ConOps and verification plan narratives.[Ref11][Ref9]
- Frame the mission in the context of mid-latitude hazard monitoring. Encourage literature coverage of multi-angle imaging campaigns, disaster response constellations, and cooperative radar-optical sensing studies (2019–2025).
- Highlight the governance structure: SERB reviews, Configuration Control Board approvals, verification milestones (VRR, CDR, LRR), and quarterly rerun mandates tracked in the compliance matrix and verification plan.[Ref8][Ref9]

### 1.2 Repository Evidence to Anchor
- `docs/project_overview.md` for mission intent, deliverables, and MR-5 to MR-7 evidence summary (command latency 1.53 h, annual \(\Delta v = 14.04\,\text{m/s}\), Monte Carlo \(p_{95} = 0.041\,\text{m/s}\)).[Ref1]
- `docs/mission_requirements.md` for requirement statements, tolerance thresholds, and verification approach taxonomy.[Ref2]
- `docs/concept_of_operations.md` for operational objectives, mission phases, scenarios, ground segment architecture, and risk register entries.[Ref11]
- `docs/system_requirements.md` for SRD taxonomy and mapping of MR-1 to MR-7 into system-level requirements with compliance status cross-references.[Ref12]
- `docs/compliance_matrix.md` for SERB dispositions, evidence tags, and outstanding action items (quarterly rerun governance, drag dispersion margins).[Ref8]

### 1.3 Literature & Standards Prompt
- Survey peer-reviewed formation-flying missions (e.g., TanDEM-X, PRISMA, PROBA-3) emphasising dual-plane architectures and transient triangular geometries. Extract alignment strategies, inter-satellite link requirements, and maintenance policies.
- Review guidance on mission assurance frameworks (NASA-STD-7009A, ECSS-E-ST-10-02C) to contextualise the repository’s verification plan and compliance matrix structure.[Ref9]
- Investigate single-ground-station operations and command latency management for Earth observation constellations, focusing on X-band networks and contingency agreements (Redu, MBRSC) similar to ConOps arrangements.[Ref11]
- Compile multi-angle imaging literature addressing rapid change detection, structural health monitoring, and tri-stereo processing pipelines to justify the mission’s high-level value proposition.
- Explore risk governance best practices for LEO constellations (e.g., anomaly response boards, risk registers, delta-v budgeting) to align with ConOps and compliance matrix expectations.

### 1.4 Analytical Narrative Outline
1. **Contextual Introduction:** Present the mission overview, highlighting the Tehran case study and the repeatable triangular formation requirement.[Ref1]
2. **Stakeholder Motivations:** Map stakeholder objectives to MR-1 through MR-7, referencing ConOps scenarios and operational objectives.[Ref2][Ref11]
3. **Requirement Hierarchy:** Explain the cascade from mission requirements to SRD entries, using compliance matrix evidence tags to demonstrate current status.[Ref8][Ref12]
4. **Operational Constraints:** Discuss single ground-station operations, command latency, data handling, and risk mitigations with references to ConOps tables and checklists.[Ref11]
5. **Mission Assurance Structure:** Summarise SERB, CCB, and V&V milestone governance, integrating verification plan schedule entries and resource allocations.[Ref9]
6. **Literature Synthesis:** Compare repository requirements to published mission precedents, standards, and guidelines. Identify gaps requiring additional literature support.
7. **Forward-Looking Recommendations:** Propose requirement refinement or stakeholder engagement tasks aligned with roadmap stages and outstanding compliance actions.[Ref8][Ref9]

### 1.5 Data Tables & Figures Brief
- Reproduce a requirement traceability matrix mapping MR-1 to MR-7 to SRD entries, referencing the compliance matrix evidence tags (EV-1 to EV-5).[Ref8]
- Include a stakeholder-objective table summarising needs, associated requirements, and evidence artefacts (triangle run, daily pass locked run, maintenance study).[Ref6][Ref7]
- Propose a timeline figure aligning roadmap stages with verification milestones (VRR, Simulation Qualification, CDR, LRR) and corresponding artefacts.[Ref9]
- Present a risk matrix referencing ConOps risk register entries (R-01 to R-05) and proposed mitigations.[Ref11]

### 1.6 Validation & Assurance Hooks
- Clarify how requirement statements map to automated tests (`tests/unit/test_triangle_formation.py`, `tests/integration/test_simulation_scripts.py`) and exporter regressions (`tests/test_stk_export.py`).[Ref10]
- Indicate the evidence closure for MR-5 to MR-7 using the triangular formation maintenance run metrics (command latency 1.5338 h, annual \(\Delta v\) margins) and ensure the narrative reiterates these values with citations.[Ref6]
- Note the compliance matrix outstanding actions (quarterly rerun, drag dispersion monitoring) and connect them to roadmap tasks and verification milestones.[Ref8][Ref9]

### 1.7 Future Work & Risk Register Inputs
- Recommend literature reviews on evolving command latency mitigation techniques and multi-ground-station contingency architectures to refine MR-5 risk handling.
- Suggest stakeholder interviews focusing on data latency (<4 h) to ensure ConOps objectives remain aligned with user expectations.[Ref11]
- Highlight the need for updated SRD entries should platform or payload parameters evolve in `config/project.yaml` (e.g., changes to communications or propulsion data).[Ref3]
- Encourage integration of cyber-security standards into the risk register, expanding upon ConOps R-04 mitigation strategies.

---

## Chapter 2 – Configuration, Geometry, and Relative Motion Foundations

### 2.1 Research Orientation
- Describe the programme-wide configuration stored in `config/project.yaml`, emphasising Earth model (WGS84), gravitational parameter, nominal altitude (550 km), and Monte Carlo dispersion settings (semi-major-axis \(\sigma = 5\,\text{m}\), inclination \(\sigma = 0.01°\), drag coefficient \(\sigma = 0.05\), clock bias \(\sigma = 0.5\,\text{ms}\)).[Ref3]
- Summarise the orbital architecture: leader orbital elements (semi-major axis 6,878.137 km, inclination 97.6°), formation design offsets (±20 km along-track, ±0.2 km cross-track, ±0.05 km radial), and maintenance strategy (14-day cadence, 100 m tolerance, 20% \(\Delta v\) reserve).[Ref3]
- Detail the Tehran triangle configuration (`config/scenarios/tehran_triangle.json`): 6,000 m side length, 180 s duration, 1 s sampling, ±350 km ground tolerance, aspect ratio tolerance 1.02, weekly maintenance burns (32 s duration, 15 m/s budget), command station coordinates (30.283° N, 57.083° E), Monte Carlo sample count 300, drag dispersion sample count 200.[Ref4]
- Explain the Tehran daily pass configuration (`config/scenarios/tehran_daily_pass.json`): RAAN 350.7885044642857°, access window 07:39:25Z–07:40:55Z, centroid midpoint 07:40:10Z, cross-track limits ±30 km/±70 km, Monte Carlo 1,000 runs (seed 4,242), payload constraints (max off-nadir 25°, daily calibration), power and attitude requirements.[Ref5]
- Introduce relative orbital element (ROE) theory implemented in `src/constellation/roe.py` and transformation utilities in `src/constellation/orbit.py` and `src/constellation/frames.py`. Highlight functions such as `roe_from_absolute`, `absolute_from_roe`, `propagate_roe`, and inertial-to-LVLH conversions that underpin geometry analysis.[Ref13][Ref14]

### 2.2 Repository Evidence to Anchor
- `config/project.yaml` for programme constants, platform parameters, orbital formation design, simulation controls, and output policies.[Ref3]
- `config/scenarios/tehran_triangle.json` and `config/scenarios/tehran_daily_pass.json` for scenario-specific geometry, tolerances, maintenance cadence, Monte Carlo seeds, and STK validation metadata.[Ref4][Ref5]
- `docs/triangle_formation_results.md` for formation geometry metrics, orbital element reconstruction table, and discussion of windowed vs full propagation ground distances.[Ref3]
- `docs/tehran_daily_pass_scenario.md` for RAAN optimisation narrative, centroid cross-track evidence, Monte Carlo statistics, and STK validation status.[Ref5]
- `src/constellation/orbit.py`, `src/constellation/geometry.py`, and `src/constellation/frames.py` for computational kernels supporting geometry reconstruction, triangle metrics, and frame transformations.[Ref13][Ref14][Ref15]

### 2.3 Literature & Standards Prompt
- Investigate modern ROE-based formation design literature (2018–2025) covering transient triangles, LVLH frame transformations, and maintenance strategies for dual-plane configurations. Focus on papers referencing D'Amico et al. (2005) and more recent extensions.
- Review analytical treatments of RAAN alignment and repeat-ground-track design for sun-synchronous orbits, emphasising J2-driven drift correction and cross-track minimisation techniques.
- Compile studies on geometry tolerance allocation (aspect ratio, side-length stability) for cooperative imaging, including guidance on selecting ground tolerance thresholds and centroid metrics.
- Examine literature on command station geometry, single-ground-station coverage, and contact probability analyses to contextualise the `command_latency` modelling captured in the triangle summary.[Ref6]
- Survey research on Monte Carlo dispersion analysis for injection errors and atmospheric drag modelling, linking repository parameters to published methodologies.

### 2.4 Analytical Narrative Outline
1. **Programme Configuration Overview:** Present `project.yaml` constants, linking to platform capabilities (communications, propulsion) and simulation controls.[Ref3]
2. **Formation Geometry Definition:** Explain the LVLH offsets used to produce the 6 km equilateral triangle, referencing `triangle_formation_results.md` and the `triangle_summary.json` metrics (aspect ratio unity, side length stability).[Ref3][Ref6]
3. **Relative Motion Theory:** Discuss ROE formulation and propagation, showing how `roe.py` functions support alignment and maintenance strategies.[Ref13]
4. **Scenario Parameterisation:** Detail both scenario JSON files, emphasising RAAN, access windows, maintenance, and dispersion configurations. Compare metadata fields (validated_against_stk_export, alignment_validation) and how they enforce traceability.[Ref4][Ref5]
5. **Ground-Track & Command Geometry:** Interpret the `command_latency` section of `triangle_summary.json` (contact probability 0.03157, max latency 1.5338 h, mean latency 0.7669 h) and relate to ground station assumptions.[Ref6]
6. **Monte Carlo & Drag Settings:** Describe the injection recovery and drag dispersion parameters, seeds, and sample counts defined in the scenario JSON, anticipating usage in later chapters.[Ref4]
7. **Comparative Literature Synthesis:** Align repository configuration choices with external formation flying and mission design references, noting convergence or divergence from published practices.

### 2.5 Data Tables & Figures Brief
- Create a table summarising configuration parameters across `project.yaml`, `tehran_triangle.json`, and `tehran_daily_pass.json`, including altitude, inclination, RAAN, window durations, tolerance values, maintenance cadences, Monte Carlo seeds, and drag sample counts.[Ref3][Ref4][Ref5]
- Present an LVLH triangle diagram referencing the offsets defined in `_formation_offsets` within `sim/formation/triangle.py`.[Ref16]
- Include a figure showing RAAN convergence from 350.9838169642857° (seed) to 350.7885044642857° (optimised), annotated with centroid cross-track values at the pass midpoint.[Ref5][Ref7]
- Tabulate the command station coverage metrics (contact probability, passes per day, latency margins) drawn from `triangle_summary.json` for each satellite, referencing the relevant CSV outputs.[Ref6]

### 2.6 Validation & Assurance Hooks
- Note how configuration metadata feeds automated tests (triangle geometry, scenario pipeline) and STK exports. Emphasise naming conventions enforced by `tools/stk_export.py` (`SAT_1.e`, underscores replacing spaces) and validated by `tests/test_stk_export.py`.[Ref6][Ref10]
- Highlight scenario `validated_against_stk_export` flags and `alignment_validation` blocks that connect JSON configuration to authoritative runs.[Ref4][Ref5]
- Discuss how configuration changes trigger documentation updates (project overview, scenario memoranda, compliance matrix) and reruns using the naming convention `run_YYYYMMDD_hhmmZ`.[Ref8]

### 2.7 Future Work & Risk Register Inputs
- Recommend sensitivity studies exploring alternative side lengths or altitude regimes to evaluate formation robustness beyond the 6 km design.
- Suggest expanding configuration metadata to capture sensor alignment budgets, thermal constraints, or alternative ground station networks.
- Encourage establishing configuration baselines for other mid-latitude targets to generalise beyond Tehran while preserving repeatable geometry.
- Identify risks related to configuration drift (e.g., inconsistent RAAN across documents) and propose mitigation via automated schema validation.

---

## Chapter 3 – Simulation Pipeline, Toolchain Integration, and Automation

### 3.1 Research Orientation
- Introduce the simulation pipeline implemented in `sim/scripts/run_scenario.py`, emphasising stage sequencing (RAAN alignment, access nodes, mission phases, two-body propagation, J2+drag propagation, metric extraction, optional STK export).[Ref17]
- Present the dedicated triangle runner `sim/scripts/run_triangle.py` and campaign orchestration tool `sim/scripts/run_triangle_campaign.py`, noting artefact generation (summary JSON, CSVs, SVG CDF, STK directory) and Monte Carlo/drag dispersion workflows.[Ref16][Ref18]
- Describe supporting utilities (`scenario_execution.py`, `metric_extraction.py`, `extract_metrics.py`, `baseline_generation.py`) and their integration within CI tests.[Ref18][Ref10]
- Highlight the interactive execution pathways (`run.py` FastAPI service, `run_debug.py` CLI) documented in `docs/interactive_execution_guide.md`, which feed artefact repositories and debugging outputs.[Ref19]
- Explain the STK exporter architecture defined in `tools/stk_export.py`, including data classes, interpolation strategy, naming sanitisation, and scenario metadata handling.[Ref6]

### 3.2 Repository Evidence to Anchor
- `sim/scripts/run_scenario.py` for pipeline logic, RAAN optimisation, STK export integration, and artefact summary structure.[Ref17]
- `sim/formation/triangle.py` for geometry generation, centroid metrics, maintenance estimation, command latency analysis, Monte Carlo and drag simulations, and STK export invocation.[Ref16]
- `tools/stk_export.py` for exporter data structures and file generation (ephemeris, ground track, facility, interval, event, scenario files).[Ref6]
- `tests/integration/test_simulation_scripts.py` for smoke tests verifying stage sequencing, CLI execution, and artefact output expectations.[Ref10]
- `docs/triangle_formation_results.md` and `docs/tehran_triangle_walkthrough.md` for guidance on reproducing simulations and interpreting outputs.[Ref3][Ref20]
- `docs/how_to_import_tehran_daily_pass_into_stk.md` for automated STK validation workflow leveraging exported artefacts.[Ref7]

### 3.3 Literature & Standards Prompt
- Review software assurance practices for mission analysis pipelines, focusing on provenance tracking, deterministic outputs, and CI integration (2018–2025).
- Survey RAAN optimisation algorithms and their application to daily pass alignment, highlighting techniques for coupling RAAN sweeps with high-fidelity propagation.
- Examine Monte Carlo and drag dispersion methodologies for LEO formation flying, identifying best practices for sample sizes, seeds, and statistical reporting.
- Investigate digital twin or interactive execution frameworks for mission analysis, comparing repository interactive tooling with published case studies.
- Consult STK interoperability standards and exporter design literature to ensure data exchange practices align with industry expectations.

### 3.4 Analytical Narrative Outline
1. **Pipeline Overview:** Describe the sequential pipeline stages, referencing the `stage_sequence` recorded in `scenario_summary.json` and confirmed by integration tests.[Ref17][Ref10]
2. **RAAN Optimiser:** Explain the alignment process, metrics logged (`centroid_abs_cross_track_km`, `worst_vehicle_abs_cross_track_km`), and alignment validation metadata captured in scenario JSON and run directories.[Ref5][Ref7]
3. **Propagation Stack:** Detail the two-body and J2+drag propagations, outputs (orbital periods, Monte Carlo statistics), and run artefact structures (deterministic and Monte Carlo summaries).[Ref7]
4. **Triangle Simulation Core:** Discuss geometry construction, maintenance estimation (mean differential acceleration, per-spacecraft \(\Delta v\)), command latency analysis (contact probability, latency margins), injection recovery success (300/300, \(p_{95}\) \(0.041\,\text{m/s}\)), and drag dispersion metrics stored in CSVs and summary dictionaries.[Ref6]
5. **Exporter Integration:** Outline how `simulate_triangle_formation` prepares `SimulationResults` for `export_simulation_to_stk`, emphasising naming sanitisation and STK compatibility checks.[Ref16][Ref6]
6. **Automation & Testing:** Summarise unit and integration tests that guard pipeline behaviour, referencing `tests/unit/test_triangle_formation.py` assertions (window ≥90 s, tolerance compliance, command latency ≤12 h, success rates ≥0.95).[Ref10]
7. **Interactive Tooling:** Describe how the web and debug interfaces orchestrate runs, stream logs, and produce artefacts, aligning with the interactive execution guide.[Ref19]
8. **Literature Integration:** Compare pipeline design decisions with published methodologies, highlighting innovations or areas for improvement.

### 3.5 Data Tables & Figures Brief
- Construct a pipeline stage table listing inputs, outputs, run artefacts, and validation checks for each stage (RAAN alignment, node generation, propagation, metrics, STK export).[Ref17]
- Include a flow diagram illustrating the triangle simulation process, from configuration ingestion to STK export and CSV generation, referencing `triangle_summary.json` fields.[Ref16]
- Present a table summarising Monte Carlo results (sample count 300, success rate 1.0, \(p_{95}\) \(0.041\,\text{m/s}\)) and drag dispersion sample statistics (200 samples, density \(\sigma = 0.25\), drag coefficient \(\sigma = 0.05\)) using CSV outputs.[Ref4][Ref6]
- Offer a figure showing the command latency distribution and contact windows, derived from `command_windows.csv` and `command_latency` summary metrics.[Ref6]

### 3.6 Validation & Assurance Hooks
- Emphasise regression coverage: triangle unit tests, scenario integration tests, exporter tests, and `tests/baseline_compare.py` (JSON diff utility) safeguarding artefact stability.[Ref10]
- Note the CI workflow described in `README.md` (make targets, GitHub Actions) and how it executes pipeline components (`make simulate`, `make triangle`, `make scenario`).[Ref21]
- Highlight exporter validation instructions from `docs/stk_export.md` and `docs/how_to_import_tehran_daily_pass_into_stk.md`, including ephemeris resampling and COM automation scripts (`tools/stk_tehran_daily_pass_runner.py`).[Ref7]
- Address provenance logging: `run_metadata.json`, `run_log.jsonl`, command-line logs, seeds recorded in summary files, and naming convention `run_YYYYMMDD_hhmmZ`.

### 3.7 Future Work & Risk Register Inputs
- Recommend expanding RAAN optimiser to incorporate atmospheric drag and solar radiation pressure sensitivity, referencing future toolchain enhancements.
- Suggest integrating high-fidelity attitude dynamics or sensor alignment models within the pipeline.
- Propose automated comparison of regenerated runs against authoritative baselines using `tests/baseline_compare.py` to detect drift.
- Highlight risks related to dependency updates affecting exporter compatibility or pipeline reproducibility; propose mitigation via pinned environments (`requirements.txt`, `pyproject.toml`).

---

## Chapter 4 – Authoritative Runs, Quantitative Evidence, and Result Interpretation

### 4.1 Research Orientation
- Focus on the authoritative triangular formation maintenance run `run_20251018_1207Z` and the Tehran daily pass locked geometry run `run_20251020_1900Z_tehran_daily_pass_locked` as the primary evidence sets supporting MR-2 to MR-7 compliance.[Ref6][Ref7]
- Highlight supporting artefacts: `artefacts/triangle_run/` (curated snapshot mirroring `run_20251018_1207Z`), `artefacts/run_20251018_1308Z_tehran_daily_pass` (STK validation package), `artefacts/run_20251018_1424Z` (drag-inclusive rerun), and `docs/_authoritative_runs.md` ledger.[Ref6][Ref22]
- Emphasise key metrics: 96 s formation window, \(343.62\,\text{km}\) maximum ground distance within the window vs \(641.89\,\text{km}\) full propagation, command latency 1.5338 h, annual \(\Delta v\) max 14.0371 m/s, Monte Carlo success 100% with \(p_{95}\) \(0.04117\,\text{m/s}\), centroid cross-track 12.142754610722838 km at pass midpoint, worst vehicle 27.759459081570284 km, Monte Carlo centroid \(p_{95}\) 24.180422084370257 km, worst vehicle \(p_{95}\) 39.76060090817563 km.[Ref3][Ref6][Ref7]
- Discuss supporting CSVs (`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`) and plots (`injection_recovery_cdf.svg`) that document the evidence stack.
- Outline STK export directories (`stk/`, `stk_export/`) and naming conventions derived from exporter sanitisation.

### 4.2 Repository Evidence to Anchor
- `artefacts/run_20251018_1207Z/triangle_summary.json` and associated CSV/SVG outputs.[Ref6]
- `artefacts/triangle_run/` for quick-access version of the triangle run.[Ref6]
- `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` deterministic and Monte Carlo summaries, scenario metadata, STK exports.[Ref7]
- `docs/triangle_formation_results.md`, `docs/tehran_daily_pass_scenario.md`, and `docs/tehran_triangle_walkthrough.md` for narrative interpretation and reproduction guidance.[Ref3][Ref5][Ref20]
- `docs/_authoritative_runs.md` for ledger of runs and compliance notes.[Ref22]
- `docs/compliance_matrix.md` for mapping evidence tags to requirements.[Ref8]

### 4.3 Literature & Standards Prompt
- Survey best practices for presenting formation flying evidence in mission design reviews, focusing on how to report windowed vs global metrics, centroid statistics, and maintenance budgets.
- Examine methodologies for interpreting Monte Carlo dispersion outcomes, including presentation of success rates, \(p_{95}\) statistics, and compliance thresholds.
- Review standards for evidence traceability (e.g., NASA NPR 7123.1, ECSS standards) to ensure run documentation aligns with engineering expectations.
- Investigate techniques for summarising command latency and contact probability analyses in operations planning documents.
- Explore case studies on RAAN alignment validation and STK handover packages in comparable missions.

### 4.4 Analytical Narrative Outline
1. **Run Overview:** Describe the purpose, configuration, and output structure of each authoritative run, referencing `docs/_authoritative_runs.md` and scenario metadata blocks.[Ref22]
2. **Triangle Formation Metrics:** Interpret the triangle summary metrics (duration, aspect ratio, side lengths, ground distances), emphasising the difference between the validated 96 s window (max 343.62 km) and full propagation (max 641.89 km). Discuss centroid altitude and orbital element reconstruction.[Ref3][Ref6]
3. **Maintenance & Command Analysis:** Present maintenance metrics (annual \(\Delta v\) per spacecraft, mean/peak differential acceleration), command latency (probability 0.03157, max latency 1.5338 h), and contact window durations.[Ref6]
4. **Injection Recovery & Drag Dispersion:** Analyse Monte Carlo success (300/300, \(p_{95}\) \(0.04117\,\text{m/s}\)), per-satellite metrics, aggregate statistics, and drag dispersion results (density sigma 0.25, drag coefficient sigma 0.05, success rate as reported in CSV).[Ref6]
5. **Daily Pass Alignment:** Detail deterministic centroid metrics (12.142754610722838 km), worst vehicle 27.759459081570284 km, cross-track compliance, Monte Carlo centroid \(p_{95} = 24.180422084370257\,\text{km}\), worst vehicle \(p_{95} = 39.76060090817563\,\text{km}\), and plane intersection analysis.[Ref7]
6. **STK Validation Outputs:** Summarise exported files, naming conventions, and import instructions validated by `docs/how_to_import_tehran_daily_pass_into_stk.md`.[Ref7]
7. **Compliance Mapping:** Connect metrics to MR-2 through MR-7 compliance statements, referencing the compliance matrix evidence tags and narrative notes.[Ref8]
8. **Comparative Analysis:** Contextualise metrics against literature or mission benchmarks, identifying margins and areas requiring further study.

### 4.5 Data Tables & Figures Brief
- Create a consolidated evidence table summarising key metrics for each run (formation window, ground distances, command latency, \(\Delta v\) budgets, Monte Carlo success, centroid statistics) with references to JSON fields and CSV outputs.[Ref6][Ref7]
- Include a figure depicting ground distance over time, highlighting the 96 s window and full propagation maxima, adapted from `triangle_summary.json` samples.[Ref6]
- Present cumulative distribution plots of \(\Delta v\) from `injection_recovery_cdf.svg` and summarise per-satellite statistics.[Ref6]
- Tabulate Monte Carlo centroid results (mean, \(p_{95}\), min, max) from `monte_carlo_summary.json`, emphasising compliance thresholds.[Ref7]
- Reproduce an STK product inventory (ephemerides, satellites, ground tracks, facilities, intervals, event sets) with file naming conventions.[Ref6][Ref7]

### 4.6 Validation & Assurance Hooks
- Reinforce the linkage between run artefacts and automated tests. Note that changes to triangle simulation must maintain unit test expectations (duration ≥90 s, tolerance compliance, success rates ≥0.95).[Ref10]
- Emphasise the need to update `docs/_authoritative_runs.md` and `docs/compliance_matrix.md` when new runs supersede existing evidence, maintaining traceability.[Ref22][Ref8]
- Reference STK validation procedures to confirm run artefacts remain ingestible (naming sanitisation, monotonic epochs, COM automation scripts).[Ref7]
- Highlight the compliance matrix outstanding action for quarterly reruns and the history recorded in `artefacts/triangle_campaign/history.csv`.

### 4.7 Future Work & Risk Register Inputs
- Recommend expanded Monte Carlo campaigns exploring alternative dispersions (e.g., drag coefficient variations, injection biases) and recording statistical summaries in future runs.
- Suggest cross-validation with high-fidelity propagators or STK Astrogator to confirm maintenance budgets and cross-track metrics.
- Identify potential evidence gaps (e.g., sensor alignment errors, data latency analytics) and propose targeted simulations or analyses to close them.
- Encourage maintaining a provenance log summarising software versions, dependency hashes, and exporter versions for each run.

---

## Chapter 5 – STK Validation, Compliance Integration, and Governance

### 5.1 Research Orientation
- Focus on STK interoperability workflows (`docs/stk_export.md`, `docs/how_to_import_tehran_daily_pass_into_stk.md`, `tools/stk_tehran_daily_pass_runner.py`) and how exported artefacts support compliance demonstrations.[Ref6][Ref7][Ref23]
- Discuss compliance governance documented in `docs/compliance_matrix.md`, linking requirements to evidence tags and highlighting outstanding actions (quarterly reruns, drag dispersion documentation).[Ref8]
- Reference `docs/final_delivery_manifest.md` and `docs/tehran_triangle_walkthrough.md` to show how artefacts are packaged and verified for handover.[Ref20][Ref24]
- Integrate `docs/interactive_execution_guide.md` to connect interactive tooling with artefact generation and STK validation pipelines.[Ref19]
- Emphasise the integration of compliance records with verification milestones and configuration management processes.

### 5.2 Repository Evidence to Anchor
- `docs/stk_export.md` for exporter usage guidance and data structure definitions.[Ref6]
- `tools/stk_export.py` and `tests/test_stk_export.py` for exporter implementation and regression coverage.[Ref6][Ref10]
- `docs/how_to_import_tehran_daily_pass_into_stk.md` and `tools/stk_tehran_daily_pass_runner.py` for STK import automation steps and validation captures.[Ref7][Ref23]
- `docs/compliance_matrix.md` for SERB scoring, evidence tags, and outstanding actions.[Ref8]
- `docs/final_delivery_manifest.md` for deliverable register and reproduction procedure.[Ref24]
- `docs/tehran_triangle_walkthrough.md` for procedural reproduction guidance and STK validation steps.[Ref20]
- `docs/interactive_execution_guide.md` for web and debug execution workflows interfacing with STK exports.[Ref19]

### 5.3 Literature & Standards Prompt
- Review STK export best practices, including ephemeris formatting, ground track generation, contact interval management, and COM automation integration.
- Investigate compliance matrix methodologies used in aerospace programmes to benchmark SERB scoring and evidence tagging.
- Survey configuration management and traceability standards (e.g., ISO 10007, ECSS-M-ST-40C) to align repository governance with industry norms.
- Examine digital handover protocols for mission analysis artefacts to refine the final delivery manifest structure.
- Explore interactive execution frameworks for mission analysis to contextualise the repository's FastAPI and CLI tooling.

### 5.4 Analytical Narrative Outline
1. **STK Export Overview:** Explain exporter data structures, interpolation logic, naming sanitisation (`sanitize_stk_identifier`, underscore replacement), and scenario metadata usage.[Ref6]
2. **Validation Workflow:** Detail the steps in `docs/how_to_import_tehran_daily_pass_into_stk.md` (COM automation, 3D/2D graphics inspection, contact interval validation, screenshot capture, metadata confirmation).[Ref7]
3. **Exporter Assurance:** Discuss regression tests ensuring STK compatibility (`tests/test_stk_export.py`) and highlight future checks (ephemeris monotonicity, facility definitions, event sets).[Ref10]
4. **Compliance Matrix Integration:** Present how evidence tags [EV-1] to [EV-5] connect requirements to artefacts, referencing compliance status and outstanding actions.[Ref8]
5. **Handover Artefacts:** Summarise the final delivery manifest contents, reproduction steps, and STK export packaging guidelines.[Ref24]
6. **Interactive Execution Hooks:** Illustrate how web/CLI tools produce artefacts, stream logs, and feed STK validation pipelines.[Ref19]
7. **Governance Alignment:** Relate compliance records to verification milestones and configuration management processes documented in the verification plan and roadmap.[Ref9]
8. **Literature Comparison:** Align repository practices with published standards and case studies, identifying improvements.

### 5.5 Data Tables & Figures Brief
- Compile a table of exported file types (ephemeris `.e`, satellite `.sat`, ground track `.gt`, facility `.fac`, interval `.int`, event `.evt`, scenario `.sc`), describing content, naming convention, and validation step.[Ref6]
- Present a compliance traceability matrix linking MR-1 to MR-7 and SRD requirements to evidence tags, run directories, and validation status.[Ref8]
- Include a flow diagram showing STK validation steps, from exporter invocation to COM automation, screenshot capture, and compliance logging.[Ref7]
- Tabulate outstanding compliance actions with owners, due dates, and mitigation notes (e.g., quarterly rerun scheduling, drag dispersion follow-up).[Ref8]

### 5.6 Validation & Assurance Hooks
- Emphasise the necessity of recording STK validation status in scenario metadata (`validated_against_stk_export`, `alignment_validation`) and compliance matrix notes.[Ref4][Ref5][Ref8]
- Highlight automated guards: exporter tests, scenario smoke tests, triangle CLI tests, interactive execution logs, and `generate_docs_summary.py` (if used) for documentation digests.[Ref10]
- Stress the importance of storing STK validation evidence (SVG captures, logs) alongside run directories and referencing them in compliance records.[Ref7]
- Connect interactive execution monitoring to assurance reporting, ensuring debug logs and run metadata feed audit trails.[Ref19]

### 5.7 Future Work & Risk Register Inputs
- Recommend implementing automated STK validation scripts within CI (e.g., headless COM automation) to ensure exporters remain compatible with STK updates.
- Suggest expanding the compliance matrix to include SRD verification status breakdowns and link to verification plan activities.
- Propose integration of configuration management tools to track exporter versions, COM automation scripts, and validation outcomes.
- Identify risks related to STK version drift or exporter changes and propose mitigation via regression test expansion and change-control procedures.

---

## Chapter 6 – Verification, Testing, and Future Mission Evolution

### 6.1 Research Orientation
- Address the verification and validation strategy articulated in `docs/verification_plan.md`, including method taxonomy, schedule, milestones, resource planning, and risk mitigation.[Ref9]
- Reference automated tests under `tests/`, focusing on unit, integration, and exporter tests safeguarding mission evidence.[Ref10]
- Connect roadmap stages (`docs/project_roadmap.md`) to verification milestones and outstanding actions.
- Incorporate interactive execution capabilities, regression tooling (`tests/baseline_compare.py`), and artefact management practices as part of the verification narrative.[Ref19][Ref10]
- Discuss future mission evolution opportunities (e.g., alternative targets, expanded maintenance policies) supported by repository scaffolding.

### 6.2 Repository Evidence to Anchor
- `docs/verification_plan.md` for verification strategy, matrices, validation activities, schedule, resources, and references.[Ref9]
- `tests/` directory (unit, integration, exporter, documentation consistency) for regression coverage and automated safeguards.[Ref10]
- `docs/project_roadmap.md` for staged mission development tasks and supporting documentation templates.[Ref1]
- `docs/interactive_execution_guide.md` for operational tooling supporting verification rehearsals and debugging.[Ref19]
- `tests/baseline_compare.py` for JSON comparison utility enabling regression analysis against baselines.[Ref10]
- `docs/final_delivery_manifest.md` for reproduction procedures integral to verification closure.[Ref24]

### 6.3 Literature & Standards Prompt
- Consult verification and validation standards (NASA-STD-7009A, ECSS-E-ST-10-02C) referenced in the verification plan to contextualise repository practices.[Ref9]
- Review automated testing frameworks and CI strategies for aerospace mission software, emphasising reproducibility and traceability.
- Explore literature on Monte Carlo verification, dispersion analysis validation, and digital rehearsal workflows for formation-flying missions.
- Investigate risk management and non-compliance handling frameworks to align verification narratives with industry expectations.
- Survey emerging mission evolution strategies (e.g., re-taskable constellations, adaptive maintenance policies) to inform future roadmap updates.

### 6.4 Analytical Narrative Outline
1. **Verification Strategy Overview:** Summarise verification methods per requirement class (analysis, test, demonstration, inspection) and associated artefacts.[Ref9]
2. **Verification Matrix Analysis:** Interpret the matrix linking requirements to responsible teams, evidence artefacts, and completion criteria (e.g., SIM-TRI-2024-01, SIM-TRI-2024-02, OPS-DRYRUN-002).[Ref9]
3. **Validation Activities:** Describe stakeholder scenario reviews, simulation-in-the-loop validation, field data rehearsals, and user acceptance demonstrations, referencing success criteria.[Ref9]
4. **Schedule & Milestones:** Detail VRR (2024-06-14), Simulation Qualification (2024-07-05), HIL Thruster Test (2024-07-26), Operations Dry Run (2024-08-09), CDR (2024-09-12), LRR (2025-02-21), and associated risks/mitigations.[Ref9]
5. **Resource Planning:** Present resource commitments (analysis personnel, HIL facility, simulator licence, workshops, staffing, configuration management upgrades) with cost/effort estimates and procurement lead times.[Ref9]
6. **Testing Infrastructure:** Summarise regression coverage (triangle unit tests, scenario integration tests, exporter tests, documentation consistency checks, baseline comparison tool) and CI workflow (Makefile targets, GitHub Actions).[Ref10][Ref21]
7. **Interactive Tooling & Debugging:** Integrate web/CLI execution workflows into verification rehearsals, emphasising log capture and artefact retention.[Ref19]
8. **Future Mission Evolution:** Propose enhancements (expanded Monte Carlo campaigns, additional targets, advanced maintenance models) aligned with roadmap stages.[Ref1]

### 6.5 Data Tables & Figures Brief
- Reproduce the verification matrix (requirement ID, method, responsible team, evidence, completion criteria) with updates reflecting current artefacts.[Ref9]
- Present a milestone schedule Gantt chart referencing verification plan dates and dependencies.[Ref9]
- Include a resource allocation table with status, owner, estimate, notes, and procurement lead times.[Ref9]
- Summarise automated test coverage in a table mapping tests to requirements and artefacts guarded (triangle unit test, scenario CLI, exporter integrity, documentation consistency).[Ref10]
- Provide a flow diagram illustrating the CI pipeline (`make` targets, GitHub Actions workflow) and regression suites.[Ref21]

### 6.6 Validation & Assurance Hooks
- Emphasise continuous validation via automated tests executed in CI, referencing README guidance and workflow configuration.[Ref21]
- Highlight documentation consistency checks ensuring references and artefact listings remain current (`tests/test_documentation_consistency.py`).[Ref10]
- Note the role of `tests/baseline_compare.py` in detecting drift between regenerated artefacts and authoritative baselines.
- Connect verification plan risk mitigations (supply-chain delays, simulator regression) to compliance matrix outstanding actions and roadmap tasks.[Ref8][Ref9]
- Encourage alignment between verification activities and STK validation workflows to maintain evidence integrity.

### 6.7 Future Work & Risk Register Inputs
- Recommend developing automated dashboards summarising verification status, test results, and artefact freshness.
- Propose expanding verification scope to include closed-loop attitude control simulations and payload alignment analyses.
- Suggest establishing processes for revalidating maintenance budgets upon hardware updates or atmospheric model changes.
- Highlight risks related to resource constraints, schedule slips, or dependency changes, and propose mitigation strategies (buffer allocations, vendor engagement, regression automation).

---

## Appendices – Reusable Prompts, Checklists, and Reference Toolkit

### Appendix A – Literature Review Keyword Bank
- *Formation flying triangular geometries*, *dual-plane LEO constellations*, *relative orbital elements transient formations*, *J2-perturbed RAAN alignment*, *tri-stereo imaging mission design*.
- *Single ground station operations latency*, *command and control contingency agreements*, *X-band downlink scheduling*, *monte carlo injection recovery*, *delta-v budgeting LEO constellations*.
- *STK export validation*, *TEME ephemeris formatting*, *COM automation for STK*, *mission assurance compliance matrices*, *verification plan aerospace standards*.
- *Drag dispersion modelling NRLMSISE-00*, *density scaling Monte Carlo*, *cold gas propulsion formation maintenance*, *command probability analysis*, *contact window optimisation*.
- *Interactive mission analysis tooling*, *FastAPI aerospace simulation*, *debug logging for formation flight*, *JSON artefact provenance*, *regression testing mission pipelines*.

### Appendix B – STK Validation Checklist
1. Confirm exporter configuration (`SimulationResults`, `ScenarioMetadata`) matches scenario metadata (start/stop epochs, coordinate frame TEME).[Ref6]
2. Verify exported filenames are sanitised (spaces replaced with underscores) and ephemeris epochs are strictly monotonic (`tests/test_stk_export.py`).[Ref10]
3. Use `tools/stk_tehran_daily_pass_runner.py` or manual import workflow to load `.sc`, `.sat`, `.e`, `.gt`, `.fac`, `.int`, and `.evt` files into STK 11.2.[Ref7][Ref23]
4. Validate imaging and downlink windows (07:39:25Z–07:40:55Z, 20:55:00Z–21:08:00Z) against `scenario_summary.json` metadata.[Ref7]
5. Inspect ground track alignment over Tehran and confirm centroid cross-track metrics at the access midpoint (12.142754610722838 km).[Ref7]
6. Capture annotated SVG screenshots (3D orbit, 2D ground track, access reports) and archive them alongside run directories.
7. Document validation outcomes in `docs/tehran_daily_pass_scenario.md` and update `config/scenarios/` metadata (`validated_against_stk_export: true`).[Ref5]

### Appendix C – Monte Carlo Campaign Template
- **Scenario:** `config/scenarios/tehran_triangle.json` Monte Carlo block (samples: 300, position \(\sigma = 250\,\text{m}\), velocity \(\sigma = 5\,\text{mm/s}\), recovery_time 43,200 s, \(\Delta v\) budget 15 m/s, seed 314159).[Ref4]
- **Execution:** `python -m sim.scripts.run_triangle --output-dir artefacts/run_YYYYMMDD_hhmmZ` or `python -m sim.scripts.run_triangle_campaign --config config/scenarios/tehran_triangle.json` for scheduled reruns.[Ref16][Ref18]
- **Outputs:** `injection_recovery.csv`, `drag_dispersion.csv`, `triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery_cdf.svg`, `stk/` directory.[Ref6]
- **Metrics to Report:** Success rate (≥0.95, currently 1.0), \(p_{95}\) \(\Delta v = 0.04117\,\text{m/s}\), aggregate max \(\Delta v = 0.05662\,\text{m/s}\), drag dispersion success rate, along-track shifts, command distance deltas.[Ref6]
- **Traceability:** Log run identifier, seeds, tool versions, commit hashes, and STK export status. Update `docs/_authoritative_runs.md` and compliance matrix if campaign supersedes existing evidence.[Ref22][Ref8]

### Appendix D – Command Latency Analysis Prompt
- Extract `command_latency` metrics from `triangle_summary.json` (contact probability 0.03156921635613029, max latency 1.533821385870122 h, mean latency 0.766910692935061 h, contact range 2,200 km).[Ref6]
- Analyse `command_windows.csv` to summarise window start/end times, durations, and periodicity (e.g., 180 s windows per orbit).[Ref6]
- Cross-reference `config/scenarios/tehran_triangle.json` command station coordinates and maintenance cadence to evaluate robustness against MR-5 latency limits.[Ref4]
- Incorporate ConOps risk register mitigations (backup stations, quarterly tests) to contextualise command latency resilience.[Ref11]
- Propose enhancements (additional ground stations, adaptive contact scheduling) and evaluate impact on compliance margins.

### Appendix E – Repository Workflow Quick Reference
1. **Environment Setup:** `make setup` to create virtual environment and install dependencies.[Ref21]
2. **Triangle Simulation:** `make triangle` or `python -m sim.scripts.run_triangle --output-dir artefacts/triangle` to generate summary JSON, CSVs, SVG, STK exports.[Ref16][Ref21]
3. **Scenario Execution:** `make scenario` or `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ` for RAAN alignment and daily pass artefacts.[Ref17][Ref21]
4. **Testing:** `make test` or `pytest` to execute unit, integration, exporter, and documentation consistency tests.[Ref10][Ref21]
5. **STK Validation:** Follow Appendix B workflow, capturing evidence and updating scenario metadata and documentation.[Ref7]
6. **Documentation Digest:** Use `make docs` (if configured) or `tools/generate_docs_summary.py` to refresh documentation artefacts for distribution.[Ref21]
7. **Artefact Management:** Adhere to naming convention `run_YYYYMMDD_hhmmZ`, update `docs/_authoritative_runs.md`, and log assumptions, seeds, model versions in run metadata.[Ref22]

### Appendix F – Risk Register Extension Template
- **Risk ID:** Assign sequential identifier (e.g., R-06).
- **Description:** Brief summary of the risk (e.g., STK exporter incompatibility with new STK release).
- **Cause:** Underlying reason (e.g., STK API change, dependency update).
- **Consequence:** Impact on mission assurance (e.g., inability to validate runs, delayed compliance reporting).
- **Probability/Impact:** Qualitative or quantitative assessment aligned with ConOps practice (Low/Medium/High).[Ref11]
- **Mitigation:** Preventive actions (e.g., maintain regression suite, schedule pre-release testing, pin exporter versions).[Ref6][Ref10]
- **Owner:** Responsible team (e.g., Data Systems Lead).
- **Status:** Open/Monitoring/Closed.
- **Notes:** Links to artefacts, test results, or configuration control board minutes.

---

## References
- [Ref1] `docs/project_overview.md`
- [Ref2] `docs/mission_requirements.md`
- [Ref3] `docs/triangle_formation_results.md`
- [Ref4] `config/scenarios/tehran_triangle.json`
- [Ref5] `config/scenarios/tehran_daily_pass.json`
- [Ref6] `artefacts/run_20251018_1207Z/triangle_summary.json`
- [Ref7] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`
- [Ref8] `docs/compliance_matrix.md`
- [Ref9] `docs/verification_plan.md`
- [Ref10] `tests/`
- [Ref11] `docs/concept_of_operations.md`
- [Ref12] `docs/system_requirements.md`
- [Ref13] `src/constellation/roe.py`
- [Ref14] `src/constellation/orbit.py`
- [Ref15] `src/constellation/geometry.py`
- [Ref16] `sim/formation/triangle.py`
- [Ref17] `sim/scripts/run_scenario.py`
- [Ref18] `sim/scripts/run_triangle_campaign.py`
- [Ref19] `docs/interactive_execution_guide.md`
- [Ref20] `docs/tehran_triangle_walkthrough.md`
- [Ref21] `README.md`
- [Ref22] `docs/_authoritative_runs.md`
- [Ref23] `tools/stk_tehran_daily_pass_runner.py`
- [Ref24] `docs/final_delivery_manifest.md`

### 1.8 Cross-Chapter Dependencies and Research Log Prompts
- Record how Chapter 1 establishes context for subsequent chapters. Note which configuration parameters (altitude, RAAN, maintenance cadence) must be reiterated later and where deeper analysis appears (Chapters 2–4).[Ref3][Ref4]
- Maintain a research log capturing literature citations, noting publication year, relevance to mission requirements, and alignment with repository evidence. Flag gaps requiring further investigation.
- Document assumptions made when extrapolating stakeholder needs (e.g., data latency expectations, disaster response cadence) and align them with ConOps operational scenarios and verification plan milestones.[Ref11][Ref9]
- Identify cross-references to compliance actions (quarterly rerun, drag dispersion update) that should be revisited in Chapters 4, 5, and 6.[Ref8]
- Log open questions regarding requirement evolution (e.g., additional robustness metrics, expanded ground segment) and assign follow-up actions within the roadmap framework.[Ref1]
- Capture reviewer feedback from SERB or CCB minutes, linking to requirement adjustments or documentation updates for traceability.

### 1.9 Checklist for Chapter Completion
1. Requirement statements mapped to stakeholder objectives with citations to mission requirements, system requirements, and ConOps documents.[Ref2][Ref11][Ref12]
2. Governance structure (SERB, CCB, verification milestones) described with references to verification plan and roadmap entries.[Ref1][Ref9]
3. Literature synthesis covering formation flying missions, mission assurance standards, and single-station operations.
4. Compliance status summarised with evidence tags and outstanding actions from the compliance matrix.[Ref8]
5. Forward-looking recommendations aligned with roadmap tasks and verification plan risk mitigations.[Ref1][Ref9]
6. Appendices cross-referenced for reusable prompts (keyword bank, command latency analysis, risk template).

---

### 2.8 Cross-Chapter Dependencies and Research Log Prompts
- Track configuration elements (e.g., Monte Carlo seeds, drag dispersion settings) that feed simulation pipeline chapters and run analysis, ensuring consistent reporting across Chapters 3 and 4.[Ref4][Ref16]
- Maintain notes on any discrepancies between configuration files and documentation (e.g., RAAN values, maintenance intervals) for reconciliation during compliance reviews.[Ref5][Ref8]
- Log literature findings on ROE modelling, RAAN optimisation, and ground-track analysis to inform deeper analytical treatment in Chapters 3 and 4.
- Identify configuration attributes influencing verification scope (e.g., Monte Carlo sample counts, maintenance cadence) and reference them when crafting test plans in Chapter 6.[Ref9][Ref10]
- Record questions about extending configuration support to additional targets or platform variants, feeding future work recommendations.

### 2.9 Checklist for Chapter Completion
1. Programme configuration described with quantitative values and citations to `project.yaml` and scenario JSON files.[Ref3][Ref4][Ref5]
2. LVLH geometry and ROE theory explained with references to simulation code modules (`roe.py`, `orbit.py`, `geometry.py`).[Ref13][Ref14][Ref15]
3. Ground-track and command geometry metrics (contact probability, latency) interpreted with references to triangle summary outputs.[Ref6]
4. Monte Carlo and drag settings detailed, including seeds, dispersions, sample counts, and seeds recorded in configuration files.[Ref4]
5. Proposed figures and tables enumerated, linking to configuration parameters and exporter outputs.
6. Future work and risk considerations captured, pointing to potential configuration drift or expansion.

---

### 3.8 Cross-Chapter Dependencies and Research Log Prompts
- Document how pipeline stage outputs become evidence in Chapter 4, ensuring each metric is traceable to a specific stage and artefact (JSON, CSV, SVG, STK exports).[Ref16][Ref6]
- Record dependencies on configuration metadata (Chapter 2) and compliance requirements (Chapter 5) to maintain consistency.
- Track tooling or dependency changes (e.g., exporter updates, new tests) that must be reflected in verification narratives and risk registers.[Ref6][Ref10]
- Maintain a log of simulation seeds and command arguments used during test campaigns to support reproducibility claims in Chapter 4.
- Note potential automation enhancements (e.g., additional CLI options, interactive features) for future development tasks.

### 3.9 Checklist for Chapter Completion
1. Pipeline stages described sequentially with references to source files and artefact outputs.[Ref17][Ref16]
2. RAAN optimiser behaviour detailed with metrics and references to alignment metadata and run artefacts.[Ref5][Ref7]
3. Simulation outputs (triangle metrics, maintenance, command latency, Monte Carlo, drag) summarised with citations to JSON and CSV files.[Ref6]
4. Exporter integration explained, including sanitisation, interpolation, and naming conventions, with references to exporter code and tests.[Ref6][Ref10]
5. Automation and testing coverage outlined, linking to unit, integration, and exporter tests and CI workflows.[Ref10][Ref21]
6. Future work proposals documented, referencing risk mitigations and roadmap tasks.

---

### 4.8 Cross-Chapter Dependencies and Research Log Prompts
- Maintain a comparative log of run metrics across iterations (e.g., `run_20251018_1207Z`, `run_20251018_1424Z`, `run_20251020_1900Z_tehran_daily_pass_locked`) to detect trends or regressions.[Ref6][Ref7]
- Track how evidence supports compliance statements, noting any margins that shrink over time and require additional analysis or mitigation.[Ref8]
- Record requests for supplementary datasets (e.g., attitude profiles, thermal data) to support future compliance needs.
- Catalogue reviewer comments from SERB or programme boards relating to run evidence, ensuring responses are documented.
- Identify data visualisation needs (plots, tables, animations) for mission reviews and align them with exported artefacts.

### 4.9 Checklist for Chapter Completion
1. Authoritative runs described with context, configuration references, and directory structures.[Ref22][Ref6][Ref7]
2. Key metrics (formation window, ground distances, command latency, \(\Delta v\), Monte Carlo statistics) presented with exact figures and citations.[Ref6][Ref7]
3. CSV and SVG artefacts summarised, with guidance on interpretation and reuse for mission reviews.[Ref6]
4. Compliance mapping documented, linking metrics to requirement statuses and evidence tags.[Ref8]
5. STK validation outputs and naming conventions explained with references to exporter documentation and validation guides.[Ref6][Ref7]
6. Future work recommendations and risk inputs articulated based on evidence trends.

---

### 5.8 Cross-Chapter Dependencies and Research Log Prompts
- Track how compliance actions identified in Chapter 5 inform verification strategies in Chapter 6 and evidence generation in Chapter 4.[Ref8][Ref9]
- Maintain a log of STK validation sessions, including operator, STK version, exporter commit hash, and outcome, to support audits.[Ref7]
- Record enhancements to exporter tooling or validation scripts requiring documentation updates or new regression tests.[Ref6][Ref10]
- Identify governance or configuration management changes (e.g., new evidence tags, policy updates) that must propagate across documentation.

### 5.9 Checklist for Chapter Completion
1. STK export processes documented with references to exporter code, documentation, and tests.[Ref6][Ref10]
2. Validation workflows explained step by step, referencing STK guides and automation scripts.[Ref7][Ref23]
3. Compliance matrix structure and evidence mapping summarised with notes on outstanding actions and mitigation plans.[Ref8]
4. Handover artefact packaging described, linking to final delivery manifest and walkthrough documents.[Ref24][Ref20]
5. Interactive execution integration highlighted, emphasising artefact capture and audit logging.[Ref19]
6. Future work and risk considerations outlined, focusing on exporter compatibility and compliance governance.

---

### 6.8 Cross-Chapter Dependencies and Research Log Prompts
- Record how verification activities depend on configuration, pipeline, and evidence chapters, ensuring references are maintained across documents.[Ref3][Ref16][Ref6]
- Track automated test coverage against requirements, noting any gaps requiring new tests or tooling.[Ref10]
- Maintain a log of milestone readiness indicators (e.g., evidence packages, test completions, stakeholder approvals) for schedule management.[Ref9]
- Document resource utilisation and potential bottlenecks to support programme management decisions.
- Identify prospective mission evolution scenarios (e.g., new targets, payload upgrades) and map them to verification impacts.

### 6.9 Checklist for Chapter Completion
1. Verification strategy, matrix, and validation activities summarised with citations to verification plan sections.[Ref9]
2. Schedule and resource tables reproduced with current data and mitigation notes.[Ref9]
3. Automated testing infrastructure described, referencing relevant tests and CI workflows.[Ref10][Ref21]
4. Interactive tooling usage explained within verification rehearsals, referencing guide documentation.[Ref19]
5. Future mission evolution recommendations aligned with roadmap and resource planning.[Ref1][Ref9]
6. Risk register updates proposed, referencing compliance matrix and ConOps risk entries.[Ref8][Ref11]

---

### Appendix G – Extended Bibliography and Standards Prompt
- Catalogue key journals and conferences relevant to formation flying, mission analysis, and verification (e.g., *Journal of Guidance, Control, and Dynamics*, *Acta Astronautica*, AIAA/AAS Space Flight Mechanics Meeting, ESA GNC Conference).
- List international standards and agency handbooks that should be consulted when drafting the final mission dossier (NASA NPR 7123.1, ISO 21348, CCSDS publications, ECSS standards referenced in the verification plan).[Ref9]
- Encourage consultation of STK user guides, COM automation references, and vendor documentation to maintain exporter compatibility.[Ref6][Ref7]
- Suggest surveying national and regional disaster response policies to strengthen the mission justification and stakeholder alignment narratives.

### Appendix H – Template for Reviewer Comment Resolution
1. **Comment ID:** Assign unique identifier (e.g., CDR-CMT-001).
2. **Source:** Reviewer name, board, and session (e.g., SERB Q3 2025, CCB meeting 2025-06-12).
3. **Summary:** Concise description of the comment.
4. **Affected Artefacts:** List documents, configuration files, or runs requiring updates.
5. **Resolution Plan:** Actions to address the comment, responsible owner, and target date.
6. **Status:** Open/In Progress/Closed, with closure evidence references.
7. **Notes:** Links to updated artefacts, commits, or meeting minutes.

### Appendix I – Glossary of Key Terms and Acronyms
- **MR:** Mission Requirement – high-level mandate governing mission performance and architecture.[Ref2]
- **SRD:** System Requirements Document – derived requirements translating mission needs into system-level constraints.[Ref12]
- **SERB:** Systems Engineering Review Board – governance body overseeing requirement compliance.[Ref8]
- **CCB:** Configuration Control Board – authority managing configuration changes and waivers.[Ref8]
- **RAAN:** Right Ascension of the Ascending Node – orbital parameter governing plane alignment.[Ref5]
- **ROE:** Relative Orbital Elements – vector describing deputy-chosen relative orbit, enabling formation design.[Ref13]
- **STK:** Systems Tool Kit – commercial mission analysis and visualisation platform used for validation.[Ref6]
- **NRLMSISE-00:** Atmospheric density model applied in drag dispersion analysis.[Ref4]
- **\(p_{95}\):** Ninety-fifth percentile statistic capturing dispersion tails in Monte Carlo results.[Ref6][Ref7]

### Appendix J – Document Maintenance and Version Control Guidelines
- Update `docs/_authoritative_runs.md` and `docs/compliance_matrix.md` whenever new runs or evidence supersede existing baselines.[Ref22][Ref8]
- Maintain semantic versioning within `config/project.yaml` metadata (`configuration_version`) and record update dates for traceability.[Ref3]
- Capture run metadata (`run_metadata.json`, `run_log.jsonl`) and ensure naming conventions `run_YYYYMMDD_hhmmZ` remain consistent across artefacts and documentation.
- Use pull request summaries to highlight mission design progress, analytical deliverables, and testing status in accordance with repository guidelines.[Ref21]
- Avoid committing binary artefacts; convert figures to SVG and datasets to text-based formats (CSV, JSON) per repository policy.[Ref21]
- Reference automated tests and verification artefacts in commit messages to support traceability.


### 1.10 Peer Review Question Bank
- How do mission stakeholders prioritise simultaneous imaging versus revisit frequency, and how does this priority manifest in MR-3 and MR-4 tolerances?[Ref2]
- What contingencies exist if the single ground station becomes unavailable beyond the 12-hour latency threshold, and how are these documented in ConOps and verification plans?[Ref11][Ref9]
- Which external standards govern mission assurance for this programme, and how are they reflected in documentation templates and compliance tracking?[Ref9]
- How does the mission handle waiver processes for cross-track excursions up to ±70 km, and what governance ensures waivers remain exceptional?[Ref2][Ref8]
- What risk mitigation strategies are in place for injection dispersions beyond ±5 km/±0.05°, and how does the verification plan address potential exceedance scenarios?[Ref9]

### 2.10 Additional Data Collection Prompts
- Capture detailed notes on how configuration parameters translate into simulation inputs (e.g., mapping JSON fields to function arguments within `sim/formation/triangle.py`).[Ref16]
- Record assumptions regarding atmospheric models (NRLMSISE-00 parameters, solar activity index 150) and evaluate whether alternative models should be considered for sensitivity analysis.[Ref4]
- Document potential parameter ranges for altitude, inclination, or side length adjustments to inform future trades or scenario variants.
- Compile metadata on command station locations and evaluate alternative stations for redundancy (Redu, MBRSC) as suggested in ConOps.[Ref11]
- Assess whether additional metadata fields (e.g., thermal constraints, sensor alignment budgets) are required for future scenario files.

### 3.10 Data Quality and Automation Questions
- Are there pipeline stages susceptible to numerical instability (e.g., integration step size, interpolation accuracy), and how are these mitigated in code?[Ref16][Ref6]
- How does the pipeline handle logging, error reporting, and failure recovery, and what improvements could enhance audit trails?[Ref16][Ref17]
- Are seeds and random state management consistently recorded across Monte Carlo workflows, and how can reproducibility be further reinforced?[Ref4][Ref6]
- What opportunities exist to parallelise Monte Carlo simulations or drag dispersion analyses to reduce execution time without compromising determinism?
- How can pipeline metrics be exposed via dashboards or monitoring tools to support rapid review during development and testing cycles?

### 4.10 Evidence Interpretation Questions
- How do windowed versus full propagation ground distances influence mission assurance narratives, and how should both be presented to avoid ambiguity?[Ref3][Ref6]
- What thresholds or margin policies should be applied when evaluating command latency distributions, and how do they relate to MR-5 compliance?[Ref6][Ref2]
- How are drag dispersion outcomes communicated to stakeholders, and what additional statistics (e.g., confidence intervals) might enhance transparency?[Ref6]
- Do Monte Carlo results reveal any asymmetries across spacecraft, and how should such observations inform maintenance planning or robustness assessments?
- How should evidence be archived to ensure future analysts can reproduce findings without access to historical runtime environments?

### 5.10 Compliance Governance Questions
- What criteria trigger updates to the compliance matrix, and how are changes communicated to stakeholders and governance boards?[Ref8]
- How are non-compliance items escalated, tracked, and closed, and what documentation artefacts capture these processes?[Ref8][Ref9]
- What validation artefacts must accompany STK exports to satisfy audit requirements, and where are these stored in the repository?[Ref7][Ref24]
- How are exporter upgrades vetted to maintain compatibility with STK 11.2 and future releases, and what regression evidence is required before deployment?[Ref6][Ref10]
- How does the interactive execution tooling support compliance monitoring and evidence capture during development cycles?[Ref19]

### 6.10 Forward Planning Questions
- What triggers the transition from simulation-based verification to hardware-in-the-loop or integrated system tests, and how are these transitions documented?[Ref9]
- How will verification scope evolve if the mission expands to additional targets or introduces new payloads, and what documentation updates will be necessary?[Ref1][Ref3]
- Which automated tests should be prioritised for expansion based on current coverage gaps, and how will new tests be integrated into CI workflows?[Ref10][Ref21]
- What resource or schedule risks threaten upcoming milestones, and what contingency plans or buffer allocations are recommended?[Ref9]
- How should lessons learned from verification campaigns be captured and disseminated to inform future mission increments?

---

### Appendix K – Directory and Artefact Inventory Template
| Category | Path | Contents | Notes |
|----------|------|----------|-------|
| Triangle run | `artefacts/run_20251018_1207Z/` | `triangle_summary.json`, CSVs, SVG, `stk/` exports, `run_metadata.json` | Authoritative MR-5 to MR-7 evidence.[Ref6]
| Daily pass locked | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` | Deterministic and Monte Carlo summaries, `stk_export/`, `scenario_summary.json` | Supports MR-2 and SRD-P-001 compliance.[Ref7]
| Triangle curated snapshot | `artefacts/triangle_run/` | Mirror of `run_20251018_1207Z` for analyst onboarding | Use for demos and quick validation.[Ref6]
| STK automation | `tools/stk_tehran_daily_pass_runner.py` | COM automation script for daily pass scenario | Ensure Windows environment for execution.[Ref23]
| Tests | `tests/` | Unit, integration, exporter, documentation consistency, baseline comparison | Guard mission evidence and exporter compatibility.[Ref10]
| Documentation | `docs/` | Mission dossiers, compliance records, verification plans | Update when artefacts change.[Ref1][Ref8][Ref9]

### Appendix L – STK File Naming and Metadata Conventions
- **Scenario Files:** `<ScenarioName>.sc` with underscores replacing spaces (e.g., `Tehran_Triangle_Formation.sc`).[Ref6]
- **Ephemeris Files:** `<SatelliteID>.e` (e.g., `SAT_1.e`), containing TEME positions and velocities with monotonic epochs.[Ref6]
- **Satellite Definition Files:** `<SatelliteID>.sat` linking to ephemeris files and central body Earth.[Ref6]
- **Ground Track Files:** `<SatelliteID>_groundtrack.gt` with time-tagged geodetic points.[Ref6]
- **Facility Files:** `Facility_<Name>.fac` with latitude, longitude, altitude entries (e.g., `Facility_Tehran.fac`).[Ref6]
- **Contact Interval Files:** `Contacts_<Facility>.int` listing start/stop times and durations.[Ref6]
- **Event Sets:** `formation_events.evt` capturing maintenance events with optional \(\Delta v\) values.[Ref6]
- **Metadata:** Record scenario start/stop epochs, coordinate frame (TEME), ephemeris step seconds, and animation step seconds in `ScenarioMetadata`.[Ref6]

### Appendix M – Reproduction and Audit Trail Template
1. **Preparation:** Activate virtual environment, confirm repository revision, and record commit hash.
2. **Execution:** Run the appropriate simulation or scenario command with timestamped output directory; capture console logs.[Ref16][Ref17]
3. **Artefact Verification:** Confirm presence of summary JSON, CSVs, plots, and STK exports; validate file sizes and checksum hashes.
4. **STK Validation:** Follow Appendix B checklist; archive screenshots and validation logs.[Ref7]
5. **Test Execution:** Run `pytest` or targeted test suites; store results and ensure pass status.[Ref10]
6. **Documentation Update:** Modify relevant documentation (scenario overview, compliance matrix, final manifest) to reflect new evidence; cite run identifier and key metrics.[Ref5][Ref8][Ref24]
7. **Change Control:** Submit updates via pull request summarising changes, tests, and evidence impacts; link to governance approvals if required.[Ref21]

### Appendix N – Stakeholder Engagement and Communication Plan
- **Mission Planning Cell:** Provide daily pass alignment updates, centroid compliance metrics, and command latency summaries.[Ref5][Ref6]
- **Guidance and Control Working Group:** Share maintenance budgets, Monte Carlo results, and drag dispersion insights for manoeuvre planning.[Ref6]
- **Ground Segment Integration Team:** Coordinate command latency analyses, contact window schedules, and STK validation evidence.[Ref6][Ref7]
- **Data Systems Lead:** Communicate exporter updates, validation scripts, and compliance tracking status.[Ref6][Ref8]
- **Stakeholder Review Workshops:** Reference verification plan resource allocations and schedule entries to plan engagements.[Ref9]

### Appendix O – Suggested Visualisation Catalogue
- Formation geometry plots (LVLH triangle, centroid trajectory) derived from `triangle_summary.json` samples.[Ref6]
- Ground distance vs time charts showing windowed and full propagation maxima (343.62 km vs 641.89 km).[Ref3][Ref6]
- Command latency histograms and cumulative distributions from `command_windows.csv` and `command_latency` metrics.[Ref6]
- Monte Carlo \(\Delta v\) CDF derived from `injection_recovery_cdf.svg` and CSV data.[Ref6]
- RAAN sweep convergence plots from scenario RAAN optimiser logs and alignment validation metadata.[Ref7]
- STK screenshot montage (3D orbit, 2D ground track, access report) for inclusion in compliance reports.[Ref7]

### Appendix P – Extended Risk Considerations
- **Atmospheric Model Drift:** Increased solar activity could invalidate drag assumptions; plan periodic revalidation of NRLMSISE-00 parameters.[Ref4]
- **Export Format Evolution:** STK version updates may require exporter adjustments; maintain test coverage and compatibility assessments.[Ref6][Ref10]
- **Dependency Updates:** Python package upgrades (NumPy, Pandas, SciPy) may affect numerical results; lock versions and rerun regression tests.[Ref16]
- **Data Latency Exceedance:** Ground station outages or network issues could breach MR-5 limits; rehearse contingency station activation and document response time.[Ref11]
- **Monte Carlo Coverage:** Changing mission profiles may necessitate increased sample counts or alternative dispersion models; plan computational resources accordingly.[Ref4]


### Appendix Q – Metadata Fields Audit Checklist
- Confirm `metadata` blocks in scenario files include `scenario_name`, `description`, `author`, validation flags, and alignment run identifiers.[Ref4][Ref5]
- Verify `reference_orbit` sections record epoch, semi-major axis, eccentricity, inclination, RAAN, argument of perigee, and mean anomaly with appropriate units.[Ref4]
- Check `formation` sections for duration, time step, tolerances, maintenance parameters, command station coordinates, Monte Carlo settings, and drag dispersion parameters.[Ref4]
- Ensure `access_window`, `cross_track_limits`, and `timing` sections in daily pass configuration match authoritative run metrics and schedule bounds.[Ref5]
- Audit `payload_constraints`, `operational_constraints`, and communication parameters for completeness and traceability to ConOps requirements.[Ref5][Ref11]
- Record any missing or outdated fields and propose updates to maintain alignment with documentation and evidence artefacts.

### Appendix R – Chapter Outline Template
1. **Introduction:** Contextualise the chapter within the mission dossier, referencing relevant requirements and artefacts.
2. **Evidence Digest:** Summarise key repository sources, runs, and datasets with inline citations.
3. **Analytical Sections:** Break down analyses into logical subheadings (e.g., geometry synthesis, maintenance analysis, compliance mapping) and note required figures or tables.
4. **Validation Hooks:** Describe how outputs feed tests, STK validation, or compliance records.
5. **Literature Integration:** Identify external references supporting arguments or highlighting gaps.
6. **Recommendations:** Present forward-looking actions, risk considerations, or research opportunities.
7. **Summary:** Recap conclusions, evidence references, and next steps.

### Appendix S – Citation Management Guidance
- Use inline `[RefX]` tags referencing repository documents, artefacts, or code modules listed in the References section to maintain traceability.
- When citing external literature, follow journal or conference citation standards and provide full bibliographic details in chapter-level reference lists.
- For quantitative metrics, cite both the documentation source (e.g., `docs/triangle_formation_results.md`) and the underlying artefact (`triangle_summary.json`) where applicable.[Ref3][Ref6]
- Maintain a citation log to avoid duplication and ensure consistent numbering across chapters; update the reference list when adding new sources.
- Link figures and tables to their data sources, noting whether they are reproduced, adapted, or newly generated from repository datasets.


### Appendix T – Quality Assurance Sign-off Criteria
- Confirm each chapter undergoes peer review focusing on accuracy, completeness, and alignment with repository evidence.
- Ensure figures, tables, and equations include captions, units, and citations; verify data sources against artefact metadata.
- Conduct a final compliance check verifying that all referenced artefacts exist, paths are correct, and metrics match repository datasets.
- Validate that appendices provide actionable prompts and templates, enabling rapid reuse for future analyses and mission increments.
