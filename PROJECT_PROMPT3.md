# Project Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Preface and Usage Notes
This prompt orchestrates the full research and reporting workflow for the Formation Satellite Programme's triangular constellation concept centred on Tehran while generalising every instruction so the same structure can serve alternative mid-latitude targets.
It mirrors the authoritative repository evidence base, references configuration-controlled artefacts, and preserves the tone, length, and methodological expectations of the supplied exemplar prompt.
Every chapter blends literature-review directions with data-driven analysis tasks so that the final dossier simultaneously captures academic context and empirical mission proof.
Before commencing any writing or modelling, familiarise yourself with the repository conventions documented in `AGENTS.md` and the British English style requirement.
Treat this prompt as a living mission contract: deviations from the cited files or metrics must be justified through new runs that conform to the naming policy `run_YYYYMMDD_hhmmZ`.
Document all random seeds, solver tolerances, and STK 11.2 validation outcomes inside the body text and appendices whenever you execute new campaigns.
Maintain numbered references inside each chapter and replicate them in the consolidated References section at the end of the dossier.
Use Tables, Figures, and Equations placeholders exactly as indicated; replace them with final artefact identifiers once generated.

## Chapter 1 – Literature and Theoretical Foundations
The first chapter establishes the intellectual scaffolding for the mission dossier.
Blend contemporary literature (2019–2025 where possible) with the repository's baseline documents to show scholarly awareness and alignment with existing analyses.
Each subsection below specifies a literature-review deliverable followed by the empirical evidence that must be cross-checked later in the report.
Tie every theoretical insight to a future modelling or validation activity so the narrative stays cohesive across chapters.

### 1.1 Mission Architecture and Stakeholder Drivers
1. Summarise the overarching mission intent using the framing in `docs/project_overview.md`, emphasising dual-plane deployment, 90-second access windows, and Tehran-centric justification.[Ref1]
2. Survey recent journal articles and conference papers on tri-satellite formations in sun-synchronous orbits, focusing on how stakeholders articulate resilience and rapid-response imaging needs.
3. Highlight stakeholder communities (civil protection agencies, infrastructure monitors, scientific payload teams) and how their priorities translate to mission objectives recorded in the Mission Requirements Document (MRD).[Ref2]
4. Identify literature gaps concerning mid-latitude target monitoring under contested or congested space conditions and flag them for incorporation in Chapter 6's future work recommendations.
5. Annotate at least three external sources that validate the operational cadence (daily imaging, evening downlink) already captured in the Tehran daily pass scenario metadata.[Ref3]

### 1.2 Relative Orbital Elements and Triangular Geometry Theory
1. Review classical and modern treatments of relative orbital elements (ROE), ensuring D'Amico et al. (2005) or equivalent is cited to justify the use of equilateral geometry offsets encoded in the configuration files.[Ref4]
2. Explain how LVLH coordinate transformations underpin the 6 km side-length triangular formation, matching the algorithms implemented in `sim/formation/triangle.py`.[Ref5]
3. Discuss perturbation effects (\(J_2\), drag, solar radiation pressure) on relative motion and catalogue analytical solutions or linearised models that complement the repository's numerical propagation.[Ref6]
4. Clarify why aspect ratio tolerances near unity are necessary for cooperative sensing, referencing both literature findings and the regression expectations embedded in `tests/unit/test_triangle_formation.py`.[Ref7]
5. Prepare a comparison table of ROE-based control strategies versus differential drag techniques; this table will reappear in Chapter 4 when evaluating maintenance budgets.

### 1.3 Access Window Optimisation and RAAN Alignment Scholarship
1. Extract the RAAN solver context from `docs/tehran_daily_pass_scenario.md` and `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/solver_settings.json` to show how optimisation shapes daily access windows.[Ref3][Ref8]
2. Conduct a literature review on orbital plane alignment for single-target revisit maximisation, including methods that handle \(J_2\) drift and atmospheric drag.
3. Document best practices for coupling deterministic alignment with Monte Carlo catalogue validation, mirroring the repository's deterministic and probabilistic evidence sets.[Ref8]
4. Highlight studies that quantify centroid versus worst-vehicle cross-track metrics and compare them with the repository's acceptance bands (±30 km primary, ±70 km waiver).
5. Note any research addressing RAAN sensitivity to solar cycle variations; mark this as a gap to revisit in Chapter 7 recommendations.

### 1.4 Formation Maintenance, Responsiveness, and Robustness Literature
1. Summarise maintenance strategies that cap annual \(\Delta v\) near 15 m/s per spacecraft, aligning the academic narrative with the repository's maintenance metrics (annual maxima \(14.037\,\text{m/s}\)).[Ref9]
2. Review studies on single-station commanding architectures and latency guarantees to justify the MR-5 requirement and the documented \(1.53\,\text{h}\) latency evidence.[Ref9]
3. Investigate Monte Carlo recovery techniques for injection dispersions up to ±5 km along-track and ±0.05° inclination, linking them to the 300-case success record archived in the maintenance campaign.[Ref9]
4. Catalogue atmospheric drag dispersion analyses for low Earth orbits and correlate them with the 200-sample drag study results (`p95` along-track shift \(3.63\,\text{km}\)).[Ref10]
5. Establish a cross-reference between literature-specified contingency time horizons and the repository's 12-orbit drag dispersion window to justify modelling choices later in Chapter 4.

### 1.5 Systems Engineering Standards and Compliance Frameworks
1. Describe the role of compliance matrices in mission assurance, using ECSS or NASA systems engineering sources to back the approach taken in `docs/compliance_matrix.md`.[Ref11]
2. Summarise verification and validation planning standards (NASA-STD-7009A, ECSS-E-ST-10-02C) and connect them to the repository's V&V Plan, emphasising independence and credibility criteria.[Ref12]
3. Review configuration management practices for simulation artefacts, referencing guidelines that support the `run_YYYYMMDD_hhmmZ` naming convention and data retention policy defined in `config/project.yaml`.[Ref13]
4. Compile literature on STK 11.2 interoperability and data exchange standards to contextualise the exporter guidance and integration tests in later chapters.[Ref14]
5. Prepare a mapping between industry-standard assurance documentation (MRD, SRD, ConOps, V&V Plan) and the repository's documents for the methodology overview section of Chapter 2.

### 1.6 Payload, Ground Segment, and Data Handling Studies
1. Survey multispectral and GNSS occultation payload literature to substantiate the platform assumptions codified in `config/project.yaml`.[Ref13]
2. Investigate single-ground-station operational models with fallback agreements (e.g., ESA Redu) and connect them to the ground segment discussion in the Concept of Operations.[Ref15]
3. Review data handling pipelines for rapid disaster response, ensuring the four-hour latency objective is anchored in relevant mission studies.[Ref15]
4. Document communication security standards (e.g., CCSDS 355.0-B-1) and evaluate their adoption in comparable missions.
5. Highlight any emerging research on cloud-based mission planning and its implications for the repository's interactive execution guide.

### 1.7 Literature Review Output Requirements
1. For each subsection above, produce annotated bibliographies that list citation, relevance, and data products needed for the empirical chapters.
2. Organise the literature findings into a cross-reference table that maps each source to the mission requirement it supports or challenges.
3. Identify at least five gaps where literature does not yet address the repository's chosen tolerances, seeds, or commanding architecture.
4. Flag these gaps explicitly for treatment in Chapter 6 (Discussion) and Chapter 7 (Recommendations).
5. Ensure the Chapter 1 narrative closes with a synthesis paragraph linking literature themes to the mission requirements and simulation evidence that will be interrogated in later chapters.

## Chapter 2 – Mission Requirements, System Architecture, and Configuration Baselines
This chapter transitions from scholarly context to the concrete requirement sets and configuration artefacts that govern the constellation.
Use narrative prose supported by tables to demonstrate traceability from stakeholder needs to configuration parameters.
Cross-reference the compliance ledger and configuration YAML to substantiate every claim.

