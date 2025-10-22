# Project Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Preface and Global Instructions
1. Write in British English, sustain an academically rigorous yet accessible tone, and ensure every quantitative statement is supported by a repository artefact, configuration file, or authoritative literature citation.
2. Treat the six chapters below as mandatory deliverables for a single comprehensive "Mission Research & Evidence Brief". Begin the final manuscript directly with "Chapter 1" (no acknowledgements) and proceed sequentially through Chapter 6 without omissions.
3. Use the repository's run-ledger naming convention (`run_YYYYMMDD_hhmmZ`) whenever referencing simulations, and repeat the run identifier the first time each dataset appears within a chapter.
4. Cross-reference Systems Tool Kit (STK 11.2) interoperability considerations in every chapter that draws upon exported ephemerides, contact lists, or Connect automation scripts. Confirm alignment with `tools/stk_export.py`, `docs/how_to_import_tehran_daily_pass_into_stk.md`, and `docs/stk_export.md`.
5. Embed tables, equations, figure prompts, and bullet lists exactly where indicated below. Ensure tables remain text-based (Markdown) to respect repository contribution guidelines.
6. Integrate mission documentation (`docs/`), configuration baselines (`config/`), simulation code (`sim/`), constellation utilities (`src/constellation/`), and regression safeguards (`tests/`) to maintain holistic traceability.
7. Each chapter must close with a numbered reference list aligned to the inline citations you introduce. Consolidate mission artefacts, authoritative literature (2019–2025 focus, with earlier seminal works allowed), and, where relevant, patent or standards references. Use bracketed reference tags (e.g., `[1]`) within the chapter body and list the full citation details at the end of that chapter.
8. Maintain meticulous traceability between Mission Requirements (MR-1 to MR-7), System Requirements (SRD-F/P/O/R series), and compliance evidence as captured in `docs/mission_requirements.md`, `docs/system_requirements.md`, and `docs/compliance_matrix.md`.
9. Explicitly note any dataset limitations, assumptions, or outstanding actions flagged in `docs/compliance_matrix.md`, `docs/verification_plan.md`, and `docs/project_roadmap.md` so reviewers can identify residual risks.
10. The final manuscript should include forward-looking commentary on future simulation campaigns, hardware-in-the-loop testing, and cross-programme coordination opportunities; integrate insights from `docs/project_roadmap.md` and `docs/verification_plan.md`.

---

## Chapter 1 – Mission Framing & Literature Review Foundations

### 1.1 Mission Context Recap
- Summarise the mission intent using `README.md` and `docs/project_overview.md`, highlighting the requirement for a repeatable ninety-second triangular formation above Tehran (6 km side length, ±5% tolerance) and the single-station commanding constraint (≤12 h latency).
- Reiterate the dual-plane configuration (two spacecraft in Plane A, one in Plane B) and link these allocations to MR-1–MR-4 and SRD-F-001/SRD-P-001 as catalogued in `docs/mission_requirements.md` and `docs/system_requirements.md`.
- Describe stakeholder motivations (civil protection, infrastructure monitoring) from `docs/concept_of_operations.md`, emphasising imaging/downlink cadence and data latency objectives.

### 1.2 Literature Review Expectations
- Conduct a comprehensive literature review (2019–2025 preferred) across the following themes, integrating seminal older references when indispensable:
  1. **Relative Orbital Elements (ROE) and Triangular Formations** – e.g., D'Amico et al. (2005) plus contemporary refinements; emphasise analytical conditions enabling equilateral LVLH geometries and observability benefits.
  2. **Repeating Ground-Track and RAAN Optimisation Techniques** – align with the RAAN solver documented in `sim/scripts/run_scenario.py` and the locked value \(350.7885044642857^{\circ}\) stored in `config/scenarios/tehran_daily_pass.json`.
  3. **Low Earth Orbit Perturbation Modelling** – highlight \(J_2\), drag, and solar activity models (NRLMSISE-00), connecting to `config/project.yaml` and `sim/scripts/perturbation_analysis.py`.
  4. **Formation Maintenance and Delta-V Budgeting for Small Satellites** – compare cold-gas, electric, and hybrid options relative to the \(15\,\text{m/s}\) annual cap (MR-6, SRD-P-004) validated by `run_20251018_1207Z`.
  5. **Command and Control Latency Studies** – benchmark single-station architectures vs. multi-station networks; integrate insights from MR-5/SRD-O-001 and the command latency metrics (max \(1.5338\,\text{h}\)) recorded in `artefacts/run_20251018_1207Z/triangle_summary.json`.
  6. **Resilience Strategies Against Injection Dispersions** – summarise Monte Carlo correction philosophies aligning with SRD-R-001 and the 300-trial campaign embedded in `run_20251018_1207Z`.
  7. **STK 11.2 Interoperability Practices** – include best practices for TEME/J2000 conversions, Connect automation, and validation workflows (tie to `docs/how_to_import_tehran_daily_pass_into_stk.md`, `docs/stk_export.md`, and `tools/stk_export.py`).
- For each theme, cite at least two recent articles (journal, conference, or authoritative technical reports). Where the repository provides internal memoranda (e.g., `docs/triangle_formation_results.md`), integrate them as baseline references while contrasting with external sources.

### 1.3 Repository Document Crosswalk
- Create a table mapping key repository documents to their thematic coverage for quick reference. Include columns: `Document`, `Theme(s)`, `Key Metrics`, `Relevant Requirements`, `Notes on STK Validation`.
- Populate the table with at least the following artefacts: `docs/project_overview.md`, `docs/mission_requirements.md`, `docs/system_requirements.md`, `docs/concept_of_operations.md`, `docs/compliance_matrix.md`, `docs/triangle_formation_results.md`, `docs/tehran_daily_pass_scenario.md`, `docs/verification_plan.md`, and `docs/project_roadmap.md`.
- Highlight where each document references specific run identifiers, noting whether the evidence is tagged as authoritative in `docs/_authoritative_runs.md`.

### 1.4 Research Questions & Hypotheses
- Restate the primary and secondary research questions from `proposal.md`, updating the context to emphasise the confirmed ninety-six-second access window and RAAN lock achieved after the repository's latest simulations.
- Formulate hypotheses that can be tested against the repository datasets (e.g., "The \(p_{95}\) centroid offset remains below \(24.2\,\text{km}\) over a one-year horizon when RAAN is maintained within \(\pm0.01^{\circ}\) of the optimised solution.").
- Link each hypothesis to the relevant simulation outputs or code modules that can validate or refute it (e.g., `sim/formation/triangle.py`, `tests/unit/test_triangle_formation.py`).

### 1.5 Chapter 1 Narrative Flow Guidance
- Outline a suggested narrative path: start with mission motivation, segue into requirement framing, transition to a literature deep-dive grouped by the themes above, and close with gap identification that motivates Chapters 2–6.
- Emphasise how the literature review should justify the adoption of specific modelling choices present in the repository (e.g., why LVLH-based equilateral formations remain attractive given recent formation-control research).

### 1.6 Chapter 1 Visual, Equation, and Table Prompts
- **[Suggested Figure 1.1]** Conceptual illustration of the equilateral LVLH formation over Tehran, adapted from the centroid time-series in `artefacts/triangle_run/triangle_summary.json`.
- **[Suggested Figure 1.2]** RAAN convergence plot derived from `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/solver_settings.json`, overlaying pre- and post-optimisation values.
- **[Suggested Equation 1.1]** Hill–Clohessy–Wiltshire (HCW) relative motion solution linking \(\Delta a\), \(\Delta \lambda\), and centroid phasing, sourced from `src/constellation/roe.py` utilities.
- **[Suggested Table 1.1]** Literature matrix comparing formation-control approaches, including columns for author/year, method (impulsive, differential drag, hybrid), applicable altitude, and reported \(\Delta v\) cost.

### 1.7 Chapter 1 Reference Expectations
- Minimum of 12 references, including at least four external peer-reviewed sources (2019–2025) and four repository artefacts.
- Include standards or best-practice references (e.g., NASA-STD-7009A, ECSS-E-ST-10-02C) where verification methodology intersects with literature discussions.

---

## Chapter 2 – Requirements, Configuration Baselines, and Traceability

### 2.1 Requirement Hierarchy Overview
- Provide a structured exposition of MR-1 to MR-7 and their descendant SRD items, using `docs/mission_requirements.md`, `docs/system_requirements.md`, and `docs/compliance_matrix.md` as primary sources.
- Explain how each requirement is currently assessed as **Compliant (C)**, referencing the evidence tags [EV-1]–[EV-5] described in `docs/compliance_matrix.md`.
- Discuss traceability mechanisms outlined in `docs/verification_plan.md` and `docs/system_requirements.md`, including Configuration Control Board (CCB) processes.

### 2.2 Configuration Artefacts and Parameter Baselines
- Detail the contents of `config/project.yaml`, emphasising `global`, `platform`, `orbit`, `simulation`, and `output` sections. Highlight how these baselines feed into simulations and documentation.
- Describe `config/scenarios/tehran_triangle.json` and `config/scenarios/tehran_daily_pass.json`, focusing on fields such as `formation.side_length_m`, `formation.maintenance.delta_v_budget_mps`, `access_window`, `cross_track_limits`, and `raan_alignment` parameters.
- Connect configuration fields to mission requirements (e.g., `cross_track_limits.primary_km` aligning with MR-2 tolerance, `formation.monte_carlo.samples` with SRD-R-001).

