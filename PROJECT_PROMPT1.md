# Mission Research Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Preface and Usage Notes
- This prompt synthesises every configuration-controlled artefact, analytical script, and validation record within the `formation-sat-2` repository to guide the production of a comprehensive mission research dossier.
- Maintain British English spelling throughout the response that this prompt elicits, preserving the academic yet accessible tone mandated in `AGENTS.md`.
- Treat each chapter directive as mandatory. Deliver the complete dossier in a single continuous output, beginning with Chapter 1 and proceeding sequentially through Chapter 6 without interleaving commentary or metanarrative asides.
- Cite repository artefacts inline using the `[RefX]` convention provided at the close of each chapter, and compile a dedicated reference list for every chapter to mirror the structure of `docs/research_prompt.md`.
- When figures, tables, or equations are suggested, label them explicitly (e.g., `[Suggested Figure 3.2]`) and describe the data source, format, and transformation pipeline required to realise them.
- Reinforce Systems Tool Kit (STK 11.2) interoperability expectations in any section that depends on exported ephemerides, ground tracks, or contact intervals. Mention the specific exporter routines (`tools/stk_export.py`) and validation guides (`docs/how_to_import_tehran_daily_pass_into_stk.md`, `docs/stk_export.md`).
- Integrate quantitative evidence drawn from authoritative run directories (`artefacts/run_20251018_1207Z`, `artefacts/run_20251020_1900Z_tehran_daily_pass_locked`, `artefacts/triangle_run`, etc.) when substantiating analytical claims. Highlight the difference between windowed and full-propagation metrics wherever both appear in the data (e.g., \(343.62\,\text{km}\) versus \(641.89\,\text{km}\) maximum ground distances in the triangle summary).
- Include cross-references to automated regression safeguards (`tests/unit/test_triangle_formation.py`, `tests/integration/test_simulation_scripts.py`, `tests/test_stk_export.py`) in discussions of verification and future work.
- Each chapter concludes with an explicit checklist of deliverables, a proposed narrative flow, and a numbered reference roster drawing solely from repository artefacts or established aerospace standards. Augment these references with external literature only when instructed, and ensure any new sources are contextualised against the repository’s evidence base.
- Appendices consolidate reusable prompts for literature review searches, data extraction templates, and comparative analyses that span multiple chapters. These appendices are integral to the dossier; do not omit them.

---

## Chapter 1 – Mission Framing, Requirements Baseline, and Literature Review Scope

### 1.1 Mission Overview Anchors
- Summarise the mission intent articulated in `README.md`, highlighting the daily \(\approx 90\,\text{s}\) equilateral formation objective and the dual-plane constellation architecture.
- Reiterate the stakeholder motivations captured in `docs/project_overview.md`, aligning them with the Mission Requirements (`docs/mission_requirements.md`) and the Concept of Operations (`docs/concept_of_operations.md`).
- Enumerate the configuration governance expectations, including run naming conventions (`run_YYYYMMDD_hhmmZ`), semantic versioning in `config/project.yaml`, and the authoritative run ledger in `docs/_authoritative_runs.md`.
- State the STK compatibility doctrine: all exported artefacts must originate from `tools/stk_export.py` and be validated using the guides in `docs/stk_export.md` and `docs/how_to_import_tehran_daily_pass_into_stk.md`.

### 1.2 Literature Review Mandates – Mission Architecture and Requirements Traceability
- Conduct a literature review on multi-plane LEO formations targeting transient geometric events. Prioritise academic sources from 2020–2025, cross-referencing earlier seminal works when indispensable (e.g., D’Amico et al. 2005).
- Extract comparative analyses of sun-synchronous RAAN alignment strategies, emphasising methods that minimise centroid cross-track error at predetermined local solar times.
- Investigate single-ground-station commanding architectures for responsive formation flying, focusing on latency management within a 12-hour limit.
- Review maintenance strategies for small-satellite formations with \(\Delta v\) caps below \(15\,\text{m/s}\) per annum, noting drag modulation versus impulsive manoeuvres.
- Compile literature on Monte Carlo robustness validation for injection dispersions of ±5 km along-track and ±0.05° inclination, linking to the MR-7 resilience requirement.

### 1.3 Repository Artefact Integration Tasks
- Tabulate every Mission Requirement and its compliance status from `docs/compliance_matrix.md`, noting the evidence tags (EV-1 through EV-5) and associated run directories.
- Summarise the baseline configuration parameters in `config/project.yaml`, breaking down metadata, global constants, platform properties, orbital elements, simulation controls, and output directives.
- Capture scenario-level metadata for `config/scenarios/tehran_daily_pass.json` and `config/scenarios/tehran_triangle.json`, highlighting RAAN values, access windows, Monte Carlo specifications, and maintenance cadences.
- Document how the run ledger in `docs/_authoritative_runs.md` maps onto the compliance matrix, emphasising which runs are exploratory versus configuration-controlled.

### 1.4 Literature Review Prompt Blocks
- **Block A – Mission Geometry Foundations**: Survey repeating-ground-track theory, RAAN drift mitigation under \(J_2\) perturbations, and relative orbital elements framing. Distil at least five contemporary sources and map them to MR-1 through MR-4.
- **Block B – Operations and Ground Segment**: Investigate case studies of single-station operations supporting rapid uplink cycles. Compare their latency assurances with MR-5 expectations and cite how they achieved redundancy (e.g., cross-support agreements akin to Kerman–Redu contingencies).
- **Block C – Maintenance and Robustness**: Evaluate trade-offs between cold-gas and electric propulsion for low-thrust maintenance manoeuvres, including delta-v budgeting methodologies. Relate findings to MR-6 and MR-7 evidence.
- **Block D – STK Interoperability**: Review best practices for ensuring text-based ephemeris compatibility with STK 11.2. Contrast exporter design choices against third-party tools, referencing repository implementation decisions.

### 1.5 Narrative Flow Outline
- Initiate with the mission statement, segue into stakeholder drivers, and articulate the requirement hierarchy. Introduce the literature review pillars, weaving repository artefacts into the motivation. Conclude with a roadmap preview of how subsequent chapters operationalise the mission framing.

### 1.6 Chapter 1 Deliverable Checklist
1. Mission overview narrative aligned with repository intent statements.
2. Literature review synthesis spanning geometry, operations, maintenance, and STK interoperability.
3. Tables summarising configuration baselines and requirement compliance statuses.
4. Annotated discussion of run identifiers and governance conventions.
5. References section enumerating all cited artefacts and external sources.

### 1.7 Chapter 1 Suggested Figures, Tables, and Equations
- [Suggested Figure 1.1] Timeline schematic illustrating roadmap stages from `docs/project_roadmap.md` mapped to mission phases.
- [Suggested Table 1.1] Mission Requirement versus compliance status matrix derived from `docs/compliance_matrix.md` (include deterministic and Monte Carlo metrics).
- [Suggested Equation 1.1] Hill–Clohessy–Wiltshire relative motion relations underpinning relative orbital elements (`src/constellation/roe.py`).
- [Suggested Equation 1.2] Definition of mission-aligned cross-track error \(d = R_E \Delta\theta\), contextualised with Tehran centroid offsets.