### 2.1 Mission Requirements Decomposition
1. Present a table summarising MR-1 through MR-7, reusing wording from `docs/mission_requirements.md` and ensuring verification approaches align with the latest plan.[Ref2]
2. Discuss how each requirement translates into measurable metrics, drawing on the specific values captured in `artefacts/run_20251018_1207Z/triangle_summary.json` (e.g., \(96\,\text{s}\) window duration, \(343.62\,\text{km}\) maximum ground distance inside the window).[Ref9]
3. Explain how the ±30 km primary and ±70 km waiver cross-track thresholds are enforced in both deterministic and Monte Carlo analyses, referencing compliance matrix notes.[Ref11]
4. Detail the interplay between MR-5 (single-station command), MR-6 (annual \(\Delta v\)), and MR-7 (robustness), showing how they constrain maintenance policy.[Ref9]
5. Provide a paragraph on risk considerations that stem from each requirement, teeing up Chapter 5's validation narrative.

### 2.2 System Requirements Hierarchy and Traceability
1. Extract SRD-F/P/O/R entries from `docs/system_requirements.md`, especially the ones already marked Compliant in the matrix, and show their parent-child mapping to mission requirements.[Ref16]
2. Illustrate how verification methods (Analysis, Test, Demonstration, Inspection) align between SRD entries and the V&V Plan's taxonomy.[Ref12]
3. Include a miniature SysML-like table or bullet mapping to emphasise traceability for SRD-F-001 (plane allocation) and SRD-P-001 (cross-track control).[Ref16]
4. Identify any SRD entries awaiting future evidence, even if currently marked compliant, to ensure vigilance in future updates.
5. Cross-check traceability statements with the compliance matrix to ensure consistency.[Ref11]

### 2.3 Configuration Baselines in `config/project.yaml`
1. Summarise the metadata block (project name, version, authoring team, last updated) and emphasise the need to increment versions when modifications occur.[Ref13]
2. Present the global constants (earth model, gravitational parameter, nominal altitude) and connect them to simulation assumptions inside `sim/formation/triangle.py` and scenario scripts.[Ref5]
3. Document platform parameters (mass, design life, power margins, payload specs, communication characteristics, propulsion system) and tie them to operational narratives in the ConOps.[Ref15]
4. Explain the maintenance strategy (7-day cadence, 100 m separation tolerance, 20% \(\Delta v\) reserve) in light of the maintenance metrics produced by the simulation pipeline.[Ref9]
5. Describe simulation settings (start/stop times, integrator method RKF78, tolerances, perturbation toggles, Monte Carlo dispersions) and highlight how they influence results in `artefacts/run_20251018_1424Z`.[Ref10]

### 2.4 Scenario Configurations Overview
1. Provide a side-by-side comparison of `config/scenarios/tehran_triangle.json` and `config/scenarios/tehran_daily_pass.json`, noting metadata fields, epoch alignment, tolerances, and maintenance assumptions.[Ref5][Ref3]
2. Elaborate on plane allocations (SAT-1 and SAT-2 in Plane A, SAT-3 in Plane B) and how they map to orbital element reconstructions recorded in the triangle summary metrics.[Ref9]
3. Explain the Monte Carlo settings for both scenarios (sample counts, dispersions, seeds) and how they drive the probabilistic outputs archived in the corresponding artefact directories.[Ref8][Ref10]
4. Highlight differences in command and contact modelling (formation command range 2200 km vs. daily pass downlink schedule) and their implications for operations chapters.[Ref3][Ref9]
5. Document the STK validation flags within each scenario metadata block and emphasise the requirement to keep them truthful when regenerating exports.[Ref3]

### 2.5 Documentation Ecosystem Summary
1. Create a narrative map showing how `docs/project_overview.md`, `concept_of_operations.md`, `system_requirements.md`, `mission_requirements.md`, `verification_plan.md`, and `compliance_matrix.md` interact within the systems engineering stack.[Ref1][Ref15][Ref16][Ref2][Ref12][Ref11]
2. Summarise the role of `docs/interactive_execution_guide.md` in onboarding analysts to the web and CLI tooling, bridging this chapter with the simulation pipeline chapter.[Ref17]
3. Note the function of `_authoritative_runs.md` in preserving evidence integrity and how it supports configuration control.[Ref18]
4. Explain how the final delivery manifest structures deliverables for stakeholder review.[Ref19]
5. Close the chapter by previewing which configuration elements will be interrogated in the simulation and results chapters.

## Chapter 3 – Simulation Infrastructure and Data Provenance
This chapter documents the tooling stack, pipelines, and artefact structure that underpin the mission evidence.
Describe each software component, command, and artefact directory so readers can reproduce results without ambiguity.

### 3.1 Triangle Formation Simulation (`sim/formation/triangle.py`)
1. Break down the simulation stages: configuration loading, Keplerian propagation, LVLH frame construction, geometry computation, centroid tracking, and STK export preparation.[Ref5]
2. Explain how `TriangleFormationResult.to_summary` serialises metrics, focusing on the `samples`, `geometry`, `metrics`, and `artefacts` sections consumed by downstream documents.[Ref5]
3. Discuss numerical parameters (sample count derived from duration/time-step, offset arrays, orientation frame derivation) and how they align with configuration tolerances.[Ref5]
4. Note the integration with `constellation.geometry` and `constellation.orbit` modules, highlighting functions such as `triangle_side_lengths`, `triangle_area`, `geodetic_coordinates`, and `propagate_kepler`.[Ref20]
5. Clarify how STK export helpers (`unique_stk_names`, `sanitize_stk_identifier`, `export_simulation_to_stk`) enforce compatibility constraints, linking to the exporter guide and tests.[Ref14][Ref21]

### 3.2 General Scenario Pipeline (`sim/scripts/run_scenario.py` and friends)
1. Describe the stage sequence executed by the scenario runner: access node generation, mission phase compilation, two-body propagation, high-fidelity \(J_2\)+drag propagation, metric extraction, optional STK export.[Ref22]
2. Explain how configuration files are resolved and how CLI overrides or inline configurations are handled.[Ref22]
3. Highlight the RAAN optimisation logic and solver outputs stored in the artefact directories, emphasising reproducibility.[Ref8]
4. Outline the CLI interface and expected outputs when running `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir <dir>`.[Ref22]
5. Connect the scenario runner to integration tests that assert stage ordering and Monte Carlo metric presence.[Ref23]