### 2.3 Traceability Matrix Construction
- Present a Markdown table linking each requirement to: `Configuration Field(s)`, `Simulation Module(s)`, `Authoritative Run(s)`, `Test Coverage`, `Outstanding Actions`.
- Populate the table for at least MR-1–MR-7 and SRD-F-001, SRD-P-001, SRD-P-003, SRD-O-001, SRD-P-004, SRD-R-001. Include references to `tests/unit/test_triangle_formation.py`, `tests/test_stk_export.py`, and relevant integration tests.
- Annotate rows with compliance status from `docs/compliance_matrix.md` and note where future work (e.g., sensor alignment effects, Monte Carlo extensions) remains.

### 2.4 Configuration Change Management
- Summarise procedures for updating configurations based on `config/README.md`, `docs/compliance_matrix.md`, and `docs/verification_plan.md`.
- Discuss versioning, metadata updates, and STK export regeneration requirements whenever `project.yaml` or scenario JSON files change.
- Highlight the expectation to regenerate artefacts via `tools/stk_export.py` and rerun regression tests after configuration edits.

### 2.5 Chapter 2 Narrative Flow Guidance
- Recommend a narrative that transitions from requirement hierarchy to configuration instantiation, emphasising traceability. Encourage interleaving of textual explanations with tables capturing requirement-to-artefact mapping.
- Stress the relationship between configuration parameters and the simulation pipeline, preparing the reader for Chapter 3.

### 2.6 Chapter 2 Visual, Equation, and Table Prompts
- **[Suggested Table 2.1]** Mission Requirement Compliance Summary (adapted from `docs/compliance_matrix.md`, Table 1).
- **[Suggested Table 2.2]** Configuration Parameter Crosswalk linking `project.yaml` values to requirement IDs and simulation hooks.
- **[Suggested Figure 2.1]** Sankey-style diagram illustrating traceability from mission objectives through configuration, simulation outputs, and compliance evidence (construct from repository data).
- **[Suggested Equation 2.1]** \(\Delta v_{annual} = N_{burns} \times \Delta v_{per\_burn}\) with parameters drawn from `artefacts/run_20251018_1207Z/triangle_summary.json` maintenance metrics.

### 2.7 Chapter 2 Reference Expectations
- At least 10 references, blending repository documentation (requirements, configuration guides, compliance matrix) with systems engineering standards or traceability best practices.

---

## Chapter 3 – Simulation Infrastructure and Toolchain Integration

### 3.1 Pipeline Overview
- Describe the stage sequence implemented by `sim/scripts/run_scenario.py`: RAAN alignment, access node discovery, mission phase synthesis, two-body propagation, high-fidelity \(J_2\)+drag propagation, metric extraction, and STK export.
- Explain how `sim/scripts/scenario_execution.py`, `sim/scripts/baseline_generation.py`, and `sim/scripts/run_triangle.py` interface with the broader pipeline.
- Note dependencies on `sim/scripts/configuration.py`, `sim/scripts/perturbation_analysis.py`, and the role of `tools/stk_export.py` in serialising results.

### 3.2 Triangle Formation Engine
- Analyse `sim/formation/triangle.py`, detailing how it loads configuration files, computes LVLH offsets, propagates via Keplerian motion, calculates geometric metrics (area, aspect ratio, side lengths), and assembles maintenance/latency/injection statistics.
- Highlight integration with `constellation.geometry`, `constellation.orbit`, and `constellation.roe`, referencing functions like `propagate_kepler`, `cartesian_to_classical`, and `triangle_aspect_ratio`.
- Discuss the `TriangleFormationResult` dataclass structure and how `to_summary()` prepares JSON artefacts for documentation and regression tests.

### 3.3 STK Export Workflow
- Detail the data classes in `tools/stk_export.py` (`StateSample`, `PropagatedStateHistory`, `GroundTrack`, `GroundContactInterval`, `FacilityDefinition`, `FormationMaintenanceEvent`, `ScenarioMetadata`, `SimulationResults`).
- Explain the sanitisation logic (`sanitize_stk_identifier`, `unique_stk_names`) and file outputs (`*.e`, `*.sat`, `*.gt`, `*.fac`, `Contacts_*.int`, `formation_events.evt`, scenario `.sc`).
- Reference `tests/test_stk_export.py` to demonstrate regression coverage ensuring monotonic epochs, naming consistency, and asset linkages.

### 3.4 Automation & Interactive Tools
- Summarise the FastAPI interface (`run.py`), debugging companion (`run_debug.py`), and STK automation script (`sim/scripts/run_stk_tehran.py`) as described in `docs/interactive_execution_guide.md`.
- Explain how `make` targets (see `Makefile`) orchestrate environment setup, linting, testing, simulations (`make triangle`, `make simulate`, `make scenario`), and documentation snapshots.
- Discuss containerisation or environment expectations (Python 3.10, dependencies pinned in `requirements.txt`, poetry/pyproject references if applicable).