### 1.8 Chapter 1 References
1. `README.md` – Mission intent overview and automation summary.
2. `docs/project_overview.md` – Academic mission framing and recent verification evidence.
3. `docs/mission_requirements.md` – Mission Requirement matrix.
4. `docs/concept_of_operations.md` – Operational objectives and scenarios.
5. `docs/_authoritative_runs.md` – Run ledger and evidence catalogue.
6. `config/project.yaml` – Baseline configuration snapshot.
7. `docs/compliance_matrix.md` – Compliance status and evidence references.
8. `docs/stk_export.md` – STK exporter guidance.
9. `docs/how_to_import_tehran_daily_pass_into_stk.md` – STK validation workflow.
10. `docs/project_roadmap.md` – Staged research roadmap.
11. `src/constellation/roe.py` – Relative orbital element utilities.
12. D’Amico, S. et al. (2005) – Relative orbital elements reference.

### 1.9 Extended Task Breakdown – Chapter 1
1. Draft a mission intent synopsis (250–300 words) explicitly citing repository artefacts listed in Section 1.8. Ensure the synopsis introduces the Tehran focus, dual-plane architecture, and \(90\,\text{s}\) formation requirement.
2. Construct a requirement traceability table linking MR-1 through MR-7 to stakeholder motivations extracted from `docs/concept_of_operations.md` and `docs/project_overview.md`.
3. Document the configuration control lifecycle: propose a paragraph on run ID allocation, a paragraph on semantic versioning (`config/project.yaml`), and a paragraph on STK validation logging.
4. Prepare a literature review matrix with the following columns: Topic, Key Findings, Repository Alignment, Identified Gap, Proposed Citation Tag. Populate at least five rows per literature review block.
5. Summarise cross-discipline implications (e.g., imaging payload design, ground segment staffing) in bullet form, referencing where deeper treatment will occur in later chapters.
6. Draft a risk statement addressing the consequences of omitting STK validation references in Chapter 1, and note the corrective actions.
7. Compile a glossary snippet for Chapter 1 introducing mission-specific terminology (e.g., “transient formation event”, “centroid cross-track magnitude”).
8. Outline interview questions for subject-matter experts covering mission framing topics, noting how their responses would integrate into the dossier.
9. Schedule follow-up literature searches with priorities (High, Medium, Low) and responsible analysts. Include due dates aligned to roadmap Stage 1 milestones.
10. Develop a peer-review checklist to validate Chapter 1 outputs before progressing to Chapter 2.

---

## Chapter 2 – Configuration, Geometry, and Data Foundations

### 2.1 Configuration Audit Tasks
- Provide a structured walkthrough of `config/project.yaml`, detailing how metadata, global constants, platform characteristics, orbit definitions, simulation controls, and output preferences support the triangular formation mission.
- Describe the schema of scenario JSON files, noting required keys (`metadata`, `orbital_elements`/`reference_orbit`, `formation`, `access_window`, `payload_constraints`, etc.) and their cross-links to run artefacts.
- Explain the repository naming conventions enforced in scenario metadata (`identifier`, `scenario_name`, `alignment_validation`, `validated_against_stk_export`).
- Highlight the interplay between configuration files and the FastAPI service (`run.py`), including how scenario listings and inline overrides are exposed via `/runs/configs`.

### 2.2 Geometry Reconstruction Exercises
- Using `sim/formation/triangle.py`, reconstruct how LVLH offsets create the 6 km equilateral formation and translate into inertial coordinates. Discuss the `_formation_offsets`, `_lvlh_frame`, and `_summarise_triangle_metrics` routines.
- Outline the computation of centroid geodetic coordinates and maximum ground distances, emphasising the difference between windowed and global propagation statistics (e.g., \(343.62\,\text{km}\) vs \(641.89\,\text{km}\)).
- Detail how orbital elements are reconstructed at the midpoint sample via `cartesian_to_classical`, confirming plane allocations (two spacecraft in Plane A, one in Plane B).
- Describe the maintenance, command latency, injection recovery, and drag dispersion analyses embedded in the triangle simulator.