### 3.3 Triangle Campaign and Baseline Generation Utilities
1. Summarise `sim/scripts/run_triangle.py` for dedicated triangle runs, including CLI arguments, output directory structure, and metric files generated (`triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, `injection_recovery_cdf.svg`).[Ref24]
2. Document `sim/scripts/run_triangle_campaign.py` and `artefacts/triangle_campaign/history.csv` to show how quarterly drag dispersion reruns are scheduled and tracked.[Ref25]
3. Explain the placeholder status of `baseline_generation.generate_baseline` and how integration tests enforce the current `NotImplementedError` until the feature is delivered.[Ref23]
4. Note how `sim/scripts/scenario_execution.py` and `metric_extraction.py` wrap and augment metric outputs, referencing integration tests for coverage.[Ref23]
5. Detail `sim/scripts/perturbation_analysis.py` and `sim/scripts/sweep_daily.py` if utilised in future work, clarifying their current readiness state.

### 3.4 Interactive and Debug Tooling
1. Describe the FastAPI application in `run.py`, including endpoints for listing scenarios, launching triangle runs, launching general scenario runs, and streaming debug logs.[Ref26]
2. Explain the artefact structure under `artefacts/web_runs`, the role of `run_log.jsonl`, and the job management pattern implemented via `JobManager` and `SubprocessJob`.[Ref26]
3. Summarise `run_debug.py`, detailing argument options (`--triangle`, `--scenario`, `--triangle-config`, `--output-root`), logging behaviour, and generated CSV diagnostics.[Ref27]
4. Document how debug runs populate `artefacts/debug/<timestamp>` and the expectation to archive logs after significant investigations.[Ref27]
5. Reference `docs/interactive_execution_guide.md` as the authoritative operational guide for both web and CLI workflows.[Ref17]

### 3.5 Tests, Automation, and Continuous Integration Hooks
1. Outline the unit tests guarding geometry and exporter correctness, with emphasis on `tests/unit/test_triangle_formation.py` and `tests/test_stk_export.py`.[Ref7][Ref21]
2. Detail integration tests in `tests/integration/test_simulation_scripts.py`, including stage sequence assertions, CLI smoke tests, and metric extraction checks.[Ref23]
3. Summarise `tests/baseline_compare.py` and `tests/test_documentation_consistency.py` if leveraged to ensure documentation alignment with code.
4. Clarify how the `Makefile` and GitHub Actions pipeline (CI workflow referenced in `README.md`) run linting, testing, and simulation targets.[Ref28]
5. Note any pending test scaffolding or placeholders that require completion as algorithms mature.

### 3.6 Artefact Directory Structure and Naming
1. Provide a directory map for `artefacts/`, describing the contents and purpose of each run folder (e.g., `run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`, `run_20260321_0740Z_tehran_daily_pass_resampled`, `triangle_run`).[Ref9][Ref8][Ref10]
2. Explain the difference between curated snapshots (e.g., `triangle_run`) and authoritative runs referenced in `_authoritative_runs.md`.[Ref18]
3. Document the naming conventions for STK export subdirectories (`stk_export` or `stk`) and file types (`.e`, `.sat`, `.gt`, `.fac`, `.int`).[Ref14]
4. Highlight metadata files such as `scenario_summary.json`, `deterministic_summary.json`, `monte_carlo_summary.json`, `solver_settings.json`, and `run_metadata.json`.
5. Emphasise the requirement to update `docs/_authoritative_runs.md` whenever new runs replace baseline evidence.[Ref18]

## Chapter 4 – Analytical and Experimental Workflow
This chapter provides a step-by-step plan for regenerating and extending the mission evidence while ensuring consistency with literature findings and configuration baselines.
Structure the narrative as a combination of procedural instructions, experimental checklists, and tie-ins to earlier theoretical insights.

### 4.1 Triangle Formation Regeneration Procedure
1. Execute `make setup` to prepare the Python environment, ensuring dependencies in `requirements.txt` are installed.[Ref28]
2. Run `python -m sim.scripts.run_triangle --output-dir artefacts/triangle` and confirm the command emits the expected artefacts (summary JSON, CSV tables, SVG plot, STK export directory).[Ref24]
3. Compare the regenerated metrics against `artefacts/triangle_run/triangle_summary.json`, verifying formation window duration (\(96\,\text{s}\)), maximum ground distance within the window (\(343.62\,\text{km}\)), and aspect ratio (~1.0).[Ref9]
4. Inspect `maintenance_summary.csv` to ensure annual \(\Delta v\) remains below the 15 m/s budget; reconcile any deviations with the maintenance strategy described in Chapter 2.[Ref9]
5. Review `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, and `injection_recovery_cdf.svg` to confirm MR-5 through MR-7 evidence remains intact; document anomalies in the lab notebook and update regression tests if limits shift.[Ref9][Ref10]

### 4.2 Tehran Daily Pass Scenario Execution and RAAN Validation
1. Invoke `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ_tehran_daily_pass` to regenerate the daily pass dataset.[Ref22]
2. Verify deterministic centroid cross-track metrics against `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`: centroid \(12.1428\,\text{km}\), worst vehicle \(27.7595\,\text{km}\), compliance flags true.[Ref8]
3. Check Monte Carlo statistics (`centroid_abs_cross_track_km` mean 23.914 km, `p95` 24.180 km; `worst_vehicle_abs_cross_track_km` mean 39.631 km, `p95` 39.761 km) to ensure probabilistic compliance.[Ref8]
4. Confirm STK exports exist and are up to date; re-import them following the STK validation guide to maintain `validated_against_stk_export: true` in the scenario configuration.[Ref14][Ref29]
5. Update `_authoritative_runs.md` if a new run supersedes the locked dataset; note whether previous runs remain available for comparison.[Ref18]

### 4.3 Maintenance and Responsiveness Analysis
1. Recompute annual \(\Delta v\) and commanding latency metrics using `maintenance_summary.csv` and `command_windows.csv`, confirming values align with MR-6 and MR-5 limits (max latency \(1.53\,\text{h}\), latency margin \(10.47\,\text{h}\)).[Ref9]
2. Analyse the injection recovery catalogue (300 samples, \(p_{95}\) \(\Delta v\) 0.041 m/s) to assess robustness; compare to literature findings from Chapter 1.[Ref9]
3. Evaluate drag dispersion statistics from `artefacts/run_20251018_1424Z` to ensure along-track shifts remain within tolerance and update the literature gap assessment if new perturbations become significant.[Ref10]
4. Document command contact probability (0.0316) and passes per day (15.15) to show commanding feasibility.[Ref9]
5. Summarise findings in a table that cross-references MR-5 to MR-7 with measured margins and literature rationale.

### 4.4 Comparative Scenario Studies and Sensitivity Analyses
1. Use `sim/scripts/run_triangle_campaign.py` to schedule drag dispersion reruns; log execution details in `artefacts/triangle_campaign/history.csv` and highlight upcoming due dates (e.g., next rerun 16 January 2026).[Ref25]
2. Replicate exploratory runs such as `run_20260321_0740Z_tehran_daily_pass_resampled` to evaluate resampling workflows; compare metrics to the locked baseline and record differences.[Ref30]
3. Conduct sensitivity sweeps on Monte Carlo dispersions (e.g., varying `position_sigma_m`, `velocity_sigma_mmps`) and document results in new artefact directories, ensuring compliance with naming conventions.
4. Investigate potential solar activity impacts by adjusting `solar_activity_index` within `config/project.yaml` and evaluating RAAN drift outcomes.
5. Capture all modifications in the literature gap log initiated in Chapter 1.7.

### 4.5 Data Visualisation and Reporting Assets
1. Plan figures for each chapter, referencing existing artefacts: e.g., `[Suggested Figure 2.1] Formation geometry time series derived from `triangle_summary.json`; `[Suggested Figure 4.1] Monte Carlo centroid cumulative distribution`; `[Suggested Figure 4.2] Drag dispersion along-track shifts`.[Ref9][Ref10]
2. Identify equations to include, such as Hill-Clohessy-Wiltshire relations for drift, maintenance \(\Delta v\) accumulation formulas, or RAAN drift approximations, tying them to literature and code implementations.[Ref5][Ref6]
3. Define tables to present: e.g., requirement compliance margins, maintenance budget breakdown, Monte Carlo summary, RAAN optimisation steps.[Ref9][Ref8]
4. Ensure all figures are generated in SVG format per repository policy; convert any intermediate plots accordingly.
5. Maintain a log of figure/table placeholders to cross-reference when compiling the final report.

## Chapter 5 – Results Interpretation, Validation, and Compliance Integration
This chapter weaves empirical findings into a rigorous discussion, corroborating requirement compliance and addressing validation protocols.
Emphasise cross-references between simulation outputs, compliance documents, and STK validation activities.

### 5.1 Mission Requirement Compliance Narrative
1. For each MR, articulate how simulation evidence and tests confirm compliance, citing both deterministic and probabilistic data (e.g., MR-2: deterministic centroid 12.1428 km, Monte Carlo `p95` 24.180 km, worst spacecraft `p95` 39.761 km).[Ref8]
2. Discuss residual margins and highlight any assumptions that require monitoring (e.g., maintenance \(\Delta v\) margin 0.963 m/s).[Ref9]
3. Reference regression tests that guard each requirement so the reader understands ongoing assurance (unit test for geometry, integration test for stage sequence, exporter tests).[Ref7][Ref23][Ref21]
4. Address risk items noted in the ConOps risk register (single-station commanding, delta-v overuse, injection dispersion, cyber security, STK export issues) and explain how current evidence mitigates each.[Ref15]
5. Integrate a compliance matrix excerpt summarising status and evidence tags [EV-1] through [EV-5].[Ref11]

### 5.2 STK Validation Evidence and Workflow
1. Detail the STK import procedure executed for the triangle and daily pass scenarios, referencing `docs/how_to_import_tehran_daily_pass_into_stk.md` and `docs/tehran_triangle_walkthrough.md`.[Ref29][Ref31]
2. Summarise key validation metrics recorded inside STK (access times, orbital period confirmation, facility locations) and cross-check with JSON summaries.[Ref8][Ref9]
3. Explain how automation scripts (`tools/stk_tehran_daily_pass_runner.py`, `sim/scripts/run_stk_tehran.py`) streamline validation and how their outputs are archived.[Ref29][Ref24]
4. Clarify how STK validation status is communicated in scenario metadata (`validated_against_stk_export: true`) and the compliance matrix.
5. Document any observed limitations or manual adjustments required during import and how they were resolved.

### 5.3 Verification and Validation Plan Execution
1. Map executed verification activities to the V&V plan schedule (VRR, Simulation Qualification, HIL test, Operations Dry Run) and note their completion status.[Ref12]
2. Provide evidence references for each activity (e.g., SIM-TRI-2024-01 results from triangle runs, SIM-NODE-2024-01 from daily pass scenario).[Ref12]
3. Discuss resource utilisation (personnel hours, facility costs) in line with the plan's resource table and identify any variances.[Ref12]
4. Highlight outstanding tasks or future milestones, ensuring the narrative matches the roadmap timeline.[Ref28]
5. Connect validation outcomes to stakeholder engagement activities (tabletop reviews, user acceptance demonstrations) described in the plan.

### 5.4 Discussion of Modelling Assumptions and Limitations
1. Critically evaluate modelling assumptions (e.g., RKF78 integrator tolerances, absence of solar radiation pressure, uniform command request distribution) and their implications for results.[Ref5][Ref13]
2. Compare simulation assumptions with literature findings from Chapter 1 and note discrepancies or validation needs.
3. Discuss sensitivity to initial conditions and atmospheric model uncertainties, referencing drag dispersion results.[Ref10]
4. Address limitations in the Monte Carlo catalogue size or seed selection, and propose expansions if necessary.
5. Provide recommendations for enhancing model fidelity (e.g., coupling attitude dynamics, adding SRP) in subsequent phases.

### 5.5 Integration of Interactive and Debug Outputs into the Evidence Set
1. Explain how interactive runs captured in `artefacts/web_runs` can be promoted to authoritative evidence (e.g., verifying metrics, importing to STK, updating run ledgers).[Ref26]
2. Detail how debug outputs (CSV time series, logs) supplement the main datasets and should be cited when diagnosing anomalies or demonstrating reproducibility.[Ref27]
3. Recommend archival practices for debug artefacts, including naming conventions and retention policies.
4. Highlight how interactive and debug tooling supports validation rehearsals and stakeholder demonstrations.
5. Encourage cross-referencing between interactive runs, formal simulations, and literature to maintain coherence.

## Chapter 6 – Synthesis, Discussion, and Cross-Chapter Linkages
This chapter synthesises insights from literature, requirements, simulations, and validation to answer the mission problem statement comprehensively.
Use structured prose to relate theoretical expectations with empirical findings and to identify future research directions.

### 6.1 Triangulation of Literature and Empirical Evidence
1. Compare literature-derived expectations for triangle geometry, RAAN alignment, maintenance, and robustness with the empirical metrics recorded in Chapters 4 and 5.
2. Highlight areas where repository evidence confirms literature predictions (e.g., equilateral geometry stability) and where it extends or challenges published findings (e.g., command latency margins).[Ref9]
3. Identify how the ConOps operational scenarios are validated by simulation results and literature case studies.[Ref15]
4. Discuss the sufficiency of compliance documentation relative to industry standards, referencing both internal documents and external sources.[Ref11][Ref12]
5. Summarise the integrated evidence picture in a narrative that demonstrates requirement closure and mission readiness.

### 6.2 Risk, Uncertainty, and Mitigation Strategies
1. Analyse risk items enumerated in the ConOps and discuss mitigation effectiveness in light of simulation data (e.g., backup ground stations, \(\Delta v\) reserves, Monte Carlo success rates).[Ref15]
2. Address uncertainties in atmospheric modelling, RAAN drift, or command availability and propose monitoring plans.
3. Evaluate the robustness of the RAAN optimisation process to environmental or configuration changes.
4. Consider cyber security and configuration management risks in the context of interactive tooling and collaborative workflows.[Ref26]
5. Recommend updates to risk registers or contingency plans based on findings.

### 6.3 Implications for Stakeholders and Operations
1. Discuss how mission evidence supports stakeholder needs identified in Chapter 1 (e.g., rapid imagery delivery, resilience monitoring).
2. Evaluate ground segment workload and command planning implications derived from the maintenance schedule and command latency metrics.[Ref9]
3. Explore how payload performance assumptions align with formation behaviour and access windows.[Ref13]
4. Consider scalability to other mid-latitude targets and note configuration adjustments required.
5. Summarise how the dossier will inform operations readiness reviews.

### 6.4 Cross-Chapter Traceability and Narrative Flow
1. Revisit the literature gaps flagged in Chapter 1 and discuss whether empirical evidence fills them or whether further study remains necessary.
2. Ensure every major dataset introduced in Chapter 3 and analysed in Chapter 4 is referenced in the discussion, maintaining traceability.
3. Link compliance and validation results (Chapter 5) back to requirement statements (Chapter 2).
4. Confirm that figures, tables, and equations previewed earlier are actually produced and referenced.
5. Draft transition paragraphs that lead naturally into the concluding chapter.

## Chapter 7 – Conclusions and Recommendations
This chapter distils the mission research into key conclusions, highlights residual gaps, and proposes actionable next steps.
Ensure recommendations are traceable to evidence and literature.

### 7.1 Summary of Findings
1. Provide bullet-point conclusions for each mission requirement and system requirement, referencing the evidence sets used (e.g., `[EV-1]`, `[EV-5]`).[Ref11]
2. Restate the mission problem statement and confirm how the results satisfy or exceed expectations (e.g., 96-second window, compliance margins, validated STK exports).[Ref9][Ref8]
3. Highlight major insights from the literature review that influenced analysis choices or interpretations.
4. Summarise validation achievements (e.g., successful STK imports, completed verification activities).[Ref29][Ref12]
5. Present an executive narrative linking mission readiness to stakeholder objectives.

### 7.2 Recommendations for Future Work
1. Outline planned improvements to modelling fidelity (e.g., include SRP, refine atmospheric models, integrate attitude dynamics) and tie them to Chapter 6's limitations discussion.
2. Propose additional verification activities (e.g., hardware-in-the-loop rehearsals, extended Monte Carlo campaigns) aligned with the V&V plan.[Ref12]
3. Suggest documentation updates (e.g., augment compliance matrix, expand ConOps risk register, refresh project roadmap) triggered by new findings.[Ref11][Ref15][Ref28]
4. Recommend collaboration or data-sharing initiatives (e.g., with other agencies or universities) to address literature gaps.
5. Provide a schedule overview for implementing recommendations, referencing roadmap milestones.[Ref28]

### 7.3 Knowledge Management and Configuration Control Actions
1. Specify which artefact directories must be updated or archived following new runs, referencing the run ledger and naming conventions.[Ref18]
2. Detail required updates to configuration files (`config/project.yaml`, scenario JSONs) when new baselines are adopted.[Ref13]
3. Encourage peer review of code changes affecting mission-critical computations (triangle simulation, scenario runner, exporter) before merging.
4. Document protocols for maintaining STK validation status and capturing evidence for future audits.[Ref14][Ref29]
5. Summarise configuration management actions in a table linking tasks, responsible owners, and due dates.

## Chapter 8 – Appendices, Submission Checklist, and Style Guide
Conclude the dossier with appendices that support reproducibility, a submission checklist, and style guidance to maintain academic rigour.

### 8.1 Appendix Structure Recommendations
1. Include Appendix A for configuration snapshots (key YAML excerpts, scenario JSON highlights).
2. Reserve Appendix B for supplementary figures (Monte Carlo histograms, drag dispersion plots, command latency charts).
3. Allocate Appendix C to detailed tables (maintenance budgets, RAAN optimisation sweeps, solver tolerance sensitivity).
4. Dedicate Appendix D to methodological notes (integrator settings, random seeds, solver tolerances, computational resources).
5. Add Appendix E for glossary and acronym definitions relevant to mission analysis.

### 8.2 Submission Checklist
1. Confirm all chapters adhere to British English and academic tone.
2. Verify numbered references appear both inline and in the References list.
3. Ensure all figures are SVG files stored under controlled directories and cited correctly.
4. Run `pytest` and `make lint` (or equivalent) to confirm regression tests pass before publishing findings.[Ref28]
5. Check that new artefacts follow naming conventions and that `_authoritative_runs.md` reflects any baseline changes.[Ref18]

### 8.3 Citation and Referencing Style
1. Use inline bracketed references `[RefX]` corresponding to the list below; avoid duplicate numbers for different sources.
2. Cite repository artefacts (JSON, CSV, SVG) by directory path and file name; include run identifiers where applicable.
3. Reference external literature with full bibliographic details; ensure DOIs or URLs are captured where possible.
4. When citing figures or tables, provide both the artefact source and the chapter location.
5. Maintain a master bibliography file (e.g., BibTeX or Zotero export) to streamline updates.

### 8.4 Writing Style and Formatting Expectations
1. Employ hierarchical headings starting at `#` and progressing sequentially; avoid skipping levels.[Ref0]
2. Use numbered lists for ordered procedures and bullet lists for unordered insights, mirroring repository documentation style.[Ref0]
3. Integrate tables where they enhance clarity (requirements compliance, metric comparisons, risk registers).
4. Present mathematical expressions in inline LaTeX notation (`\(\)`) to maintain consistency with existing docs.[Ref0]
5. Balance accessibility with rigour: explain specialised terms upon first use and provide cross-references to appendices or glossary entries.

### 8.5 Document Control and Review Cycle
1. Record the dossier version number, authorship team, and last updated date in the front matter, aligning with `config/project.yaml` metadata conventions.[Ref13]
2. Schedule periodic reviews aligned with roadmap milestones (VRR, CDR, LRR) to maintain freshness.[Ref12][Ref28]
3. Store publication-ready PDFs in a controlled repository while keeping Markdown source under version control for collaboration.
4. Tag Git commits associated with major dossier revisions for traceability.
5. Ensure review comments and dispositions are archived alongside the document for audit trails.

## References
- [Ref0] `AGENTS.md` – Repository-wide documentation style and collaboration guidelines.
- [Ref1] `docs/project_overview.md` – Mission framing and recent verification evidence for the Tehran triangular formation.
- [Ref2] `docs/mission_requirements.md` – Mission Requirements (MR-1 to MR-7) and verification approaches.
- [Ref3] `config/scenarios/tehran_daily_pass.json` & `docs/tehran_daily_pass_scenario.md` – Tehran daily pass configuration and validation narrative.
- [Ref4] D'Amico, S., et al., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
- [Ref5] `sim/formation/triangle.py` – Triangle formation simulation implementation and metrics extraction logic.
- [Ref6] `docs/triangle_formation_results.md` – Methodology and results for the 6 km triangular formation including perturbation context.
- [Ref7] `tests/unit/test_triangle_formation.py` – Regression guard for formation duration, aspect ratio, and maintenance metrics.
- [Ref8] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` – Deterministic and Monte Carlo RAAN alignment evidence.
- [Ref9] `artefacts/run_20251018_1207Z/triangle_summary.json` – Maintenance, command latency, and injection recovery metrics.
- [Ref10] `artefacts/run_20251018_1424Z/triangle_summary.json` – Drag dispersion analysis and tolerance verification.
- [Ref11] `docs/compliance_matrix.md` – Compliance statuses, evidence tags, and outstanding actions.
- [Ref12] `docs/verification_plan.md` – Verification and validation strategy, milestones, and resource allocations.
- [Ref13] `config/project.yaml` – Mission-wide configuration including global constants, platform, orbit, simulation, and output settings.
- [Ref14] `docs/stk_export.md` & `tests/test_stk_export.py` – STK exporter usage and regression tests ensuring compatibility.
- [Ref15] `docs/concept_of_operations.md` – Operational scenarios, risk register, and ground segment description.
- [Ref16] `docs/system_requirements.md` – System-level requirements, rationale, and verification mappings.
- [Ref17] `docs/interactive_execution_guide.md` – FastAPI service and debug tooling instructions.
- [Ref18] `docs/_authoritative_runs.md` – Ledger of configuration-controlled runs and maintenance guidance.
- [Ref19] `docs/final_delivery_manifest.md` – Deliverable register and reproduction procedure.
- [Ref20] `src/constellation/geometry.py` & `src/constellation/orbit.py` – Geometry and orbital utilities underpinning simulations.
- [Ref21] `tests/test_stk_export.py` – Validation of exporter outputs, naming sanitation, and file structures.
- [Ref22] `sim/scripts/run_scenario.py` – Scenario pipeline orchestrator with RAAN optimisation and export hooks.
- [Ref23] `tests/integration/test_simulation_scripts.py` – Integration tests verifying scenario execution, CLI operation, and metric extraction.
- [Ref24] `sim/scripts/run_triangle.py` – Triangle simulation CLI entry point and artefact generation.
- [Ref25] `artefacts/triangle_campaign/history.csv` – Quarterly rerun schedule and metadata.
- [Ref26] `run.py` – FastAPI interactive run service and artefact management.
- [Ref27] `run_debug.py` – Debug CLI for triangle and scenario workflows with logging outputs.
- [Ref28] `README.md` & `Makefile` – Repository overview, automation commands, and CI workflow summary.
- [Ref29] `docs/how_to_import_tehran_daily_pass_into_stk.md` – STK 11.2 validation procedure for the daily pass.
- [Ref30] `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/` – Exploratory resampled daily pass dataset for methodological comparison.
- [Ref31] `docs/tehran_triangle_walkthrough.md` – Step-by-step STK validation guide for the triangular formation scenario.
#### 1.A Evidence Mapping Checklist
- Map each literature source to a specific mission requirement identifier and note whether it supports, refines, or challenges the current acceptance criteria.
- Record the simulation artefact or configuration file that will later validate or contradict the literature claim, ensuring traceability in Chapter 4 tables.
- Capture any assumptions (e.g., atmospheric model, command latency) inherent to each source and align them with repository defaults.
- Identify required data visualisations (plots, tables) needed to illustrate the literature insight within the dossier.
- Note potential collaborators or subject-matter experts who could review the selected literature domains for accuracy.
- Flag cross-disciplinary references (e.g., disaster response logistics, communications security) that must be harmonised with mission analysis findings.
- Maintain a living spreadsheet or database with columns for citation, summary, relevance, evidence linkage, and action owner.
- Highlight sources that provide equations or algorithms to be replicated in the simulation chapters.
- Document publication recency and peer-review status to prioritise high-confidence references.
- Ensure all citations include complete bibliographic details for the final References section.

#### 1.B Literature Review Output Templates
- Draft template paragraphs for each subtopic, including placeholders for key statistics, citations, and cross-references to repository artefacts.
- Prepare a figure template that juxtaposes literature-derived tolerances with measured simulation values for cross-track offsets, formation geometry, and maintenance budgets.
- Design a comparative table layout featuring rows for literature sources and columns for requirement alignment, modelling assumptions, and empirical validation plans.
- Create an appendix template to house extended quotations, formula derivations, or data tables extracted from external sources.
- Incorporate footnote placeholders for clarifying terminology differences between literature and repository conventions.
- Build a checklist to confirm that each subsection addresses historical context, current state-of-the-art, and future research avenues.
- Allocate space for commentary on how each source influences experimental design or verification priorities.
- Include guidance on paraphrasing versus direct quotation to maintain academic integrity.
- Outline a process for reconciling conflicting findings between sources and documenting resolution rationale.
- Embed prompts to update the compliance matrix narrative when literature uncovers new verification considerations.

#### 1.C Review Questions for Chapter 1
- Which mission requirement relies most heavily on external literature and how is that dependence mitigated through simulation evidence?
- Do the referenced studies account for mid-latitude atmospheric conditions comparable to Tehran, or is extrapolation required?
- How do published RAAN alignment techniques compare with the repository's optimisation approach in terms of computational cost and accuracy?
- What maintenance strategies dominate the literature, and how do they align with the current 7-day cadence and \(15\,\text{m/s}\) budget?
- Are there emerging payload technologies that could alter the formation geometry or operations assumptions recorded in the configuration files?
- How does literature address single-station commanding resilience, and what lessons inform MR-5 compliance margins?
- Where do publications diverge on acceptable Monte Carlo catalogue sizes, and how does the 300-sample repository standard measure up?
- What best practices exist for documenting compliance evidence in academic missions, and how can they inform Chapter 5's structure?
- Which external datasets or toolkits (beyond STK) are cited, and should they be integrated into the repository workflow?
- What ethical or policy considerations emerge from literature on urban monitoring missions, and how should they be acknowledged in the dossier?
#### 2.A Requirement Traceability Tasks
- Build a matrix linking each mission requirement to its system requirement descendants and verification methods.
- Note the artefact directories and files that currently evidence each requirement; include both deterministic and Monte Carlo data.
- Identify requirements that depend on future algorithm development (e.g., baseline generation) and describe interim evidence strategies.
- Highlight assumptions that require explicit documentation in the dossier (e.g., command request distribution, maintenance cadence).
- Cross-reference requirement statements with ConOps operational scenarios to ensure consistent terminology.
- Annotate which requirements are sensitive to configuration changes (e.g., RAAN adjustments) and plan change-control checkpoints.
- Record review dates from the compliance matrix to schedule future updates.
- Allocate responsibility for maintaining requirement evidence across team members and include their contact details.
- Note any requirement metrics that should be visualised (e.g., cross-track offsets over time) and assign them to figure placeholders.
- Prepare a validation checklist to be used during milestone reviews (VRR, CDR, LRR).

#### 2.B Configuration Audit Prompts
- Verify that `config/project.yaml` metadata matches the dossier front matter and update version numbers as needed.
- Confirm that scenario JSON files reference the correct alignment validation run identifiers and epochs.
- Review Monte Carlo dispersion parameters for realism and alignment with literature values; flag any necessary adjustments.
- Ensure output directory paths and naming templates comply with repository policy and facilitate audit trails.
- Check that STK export settings list all required facilities and that they align with ConOps ground segment descriptions.
- Validate maintenance strategy parameters against recorded metrics and highlight discrepancies for investigation.
- Confirm that simulation start/stop times align with scenario descriptions and captured artefact horizons.
- Document any temporary overrides used during experimentation and plan to revert or formalise them.
- Review communication subsystem parameters for consistency with ConOps link budgets.
- Assess whether data retention and checksum policies meet organisational governance standards.

#### 2.C Review Questions for Chapter 2
- Are there any mission or system requirements lacking current evidence, and what is the plan to obtain it?
- How resilient is the configuration to parameter drift (e.g., RAAN, drag coefficients) over the mission timeline?
- Do the scenario configurations capture all necessary metadata for reproduction and STK validation?
- How do configuration settings align with external standards or best practices identified in Chapter 1?
- Which parameters should be highlighted as potential sensitivity study candidates in Chapter 4?
- Are there conflicts between ConOps assumptions and configuration values that must be reconciled?
- What triggers a configuration version increment, and how is that documented in the dossier?
- Are Monte Carlo seeds and sample counts documented sufficiently for reproducibility?
- How will configuration changes be communicated to stakeholders and preserved for audit?
- What gaps exist in the documentation ecosystem that require creation of new templates or annexes?
#### 3.A Pipeline Verification Checklist
- Trace data flow from configuration loading to STK export for both triangle and daily pass scenarios.
- Confirm that each stage logs sufficient metadata for post-run auditing, including timestamps, seeds, and configuration hashes.
- Validate that artefact directories include README or metadata files summarising run context and key metrics.
- Cross-check CLI help messages against documentation to ensure consistency and completeness.
- Ensure error handling paths are exercised and documented, especially for missing configuration keys or invalid JSON payloads.
- Review logging levels (INFO, DEBUG) to guarantee analysts can diagnose issues without altering source code.
- Verify compatibility with the interactive web service by running both API and CLI workflows for a selected scenario.
- Confirm that unit and integration tests cover failure modes as well as success cases.
- Document dependencies on third-party libraries and note version constraints for reproducibility.
- Plan regression tests for forthcoming features (e.g., baseline generation) even if the implementation is pending.

#### 3.B Artefact Management Prompts
- Catalogue each file type produced by the simulations and describe its intended consumers (analysts, operators, stakeholders).
- Establish naming conventions for exploratory runs versus authoritative baselines to avoid confusion during reviews.
- Record checksum or hash values for critical artefacts to facilitate integrity checks.
- Define archival policies for large Monte Carlo datasets, including criteria for pruning or compressing data.
- Encourage the use of `run_metadata.json` or equivalent summaries to capture environment details (Python version, dependency hashes).
- Outline a directory structure for storing derived plots, tables, and presentation materials generated from artefacts.
- Ensure the `artefacts/triangle_campaign` ledger is updated whenever new drag dispersion runs are executed.
- Document any manual post-processing steps applied to artefacts (e.g., smoothing, subsampling) and justify them.
- Plan for synchronising artefact repositories with remote storage or institutional archives if required by policy.
- Create a checklist for verifying STK export completeness (presence of `.e`, `.sat`, `.gt`, `.fac`, `.int`, `.evt` files) before validation sessions.

#### 3.C Review Questions for Chapter 3
- Are simulation scripts modular enough to support new targets or alternative formation geometries without major refactoring?
- How will the tooling accommodate future force models (e.g., SRP, higher-order gravity) if required by mission evolution?
- Do integration tests sufficiently guard against regressions when refactoring pipeline components?
- Are there opportunities to streamline artefact production or reduce redundant data outputs?
- How effectively do interactive tools support collaboration among geographically distributed analysts?
- What documentation gaps exist for onboarding new contributors to the simulation stack?
- How will the project ensure long-term compatibility with STK updates or alternative visualisation platforms?
- Are there performance bottlenecks that could hinder extensive Monte Carlo campaigns or sensitivity sweeps?
- How is provenance handled when analysts derive secondary artefacts (e.g., aggregated statistics, presentation graphics)?
- What metrics should be tracked to evaluate tooling effectiveness (e.g., run success rate, average execution time)?
#### 4.A Experimental Logging Requirements
- Maintain a run log capturing command invocation, timestamp, Git commit hash, Python version, and environment variables.
- Record configuration overrides, seed values, and simulation durations for each experiment.
- Archive terminal output and relevant log files (`debug.txt`) alongside generated artefacts.
- Document any manual interventions or reruns performed to resolve anomalies.
- Capture hardware specifications (CPU, memory) for reproducibility and performance tracking.
- Note unexpected warnings or errors and describe mitigation steps.
- Update `_authoritative_runs.md` or a draft changelog immediately after completing significant experiments.
- Tag datasets intended for publication or stakeholder delivery with clear labels in the artefact directory.
- Maintain a backlog of pending experiments or reruns flagged during analysis.
- Ensure all logging practices comply with organisational data-handling policies.

#### 4.B Analytical Cross-Checks
- Compare regenerated metrics with archived baselines using automated scripts or spreadsheets.
- Evaluate percentage differences for key parameters (e.g., centroid offsets, \(\Delta v\), aspect ratio) and apply acceptance thresholds.
- Plot time-series overlays to visualise deviations between runs.
- Compute statistical summaries (mean, standard deviation, percentiles) for Monte Carlo catalogues and compare with prior values.
- Inspect STK visualisations to confirm geometric behaviour matches analytical expectations.
- Validate CSV headers and units to ensure consistency across artefacts.
- Confirm that any new metrics introduced align with requirement statements and compliance tracking.
- Document rationale for accepting deviations or updating baselines.
- Update regression tests or documentation if recurring deviations indicate a model change.
- Integrate results into Chapter 5 narratives by drafting preliminary text snippets.

#### 4.C Sensitivity Study Planning
- Define parameter ranges and increments for each sensitivity variable (e.g., drag coefficient, maintenance cadence).
- Determine the number of simulations required and assess computational resource needs.
- Plan data capture formats for efficient aggregation (e.g., consolidated CSV, database entries).
- Establish criteria for interpreting sensitivity results (e.g., identifying thresholds where compliance risk increases).
- Assign responsibilities for running and analysing sensitivity campaigns.
- Schedule sensitivity studies around major milestones to inform decision-making.
- Ensure sensitivity outputs feed into risk assessments and compliance documentation.
- Document any coupling effects observed between variables (e.g., drag and command latency).
- Prepare summary tables and graphics for inclusion in the discussion chapter.
- Archive all sensitivity configurations and outputs with descriptive naming conventions.

#### 4.D Review Questions for Chapter 4
- Do experimental procedures fully reproduce baseline results, and if not, what factors contribute to deviations?
- Are logging and artefact management practices sufficient for audit and peer review?
- How do new experiments influence requirement compliance margins or risk assessments?
- Are there opportunities to automate repetitive analysis tasks to reduce human error?
- How will sensitivity studies inform future configuration updates or literature reviews?
- Are Monte Carlo catalogues large enough to capture tail-risk behaviour for mission assurance?
- What steps are needed to prepare simulation outputs for stakeholder briefings or regulatory submissions?
- Do experimental findings necessitate updates to ConOps scenarios or operational checklists?
- How are exploratory runs distinguished from baseline evidence in documentation and repositories?
- What additional experiments should be prioritised before upcoming milestones?
#### 5.A Compliance Evidence Synthesis Tasks
- Prepare a compliance summary table listing each requirement, measured value, margin, and evidence reference tag.
- Draft narrative sections that explain how deterministic and Monte Carlo results jointly substantiate compliance.
- Identify where regression tests provide ongoing assurance and cite them in the text.
- Integrate risk mitigations from ConOps into the compliance discussion, emphasising operational readiness.
- Document any waivers or conditional acceptances and their associated decision records.
- Highlight dependencies between requirements (e.g., maintenance budgeting affecting robustness) and discuss cascading impacts.
- Include qualitative commentary from validation activities (e.g., stakeholder reviews) to complement quantitative metrics.
- Prepare figure captions that describe how each plot supports compliance arguments.
- Annotate which compliance statements require periodic re-verification and schedule future checks.
- Summarise lessons learned from the compliance process to inform future missions.

#### 5.B Validation Reporting Prompts
- Compile a validation log summarising STK import results, including screenshots, metrics, and analyst notes.
- Document any manual adjustments made within STK (e.g., camera settings, animation parameters) and justify them.
- Record automation script versions and parameters used during validation runs.
- Capture stakeholder feedback from validation sessions and note action items.
- Ensure validation evidence is stored alongside corresponding simulation artefacts with clear references.
- Prepare a checklist for repeating validation after configuration or code changes.
- Note any observed discrepancies between STK outputs and Python-generated metrics and plan resolutions.
- Verify that validation activities align with V&V plan milestones and update schedules if necessary.
- Summarise resource utilisation (time, personnel) for validation activities to inform planning.
- Capture outstanding validation tasks or dependencies on external systems.

#### 5.C Discussion Enhancement Points
- Compare measured performance with literature expectations and comment on alignment or divergence.
- Evaluate risk reduction achieved through mitigation strategies and identify residual concerns.
- Discuss the robustness of the mission concept under worst-case scenarios revealed by Monte Carlo results.
- Reflect on the maturity of the simulation pipeline and its suitability for future mission phases.
- Highlight cross-functional insights (e.g., operations, payload, compliance) that emerged from the analysis.
- Identify policy or ethical considerations that should be addressed in the concluding chapter.
- Suggest metrics for ongoing monitoring during operations based on simulation findings.
- Evaluate stakeholder readiness and confidence based on validation outcomes.
- Consider how the mission evidence supports broader organisational objectives or research goals.
- Recommend updates to documentation templates or processes based on discussion insights.

#### 5.D Review Questions for Chapter 5
- Does the compliance narrative convincingly link evidence to each requirement without gaps?
- Are validation procedures reproducible and documented to a standard acceptable for audits?
- What additional evidence might stakeholders request before approving mission readiness?
- How do discussion sections integrate literature findings with empirical data?
- Are risk mitigations adequately substantiated by simulation and validation results?
- Do figures and tables enhance understanding of compliance status, or are further visuals needed?
- How are uncertainties communicated to avoid overstating confidence?
- What follow-on tests or analyses are recommended to maintain compliance assurance?
- Are there any conflicts between validation outcomes and requirements that need resolution?
- How will compliance status be monitored and reported post-publication?
#### 6.A Synthesis Workflow Prompts
- Create a thematic map linking literature themes, requirement outcomes, and simulation evidence to ensure cohesive discussion.
- Develop summary tables that juxtapose expected versus observed performance across mission dimensions.
- Integrate quotes or insights from stakeholder engagements to add qualitative context.
- Identify contradictions or unresolved questions and document plans for resolution.
- Highlight contributions to broader research fields (e.g., formation flying, disaster response) and cite relevant literature.
- Prepare cross-chapter pointers (e.g., "see Chapter 4 sensitivity analysis") to guide readers through complex arguments.
- Draft executive summaries for each synthesis subsection to facilitate stakeholder review.
- Use colour-coded annotations (in drafting tools) to track where additional evidence or references are needed.
- Establish review checkpoints with subject-matter experts to validate interpretations.
- Document how synthesis insights influence recommendations in the next chapter.

#### 6.B Risk and Uncertainty Analysis Tasks
- Update risk registers with quantified probabilities and impacts based on simulation data.
- Evaluate whether mitigation strategies remain effective under worst-case Monte Carlo outcomes.
- Assess the sensitivity of risks to configuration changes identified in earlier chapters.
- Document assumptions underpinning risk evaluations and flag those requiring further validation.
- Prepare visual aids (heat maps, bow-tie diagrams) to communicate risk posture to stakeholders.
- Coordinate with operations teams to align risk mitigations with procedural updates.
- Capture contingency triggers and decision thresholds derived from sensitivity studies.
- Monitor risk interdependencies and potential cascading effects.
- Integrate uncertainty analysis results into compliance and validation reporting.
- Plan ongoing risk monitoring mechanisms post-publication.

#### 6.C Stakeholder Impact Assessment
- Map mission results to stakeholder objectives (e.g., rapid imagery delivery, resilient operations) and evaluate fulfilment.
- Document anticipated workflow adjustments for ground segment teams based on maintenance and command metrics.
- Assess payload utilisation opportunities enabled by the triangular formation and access window.
- Consider data-sharing or interoperability implications for partner organisations.
- Identify training or resource requirements arising from the mission concept.
- Evaluate potential societal or policy impacts of sustained urban monitoring.
- Prepare communication materials tailored to different stakeholder groups (technical, managerial, policy).
- Align recommendations with stakeholder decision timelines and review boards.
- Capture feedback loops for incorporating stakeholder insights into future updates.
- Ensure stakeholder narratives remain consistent with evidence presented throughout the dossier.

#### 6.D Review Questions for Chapter 6
- Does the synthesis convincingly integrate literature, simulation, and validation evidence?
- Are risk analyses transparent about assumptions and limitations?
- How will stakeholder needs evolve based on the presented findings, and are recommendations responsive?
- Are there conflicting interpretations of evidence that require adjudication or further study?
- Does the chapter set up the conclusions with clear, evidence-backed arguments?
- What additional data or studies would strengthen the synthesis?
- Are ethical considerations adequately addressed in the context of mission objectives?
- How will insights from this chapter inform future documentation or research initiatives?
- Are cross-references to earlier chapters sufficient to guide readers through complex topics?
- What metrics should be tracked post-publication to monitor ongoing relevance?
#### 7.A Conclusion Drafting Prompts
- Summarise key numerical achievements (e.g., access window duration, centroid offsets, maintenance margins) in concise bullet points.
- Highlight strategic benefits (e.g., resilient operations, rapid data delivery) for stakeholder messaging.
- Reflect on methodological contributions (e.g., integrated RAAN optimisation, drag dispersion campaign) and their broader value.
- Acknowledge limitations and areas requiring further validation to maintain credibility.
- Reinforce alignment with stakeholder objectives and organisational strategy.
- Emphasise compliance milestones achieved and outline residual actions.
- Prepare short-form takeaways for executive readers or presentation slides.
- Identify quotes or sound bites suitable for communications material.
- Ensure conclusions flow logically from synthesis discussions and do not introduce new evidence.
- Cross-reference relevant chapters to guide readers seeking deeper details.

#### 7.B Recommendation Prioritisation Tasks
- Categorise recommendations by timeframe (near-term, mid-term, long-term) and urgency.
- Assign responsible teams or roles for each recommendation and confirm resource availability.
- Estimate effort or cost implications and note dependencies on external partners or approvals.
- Define success criteria or metrics for evaluating recommendation implementation.
- Align recommendations with roadmap milestones and verification plan schedules.
- Identify potential risks associated with implementing recommendations and propose mitigations.
- Highlight quick wins that demonstrate progress while longer-term work is planned.
- Provide rationale for deferring or deprioritising certain improvements.
- Ensure recommendations are actionable and measurable rather than aspirational.
- Prepare a summary table capturing recommendation, owner, timeline, resources, and status.

#### 7.C Configuration Control Actions Checklist
- Review all artefacts generated during analysis and mark those requiring archival or promotion to baseline status.
- Update configuration files and metadata to reflect adopted changes and record reasons.
- Confirm that documentation (ConOps, SRD, compliance matrix) reflects the latest evidence and decisions.
- Schedule configuration control board reviews if major updates are proposed.
- Ensure STK exports are regenerated and validated when configuration changes affect orbital parameters.
- Archive obsolete artefacts with clear superseded-by references to maintain traceability.
- Communicate configuration changes to all stakeholders, including operations and analysis teams.
- Document lessons learned from configuration control activities to improve future processes.
- Verify that version control history captures all updates with descriptive commit messages.
- Plan follow-up audits to confirm configuration control actions were completed successfully.

#### 7.D Review Questions for Chapter 7
- Do conclusions accurately reflect the evidence without overstating certainty?
- Are recommendations feasible given resource and schedule constraints?
- How will progress on recommendations be tracked and reported?
- Are configuration control actions sufficient to maintain evidence integrity?
- Do conclusions and recommendations address stakeholder expectations articulated in Chapter 1?
- Are there conflicts between recommendations that require prioritisation or compromise?
- How will future updates be integrated into the dossier without duplicating effort?
- What governance mechanisms are needed to oversee recommendation implementation?
- Do knowledge management plans ensure long-term accessibility of evidence and documentation?
- Are there communication strategies in place to share conclusions with broader audiences?
#### 8.A Appendix Development Tasks
- Draft outlines for each appendix, listing the data, figures, or tables to be included.
- Ensure appendices include context-setting introductions and cross-references to main chapters.
- Prepare templates for configuration snapshots that highlight key parameters and change logs.
- Collect supplementary plots and annotate them with generation scripts and seeds.
- Assemble detailed tables (e.g., maintenance budgets, RAAN sweeps) with clear units and footnotes.
- Document computational resource usage and execution environments in the methodological appendix.
- Curate a glossary of terms and acronyms, confirming definitions align with industry standards.
- Include a bibliography appendix if extended references exceed main text capacity.
- Provide guidance on updating appendices when new artefacts or analyses become available.
- Ensure appendices adhere to formatting and citation standards consistent with the main document.

#### 8.B Submission Quality Assurance Checklist
- Perform spell-check and grammar reviews focusing on British English usage.
- Validate internal hyperlinks and cross-references within the document.
- Confirm figure and table numbering is sequential and consistent.
- Verify that all references in the text appear in the References list and vice versa.
- Check that document metadata (title, authors, version) is accurate and current.
- Ensure page layouts or PDF exports preserve table readability and figure clarity.
- Review accessibility considerations (alt text for figures, descriptive captions).
- Conduct a peer review or red-team edit to challenge assumptions and catch omissions.
- Confirm compliance with organisational publication policies or templates.
- Prepare a final sign-off sheet capturing reviewer approvals and outstanding actions.

#### 8.C Citation Management Prompts
- Maintain a central bibliography file that can be reused across related projects.
- Tag references with keywords (e.g., maintenance, RAAN, ConOps) to facilitate retrieval.
- Record access dates for online sources and ensure persistent identifiers (DOI, URI) are captured.
- Standardise citation formatting to match institutional guidelines.
- Track which references support figures, tables, or equations to streamline updates.
- Plan periodic audits of references to retire outdated or superseded sources.
- Coordinate with collaborators to avoid duplicate or inconsistent citations.
- Document any proprietary or restricted sources and manage access permissions.
- Integrate citation management with collaborative writing tools if applicable.
- Prepare citation style guides or cheat sheets for contributors.

#### 8.D Review Questions for Chapter 8
- Do appendices provide sufficient depth without duplicating main text content?
- Are submission processes robust enough to catch errors before publication?
- Is citation management organised to support future updates and reuse?
- How will appendices be updated as new evidence or analyses emerge?
- Are style and formatting guidelines clear and consistently applied?
- What tools or processes could improve document maintenance efficiency?
- Are there training needs for contributors unfamiliar with the documentation standards?
- How will reviewer feedback be captured and tracked through resolution?
- Are there external compliance or publication requirements that must be met?
- What lessons from this documentation cycle should inform future projects?