### 3.5 Metrics and Artefact Management
- Outline the structure of JSON and CSV artefacts generated by the simulation pipeline (e.g., `triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, `scenario_summary.json`, `deterministic_summary.json`, `monte_carlo_summary.json`).
- Emphasise metadata fields capturing seeds, tolerances, epoch bounds, and STK validation flags.
- Describe data-retention expectations and naming conventions, referencing `artefacts/triangle_run/run_metadata.json` and `docs/compliance_matrix.md` (evidence catalogue).

### 3.6 Regression Safeguards
- Detail unit and integration tests ensuring pipeline fidelity: `tests/unit/test_triangle_formation.py`, `tests/unit/test_geometry.py`, `tests/unit/test_orbit.py`, `tests/unit/test_roe.py`, `tests/unit/test_scenario_configuration.py`, integration tests under `tests/integration/`.
- Explain continuous integration expectations described in `README.md` and `Makefile`, including GitHub Actions workflow references.

### 3.7 Chapter 3 Narrative Flow Guidance
- Suggest starting with an architectural overview, then delving into triangle simulation specifics, pipeline orchestration, STK export integration, automation tooling, and regression strategy.
- Encourage inclusion of pseudo-code snippets or flowcharts to aid comprehension.

### 3.8 Chapter 3 Visual, Equation, and Table Prompts
- **[Suggested Figure 3.1]** Flow diagram of the scenario runner pipeline showing data transformations and artefact outputs (source: `sim/scripts/run_scenario.py`).
- **[Suggested Figure 3.2]** Class diagram of STK exporter data classes (`tools/stk_export.py`).
- **[Suggested Equation 3.1]** Great-circle distance computation (Haversine) as implemented via `constellation.orbit.haversine_distance` to quantify ground-track separation.
- **[Suggested Table 3.1]** Artefact inventory mapping each output file to its generating script, data contents, and downstream consumer.

### 3.9 Chapter 3 Reference Expectations
- Minimum of 12 references combining code modules, documentation guides, regression tests, and external software engineering or verification standards relevant to simulation toolchains.

---

## Chapter 4 – Authoritative Runs, Quantitative Evidence, and Data Interpretation

### 4.1 Run Ledger Overview
- Introduce the authoritative run register in `docs/_authoritative_runs.md`, detailing each listed run, scenario purpose, directory, key artefacts, and compliance linkage.
- Emphasise the status of each run (baseline vs. exploratory), noting that `run_20251018_1207Z` and `run_20251020_1900Z_tehran_daily_pass_locked` are baseline evidence sets.

### 4.2 Tehran Triangle Formation Evidence (`run_20251018_1207Z`)
- Summarise the key metrics from `triangle_summary.json`: formation window duration (96 s), start/end times, mean triangle area (\(1.5588\times10^7\,\text{m}^2\)), maximum aspect ratio (≈1.00000000000018), side-length stability.
- Discuss ground-distance metrics (343.62 km maximum within validated window; 641.89 km across full propagation) and justify why reports must cite the window-constrained figure for compliance.
- Analyse maintenance metrics: per-spacecraft annual \(\Delta v\) (SAT-1 \(9.33\,\text{m/s}\), SAT-2 \(9.29\,\text{m/s}\), SAT-3 \(14.04\,\text{m/s}\)), fleet max \(14.04\,\text{m/s}\), consistent with MR-6.
- Present command latency outcomes (max \(1.5338\,\text{h}\), mean \(0.7669\,\text{h}\), contact probability 0.0316) supporting MR-5.
- Describe Monte Carlo injection recovery statistics (300/300 success, \(p_{95}\) \(0.0412\,\text{m/s}\) delta-v) and drag dispersion results (refer to `artefacts/triangle_run/drag_dispersion.csv` if necessary).

### 4.3 Tehran Daily Pass Alignment (`run_20251020_1900Z_tehran_daily_pass_locked`)
- Detail deterministic metrics from `deterministic_summary.json`: centroid cross-track \(12.143\,\text{km}\), worst-vehicle \(27.759\,\text{km}\) at evaluation, compliance with ±30 km/±70 km thresholds, orbital period, altitude range.
- Interpret Monte Carlo statistics from `monte_carlo_summary.json`: centroid mean \(23.914\,\text{km}\), \(p_{95}\) \(24.180\,\text{km}\); worst vehicle \(p_{95}\) \(39.761\,\text{km}\); compliance fractions (primary/waiver 1.0).
- Explain solver configuration stored in `solver_settings.json`, referencing RAAN optimisation parameters, evaluation windows, and seeds.
- Link these outcomes to MR-2, SRD-P-001, and compliance matrix entries.

### 4.4 Additional Campaigns and Snapshots
- Summarise the curated snapshot `artefacts/triangle_run/` (mirrors `run_20251018_1424Z`) and the drag dispersion summary recorded in `run_metadata.json`.
- Mention exploratory runs (`run_20260321_0740Z`, `run_20260321_0740Z_tehran_daily_pass_resampled`) and clarify their non-baseline status while noting methodological insights (e.g., resampling workflow tests).
- Reference `artefacts/run_20251018_1308Z_tehran_daily_pass` and `artefacts/run_20251020_0813Z_tehran_daily_pass` if relevant to demonstrate STK validation or solver evolution.

### 4.5 Data Interpretation & Uncertainty Analysis
- Discuss interpretation strategies for balancing deterministic vs. probabilistic evidence, referencing compliance guidance in `docs/compliance_matrix.md` and the verification plan.
- Evaluate uncertainties: integrator tolerances, atmospheric model assumptions, command latency modelling simplifications (contact probability 0.0316 indicates ~15 passes/day assumptions).
- Note outstanding evidence actions from `docs/compliance_matrix.md` (e.g., incorporate sensor alignment effects in future reruns).

### 4.6 Chapter 4 Narrative Flow Guidance
- Recommend structuring the chapter around each authoritative run, followed by cross-run synthesis and uncertainty discussion.
- Encourage inclusion of comparisons (e.g., windowed vs. full propagation distances) and compliance statements directly tied to requirement IDs.

### 4.7 Chapter 4 Visual, Equation, and Table Prompts
- **[Suggested Table 4.1]** Summary of key metrics for `run_20251018_1207Z`: geometry, maintenance, command latency, injection recovery, drag dispersion.
- **[Suggested Table 4.2]** Summary of `run_20251020_1900Z_tehran_daily_pass_locked`: RAAN, centroid metrics, compliance fractions, Monte Carlo outcomes.
- **[Suggested Figure 4.1]** CDF plot of injection recovery \(\Delta v\) from `injection_recovery_cdf.svg` (ensure reproduction as SVG).
- **[Suggested Figure 4.2]** Cross-track time histories (deterministic vs. Monte Carlo mean) derived from `deterministic_cross_track.csv` and `monte_carlo_cross_track.csv`.
- **[Suggested Equation 4.1]** Centroid absolute cross-track calculation, linking great-circle distance metrics with RAAN alignment conditions.

### 4.8 Chapter 4 Reference Expectations
- Minimum of 12 references, including the authoritative artefact paths, compliance documentation, and any external validation literature supporting uncertainty treatment.

---

## Chapter 5 – Results Discussion, Compliance Integration, and STK Validation

### 5.1 Compliance Synthesis
- Reconcile simulation outcomes with requirement compliance status recorded in `docs/compliance_matrix.md` and `docs/system_requirements.md`.
- Highlight margins for MR-1–MR-7, referencing specific metrics (e.g., MR-2 centroid margin \(17.857\,\text{km}\) vs. ±30 km limit, MR-6 \(0.96\,\text{m/s}\) delta-v margin).
- Discuss how regression tests (`tests/unit/test_triangle_formation.py`, `tests/test_stk_export.py`) guard these compliance statements.

### 5.2 STK Validation Workflow Integration
- Detail the import procedures from `docs/how_to_import_tehran_daily_pass_into_stk.md` and `docs/tehran_triangle_walkthrough.md`, emphasising the role of `tools/stk_export.py` outputs.
- Discuss Connect automation (e.g., `sim/scripts/run_stk_tehran.py`), highlighting naming conventions enforced by `sanitize_stk_identifier` and `unique_stk_names`.
- Note any observed limitations (e.g., requirement to maintain TEME frame, ensuring monotonic ephemeris time tags).

### 5.3 Discussion of Operational Scenarios
- Integrate findings with operational scenarios in `docs/concept_of_operations.md`, especially daily imaging passes, recovery manoeuvres, and ground station outages.
- Reflect on risk register entries (R-01 to R-05), linking simulation evidence to mitigation strategies (e.g., command latency margins supporting R-01 mitigation).

### 5.4 Sensitivity and Trade Studies
- Discuss sensitivity analyses (e.g., RAAN perturbations, drag dispersions, Monte Carlo spreads) and their implications for operations and maintenance budgets.
- Identify trade-off opportunities (altitude vs. delta-v, plane phasing vs. revisit time) supported by repository artefacts.
- Reference `docs/project_roadmap.md` Stage 4 and Stage 5 deliverables for future analyses.

### 5.5 Visual, Equation, and Table Prompts
- **[Suggested Table 5.1]** Compliance matrix excerpt summarising requirement, metric, margin, evidence, outstanding actions (update from `docs/compliance_matrix.md`).
- **[Suggested Figure 5.1]** STK screenshot placeholders or description referencing importer workflow (ensure actual images are generated externally as SVG when implementing the manuscript).
- **[Suggested Equation 5.1]** Command latency expectation formula linking pass frequency and probability to expected latency (`mean_latency_hours = 1/(pass_rate * contact_probability)` logic derivable from `triangle_summary.json`).

### 5.6 Chapter 5 Narrative Flow Guidance
- Encourage a structure that opens with compliance confirmation, transitions to STK validation, then broadens into operational discussion and sensitivities.
- Ensure the chapter clearly communicates mission readiness, residual risks, and alignment with verification plans.

### 5.7 Chapter 5 Reference Expectations
- At least 10 references, combining compliance documentation, operational guides, risk registers, STK validation notes, and relevant standards.

---

## Chapter 6 – Conclusions, Recommendations, and Future Work

### 6.1 Synthesis of Findings
- Summarise key results from Chapters 1–5, explicitly tying back to mission objectives and research questions.
- Highlight validated achievements: sustained ninety-six-second formation, RAAN lock, compliance with MR-1–MR-7, STK interoperability.

### 6.2 Limitations and Assumptions
- Enumerate modelling and operational assumptions (e.g., perfect state knowledge, cold-gas propulsion performance, ground station uptime) and discuss their impact on confidence levels.
- Reference outstanding actions from `docs/compliance_matrix.md` and `docs/verification_plan.md` (sensor alignment effects, future STK validation reruns, automation enhancements).

### 6.3 Recommendations for Future Work
- Outline next steps aligned with `docs/project_roadmap.md` Stage 4 (perturbation & maintenance strategy refinement) and Stage 5 (verification & validation).
- Suggest enhancements: integration of higher-fidelity perturbations (SRP, third-body effects), closed-loop control simulations, hardware-in-the-loop testing (refer to `docs/verification_plan.md` milestones), multi-station command studies, and payload alignment modelling.
- Include recommendations on data management (e.g., automated archiving of SVG figures, expanded regression coverage).

### 6.4 Broader Applications and Collaboration Opportunities
- Discuss applicability of the methodology to other mid-latitude targets or alternative mission objectives (e.g., disaster monitoring, scientific campaigns).
- Identify collaboration prospects with external agencies or universities for validation, referencing potential partners noted in `docs/concept_of_operations.md` (e.g., ESA Redu, MBRSC).

### 6.5 Chapter 6 Visual, Equation, and Table Prompts
- **[Suggested Table 6.1]** Summary of recommended future campaigns, including objective, responsible team, required resources, schedule alignment (tie to `docs/verification_plan.md` milestones).
- **[Suggested Figure 6.1]** Roadmap timeline highlighting upcoming verification milestones (VRR, Simulation Qualification, HIL tests, CDR, LRR).
- **[Suggested Equation 6.1]** Simple delta-v budget forecasting relation for extended mission durations (extend Eq. 2.1 with reserve fraction from `config/project.yaml`).

### 6.6 Chapter 6 Reference Expectations
- Minimum of 8 references, combining prior chapters' key artefacts, roadmap documents, verification plan entries, and relevant literature on future mission extensions.

---

## Appendices and Supporting Material Instructions

### Appendix A – Data Artefact Index
- Provide an expanded table listing every referenced artefact directory (`artefacts/run_20251018_1207Z/`, `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/`, `artefacts/triangle_run/`, `artefacts/run_20251018_1424Z/`, `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/`, etc.).
- For each entry, include columns for `Run ID`, `Purpose`, `Key Files`, `STK Export Status`, `Notes`. Explicitly note whether the directory is baseline, exploratory, or curated snapshot.

### Appendix B – Script and Module Catalogue
- Compile a table summarising key scripts/modules (`sim/scripts/run_scenario.py`, `sim/scripts/run_triangle.py`, `sim/scripts/run_triangle_campaign.py`, `sim/scripts/run_stk_tehran.py`, `sim/scripts/extract_metrics.py`, `sim/scripts/perturbation_analysis.py`, `sim/scripts/configuration.py`, `run.py`, `run_debug.py`, `tools/stk_export.py`, `src/constellation/*`).
- Include columns for `Module`, `Functionality`, `Primary Inputs`, `Primary Outputs`, `Tests Covering Module`, `Relevant Requirements`.

### Appendix C – Test Coverage Summary
- Document unit and integration tests, linking them to requirements and artefacts. Include `tests/unit/test_triangle_formation.py`, `tests/unit/test_geometry.py`, `tests/unit/test_orbit.py`, `tests/unit/test_roe.py`, `tests/unit/test_scenario_configuration.py`, `tests/test_stk_export.py`, `tests/test_documentation_consistency.py`, integration harnesses under `tests/integration/`.
- Note the `Makefile` targets `make test`, `make lint`, `make simulate`, `make triangle`, `make scenario`, `make baselines`, `make docs`, `make clean` and describe their role in maintaining coverage.

### Appendix D – Standards and External References
- List all standards, handbooks, and external guidance documents cited (NASA-STD-7009A, ECSS-E-ST-10-02C, ISO/IEC 27001, ESA Ground Station Manual, etc.).
- Provide context for how each standard informs modelling, verification, or operations practices in the mission.

### Appendix E – Glossary and Acronyms
- Develop a glossary covering mission-specific terminology (e.g., LVLH, RAAN, ROE, MR, SRD, CCB, TMOC, TM/TC, TEME, STK, Monte Carlo, injection recovery, delta-v, contact probability).
- Define each term succinctly, referencing relevant repository artefacts or literature where applicable.

### Appendix F – Citation Management Plan
- Specify expectations for citation style (e.g., bracketed numeric references aligned with chapter-specific lists), reference management tools, and repository cross-references.
- Encourage inclusion of DOIs, report identifiers, or dataset URIs for external sources. Require git commit hashes or run IDs for internal data citations.

---

## Writing Checklist for the Final Manuscript
1. Confirm each chapter includes the mandated sections, figure/table/equation prompts, and minimum reference counts.
2. Validate that STK interoperability notes appear wherever exported artefacts are discussed.
3. Ensure every requirement ID (MR or SRD) mentioned in prose links to a compliance statement backed by artefacts or tests.
4. Cross-check that run identifiers are spelled exactly as stored in `docs/_authoritative_runs.md` and `artefacts/` directories.
5. Verify that quantitative values (e.g., \(12.142754610722838\,\text{km}\) centroid offset, \(14.037121738419275\,\text{m/s}\) max annual delta-v, \(0.04117037812182684\,\text{m/s}\) injection \(p_{95}\)) match repository artefacts to at least three significant figures, unless rounding is justified.
6. Include explicit statements on model assumptions, validation status, and open actions at the end of each chapter.
7. Maintain consistent terminology (e.g., "Tehran Daily Pass Scenario", "Tehran Triangular Formation", "Formation Satellite Programme Phase 2").
8. Double-check alignment between textual descriptions and table/figure references to avoid discrepancies.
9. Prepare supplementary materials (SVG figures, CSV tables) for inclusion or referencing, ensuring they remain text-based or vector-based as required by repository policy.
10. Conduct a final audit to confirm the manuscript is self-contained, reproducible (links to scripts and artefacts), and suitable for academic peer review or design reviews.


### Chapter 1 Detailed Task Checklist
1. Catalogue the parameter values for the Tehran centroid (latitude 35.6892°, longitude 51.3890°) and the triangle side length (6000 m) to contextualise literature comparisons.
2. For each literature theme, identify at least one dataset or analytical expression from the repository that demonstrates the concept (e.g., use `triangle_summary.json` to exemplify LVLH geometry maintenance).
3. Document historical mission analogues (TanDEM-X, GRACE-FO, MMS, PRISMA, CanX-4/5) and contrast their formation regimes with the transient triangle requirement.
4. Tabulate current best practices for RAAN locking, referencing `run_20251020_1900Z_tehran_daily_pass_locked` and noting solver parameters like time step (10 s) and propagation margin (300 s).
5. Summarise atmospheric density model assumptions (NRLMSISE-00, solar activity index 150) from `config/project.yaml` and align them with literature on drag prediction accuracy.
6. Collate command-and-control case studies where single-station architectures were validated, highlighting how the mission's 1.5338 h latency margin compares to industry norms.
7. Compile resilience research focusing on injection dispersions of ±5 km along-track and ±0.05° inclination, matching MR-7's envelope and citing Monte Carlo outcomes.
8. Investigate STK integration white papers or vendor guidance to support exporter workflows, ensuring compatibility with the repository's text-based artefacts.
9. Record all assumptions about sensor payloads (multispectral VNIR/SWIR, 0.05° pointing accuracy) from `config/project.yaml` to inform later performance analyses.
10. Establish a bibliography management approach that links DOIs, run IDs, and git commit hashes for reproducibility notes.

### Chapter 2 Extended Guidance
1. Provide paragraph-level explanations for each mission requirement, clarifying stakeholders and success criteria drawn from `docs/concept_of_operations.md` and `docs/mission_requirements.md`.
2. Enumerate how MR-2's ±30 km/±70 km tolerances correspond to scenario JSON fields, specifically `cross_track_limits.primary_km` and `cross_track_limits.waiver_km`.
3. Detail the interpretation of `formation.monte_carlo.samples` (300) and how it underpins SRD-R-001 resilience assessments.
4. Explain the linkage between `formation.maintenance.delta_v_budget_mps` (15 m/s) and the maintenance metrics recorded across runs, including the derivation of weekly burn cadence (interval_days = 7).
5. Illustrate how `formation.command.contact_range_km` (2200 km) maps to command latency calculations within the triangle summary metrics.
6. Summarise metadata fields `validated_against_stk_export` and `alignment_validation` to show how configuration files capture STK readiness and run provenance.
7. Highlight risk governance processes described in `docs/compliance_matrix.md` (Non-Compliance Log, SERB oversight) and relate them to configuration updates.
8. Include a discussion on version control discipline: semantic versioning in `project.yaml`, run directory naming conventions, and expectations for artefact archival.
9. Provide a checklist ensuring that any configuration change is accompanied by rerunning affected simulations, updating `docs/_authoritative_runs.md`, and revising compliance entries.
10. Present a mapping between configuration parameters and tests: e.g., `tehran_triangle.json` verified by `tests/unit/test_scenario_configuration.py` and `tests/unit/test_triangle_formation.py`.

### Chapter 3 Extended Guidance
1. Describe the command-line interfaces for `run_triangle.py`, `run_scenario.py`, and `run_stk_tehran.py`, including default arguments (`--config`, `--output-dir`, dry-run options).
2. Break down the data flow within `simulate_triangle_formation`: configuration loading, LVLH frame generation, propagation loops, metric accumulation, summary serialisation.
3. Itemise each metric stored in `TriangleFormationResult.metrics`, clarifying how `formation_window`, `triangle`, `ground_track`, `orbital_elements`, `maintenance`, `command_latency`, `injection_recovery`, and `drag_dispersion` entries are computed.
4. Explain the orientation frame calculation `_lvlh_frame` and how it underpins coordinate transformations to ECEF for ground track generation.
5. Discuss the use of numpy/pandas within the formation simulation for vectorised operations and CSV output handling.
6. Enumerate STK exporter steps, emphasising interpolation safeguards (SciPy `interp1d` fallback) and file naming sanitisation.
7. Summarise automation features within `run.py` (FastAPI endpoints) and how they expose scenario execution, artefact downloads, and debug log streaming.
8. Detail debugging workflows via `run_debug.py`, including CLI flags (`--triangle`, `--scenario`, `--output-dir`) and outputs under `artefacts/debug/`.
9. Outline continuous integration expectations: `make lint` (byte-compilation), `make test` (pytest), `make simulate` (pipeline smoke test), `make triangle`, `make scenario`, `make baselines`, `make docs`, `make clean`.
10. Highlight environment setup steps: `make setup` or `pip install -r requirements.txt`, Python 3.10 requirement, optional dependencies (`scipy`, `poliastro`) and their handling in exporter code.

### Chapter 4 Extended Guidance
1. Provide detailed bullet summaries for each CSV artefact in `run_20251018_1207Z` (e.g., columns within `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`).
2. Explain how `command_windows.csv` timestamps align with the 96 s access window and support command latency calculations.
3. Interpret `maintenance_summary.csv` columns (`satellite_id`, `delta_v_per_burn_mps`, `annual_delta_v_mps`) and relate them to MR-6 compliance.
4. Analyse the injection recovery dataset, noting distribution statistics (`mean_delta_v_mps`, `p95_delta_v_mps`, `max_delta_v_mps`) per spacecraft and aggregated values.
5. Describe the drag dispersion outputs, emphasising `p95_ground_distance_delta_km`, `max_ground_distance_delta_km`, `p95_along_track_shift_km`, and `max_along_track_shift_km`.
6. Break down the deterministic RAAN alignment metrics, clarifying `overall_max_abs_cross_track_km`, `overall_min_abs_cross_track_km`, and evaluation times.
7. Summarise Monte Carlo statistics beyond centroid metrics, including min/max cross-track values and relative cross-track limits.
8. Document STK export inventories: list `.e`, `.sat`, `.gt`, `.fac`, `.int`, `.sc`, `.evt` files present in each run directory, and note their import readiness.
9. Highlight methodological differences between baseline runs and exploratory reruns (resampling workflows, drag-inclusive Monte Carlo, solver tuning).
10. Identify any outstanding follow-up actions or caveats noted in `docs/_authoritative_runs.md`, `docs/tehran_daily_pass_scenario.md`, or `docs/triangle_formation_results.md`.

### Chapter 5 Extended Guidance
1. Compile a requirement-by-requirement compliance narrative, specifying metric values, margins, and evidence tags for MR-1 through MR-7 and key SRD items.
2. Explain how regression tests enforce compliance: e.g., `test_triangle_formation_meets_requirements` verifying window duration, aspect ratio, ground distance tolerance, plane assignments, maintenance budget, command latency, injection recovery, drag dispersion.
3. Summarise the STK import procedure with explicit steps (launch helper script, verify 3D/2D graphics, check interval lists, confirm RAAN and timing) referencing repository guides.
4. Discuss Connect automation outputs (`formation_metrics.json`, Connect scripts) generated by `run_stk_tehran.py`, emphasising reproducibility of STK sessions.
5. Align operational scenarios (daily imaging, formation recovery, ground station outage) with simulation evidence, highlighting how metrics inform decision thresholds.
6. Integrate risk register mitigation strategies with simulation outcomes (e.g., command latency margin addressing R-01, delta-v budgeting addressing R-02).
7. Present sensitivity study results (RAAN adjustments, drag dispersions, Monte Carlo spreads) and their implications for operations planning.
8. Outline data validation practices, including cross-checks between STK measurements and Python-derived metrics.
9. Discuss documentation governance: how updates to `docs/` are triggered by new runs, compliance reviews, or verification activities.
10. Provide guidance on structuring the discussion to transition from quantitative compliance to qualitative operational readiness.

### Chapter 6 Extended Guidance
1. Summarise mission achievements concisely: RAAN lock at \(350.7885^{\circ}\), ninety-six-second formation window, command latency margins, annual delta-v compliance, injection recovery success rate.
2. Enumerate limitations explicitly: point-mass spacecraft assumption, absence of sensor alignment modelling, reliance on single ground station, idealised thrust execution.
3. Identify future research directions: drag-modulation strategies, solar radiation pressure inclusion, autonomous guidance algorithms, sensor alignment error modelling, multi-station command architecture.
4. Reference upcoming verification milestones (VRR 2024-06-14, Simulation Qualification 2024-07-05, HIL Thruster Test 2024-07-26, Operations Dry Run 2024-08-09, CDR 2024-09-12, LRR 2025-02-21) and align recommendations accordingly.
5. Suggest additional simulation campaigns: long-term propagation with higher fidelity forces, combined attitude-orbit control analyses, contingency response drills.
6. Recommend documentation updates: integration of new compliance evidence, expansion of `docs/tehran_daily_pass_scenario.md`, maintenance of run ledger, periodic roadmap revisions.
7. Propose collaboration initiatives: joint validation with ESA Redu, data sharing with civil protection agencies, academic partnerships for control algorithm research.
8. Encourage adoption of automation enhancements: scheduled reruns with `run_triangle_campaign.py`, automated STK import verification, continuous documentation linting.
9. Outline data stewardship practices: archiving artefacts, maintaining checksums (SHA-256), ensuring retention periods (365 days) per `project.yaml`.
10. Define success metrics for future work: target margins for centroid offsets, delta-v reserves, command latency, compliance reliability.

### Appendix Expansion Guidance
1. For Appendix A, enumerate each artefact directory with description, key files, validation status, and outstanding notes (baseline vs. exploratory).
2. For Appendix B, include script/module responsibilities, major functions, I/O schemas, and corresponding tests.
3. For Appendix C, list tests with scope (unit/integration), requirement mapping, and artefact dependencies.
4. For Appendix D, supply citation details for all standards (publisher, year, identifier) and describe their applicability.
5. For Appendix E, define at least 25 mission-specific terms, referencing documents or artefacts for context.
6. For Appendix F, outline processes for cross-referencing run IDs, commit hashes, and DOIs, including recommended citation managers or templates.
7. Recommend a data lineage diagram illustrating how artefacts flow from simulations to documentation and compliance records.
8. Advise on archival practices for SVG figures generated from repository data (triangle geometry plots, RAAN convergence, command latency histograms).
9. Encourage creation of a reusable bibliography file (e.g., BibTeX) capturing literature and internal documents for consistent citation across chapters.
10. Suggest including a contribution log summarising updates made when new runs or documents are added to the repository.

### Global Quality Assurance Checklist
1. Verify that all instructions relating to STK exports explicitly mention compatibility with `tools/stk_export.py` and the requirement for vector-based artefacts.
2. Confirm that run identifiers are consistently referenced with the correct timestamp and scenario suffixes.
3. Check that every table/figure prompt is accompanied by sufficient context so that future authors can generate the assets from repository data.
4. Ensure that each requirement ID (MR-#, SRD-#) is tied to evidence and that no requirement is omitted.
5. Audit that literature review tasks encompass both classical references and recent publications, with clear instructions on sourcing.
6. Confirm that every simulation or analysis tool mentioned has an associated description, input/output summary, and test coverage note.
7. Ensure that risk and mitigation discussions align with the risk register and operational scenarios documented in `docs/concept_of_operations.md`.
8. Review that future work recommendations align with roadmap milestones and verification plan commitments.
9. Validate that glossary and acronym instructions cover all mission-specific terminology introduced throughout the prompt.
10. Cross-check that appendices collectively provide the necessary depth to reproduce analyses, understand tooling, and maintain configuration control.

## Supplementary Parameter Catalogues

### SP1 – `config/project.yaml` Highlights
- Project name: "Formation Satellite Programme Phase 2" – mention in Chapter 1 when framing mission branding.
- Configuration version `0.1.0` – reference in Chapter 2 to demonstrate semantic versioning discipline.
- Earth model `WGS84` and gravitational parameter `398600.4418 km^3/s^2` – include in theoretical background discussions.
- Nominal altitude `550.0 km` – connect to perturbation analysis and maintenance budgeting.
- Window targets: `AuroraScience` (69°, 23°) with 12 h revisit; `EquatorialEnergy` (0°, -75°) with 24 h revisit – discuss when generalising methodology beyond Tehran.
- Platform bus properties: 120 kg dry mass, five-year design life, 15% power margin, 1.2 × 1.0 × 0.8 m envelope – include in system context narrative.
- Payload specifics: multispectral imager (60 km swath, VNIR/SWIR, 0.05° pointing) and GNSS occultation payload (24 daily pairs) – cite when evaluating observation requirements.
- Communications subsystem: X-band, 150 Mbps downlink, 12.5 dBi antenna gain, ground network [Kiruna, Svalbard, Inuvik] – contrast with single-station assumption in ConOps.
- Propulsion: cold gas, 45 m/s total delta-v, 0.2 N thrust, 70 s Isp – discuss feasibility relative to maintenance budgets.
- Simulation controls: RKF78 integrator, relative tolerance 1e-9, absolute tolerance 1e-12, drag enabled with NRLMSISE-00 and solar activity index 150 – reference in methodology chapters.
- Monte Carlo settings: 200 runs, semi-major-axis dispersion 5 m, inclination sigma 0.01°, drag coefficient sigma 0.05, clock bias sigma 0.5 ms – inform robustness analysis.
- Output policy: directory `outputs/baseline`, naming template `FSAT_{asset}_{product}_{epoch}`, reporting interval 60 s, STK export enabled with facilities [Kiruna, Svalbard, Inuvik], data retention 365 days, checksum SHA-256 – include in documentation on artefact governance.

### SP2 – `config/scenarios/tehran_triangle.json`
- Scenario metadata: validated against STK export (`true`), alignment validation referencing `run_20260321_0740Z` at epoch 2026-03-21T07:40:10Z – emphasise provenance requirements.
- Reference orbit: semi-major axis 6898.137 km, eccentricity 0.0, inclination 97.7°, RAAN 350.9838169642857°, mean anomaly 36.064547° – integrate into orbital element reconstruction discussion.
- Formation parameters: side length 6000 m, duration 180 s, time step 1 s, ground tolerance 350 km, aspect ratio tolerance 1.02 – cite when describing simulation assumptions.
- Target geodetic coordinates: 35.6892° lat, 51.3890° lon – use in literature review and compliance analysis.
- Plane allocations: SAT-1/2 Plane A, SAT-3 Plane B – tie to MR-1 compliance.
- Maintenance schedule: burn duration 32 s, interval 7 days, delta-v budget 15 m/s – map to maintenance metrics.
- Command parameters: contact range 2200 km, station coordinates 30.283°, 57.083° – align with command latency evaluation.
- Monte Carlo specification: 300 samples, position sigma 250 m, velocity sigma 5 mm/s, recovery time 43200 s (12 h), delta-v budget 15 m/s, seed 314159 – integrate into robustness discussion.
- Drag dispersion settings: 200 samples, density sigma 0.25, drag coefficient sigma 0.05, reference density 3.2e-12 kg/m^3, coefficient 2.2, area 1.1 m^2, mass 165 kg, horizon 12 orbits, step 120 s, seed 20260321 – mention when interpreting dispersion results.

### SP3 – `config/scenarios/tehran_daily_pass.json`
- Scenario metadata: RAAN 350.7885044642857°, imaging window 2026-03-21T07:39:25Z to 07:40:55Z, midpoint 07:40:10Z – embed in Chapter 4 analysis of RAAN lock.
- Repeat ground track: cycle 1 day, 15 orbits, local time of descending node 10:30 – include in literature discussion on repeating ground-track theory.
- Access windows: Morning imaging (min elevation 20°, target "Tehran Urban Core"), Evening downlink (20:55:00Z–21:08:00Z, Svalbard, min elevation 12°) – link to ConOps scenarios.
- Payload constraints: imager max off-nadir 25°, GSD 1 m, dwell time 12 s; thermal max 35°C, cooldown 15 min; data handling quota 96 GB/day, preferred nodes [Svalbard, Inuvik], encryption CCSDS 355.0-B-1 – integrate into operational planning.
- Operational constraints: power minimum state-of-charge 35%, payload duty cycle 28%; attitude slew rate 0.5°/s, stability 45 arcsec – highlight when discussing spacecraft capabilities.
- RAAN alignment block: propagation margin 300 s, window duration 90 s, time step 10 s – use when describing solver configuration.
- Validation metadata: `validated_against_stk_export: true`, alignment run ID `run_20251020_1900Z_tehran_daily_pass_locked` – emphasise configuration control.

### SP4 – `artefacts/run_20251018_1207Z/triangle_summary.json` Key Metrics
- Formation window: duration 96 s, start 2026-03-21T09:31:12Z, end 09:32:48Z – cite in compliance sections.
- Triangle metrics: mean area 15,588,457.2681 m², aspect ratio max 1.0000000000001763, side lengths ≈6000 m – highlight geometric fidelity.
- Ground track: tolerance 350 km, windowed max 343.62 km, full propagation max 641.89 km – clarify reporting conventions.
- Orbital elements at midpoint: SAT-1/2 semi-major axis 6891.215 km, SAT-3 6912.017 km, RAAN 18.881° for Plane A, 18.881° with different arguments for Plane B – integrate into orbital analysis.
- Maintenance: per burn delta-v 0.1781–0.2690 m/s, annual maxima 14.0371 m/s, mean 10.8748 m/s – tie to MR-6.
- Command latency: passes per day 15.1532, contact probability 0.0315692, max latency 1.5338 h, mean 0.7669 h, margin 10.4662 h – use in MR-5 discussion.
- Injection recovery: success 1.0, aggregate mean delta-v 0.0263 m/s, p95 0.04117 m/s, max 0.05662 m/s – use for SRD-R-001.
- Drag dispersion summary: success rate, ground distance deltas, along-track shifts – emphasise robustness to atmospheric variations.

### SP5 – `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`
- Orbital period 5679.4704 s (two-body and perturbed identical) – note negligible difference due to modelling choices.
- Vehicle-specific cross-track metrics: FSAT-LDR evaluation 12.2067 km, FSAT-DP1 27.7595 km, FSAT-DP2 -3.5379 km (abs 3.5379 km) – emphasise compliance margins.
- Centroid evaluation: 12.1428 km absolute cross-track, worst vehicle 27.7595 km – restate compliance results.
- Altitude range: 485,849.55 m to 513,409.88 m – include for context.
- Plane intersection candidates: highlight distances to Tehran (7602.54 km, 12,434.97 km) – note the geometric significance.
- Relative cross-track: max abs 0.2000 km, min abs 0.14285 km – relate to relative geometry control.

### SP6 – `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`
- Run count 1000, seed 4242 – emphasise statistical robustness.
- Max absolute cross-track means: FSAT-LDR 2469.99 km, FSAT-DP1 2478.25 km, FSAT-DP2 2466.11 km – note large values outside evaluation interval due to propagation window.
- Min absolute cross-track means: FSAT-LDR 23.7598 km, FSAT-DP1 8.3511 km, FSAT-DP2 32.5610 km – interpret relative alignment.
- Evaluation absolute cross-track p95: FSAT-DP2 39.7606 km – tie to waiver limits.
- Relative cross-track metrics: fleet max mean 0.1999675 km, min mean 0.1428512 km – show formation tightness.
- Compliance fractions: primary 1.0, waiver 1.0, relative 1.0 – highlight statistical compliance.
- Centroid abs cross-track mean 23.9141 km, p95 24.1804 km – integrate into compliance narrative.

### SP7 – `artefacts/triangle_run/run_metadata.json`
- Run ID `run_20251018_1424Z`, timestamp 2025-10-18T14:24:25.333551Z – document curated snapshot provenance.
- Cadence 90 days – discuss in maintenance scheduling context.
- Notes emphasising drag-inclusive rerun for quick reference – instruct authors to clarify curated vs. authoritative runs.
- Drag dispersion aggregate metrics: p95 ground distance delta 0.000486 km, max 0.000567 km, p95 along-track shift 0.003628 km, max 0.004231 km, p95 altitude delta -0.013643 m – include when discussing environmental robustness.
- Artefact inventory: summary JSON, STK directory, maintenance CSV, command windows CSV, injection recovery CSV, injection recovery plot, drag dispersion CSV – emphasise reproducibility kit.

### SP8 – Documentation Highlights
- `docs/project_overview.md`: mission problem statement, objectives, deliverables, verification evidence referencing run_20251018_1207Z – cite in Chapter 1 and 4.
- `docs/triangle_formation_results.md`: detailed methodology steps, tables summarising metrics, STK validation notes – use extensively in Chapter 4.
- `docs/tehran_daily_pass_scenario.md`: RAAN alignment narrative, Monte Carlo statistics, STK validation guidance – integrate into Chapters 3–5.
- `docs/compliance_matrix.md`: requirement status table, evidence catalogue (EV-1 to EV-5), outstanding actions – key for Chapter 5.
- `docs/verification_plan.md`: verification matrix, schedule, resources, success metrics – reference in Chapters 2, 5, and 6.
- `docs/concept_of_operations.md`: mission phases, operational scenarios, risk register – link to Chapter 5 discussions.
- `docs/project_roadmap.md`: staged workflow, supporting documentation templates – use for future work alignment.
- `docs/final_delivery_manifest.md`: reproduction procedure, deliverable list – mention in conclusion.
- `docs/interactive_execution_guide.md`: FastAPI instructions, debug workflows, STK automation – integrate into Chapter 3.
- `docs/how_to_import_tehran_daily_pass_into_stk.md`: step-by-step STK validation – emphasise in Chapter 5.

### SP9 – Test Coverage Notes
- `tests/unit/test_triangle_formation.py`: asserts duration ≥90 s, aspect ratio ≤1.02, ground distance ≤ tolerance, plane allocation (2:1), maintenance delta-v ≤ budget, command latency ≤12 h, injection recovery success ≥95%, drag dispersion sample count ≥50 – summarise in Chapters 3 and 5.
- `tests/test_stk_export.py`: verifies exporter generates STK files with correct headers, time ordering, naming sanitisation, scenario references, facility definitions, contact intervals, event sets, ground tracks – mention in Chapters 3 and 5.
- `tests/unit/test_geometry.py`, `test_orbit.py`, `test_roe.py`: ensure mathematical foundations – reference in Chapter 3.
- `tests/test_documentation_consistency.py`: enforces documentation formatting (if applicable) – highlight in quality assurance sections.
- Integration tests under `tests/integration/`: confirm simulation script execution, metric extraction – integrate into pipeline description.

### SP10 – Command and Automation Scripts
- `sim/scripts/run_triangle_campaign.py`: orchestrates periodic reruns, writes history ledger (`artefacts/triangle_campaign/history.csv`) – mention in future work automation.
- `sim/scripts/sweep_daily.py`: explore RAAN/daily pass parameter space – potential for sensitivity studies.
- `sim/scripts/extract_metrics.py`: post-process simulation outputs into CSV/JSON – include when discussing data workflows.
- `sim/scripts/perturbation_analysis.py`: handles drag and J2 perturbations – highlight in methodology sections.
- `sim/scripts/configuration.py`: loads and validates scenario configurations – tie to configuration management.
- `sim/scripts/scenario_execution.py`: modular execution harness for scenario pipelines – detail in Chapter 3.
- `run.py` and `run_debug.py`: user-facing interfaces – connect to interactive operations.
- `tools/stk_tehran_daily_pass_runner.py` (if present) or `sim/scripts/run_stk_tehran.py`: STK automation – emphasise in STK validation narrative.

## Implementation Trace Logs
1. Note that `triangle_summary.json` includes a `samples` array with timestamped geometry snapshots – instruct authors to consider plotting these for figure prompts.
2. `deterministic_cross_track.csv` and `monte_carlo_cross_track.csv` provide time-series data enabling line plots; encourage comparisons in Chapter 4.
3. `command_windows.csv` records start/end/duration, enabling heat-map style visualisations of contact opportunities – suggest as optional figure.
4. `maintenance_summary.csv` can be reformatted into bar charts showing annual delta-v per spacecraft – align with maintenance discussion.
5. `injection_recovery_cdf.svg` demonstrates probability distributions – replicate as vector graphics for inclusion.
6. `drag_dispersion.csv` captures along-track, cross-track, altitude deltas for each sample – propose scatter plots or statistical tables.
7. `scenario_summary.json` (daily pass) includes `stage_sequence` arrays logging execution steps – use to illustrate pipeline operations.
8. `solver_settings.json` retains optimiser parameters (search range, tolerance, evaluations) – summarise when discussing RAAN solver methodology.
9. `run_metadata.json` for curated runs documents cadence and source directory – emphasise the importance of metadata for reproducibility.
10. Document that all artefact directories follow `run_YYYYMMDD_hhmmZ` naming with optional suffixes (e.g., `_tehran_daily_pass_locked`) – restate naming conventions in multiple chapters.

## Additional Review Prompts
1. Encourage authors to cross-validate Monte Carlo outcomes by recomputing percentiles from `monte_carlo_summary.json` to confirm dataset integrity.
2. Advise verifying units (km vs. m) when transferring values from JSON/CSV to narrative text or tables.
3. Suggest performing independent RAAN optimisation sanity checks using the stored solver configuration to validate convergence behaviour.
4. Recommend re-running `run_triangle.py` and `run_scenario.py` in a clean environment to confirm reproducibility before finalising the manuscript.
5. Encourage capturing STK screenshots or animations post-import to supplement textual descriptions (ensuring output as SVGs per policy).
6. Propose documenting any discrepancies encountered between regenerated artefacts and committed baselines, including git commit hashes and run IDs.
7. Advise maintaining a changelog in `docs/_authoritative_runs.md` whenever new runs supersede existing evidence.
8. Suggest verifying that all CSV/JSON artefacts referenced in the manuscript remain under version control and have not been altered by environment-specific formatting.
9. Encourage running `pytest` to confirm regression suite status prior to claiming compliance in the manuscript.
10. Recommend storing derived analysis scripts (e.g., notebooks for figure generation) under `artefacts/` or `docs/` with clear metadata to support audit trails.

## Reconstruction Workflows

### RW1 – Reproducing `run_20251018_1207Z`
1. Execute `make setup` to ensure the virtual environment is prepared with requirements pinned in `requirements.txt`.
2. Run `python -m sim.scripts.run_triangle --config config/scenarios/tehran_triangle.json --output-dir artefacts/run_YYYYMMDD_hhmmZ` using a fresh timestamped directory.
3. Confirm the console output reports the formation window duration and start/end times; capture the log for archival.
4. Compare the regenerated `triangle_summary.json` with the committed version using `jq` or diff tools, verifying metrics match within tolerance.
5. Validate that `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, and `drag_dispersion.csv` replicate expected column headers and key statistics.
6. Inspect the regenerated `stk_export/` directory for `.e`, `.sat`, `.gt`, `.fac`, `.int`, `.evt`, and `.sc` files; confirm naming sanitisation (e.g., `SAT_1.e`).
7. Import the STK package following `docs/tehran_triangle_walkthrough.md`, capturing screenshots or SVG exports of the 3D orbit and ground tracks.
8. Run `pytest tests/unit/test_triangle_formation.py` to confirm the regression suite continues to pass against regenerated artefacts.
9. Update `docs/_authoritative_runs.md` if a new authoritative run supersedes the prior baseline, including rationale and cross-links.
10. Archive regenerated artefacts with metadata (command used, git commit hash, environment details) to maintain traceability.

### RW2 – Reproducing `run_20251020_1900Z_tehran_daily_pass_locked`
1. Launch `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass_locked`.
2. Verify the stage sequence includes `raan_alignment`, `access_nodes`, `mission_phases`, `two_body_propagation`, `high_fidelity_j2_drag_propagation`, `metric_extraction`, and `stk_export`.
3. Review `scenario_summary.json` to ensure metadata (`configuration_summary`, `metrics`, `stage_sequence`) matches expectations.
4. Inspect `deterministic_summary.json`, confirming centroid and worst-vehicle cross-track metrics align with compliance thresholds.
5. Analyse `monte_carlo_summary.json`, recalculating means and percentiles to confirm integrity.
6. Examine `solver_settings.json` to document optimiser parameters (initial RAAN, optimised RAAN, tolerance, iterations).
7. Import the STK package using `tools/stk_tehran_daily_pass_runner.py` or manual import instructions, verifying contact intervals and ground-track overlays.
8. Run associated regression tests (e.g., `pytest tests/test_stk_export.py`) to confirm exporter integrity post-run.
9. Update documentation references (`docs/tehran_daily_pass_scenario.md`, `docs/compliance_matrix.md`) if a new run becomes authoritative.
10. Capture comparative plots (e.g., deterministic vs. Monte Carlo cross-track time series) for inclusion in the manuscript.

### RW3 – Reproducing Exploratory Resampled Runs
1. Invoke `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass_resampled --resample` (if resampling options exist) to mirror exploratory studies.
2. Document any deviations from baseline geometry, noting whether RAAN alignment remains within tolerance.
3. Compare Monte Carlo statistics against baseline to evaluate impacts of resampling or alternative seeds.
4. Catalogue differences in STK exports (naming, timing) and note whether additional validation steps are required.
5. Flag exploratory runs clearly in documentation to avoid confusion with authoritative datasets.

### RW4 – Quarterly Drag Dispersion Campaigns
1. Use `python -m sim.scripts.run_triangle_campaign --output-dir artefacts/run_YYYYMMDD_hhmmZ_campaign` to execute scheduled dispersion analyses.
2. Review `artefacts/triangle_campaign/history.csv` to confirm cadence compliance and schedule the next rerun date.
3. Summarise drag dispersion metrics, comparing p95 ground distance deltas and along-track shifts against prior campaigns.
4. Update `run_metadata.json` snapshots if a new curated dataset is to be committed for analyst convenience.
5. Record any observed trends in drag sensitivity that may inform maintenance planning.

## Analytical Derivation Prompts
1. Derive the transformation from LVLH offsets to inertial coordinates using the orientation matrices in `sim/formation/triangle.py`.
2. Present the relationship between RAAN drift and nodal crossing timing, referencing `constellation/orbit.py` utilities and literature on J2-induced node regression.
3. Expand on the delta-v budgeting formula using maintenance cadence (weekly burns) and per-burn magnitudes from `triangle_summary.json`.
4. Illustrate how the great-circle distance (Haversine) formula supports the centroid cross-track evaluation, referencing `constellation/orbit.haversine_distance`.
5. Detail the Monte Carlo aggregation methodology (mean, p95, max) as implemented in the simulation summaries, ensuring statistical interpretations are accurate.
6. Provide guidance on constructing covariance ellipsoids for injection dispersions based on the simulation’s sigma values.
7. Suggest including a derivation of command latency expectations using pass frequency and contact probability metrics.
8. Offer prompts for calculating energy or momentum budgets associated with formation maintenance, referencing outputs from `maintenance_summary.csv`.
9. Encourage deriving sensitivity of centroid offset to RAAN perturbations using numerical approximations from solver settings.
10. Outline a method to propagate uncertainty through the STK exporter by perturbing state samples and observing file output differences.

## Narrative Integration Tips
1. Begin each chapter with a concise reminder of its objective and how it relates to preceding material, reinforcing logical flow.
2. Weave repository artefact references seamlessly into the prose, ensuring each citation is paired with descriptive context.
3. Alternate between quantitative data presentation (tables, figures) and qualitative interpretation to maintain reader engagement.
4. Use subheadings to segment long discussions, making it easier for reviewers to locate specific analyses.
5. Highlight compliance outcomes explicitly, connecting metric values to requirement thresholds and margins.
6. When discussing uncertainties or limitations, propose concrete mitigation strategies drawn from roadmap or verification plan documents.
7. Ensure comparisons between baseline and exploratory runs are grounded in metric differences rather than qualitative impressions.
8. Leverage appendices for detailed data tables to keep main chapters focused on synthesis and interpretation.
9. Maintain consistent units and significant figures throughout the manuscript, documenting any rounding decisions.
10. Incorporate forward-looking statements that tie simulation insights to operational or technological recommendations.

## Peer Review Preparation
1. Draft an executive summary capturing mission intent, key findings, and compliance status to accompany the full manuscript.
2. Prepare a slide deck highlighting major figures, tables, and conclusions for design reviews or academic defences.
3. Compile a checklist ensuring all references are complete, formatted consistently, and accessible (DOI, URL, report ID).
4. Conduct an internal peer review using the global quality assurance checklist, documenting findings and resolutions.
5. Validate that all figures are supplied in SVG format and tables remain text-based to satisfy repository guidelines.
6. Confirm that appendices include sufficient detail for independent reproduction of results.
7. Prepare an errata log template to capture any post-publication corrections or updates.
8. Establish a review schedule aligned with roadmap milestones (VRR, CDR, LRR) to ensure timely updates.
9. Provide guidance for external reviewers on repository navigation, highlighting key directories and documents.
10. Summarise risk and mitigation statuses to facilitate rapid assessment by oversight boards.

## Data Cross-Checks
1. Cross-reference centroid statistics from `triangle_summary.json` with those computed from `samples` arrays to verify internal consistency.
2. Validate that maintenance delta-v totals correspond to per-burn magnitudes multiplied by the number of burns per year.
3. Recompute command latency distributions using `command_windows.csv` to confirm metrics in the summary JSON.
4. Confirm that injection recovery results align with the assumptions (position sigma, velocity sigma, delta-v budget) listed in the metrics.
5. Ensure drag dispersion outputs respect the specified tolerances (350 km ground distance) by recalculating differences.
6. Check that RAAN values reported in configuration files match those in simulation outputs within acceptable numerical tolerances.
7. Verify that STK exports load without warnings, ensuring time tags are monotonically increasing and asset names are sanitised.
8. Compare `scenario_summary.json` metric totals (e.g., `total_contact_duration_s`) with sums derived from contact CSV files.
9. Validate that Monte Carlo statistics (mean, std, p95) recomputed from raw data match summary JSON entries to at least four significant figures.
10. Audit that all referenced artefacts exist in the repository and match the expected directory structure.

## Extended Literature Themes

### LT1 – Relative Orbital Elements and Formation Geometry
- Summarise foundational ROE definitions (\(\delta a\), \(\delta \lambda\), \(\delta e_x\), \(\delta e_y\), \(\delta i_x\), \(\delta i_y\)) and relate them to the triangular offsets used in the repository.
- Review contemporary research on LVLH-based formation designs (2019–2025), focusing on equilateral and isosceles configurations.
- Compare theoretical predictions with simulation outputs from `triangle_summary.json`, emphasising aspect ratio stability.
- Discuss observability and navigation considerations when using ROEs for small satellite formations.
- Identify open research questions where the mission’s transient formation concept contributes novel insights.

### LT2 – Repeating Ground-Track Optimisation and RAAN Control
- Analyse algorithms for RAAN optimisation, citing recent papers on deterministic and stochastic approaches.
- Relate literature methods to the solver implementation captured in `run_20251020_1900Z_tehran_daily_pass_locked/solver_settings.json`.
- Evaluate strategies for maintaining RAAN alignment under perturbations, referencing the mission’s compliance results.
- Discuss limitations of one-plane vs. multi-plane configurations for target revisit objectives.
- Highlight opportunities for future research on RAAN management with limited manoeuvre budgets.

### LT3 – Perturbation Modelling and Environmental Effects
- Survey advances in atmospheric density modelling (e.g., NRLMSISE-00 updates, machine-learning-based models) relevant to 550 km altitudes.
- Compare drag and J2 perturbation treatments in literature with the repository’s implementation.
- Discuss inclusion of solar radiation pressure and third-body effects, noting assumptions currently excluded.
- Evaluate implications of geomagnetic storms or solar activity on formation stability.
- Recommend best practices for validating perturbation models against STK or on-orbit data.

### LT4 – Formation Maintenance and Propulsion Strategies
- Review studies on propulsive formation keeping for small satellites, including cold gas, electric propulsion, and hybrid concepts.
- Compare delta-v budgets reported in literature with the mission’s \(14.04\,\text{m/s}\) annual cap.
- Analyse approaches for burn scheduling (impulsive vs. continuous, bang-bang vs. optimal control) and relate to weekly maintenance cadence.
- Discuss propulsion system sizing constraints for CubeSat-class platforms supporting the mission profile.
- Identify research gaps in autonomous maintenance planning under single ground-station constraints.

### LT5 – Command, Control, and Communications Architectures
- Explore literature on single-station vs. networked ground segment designs for small satellite constellations.
- Assess how command latency requirements (≤12 h) align with industry benchmarks and operational case studies.
- Review security and encryption standards (e.g., CCSDS, ISO/IEC 27001) pertinent to mission operations.
- Discuss telemetry, tracking, and command (TT&C) load balancing strategies for daily imaging and downlink schedules.
- Highlight contingency communication strategies (cross-support agreements, backup stations) referenced in ConOps.

### LT6 – Resilience, Robustness, and Monte Carlo Methods
- Examine recent work on Monte Carlo analysis for injection error recovery and station-keeping robustness.
- Compare sample sizes and statistical measures (p95, p99) used in literature with the repository’s 300-trial and 1000-trial campaigns.
- Discuss techniques for uncertainty quantification (polynomial chaos, unscented transforms) as potential enhancements.
- Analyse recovery strategies (impulsive manoeuvres, differential drag) documented in literature for similar error envelopes.
- Identify best practices for presenting probabilistic compliance evidence in mission assurance reviews.

### LT7 – STK Interoperability and Toolchain Integration
- Survey guidance on generating STK-compatible artefacts (OEM ephemerides, Connect scripts) from custom simulations.
- Compare the repository’s text-based exporter with alternative workflows (AGI Connect, MATLAB/OREKIT pipelines).
- Discuss validation methodologies for ensuring STK imports reflect analytical predictions.
- Highlight literature on digital twins or co-simulation frameworks integrating STK with Python-based models.
- Suggest enhancements to exporter tooling based on best practices (e.g., metadata schemas, checksum verification).

## STK Validation Artefact Checklist
1. Verify each `.e` file begins with `stk.v.11.0` and contains `BEGIN/END EphemerisTimePosVel` sections with monotonically increasing time tags.
2. Ensure `.sat` files reference corresponding ephemerides and specify `CentralBody Earth` and correct frame identifiers.
3. Confirm `.gt` files list `BEGIN/END GroundTrack` blocks with consistent point counts.
4. Validate `.fac` files include accurate latitude, longitude, and altitude for facilities (Tehran, Kerman, Svalbard, etc.).
5. Check `.int` files record start/end times matching access windows (07:39:25Z–07:40:55Z and 20:55:00Z–21:08:00Z).
6. Review `.evt` files for manoeuvre listings (e.g., `DeltaV` events) when applicable.
7. Inspect `.sc` scenario files to ensure object names are sanitised (`Tehran_Triangle_Formation`, `SAT_1`) and include animation step settings.
8. Confirm STK Connect scripts (if generated) execute without errors and reproduce scenario states.
9. Document any warnings or errors encountered during STK import and resolve prior to final reporting.
10. Archive validation logs, screenshots, and summary notes alongside the run directory for audit trails.

## Template Table Structures
- Table Template A: Requirement Compliance – columns `Requirement ID`, `Description`, `Metric`, `Result`, `Threshold`, `Margin`, `Evidence Run`, `Outstanding Actions`.
- Table Template B: Simulation Artefact Inventory – columns `File`, `Source Script`, `Key Variables`, `Units`, `Intended Use`, `Validation Status`.
- Table Template C: Maintenance Budget Summary – columns `Spacecraft`, `Delta-v per Burn (m/s)`, `Burn Frequency (days)`, `Annual Delta-v (m/s)`, `Margin vs. Budget`, `Notes`.
- Table Template D: Monte Carlo Outcomes – columns `Statistic`, `FSAT-LDR`, `FSAT-DP1`, `FSAT-DP2`, `Centroid`, `Interpretation`.
- Table Template E: STK Import Checklist – columns `Artefact`, `Expected Value`, `Observed Value`, `Status`, `Reviewer`, `Date`.
- Table Template F: Literature Comparison – columns `Author/Year`, `Mission/Scenario`, `Method`, `Key Metrics`, `Relevance to Tehran Triangle`.

## Visualisation Suggestions
1. LVLH triangle evolution plot showing vertex trajectories during the 96 s window (data from `triangle_summary.json` samples).
2. Ground-track map overlaying Tehran access corridor and facility locations (using STK or Python mapping tools).
3. RAAN convergence curve displaying solver iterations vs. centroid cross-track error (data from `solver_settings.json`).
4. Command latency histogram derived from `command_windows.csv`, illustrating probability distribution vs. 12 h threshold.
5. Monte Carlo CDF or violin plots comparing centroid offsets across baseline and exploratory runs.
6. Drag dispersion scatter plots showing along-track vs. cross-track deviations for each spacecraft.
7. Maintenance delta-v bar chart per spacecraft with budget line overlay.
8. Timeline diagram aligning mission phases, command windows, and imaging/downlink events.
9. Sensitivity matrix heatmap illustrating impacts of parameter variations (e.g., RAAN perturbations, drag coefficients).
10. Flow diagram summarising scenario pipeline stages and artefact generation, derived from `run_scenario.py`.

## Citations and Reference Management
1. Maintain a central bibliography file (e.g., `docs/references.bib`) capturing all external sources with DOI or URL metadata.
2. Use consistent citation keys across chapters (`[Ref1]`, `[Ref2]`, etc.), aligning numbering within each chapter’s reference list.
3. Record internal references with clear descriptors (e.g., `run_20251018_1207Z`, `triangle_summary.json`) and include relative paths.
4. Document the citation date for web resources or software documentation to support reproducibility.
5. Cross-verify that each reference cited in text appears in the chapter’s reference list and vice versa.
6. For standards and handbooks, include identifier, version, publisher, and year to facilitate procurement or review.
7. Encourage authors to include annotations explaining how each reference informed the analysis.
8. Archive citation exports (BibTeX, RIS) alongside the manuscript to support future updates or derivative works.
9. Establish a review process to update references annually, ensuring literature remains current.
10. Provide examples of properly formatted internal and external citations for authors to emulate.