### 2.3 Data Artefact Inventory
- Catalogue the contents of `artefacts/triangle_run/`, noting JSON summaries, CSV tables, SVG plots, and STK export directories. Explain how the curated snapshot mirrors `run_20251018_1424Z` and why it remains analyst ready.
- Summarise the artefacts in `artefacts/run_20251018_1207Z`, focusing on `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, and `injection_recovery_cdf.svg`.
- Describe the deterministic and Monte Carlo summaries in `artefacts/run_20251020_1900Z_tehran_daily_pass_locked`, including centroid statistics, window timing, and STK exports.
- Highlight the presence of exploratory datasets (e.g., `run_20260321_0740Z_tehran_daily_pass_resampled`) and clarify how they differ from authoritative evidence.

### 2.4 Repository Script Interfaces
- Explain the inputs and outputs of `sim/scripts/run_triangle.py`, `sim/scripts/run_scenario.py`, and `sim/scripts/run_triangle_campaign.py`, including command-line arguments and expected artefact directories.
- Discuss how `run.py` orchestrates triangle and scenario runs via FastAPI endpoints, persists run metadata in `artefacts/web_runs`, and streams debug logs.
- Describe the debug workflow offered by `run_debug.py`, emphasising CSV exports for positions, velocities, and geodetic coordinates, alongside JSON summaries for scenario runs.
- Outline the role of `tools/stk_export.py`, including `StateSample`, `PropagatedStateHistory`, `GroundTrack`, `GroundContactInterval`, and `ScenarioMetadata` classes, and the sanitisation of STK identifiers.

### 2.5 Geometry-Focused Literature Review Prompts
- Survey contemporary research on LVLH frame transformations and their application to formation flying. Compare the repository’s implementation (`src/constellation/frames.py`) with alternative formulations.
- Review literature on triangle area stability metrics, centroid-based ground distance calculations, and their relevance to cooperative sensing missions.
- Investigate studies on command latency modelling for single-station operations, linking theoretical frameworks to the repository’s `_analyse_command_latency` function.
- Examine drag dispersion modelling techniques for small satellites, including density scaling factors and ballistic coefficient perturbations, contextualising with `_run_atmospheric_drag_dispersion_monte_carlo`.

### 2.6 Suggested Analytical Assets
- [Suggested Table 2.1] Breakdown of configuration parameters from `config/project.yaml`, grouped by subsystem.
- [Suggested Figure 2.1] LVLH triangle visualisation derived from `artefacts/triangle_run/triangle_summary.json`.
- [Suggested Figure 2.2] Command latency histogram built from `command_windows.csv`.
- [Suggested Equation 2.1] Great-circle distance formula implemented in `haversine_distance`.
- [Suggested Equation 2.2] Command latency probability approximation linking contact duration to orbital period (as used in `_analyse_command_latency`).

### 2.7 Narrative Flow Outline
- Begin with configuration governance, transition into geometric modelling, and then explore artefact inventories. Close with a synthesis of how scripts and tools operationalise the data foundations and motivate literature deep-dives.

### 2.8 Chapter 2 Deliverable Checklist
1. Configurational deep dive with tabulated parameters.
2. Geometric derivation explanations anchored in source code.
3. Comprehensive artefact inventory with provenance notes.
4. Script interface documentation connecting to automation pathways.
5. Geometry-centric literature review summary.
6. References section covering all cited artefacts and external works.

### 2.9 Chapter 2 References
1. `config/project.yaml` – Configuration baseline.
2. `config/scenarios/tehran_triangle.json` – Triangle formation scenario definition.
3. `config/scenarios/tehran_daily_pass.json` – Daily pass configuration.
4. `artefacts/triangle_run/triangle_summary.json` – Triangle metrics and samples.
5. `artefacts/run_20251018_1207Z/maintenance_summary.csv` – Maintenance analytics.
6. `artefacts/run_20251018_1207Z/command_windows.csv` – Command latency windows.
7. `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json` – Locked daily pass deterministic metrics.
8. `sim/formation/triangle.py` – Triangle simulation implementation.
9. `run.py` – FastAPI orchestration service.
10. `run_debug.py` – Debug workflow interface.
11. `tools/stk_export.py` – STK export utilities.
12. `src/constellation/frames.py` – Reference frame conversions.
13. Contemporary LVLH and drag dispersion literature (2020–2025) identified by the researcher.

### 2.10 Extended Task Breakdown – Chapter 2
1. Produce a configuration catalogue table covering every subsection of `config/project.yaml`. For each parameter include: Name, Value, Units, Rationale, Downstream Consumer, STK Dependency.
2. Draft JSON schema descriptions for the Tehran scenarios, noting optional versus mandatory keys and expected data types. Include validation rules and example snippets.
3. Create a crosswalk mapping configuration parameters to simulation outputs (e.g., `simulation.time_step_seconds` → sampling cadence in `triangle_summary.json`).
4. Summarise transformation pipelines in `sim/formation/triangle.py`, detailing the order of operations from LVLH offsets to artefact production. Provide pseudo-code snippets where beneficial.
5. Record filesystem inventories for key run directories using structured bullet lists capturing filenames, file types, data volumes, and verification status.
6. Draft instructions for analysts to regenerate artefacts, including command invocations, expected runtime, and output validation checks.
7. Assemble a list of metrics requiring dual reporting (windowed vs full propagation), indicating where each value appears and how to contextualise it.
8. Prepare a metadata alignment report comparing scenario JSON `alignment_validation` fields with actual run directories and `docs/_authoritative_runs.md` entries.
9. Develop a review questionnaire guiding configuration walkthrough meetings with systems engineers, including prompts on assumptions, tolerances, and data retention policies.
10. Compile an appendix-ready summary of coordinate frame conventions used across code modules (`frames.py`, `orbit.py`, `triangle.py`).

---

## Chapter 3 – Simulation Pipeline, Toolchain, and Execution Protocols

### 3.1 Scenario Runner Workflow Description
- Describe the sequential stages executed by `sim/scripts/run_scenario.py`: RAAN alignment optimisation, access node discovery, mission phase synthesis, two-body propagation, high-fidelity \(J_2\)+drag propagation, metric extraction, and optional STK export.
- Explain the structure and purpose of the `Node` and `Phase` dataclasses, including how they facilitate downstream reporting and STK validation.
- Detail the RAAN optimisation summary recorded in the `raan_alignment` block, citing the initial and optimised RAAN values and centroid cross-track magnitude.
- Summarise the stage sequence logged in `scenario_summary.json`, ensuring the narrative highlights deterministic versus Monte Carlo outputs.

### 3.2 Triangle Simulation Workflow
- Outline the execution path of `sim/scripts/run_triangle.py`, from configuration loading through LVLH transformation, metric calculation, maintenance estimation, Monte Carlo campaigns, drag dispersion analysis, and STK export.
- Describe how CSV artefacts (`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`) and SVG plots (`injection_recovery_cdf.svg`) are generated and structured.
- Explain how `TriangleFormationResult.to_summary()` organises metrics and samples for JSON serialisation.
- Discuss how the simulator enforces compliance with mission requirements (e.g., 90-second window, aspect ratio ≤1.02, command latency margin ≥0) and records assumptions.

### 3.3 Automation and Interactive Interfaces
- Detail how the FastAPI service (`run.py`) exposes triangle and scenario runs, including payload models (`TriangleRunRequest`, `ScenarioRunRequest`, `DebugRunRequest`), job management (`src/constellation/web/jobs.py`), and log streaming endpoints.
- Explain the interactive execution flow described in `docs/interactive_execution_guide.md`, including environment prerequisites, run orchestration, and artefact management.
- Summarise the debug CLI operations in `run_debug.py`, including CSV outputs and JSON summaries, and how they support audit trails.
- Describe the `tools/render_debug_plots.py` (if applicable) and other utility scripts that aid visualisation.

### 3.4 Regression Safeguards and Continuous Integration
- Document the unit and integration tests guarding the simulation pipeline: `tests/unit/test_triangle_formation.py`, `tests/integration/test_simulation_scripts.py`, and `tests/test_stk_export.py`.
- Explain how these tests enforce geometry, maintenance, latency, and export compliance, including specific assertions (e.g., Monte Carlo sample counts, STK file existence, name sanitisation).
- Summarise the role of `Makefile` targets (`make triangle`, `make scenario`, `make simulate`, `make docs`, etc.) and the CI workflow referenced in `README.md`.
- Emphasise the expectation that new scripts maintain compatibility with STK exports and integrate into regression suites.

### 3.5 Literature Review Prompts – Simulation and Tooling
- Survey state-of-the-art RAAN optimisation techniques for repeat-ground-track missions, comparing them to the repository’s search-and-evaluate approach.
- Review literature on high-fidelity propagation pipelines integrating \(J_2\) and drag perturbations, including validation against STK or similar toolchains.
- Investigate methodologies for Monte Carlo campaign automation in formation flying, focusing on reproducibility and artefact logging.
- Examine best practices for mission analysis web services or dashboards that expose run orchestration, drawing parallels to the FastAPI implementation.

### 3.6 Suggested Analytical Assets
- [Suggested Figure 3.1] Flowchart of the scenario pipeline stages with artefact outputs annotated.
- [Suggested Figure 3.2] Monte Carlo injection recovery cumulative distribution from `injection_recovery_cdf.svg`.
- [Suggested Table 3.1] Comparison of deterministic versus Monte Carlo centroid statistics for the daily pass scenario.
- [Suggested Table 3.2] Summary of regression tests, including asserted metrics and referenced artefacts.
- [Suggested Equation 3.1] Monte Carlo success rate definition and \(p_{95}\) calculation methodology used in `_run_injection_recovery_monte_carlo`.

### 3.7 Narrative Flow Outline
- Present the scenario pipeline, transition into the triangle simulator, discuss automation interfaces, and conclude with regression safeguards and supporting literature.

### 3.8 Chapter 3 Deliverable Checklist
1. Exhaustive description of scenario and triangle workflows.
2. Documentation of automation interfaces and job management.
3. Regression safeguard summary with highlighted assertions.
4. Literature review on optimisation, propagation, Monte Carlo automation, and mission analysis services.
5. Reference section aligning citations with repository artefacts and external sources.

### 3.9 Chapter 3 References
1. `sim/scripts/run_scenario.py` – Scenario pipeline implementation.
2. `sim/scripts/run_triangle.py` – Triangle simulation CLI.
3. `sim/scripts/run_triangle_campaign.py` – Campaign automation scaffold.
4. `run.py` – FastAPI orchestration service.
5. `docs/interactive_execution_guide.md` – Interactive execution guide.
6. `run_debug.py` – Debug CLI workflow.
7. `src/constellation/web/jobs.py` – Subprocess job manager.
8. `tests/unit/test_triangle_formation.py` – Triangle compliance tests.
9. `tests/integration/test_simulation_scripts.py` – Scenario pipeline tests.
10. `tests/test_stk_export.py` – STK exporter regression tests.
11. `Makefile` – Automation entry points.
12. Contemporary literature on RAAN optimisation, high-fidelity propagation, Monte Carlo automation, and mission analysis tooling (2020–2025).

### 3.10 Extended Task Breakdown – Chapter 3
1. Produce a stage-by-stage narrative of `run_scenario.py`, dedicating at least one paragraph to each pipeline stage (RAAN alignment, node discovery, phase generation, two-body propagation, \(J_2\)+drag propagation, metric extraction, STK export).
2. Illustrate data structures using UML-style diagrams or descriptive bullet hierarchies for `Node`, `Phase`, and summary payloads.
3. Document command-line usage examples for triangle and scenario runners, including optional flags, sample output directories, and error-handling behaviours.
4. Summarise FastAPI endpoint behaviours (`/runs/triangle`, `/runs/pipeline`, `/runs/debug`, `/runs/history`, `/runs/configs`) with required payload fields, response schemas, and failure modes.
5. Draft operational runbooks for the web service and debug CLI, outlining pre-run checks, monitoring procedures, and artefact archival steps.
6. Tabulate regression test coverage with columns for Module, Assertion Focus, Referenced Artefact, Failure Impact, Suggested Extensions.
7. Describe how environment variables or configuration overrides could be integrated for future automation, noting repository constraints.
8. Provide guidance on logging expectations, including log file locations, verbosity levels, and rotation/archival strategies.
9. Outline integration steps for incorporating new scenarios into the pipeline, from configuration authoring to regression test updates.
10. Recommend metrics for tracking automation health (e.g., run success rates, artefact generation counts, STK validation confirmations) and suggest dashboard concepts.

---

## Chapter 4 – Authoritative Runs, Quantitative Evidence, and Comparative Analyses

### 4.1 Authoritative Run Summaries
- Present `run_20251018_1207Z` as the maintenance and robustness campaign underpinning MR-5 to MR-7. Include command latency (\(1.53\,\text{h}\)), annual \(\Delta v\) (\(14.04\,\text{m/s}\)), and Monte Carlo \(p_{95}\) \(\Delta v = 0.041\,\text{m/s}\) metrics.
- Detail `run_20251020_1900Z_tehran_daily_pass_locked`, emphasising the optimised RAAN \(350.7885044642857^{\circ}\), centroid \(12.143\,\text{km}\), worst-vehicle \(27.759\,\text{km}\), and Monte Carlo centroid \(p_{95}\) \(24.180\,\text{km}\).
- Summarise `artefacts/triangle_run/` (mirroring `run_20251018_1424Z`), highlighting the \(96\,\text{s}\) window, \(343.62\,\text{km}\) windowed ground distance, and \(641.89\,\text{km}\) full propagation maximum.
- Mention exploratory runs (`run_20260321_0740Z_tehran_daily_pass_resampled`, etc.) and clarify their non-baseline status.

### 4.2 Comparative Metric Analysis
- Construct comparative tables showing deterministic versus Monte Carlo metrics for centroid offsets, worst-vehicle separations, and command latency margins.
- Analyse the evolution of maintenance metrics across runs, noting any changes in delta-v assumptions or contact probability.
- Compare drag dispersion outcomes (e.g., along-track shift \(p_{95} = 3.6\,\text{m}\)) against tolerance bands to contextualise robustness margins.
- Evaluate injection recovery success rates across spacecraft, highlighting any asymmetries and linking them to configuration assumptions.

### 4.3 Evidence Traceability and Compliance Links
- Map each Mission Requirement to the authoritative evidence set, referencing `docs/compliance_matrix.md` and the EV tags.
- Document how regression tests enforce the integrity of these metrics, noting specific assertions (e.g., sample counts, tolerances).
- Discuss how STK validation artefacts (ephemeris, ground track, facility, interval files) were imported and verified according to `docs/how_to_import_tehran_daily_pass_into_stk.md`.
- Explain how run metadata (`run_metadata.json`, `scenario_summary.json`) records seeds, assumptions, and exporter validation flags.

### 4.4 Literature Review Prompts – Evidence Interpretation
- Review analytical techniques for comparing deterministic and stochastic mission metrics, especially in the context of coverage and formation geometry.
- Investigate methodologies for combining Monte Carlo outputs with requirement compliance narratives in aerospace assurance documentation.
- Survey best practices for documenting STK validation results in mission dossiers, including screenshot capture, access report transcription, and cross-tool comparison.
- Explore comparative studies of maintenance campaigns for small satellite formations, focusing on delta-v expenditure tracking and command cadence analyses.

### 4.5 Suggested Analytical Assets
- [Suggested Table 4.1] Deterministic versus Monte Carlo centroid metrics for Tehran daily pass.
- [Suggested Table 4.2] Maintenance and command latency metrics from `run_20251018_1207Z`.
- [Suggested Figure 4.1] Command latency cumulative distribution derived from `command_windows.csv`.
- [Suggested Figure 4.2] Injection recovery cumulative distribution from `injection_recovery_cdf.svg`.
- [Suggested Figure 4.3] Drag dispersion scatter plot visualising along-track shift versus command distance delta.

### 4.6 Narrative Flow Outline
- Begin with authoritative run descriptions, progress into comparative analyses, integrate compliance traceability, and conclude with literature-backed interpretation frameworks.

### 4.7 Chapter 4 Deliverable Checklist
1. Authoritative run narratives with quantitative metrics.
2. Comparative tables and figures contrasting deterministic and stochastic outcomes.
3. Compliance traceability mapping between requirements, evidence, and regression safeguards.
4. Literature review on evidence interpretation and assurance practices.
5. References section listing all cited artefacts and external works.

### 4.8 Chapter 4 References
1. `artefacts/run_20251018_1207Z/triangle_summary.json` – Maintenance campaign summary.
2. `artefacts/run_20251018_1207Z/maintenance_summary.csv` – Maintenance metrics.
3. `artefacts/run_20251018_1207Z/command_windows.csv` – Command latency windows.
4. `artefacts/run_20251018_1207Z/injection_recovery.csv` – Injection recovery catalogue.
5. `artefacts/run_20251018_1207Z/injection_recovery_cdf.svg` – Monte Carlo cumulative distribution.
6. `artefacts/run_20251018_1207Z/drag_dispersion.csv` – Drag dispersion outcomes.
7. `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json` – Locked daily pass deterministic metrics.
8. `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json` – Locked daily pass Monte Carlo metrics.
9. `artefacts/triangle_run/triangle_summary.json` – Triangle formation summary.
10. `docs/compliance_matrix.md` – Requirement compliance catalogue.
11. `docs/how_to_import_tehran_daily_pass_into_stk.md` – STK validation guide.
12. `docs/triangle_formation_results.md` – Analytical memorandum.
13. `docs/tehran_daily_pass_scenario.md` – Scenario overview and validation status.
14. Literature on quantitative assurance and Monte Carlo interpretation (2020–2025).

### 4.9 Extended Task Breakdown – Chapter 4
1. Draft executive summaries for each authoritative run, highlighting scenario objectives, key metrics, compliance outcomes, and validation notes.
2. Construct comparative charts (tabular or graphical) contrasting deterministic versus Monte Carlo results for centroid offsets, worst-vehicle distances, and command latencies.
3. Document maintenance metric trends, noting any changes between archival runs and identifying triggers for reruns.
4. Prepare an evidence traceability map linking Mission Requirements, compliance matrix entries, EV tags, run artefacts, and regression tests.
5. Summarise STK validation outcomes for each run, including import confirmation, geometry checks, and recorded anomalies.
6. Identify data quality checks required before citing metrics (e.g., verifying sample counts, ensuring no missing values, confirming time ordering).
7. Draft narrative guidance on presenting windowed versus full-propagation statistics without causing ambiguity for reviewers.
8. Compile a list of follow-up analyses triggered by run findings (e.g., additional Monte Carlo sweeps, refined maintenance planning).
9. Develop peer-review prompts to verify quantitative accuracy, reproducibility, and compliance context before Chapter 4 sign-off.
10. Recommend archival practices for run artefacts, including checksum validation, metadata logging, and directory naming conventions.

---

## Chapter 5 – STK Validation, Compliance Integration, and Assurance Governance

### 5.1 STK Export and Validation Procedures
- Detail the process for generating STK exports via `sim/scripts/run_triangle.py` and `sim/scripts/run_scenario.py`, emphasising the role of `tools/stk_export.py` in producing `.e`, `.sat`, `.gt`, `.fac`, `.int`, and `.evt` files.
- Explain the sanitisation of identifiers (e.g., `SAT-1` → `SAT_1`) and scenario naming conventions (e.g., `Tehran_Triangle_Formation.sc`).
- Summarise the validation workflow outlined in `docs/how_to_import_tehran_daily_pass_into_stk.md`, including automation scripts (`tools/stk_tehran_daily_pass_runner.py`), screenshot capture, and metric cross-checks.
- Describe how validation status flags (`validated_against_stk_export`) are recorded in scenario metadata and run summaries.

### 5.2 Compliance Matrix Integration
- Analyse how `docs/compliance_matrix.md` structures requirement statuses, evidence tags, and outstanding actions. Emphasise the MR-2 and SRD-P-001 entries referencing deterministic and Monte Carlo metrics.
- Document the Non-Compliance Tracking process, including escalation pathways to the Configuration Control Board and closure criteria.
- Summarise the Evidence Catalogue (EV-1 through EV-5), highlighting directory locations, configuration notes, and outstanding actions (e.g., quarterly rerun schedules).
- Explain how updates to authoritative runs propagate into compliance documentation and regression suites.

### 5.3 Verification and Validation Strategy Alignment
- Connect the STK validation procedures to the broader Verification and Validation Plan (`docs/verification_plan.md`), including method selection (analysis, test, demonstration, inspection).
- Map requirement categories (MR, SRD-F, SRD-P, SRD-O, SRD-R) to verification activities, emphasising STK-related outputs.
- Highlight key milestones (VRR, Simulation Qualification Campaign, Operations Dry Run, CDR, LRR) and their dependencies on STK-compatible artefacts.
- Discuss resource planning for V&V activities, referencing personnel commitments, facility bookings, and tooling upgrades.

### 5.4 Literature Review Prompts – Assurance and Tool Interoperability
- Survey industry practices for documenting STK validation in mission assurance dossiers.
- Investigate regulatory or standards-based guidance (e.g., NASA-STD-7009A, ECSS-E-ST-10-02C) on simulation credibility, tool independence, and validation evidence management.
- Review case studies of compliance matrix management in aerospace projects, focusing on traceability and evidence audits.
- Examine best practices for integrating STK validation results with verification matrices and milestone readiness reviews.

### 5.5 Suggested Analytical Assets
- [Suggested Figure 5.1] STK validation workflow diagram linking exporter outputs to import steps.
- [Suggested Table 5.1] Mapping of Mission/System Requirements to STK-dependent evidence items.
- [Suggested Table 5.2] Excerpt from the Evidence Catalogue summarising EV tags, directories, and status.
- [Suggested Figure 5.2] Timeline of verification milestones with associated STK artefact deliveries.

### 5.6 Narrative Flow Outline
- Start with STK export mechanics, move into compliance matrix integration, align with verification strategy, and conclude with literature-grounded assurance guidance.

### 5.7 Chapter 5 Deliverable Checklist
1. STK validation procedure narrative linked to exporter implementation.
2. Compliance matrix analysis with evidence tracing and outstanding actions.
3. Verification plan alignment covering methods, milestones, and resources.
4. Assurance-focused literature review summary.
5. References section listing all cited artefacts and external standards.

### 5.8 Chapter 5 References
1. `tools/stk_export.py` – STK export implementation.
2. `docs/stk_export.md` – Export usage guide.
3. `docs/how_to_import_tehran_daily_pass_into_stk.md` – STK validation guide.
4. `tools/stk_tehran_daily_pass_runner.py` – Automation script for STK import.
5. `docs/compliance_matrix.md` – Compliance ledger.
6. `docs/verification_plan.md` – Verification and Validation Plan.
7. `docs/tehran_daily_pass_scenario.md` – Scenario overview and validation status.
8. `docs/triangle_formation_results.md` – Simulation memorandum.
9. NASA-STD-7009A – Standards for models and simulations.
10. ECSS-E-ST-10-02C – Verification standard.
11. Additional industry literature on STK validation and compliance management (2020–2025).

### 5.9 Extended Task Breakdown – Chapter 5
1. Detail the STK export invocation process, including input preparation, metadata configuration, file generation order, and post-export verification steps.
2. Draft validation log templates capturing import checks, animation observations, access report comparisons, and issue resolution.
3. Summarise compliance matrix update procedures when new evidence is generated, including review board approvals and documentation updates.
4. Outline escalation workflows for non-compliances, identifying responsible roles, communication channels, and closure documentation.
5. Map verification plan activities to STK artefacts, noting prerequisites, responsible teams, and expected outputs.
6. Propose enhancements to evidence cataloguing, such as automated directory audits or metadata linting scripts.
7. Develop a compliance dashboard concept integrating requirement status, run provenance, and STK validation results.
8. Prepare checklists for verifying exporter updates, ensuring compatibility with STK 11.2 and regression test coverage.
9. Recommend archival formats for validation evidence (e.g., annotated screenshots, access reports, STK scenario snapshots) and associated storage locations.
10. Draft training objectives for analysts responsible for STK validation and compliance matrix maintenance.

---

## Chapter 6 – Verification, Testing, Future Work, and Research Roadmap Extension

### 6.1 Regression Suite Expansion
- Assess current test coverage (`tests/unit/test_triangle_formation.py`, `tests/integration/test_simulation_scripts.py`, `tests/test_stk_export.py`, `tests/test_documentation_consistency.py`) and identify gaps requiring new unit, integration, or system-level tests.
- Propose additional tests to cover perturbation analysis scripts (`sim/scripts/perturbation_analysis.py`), baseline generation scaffolds, and configuration validation utilities.
- Recommend strategies for integrating Monte Carlo dispersion sanity checks into the CI pipeline (e.g., sampling small subsets for regression-friendly execution times).
- Suggest automated documentation consistency checks aligning `docs/` content with configuration and run artefacts.

### 6.2 Future Analytical Campaigns
- Outline follow-on simulations required to extend robustness assessments (e.g., solar radiation pressure inclusion, differential drag control strategies).
- Propose sensitivity analyses exploring variations in atmospheric density, drag coefficients, and command station availability.
- Recommend development of high-fidelity maintenance planners, integrating candidate guidance laws and thrust execution uncertainties.
- Suggest expansion of STK automation (e.g., scripted animation exports, access report generation, Connect command sequences for new scenarios).

### 6.3 Roadmap Integration and Milestone Planning
- Align proposed future work with the stages in `docs/project_roadmap.md`, noting dependencies and deliverable expectations.
- Update milestone projections (VRR, CDR, LRR) with additional preparatory tasks triggered by new analyses.
- Recommend updates to `docs/final_delivery_manifest.md` to incorporate forthcoming artefacts and reproduction procedures.
- Identify documentation gaps (e.g., subsystem-level requirement elaborations, risk register updates) that must be addressed before milestone reviews.

### 6.4 Literature Review Prompts – Emerging Topics
- Investigate advances in autonomous formation maintenance for small satellites, especially those integrating machine learning or adaptive control (2020–2025).
- Review emerging standards for digital mission assurance, including continuous compliance monitoring and automated evidence curation.
- Survey recent case studies of multi-satellite imaging missions delivering rapid situational awareness, focusing on operations, data latency, and resilience.
- Explore developments in interactive mission analysis platforms, particularly web-based services that integrate simulation, artefact management, and validation tracking.

### 6.5 Suggested Analytical Assets
- [Suggested Table 6.1] Regression test coverage matrix highlighting current and proposed additions.
- [Suggested Figure 6.1] Extended project roadmap with future campaign milestones.
- [Suggested Table 6.2] Future simulation campaign catalogue detailing objectives, required scripts, and output expectations.
- [Suggested Figure 6.2] Conceptual architecture for an automated compliance monitoring dashboard integrating STK validation status, run metadata, and regression outcomes.

### 6.6 Narrative Flow Outline
- Start with regression suite assessment, expand into future analytical campaigns, tie proposals to roadmap milestones, and conclude with literature-inspired innovations and tooling enhancements.

### 6.7 Chapter 6 Deliverable Checklist
1. Regression coverage analysis with recommended enhancements.
2. Future simulation campaign proposals with objectives and artefact expectations.
3. Updated roadmap alignment and milestone preparation guidance.
4. Literature review on emerging formation flying, assurance, and tooling topics.
5. References section capturing repository artefacts and external sources.

### 6.8 Chapter 6 References
1. `tests/unit/test_triangle_formation.py` – Current unit test coverage.
2. `tests/integration/test_simulation_scripts.py` – Integration test harness.
3. `tests/test_stk_export.py` – Export regression tests.
4. `tests/test_documentation_consistency.py` – Documentation consistency checks.
5. `docs/project_roadmap.md` – Project roadmap stages.
6. `docs/final_delivery_manifest.md` – Delivery manifest and reproduction procedures.
7. `docs/triangle_formation_results.md` – Analytical baseline for future campaigns.
8. `docs/verification_plan.md` – Verification strategy reference.
9. Contemporary literature on autonomous formation maintenance, digital mission assurance, and interactive mission analysis platforms (2020–2025).

### 6.9 Extended Task Breakdown – Chapter 6
1. Perform a gap analysis comparing existing regression tests against repository functionality (formation simulation, scenario pipeline, exporter utilities, documentation consistency).
2. Propose new tests with detailed specifications (input data, expected assertions, failure handling). Include priority levels and resource estimates.
3. Draft future simulation campaign briefs outlining objectives, required configuration updates, scripts to execute, metrics to capture, and validation expectations.
4. Recommend enhancements to documentation artefacts (e.g., updated manifest entries, new walkthroughs) aligned with future work proposals.
5. Prepare risk assessments for outstanding analytical tasks, noting potential impacts on roadmap milestones.
6. Suggest tooling upgrades (e.g., continuous compliance monitoring, automated STK validation scripts) with implementation steps and dependencies.
7. Compile a training needs analysis for teams executing future campaigns, including skills, tools, and knowledge resources.
8. Develop a communication plan for disseminating future work findings to stakeholders and review boards.
9. Outline archival and version-control procedures for new artefacts generated by future campaigns.
10. Establish success metrics and review cadences for each future work item, linking them to roadmap milestones and verification plan checkpoints.

---

## Appendices – Reusable Prompt Blocks and Data Templates

### Appendix A – Literature Review Search Templates
- **A.1 Mission Geometry Keywords**: “transient triangular formation”, “repeat ground track constellation”, “multi-plane LEO geometry”, “relative orbital elements daily revisit”.
- **A.2 Operations Keywords**: “single ground station latency management”, “X-band commanding logistics”, “ground segment resilience”, “command uplink window optimisation”.
- **A.3 Maintenance Keywords**: “cold gas propulsion formation keeping”, “delta-v budgeting small satellite constellation”, “drag modulation formation control”, “Monte Carlo injection recovery”.
- **A.4 STK Validation Keywords**: “STK 11.2 ephemeris text format”, “TEME frame export best practices”, “STK Connect automation formation flying”.
- **A.5 Assurance Keywords**: “compliance matrix aerospace project”, “mission assurance evidence catalogue”, “NASA-STD-7009A application”, “ECSS verification case studies”.

### Appendix B – Data Extraction Templates
- **B.1 Mission Requirement Compliance Table**: Columns for Requirement ID, Source Document, Status, Evidence Tag, Deterministic Metric, Monte Carlo Metric, Outstanding Actions.
- **B.2 Configuration Parameter Ledger**: Sections for Metadata, Global Constants, Platform, Orbit, Simulation, Output; include parameter name, value, units, rationale, and referenced document.
- **B.3 Run Artefact Inventory**: Fields for Run ID, Directory, Scenario, Key Files, Metrics Captured, STK Validation Status, Notes.
- **B.4 Regression Test Catalogue**: Columns for Test Module, Purpose, Key Assertions, Referenced Artefacts, Coverage Gaps, Proposed Enhancements.

### Appendix C – Figure and Table Production Notes
- Use SVG outputs exclusively for repository-tracked figures to align with binary artefact restrictions.
- When adapting repository plots, document any transformations (e.g., filtering windowed samples, rescaling axes) and store scripts alongside generated artefacts.
- For tables derived from CSV files, record the extraction commands (e.g., `pandas.read_csv`) and summarisation logic to ensure reproducibility.

### Appendix D – STK Validation Log Template
1. Scenario identifier and run directory.
2. STK version, licence, and workstation details.
3. Imported files list (ephemeris, satellite, ground track, facility, interval, events).
4. Animation playback observations (time span, triangle geometry checks, centroid behaviour).
5. Access report verifications (start/end times, elevation minima, cross-track offsets).
6. Screenshots captured (3D orbit, 2D ground track, access plots) with file names.
7. Deviations observed, corrective actions taken, and follow-up tasks.
8. Validation sign-off (name, date, role).

### Appendix E – Future Work Backlog Template
- **Item ID**: Unique identifier following `FW-YYYY-XX` convention.
- **Description**: Concise summary of the task.
- **Driver**: Mission Requirement, Verification Plan item, or stakeholder request prompting the work.
- **Dependencies**: Scripts, artefacts, or analyses required before commencement.
- **Deliverables**: Expected outputs (reports, datasets, tests, STK artefacts).
- **Owner**: Responsible team or individual.
- **Target Milestone**: Roadmap stage or review event.
- **Status**: Planned / In Progress / Complete.

### Appendix F – Glossary of Repository Terms
- **Access Node**: Discrete opportunity for imaging or downlink identified by `run_scenario.py`.
- **Authoritative Run**: Configuration-controlled simulation whose outputs underpin compliance statements.
- **Centroid Cross-Track Distance**: Great-circle separation between the triangle centroid and Tehran reference point, evaluated at access midpoint.
- **Formation Window**: Interval in which all geometric tolerances (side length, aspect ratio, ground distance) are satisfied simultaneously.
- **Monte Carlo Catalogue**: Collection of stochastic simulation outcomes, typically stored as CSV (`monte_carlo_summary.json`, `injection_recovery.csv`).
- **STK Export Suite**: Set of text files produced via `tools/stk_export.py` enabling STK 11.2 ingestion.
- **Windowed Metric**: Statistic computed over the validated formation window (e.g., \(343.62\,\text{km}\) ground distance) as opposed to the full propagation horizon.

### Appendix G – Reference Management Guidance
- Maintain per-chapter bibliographies with consistent numbering.
- When introducing external literature, annotate how it augments or contrasts with repository evidence.
- Store bibliographic metadata in a version-controlled reference manager or Markdown table to facilitate updates.

### Appendix H – Writing Quality Checklist
- [ ] Academic tone maintained with British English spelling.
- [ ] Inline citations align with chapter-specific reference lists.
- [ ] Figures and tables referenced in text before presentation.
- [ ] STK validation status reiterated wherever relevant data appear.
- [ ] Deterministic and Monte Carlo metrics distinguished explicitly.
- [ ] Automation and reproducibility considerations documented.
- [ ] Compliance implications and requirement traceability addressed.
- [ ] Outstanding actions and future work flagged with responsible owners.

### Appendix I – Command and Data Query Examples
- `python -m sim.scripts.run_triangle --output-dir artefacts/triangle_latest` – Recreate triangle artefacts; verify the presence of `triangle_summary.json`, CSV tables, SVG plots, and STK exports.
- `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_latest` – Execute the daily pass pipeline; confirm `scenario_summary.json` captures RAAN alignment and stage sequence entries.
- `python run_debug.py --triangle --output-root artefacts/debug` – Generate diagnostic CSVs for triangle runs; inspect `positions_m.csv`, `velocities_mps.csv`, and formation window metrics.
- `python run_debug.py --scenario tehran_daily_pass --output-root artefacts/debug` – Capture scenario debug summaries; verify stage sequence logging and JSON payload structure.
- `pytest tests/unit/test_triangle_formation.py` – Validate mission requirement guardrails in unit tests; note failure cases and remediation steps.
- `pytest tests/integration/test_simulation_scripts.py -k scenario` – Run scenario integration tests only; check STK export artefacts are generated under the temporary directory.
- `pytest tests/test_stk_export.py` – Confirm STK exporter compatibility; review generated files for correct naming and content ordering.
- `python tools/stk_tehran_daily_pass_runner.py artefacts/run_20251020_1900Z_tehran_daily_pass_locked` – Automate STK import; document Connect script behaviour and validation screenshots.
- `make triangle` / `make scenario` – Invoke Makefile shortcuts; verify resulting artefacts align with authoritative run structures.
- `python -m sim.scripts.run_triangle_campaign --output-root artefacts/triangle_campaign` – Exercise campaign automation scaffolding; inspect `history.csv` for run scheduling data.

### Appendix J – Reviewer Checklist Templates
1. **Structural Review**
   - Verify chapter sequence (1 through 6 plus appendices) matches prompt order.
   - Ensure each chapter begins with the specified heading and includes deliverable checklists, narrative flow outlines, and references.
   - Confirm appendices are present and referenced where relevant in the main text.
2. **Citation Review**
   - Check that `[RefX]` citations correspond to numbered reference entries.
   - Confirm repository artefacts are cited with precise file paths or run identifiers.
   - Ensure external literature is contextualised against repository evidence.
3. **Data Integrity Review**
   - Validate that deterministic and Monte Carlo metrics are clearly labelled and numerically consistent with source artefacts.
   - Inspect figure and table captions for data provenance statements.
   - Confirm STK validation status is documented wherever exported artefacts are referenced.
4. **Compliance Review**
   - Cross-check Mission Requirement statements against compliance matrix citations.
   - Verify that run identifiers match entries in `docs/_authoritative_runs.md`.
   - Ensure outstanding actions or waivers are noted with responsible owners.
5. **Future Work Review**
   - Assess proposed analytical campaigns for alignment with roadmap milestones.
   - Confirm regression suite expansion plans include test specifications and priorities.
   - Evaluate communication and training plans for completeness.

### Appendix K – Toolchain Logging Catalogue
- **Web Service Logs**: `debug.txt` (rotating log capturing run orchestration, accessible via FastAPI endpoints); include rotation policy and archival procedure.
- **Scenario Runner Logs**: Console output recorded during `run_scenario.py` executions; recommend redirecting to timestamped log files within run directories.
- **Triangle Simulator Logs**: Console output and `triangle_summary.json`; describe key log entries such as window duration confirmations and metric summaries.
- **Campaign Logs**: `artefacts/triangle_campaign/history.csv` and supplementary log files capturing run scheduling; outline fields (timestamp, run ID, configuration, status).
- **CI Pipeline Logs**: GitHub Actions workflow outputs for `make triangle`, `make scenario`, `pytest`; specify retention period and access procedures.
- **STK Validation Logs**: Structured using Appendix D template; note storage location (e.g., `artefacts/run_YYYYMMDD_hhmmZ/stk_validation/`).
- **Documentation Generation Logs**: `make docs` outputs summarising documentation snapshots; describe expected success indicators.
- **Debug CSV Metadata**: Include README files in debug directories summarising column definitions and generation contexts.
- **Error Reporting Protocol**: Define escalation process when logs reveal anomalies, including notification channels and issue tracking references.

### Appendix L – Extended Glossary Entries
- **Alignment Validation Run**: The authoritative simulation referenced by a scenario configuration to confirm RAAN and window geometry (e.g., `run_20251020_1900Z_tehran_daily_pass_locked`).
- **Command Probability**: Fraction of orbital period during which command link is available, derived from `_analyse_command_latency`.
- **Delta-v Reserve Fraction**: Portion of annual propulsion budget held in reserve, defined in `config/project.yaml` for maintenance planning.
- **Drag Dispersion Sample**: Individual Monte Carlo draw assessing atmospheric density and drag coefficient perturbations; recorded in `drag_dispersion.csv`.
- **Formation Maintenance Event**: Entry in STK export `.evt` files capturing manoeuvre metadata (epoch, description, delta-v).
- **Ground Distance Tolerance**: Maximum permissible great-circle distance from Tehran to triangle vertices during the validated window (350 km primary limit).
- **Monte Carlo Seed**: Random number generator initialisation value recorded in scenario configurations to ensure reproducibility.
- **Plane Allocation**: Assignment of spacecraft to orbital planes (Plane A or Plane B) to achieve formation geometry.
- **Scenario Metadata**: Top-level JSON keys capturing scenario identifiers, descriptions, authorship, creation dates, and validation flags.
- **Window Duration**: Time span of simultaneous geometry compliance; expected to exceed 90 seconds per mission requirements.

### Appendix M – Cross-Chapter Consistency Checklist
1. **Terminology Consistency**
   - Ensure terms defined in Appendices F and L are used uniformly across chapters.
   - Verify that new terms introduced in later chapters are back-referenced to glossary entries.
2. **Metric Consistency**
   - Confirm numerical values (e.g., centroid offsets, delta-v budgets) remain identical wherever repeated.
   - Cross-reference figure/table captions with textual descriptions to avoid contradictions.
3. **Citation Consistency**
   - Maintain consistent numbering for references when the same artefact is cited across chapters.
   - Update the Global Reference Index whenever chapter reference lists change.
4. **Task Consistency**
   - Ensure extended task breakdowns align with chapter deliverable checklists.
   - Validate that future work proposals in Chapter 6 correspond to outstanding actions noted in earlier chapters.
5. **Validation Consistency**
   - Check that STK validation statements align with Appendix D logs and compliance matrix entries.
   - Confirm regression safeguards cited in multiple chapters reference the same test modules.

### Appendix N – Data Transformation Playbooks
- **Triangle Metrics Extraction**
  1. Load `triangle_summary.json` into a dataframe.
  2. Filter samples within the formation window timestamps.
  3. Compute aggregate metrics (mean side lengths, aspect ratio maxima) and compare with JSON summary fields.
  4. Export summarised tables to Markdown for inclusion in Chapter 4.
- **Daily Pass Metric Comparison**
  1. Load `deterministic_summary.json` and `monte_carlo_summary.json`.
  2. Extract centroid and worst-vehicle metrics, capturing mean and \(p_{95}\) values.
  3. Highlight differences between deterministic and stochastic outputs in comparative charts.
- **Maintenance Budget Analysis**
  1. Read `maintenance_summary.csv` and compute annualised delta-v statistics.
  2. Compare per-spacecraft metrics against budget thresholds.
  3. Cross-reference with command latency metrics to correlate maintenance frequency and contact opportunities.
- **Command Latency Evaluation**
  1. Analyse `command_windows.csv` to calculate latency distributions and contact probabilities.
  2. Visualise results as histograms or cumulative distributions.
  3. Confirm computed values align with `_analyse_command_latency` outputs in JSON summaries.
- **Drag Dispersion Interpretation**
  1. Load `drag_dispersion.csv` and evaluate success rates.
  2. Plot along-track shifts versus ground distance deltas.
  3. Identify samples breaching tolerances and note follow-up actions.

### Appendix O – Quality Assurance Sign-off Template
- **Reviewer Name / Role**: ______________________
- **Review Date**: ______________________
- **Chapter(s) Reviewed**: ______________________
- **Key Findings**:
  - Strengths: _______________________________________
  - Issues Identified: _______________________________________
- **Corrective Actions**:
  - Action Item 1: _______________________________________
  - Action Item 2: _______________________________________
- **Validation Checks Performed** (tick all that apply):
  - [ ] Figures verified against source data.
  - [ ] Tables cross-checked for numeric accuracy.
  - [ ] Citations validated and references updated.
  - [ ] STK validation logs reviewed.
  - [ ] Regression safeguards referenced.
- **Approval Status**: ☐ Approved ☐ Approved with Actions ☐ Rework Required
- **Reviewer Signature**: ______________________

### Appendix P – Communication Artefact Templates
- **Stakeholder Briefing Outline**
  1. Mission update summary.
  2. Recent simulation highlights and compliance status.
  3. Upcoming verification activities and milestones.
  4. Risks, mitigations, and support requests.
  5. Q&A and action items.
- **Technical Memo Structure**
  1. Purpose and scope.
  2. Methodology (referencing scripts and configurations used).
  3. Results (including deterministic and Monte Carlo metrics).
  4. STK validation and compliance implications.
  5. Recommendations and next steps.
- **Change Request Template**
  1. Description of proposed change (configuration, code, documentation).
  2. Impact assessment (requirements, compliance, verification).
  3. Validation plan (tests, STK exports, reviews).
  4. Approval routing (responsible boards/roles).
  5. Implementation timeline and rollback considerations.

### Appendix Q – Analyst Onboarding Checklist
- [ ] Clone repository and review `AGENTS.md` guidelines.
- [ ] Execute `make setup` to provision the Python environment.
- [ ] Run `make triangle` and `make scenario` to familiarise with artefact outputs.
- [ ] Read core documentation: `README.md`, `docs/project_overview.md`, `docs/project_roadmap.md`, `docs/triangle_formation_results.md`, `docs/tehran_daily_pass_scenario.md`.
- [ ] Inspect `config/project.yaml` and scenario JSON files.
- [ ] Review authoritative run directories under `artefacts/`.
- [ ] Execute regression tests relevant to assigned tasks.
- [ ] Walk through STK validation guides and, if licensed, perform a trial import.
- [ ] Familiarise with FastAPI endpoints via `run.py` and `docs/interactive_execution_guide.md`.
- [ ] Meet with mission stakeholders to confirm expectations and communication cadence.

### Appendix R – Repository Change Control Guidelines
- **Code Changes**
  - Enforce modular commits with descriptive messages referencing objectives.
  - Update or add tests when altering simulation logic or exporter behaviour.
  - Document new scripts in `README.md` and relevant `docs/` pages.
- **Configuration Updates**
  - Increment `configuration_version` in `config/project.yaml` when baseline parameters change.
  - Update scenario metadata (`author`, `created`, `alignment_validation`) upon reruns.
  - Notify compliance and verification teams of configuration changes impacting requirements.
- **Documentation Revisions**
  - Maintain British English spelling and academic tone.
  - Update appendices and reference indices when new artefacts or external sources are cited.
  - Perform documentation consistency checks (`tests/test_documentation_consistency.py`).
- **Artefact Management**
  - Store new run outputs under `artefacts/run_YYYYMMDD_hhmmZ_identifier` following naming conventions.
  - Include metadata files (`run_metadata.json`, validation logs) for traceability.
  - Avoid committing binary artefacts; prefer text-based formats (CSV, JSON, SVG).
- **Review and Approval**
  - Submit pull requests summarising mission design progress, analytical deliverables, and testing status.
  - Ensure reviewers validate compliance implications and regression coverage.
  - Record approvals and follow-up actions for auditability.

### Appendix S – Audit Trail Requirements
- Maintain a central index of all run directories, including creation dates, responsible analysts, and associated change requests.
- Store hash digests (e.g., SHA256) for key artefacts to detect unintended modifications; regenerate upon reruns.
- Archive meeting minutes and review outcomes related to mission analyses, linking them to affected artefacts or documentation sections.
- Capture decision rationales when adopting new configurations, algorithms, or validation procedures, ensuring traceability for external audits.
- Implement periodic audits (quarterly recommended) verifying artefact completeness, metadata accuracy, and compliance matrix updates.

---

## Global Reference Index
- Compile a consolidated list of all repository artefacts, scripts, and external standards cited across chapters and appendices.
- Include hyperlinks or relative paths to each referenced file to streamline navigation for analysts assembling the dossier.
- Note version identifiers, commit hashes, or run timestamps where applicable to reinforce configuration control.
- Update the index whenever new artefacts or references are introduced to keep the prompt synchronised with repository evolution.
