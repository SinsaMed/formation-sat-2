# Project Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Purpose and Application
This prompt defines the authoritative brief for generating the comprehensive "Mission Research & Evidence Brief" that synthesises the Formation Satellite Programme repository into an academic dossier centred on the Tehran equilateral formation case study.[Ref1][Ref2] The response must fuse literature scholarship, configuration-controlled evidence, simulation artefacts, and verification practices so that a thesis-length manuscript can be produced without further clarification.[Ref3][Ref7][Ref8]

- Treat this prompt as a binding contract: every instruction is mandatory unless explicitly superseded by downstream subsections.
- Compose the dossier in British English, sustaining an academic yet accessible voice that mirrors the house style recorded in the repository root guidelines.[Ref1]
- Deliver all six chapters sequentially in a single response, each with the mandated substructure described herein.
- Integrate repository artefacts, simulation metrics, and compliance statements exactly as catalogued in the authoritative runs ledger so the manuscript remains configuration-controlled.[Ref15][Ref29][Ref30]
- When citing repository materials in the dossier, reproduce their identifiers and quantitative results verbatim; introduce no fabricated numbers or speculative claims.
- Ensure every factual assertion concludes with an inline numbered reference tag, and provide a consolidated reference list for each chapter as prescribed by the template in this prompt.[Ref4][Ref7]
- Maintain interoperability awareness: whenever the dossier references simulation outputs, state whether STK 11.2 validation has been performed or is required, highlighting dependencies on `tools/stk_export.py`.[Ref12][Ref24]
- Preserve the mission naming conventions (`run_YYYYMMDD_hhmmZ`) when mentioning campaign outputs or scheduling new analyses.[Ref7][Ref32]

## Global Mandates and Editorial Standards
All chapters must adhere to the cross-cutting standards below before addressing chapter-specific instructions.

### Response Architecture
- Begin each chapter with the heading format `## Chapter X – Title`, matching the titles defined in the chapter briefs later in this prompt.
- Under every chapter heading, include the five mandatory subsections, numbered and titled exactly as follows:
  1. `Key Artefacts & Sources (2019–2026 repository evidence)`
  2. `Synthesis of Core Findings & Arguments`
  3. `Visual & Analytical Anchors`
  4. `Proposed Narrative Flow for the Chapter`
  5. `Numbered Reference List for this Chapter`
- For Subsection 1, enumerate three to five bullet points citing the most relevant configuration files, documents, simulation directories, or tests; ensure each bullet ends with an inline reference marker.[Ref7][Ref18][Ref26]
- Subsection 2 must present a coherent academic paragraph (or two if necessary) with inline numbered citations after every sentence.[Ref5][Ref8][Ref29]
- Subsection 3 shall itemise suggested figures, tables, and equations, each on its own bullet line, prefixed by a bracketed descriptor such as `[Suggested Figure 2.1]` and concluded with references to the source artefact.[Ref8][Ref29][Ref30]
- Subsection 4 must comprise a single paragraph explaining how the chapter’s argument advances the dossier and foreshadows the next chapter.[Ref3][Ref13]
- Subsection 5 lists the numerical references cited within the chapter in ascending order; do not invent sources beyond those enumerated in the chapter’s evidence base or the repository reference set appended to this prompt.

### Source Fidelity and Traceability
- Draw quantitative evidence from the archived artefacts only; for example, the ninety-six-second access window, \(343.62\,\text{km}\) windowed ground-distance ceiling, and \(14.04\,\text{m/s}\) maximum annual delta-v shall always trace back to `run_20251018_1207Z`.[Ref8][Ref29]
- When quoting RAAN or centroid offsets from the daily-pass alignment, state \(350.7885044642857^{\circ}\) for the optimised RAAN and \(12.142754610722838\,\text{km}\) for the centroid cross-track at the evaluation midpoint, referencing the locked campaign outputs.[Ref10][Ref30]
- Cite Monte Carlo statistics such as \(p_{95}(\vert x_c\vert)=24.180422084370257\,\text{km}\) directly from the `monte_carlo_summary.json` dataset, noting that the fleet compliance probability is unity.[Ref31]
- When referencing operational cadence or rerun schedules, reproduce the exact timestamps and next-due entries listed in `artefacts/triangle_campaign/history.csv`.[Ref32]
- Summaries of 30-day access sweeps must restate the daily centroid offsets exactly as recorded in `artefacts/sweeps/tehran_30d.csv` without interpolation.[Ref33]

### Evidence Integration and Literature Review Expectations
- For every chapter that requires literature integration, explicitly contrast repository findings with contemporary mission design scholarship, drawing on classical ROE theory, formation-flying heritage missions, and perturbation analysis frameworks.[Ref2][Ref5][Ref8]
- Identify knowledge gaps exposed by repository artefacts; specify where further literature review is required to contextualise maintenance strategies, resilience envelopes, or ground-segment operations.[Ref6][Ref13]
- Highlight where empirical runs validate or contradict theoretical expectations, especially regarding drag dispersion, injection recovery success rates, and RAAN optimisation behaviour.[Ref8][Ref31]
- Encourage inclusion of external peer-reviewed sources, standards (e.g., NASA-STD-7009A, ECSS-E-ST-10-02C), and agency manuals, clearly flagging where each should be introduced in the dossier.

### Compliance and Assurance Alignment
- Map every analytical assertion back to Mission Requirements MR-1 through MR-7 and the corresponding SRD derivations; specify the compliance status and evidence tag where applicable.[Ref4][Ref5][Ref7]
- Reinforce that `tests/unit/test_triangle_formation.py` and `tests/integration/test_simulation_scripts.py` act as regression guards; whenever a chapter cites automated assurance, reference these tests alongside the narrative.[Ref26][Ref27]
- Acknowledge the STK export regression coverage provided by `tests/test_stk_export.py`; direct the reader to the exporter guide for context when discussing interoperability.[Ref12][Ref28]
- Emphasise configuration management practices, including reference to the ledger of authoritative runs and the expectation to update documentation and compliance matrices after new campaigns.[Ref7][Ref15]

## Evidence Catalogue Overview
Summarise the repository’s foundational artefacts within the dossier to orient readers before delving into chapter-level analysis.

- `README.md` articulates the mission intent, ground-track objectives, and automation pathways; use it to frame the thesis motivation and overall workflow narrative.[Ref1]
- `docs/project_overview.md` contextualises the mission within an academic research setting and enumerates deliverables linked to the Tehran formation mission.[Ref2]
- `docs/project_roadmap.md` decomposes the mission lifecycle into sequential stages; reference it whenever staging, milestone planning, or configuration control is discussed.[Ref3]
- `docs/mission_requirements.md` and `docs/system_requirements.md` provide the governing requirement matrices that underpin compliance statements; quote requirement IDs and verification approaches precisely.[Ref4][Ref5]
- `docs/concept_of_operations.md` expands operational narratives, command timelines, and risk management strategies, all of which must be echoed when describing mission operations.[Ref6]
- `docs/compliance_matrix.md` consolidates requirement dispositions and evidence tags; cite it when reporting compliance status or referencing run directories.[Ref7]
- `docs/triangle_formation_results.md` presents validated metrics for the equilateral formation, including maintenance, command latency, and drag dispersion results.[Ref8]
- `docs/tehran_triangle_walkthrough.md` and `docs/interactive_execution_guide.md` describe reproduction workflows and interactive tooling; highlight these when advising analysts on regenerating evidence or engaging with the FastAPI runner.[Ref9][Ref16]
- `docs/tehran_daily_pass_scenario.md` and `docs/how_to_import_tehran_daily_pass_into_stk.md` document the RAAN-aligned daily pass configuration and STK validation procedure; reference them whenever discussing nodal alignment or evidence capture.[Ref10][Ref11]
- `docs/stk_export.md` and `tools/stk_export.py` govern STK interoperability rules; ensure the dossier repeats key constraints such as frame assumptions, ephemeris spacing, and file naming.[Ref12][Ref24]
- `docs/verification_plan.md` and `docs/final_delivery_manifest.md` frame verification strategy, resource planning, and deliverable registers; cite them in the verification and future-work discussions.[Ref13][Ref14]
- `docs/_authoritative_runs.md` lists the run IDs anchoring compliance claims; the dossier must reference these runs verbatim whenever citing evidence.[Ref15]
- Configuration baselines (`config/project.yaml`, `config/scenarios/tehran_triangle.json`, `config/scenarios/tehran_daily_pass.json`) define mission constants, formation geometry, and access parameters that the dossier must restate when discussing setup assumptions.[Ref16][Ref17][Ref18]
- Simulation code (`sim/formation/triangle.py`, `sim/scripts/run_triangle.py`, `sim/scripts/run_scenario.py`, `sim/scripts/run_triangle_campaign.py`, `sim/scripts/run_stk_tehran.py`) outlines algorithmic foundations, CLI workflows, automation logic, and campaign scheduling; integrate these implementations into the technical exposition.[Ref19][Ref20][Ref21][Ref22][Ref23]
- Regression tests (`tests/unit/test_triangle_formation.py`, `tests/integration/test_simulation_scripts.py`, `tests/test_stk_export.py`) guarantee analytical repeatability and should be cited when asserting quality assurance coverage.[Ref26][Ref27][Ref28]
- Artefact directories capture quantitative evidence: `run_20251018_1207Z` for triangular maintenance, `run_20251020_1900Z_tehran_daily_pass_locked` for nodal alignment, `run_20260321_0740Z_tehran_daily_pass_resampled` for resampling studies, and campaign history or sweep catalogues for temporal analyses.[Ref29][Ref30][Ref31][Ref32][Ref33]

## Chapter 1 – Mission Framing & Requirements Baseline
Focus this chapter on articulating the mission rationale, requirement hierarchy, and configuration governance that anchor the Tehran formation concept.

### Scope and Intent
- Introduce the Formation Satellite Programme goals, highlighting the daily Tehran access mandate and the transient triangular formation concept.[Ref1][Ref2]
- Explain the linkage between stakeholder objectives, mission requirements (MR-1…MR-7), and their translation into system requirements (SRD-F/P/O/R series).[Ref4][Ref5]
- Describe the traceability mechanisms tying requirements to evidence, including the compliance matrix, authoritative runs ledger, and regression tests.[Ref7][Ref15][Ref26]
- Summarise mission assumptions captured in `config/project.yaml`, such as earth model, altitude, platform mass, propulsion reserves, and maintenance strategy.[Ref16]
- Clarify naming conventions, run identifiers, and documentation update expectations mandated by the repository.[Ref7][Ref15]

### Repository Artefacts to Cite
- `docs/project_overview.md` for mission problem statement, objectives, and deliverables.[Ref2]
- `docs/mission_requirements.md` for the requirement matrix and verification approaches.[Ref4]
- `docs/system_requirements.md` for requirement taxonomy and compliance mapping.[Ref5]
- `docs/compliance_matrix.md` for current requirement dispositions and evidence references.[Ref7]
- `docs/_authoritative_runs.md` for the canonical run catalogue anchoring compliance claims.[Ref15]
- `config/project.yaml` for mission-wide configuration constants and maintenance policy.[Ref16]
- `tests/unit/test_triangle_formation.py` for regression coverage of requirement thresholds.[Ref26]

### Analytical Threads to Expand
- Detail how MR-2 and SRD-P-001 enforce centroid and worst-spacecraft cross-track limits, referencing the ±30 km primary and ±70 km waiver thresholds verified by the daily-pass alignment campaign.[Ref4][Ref5][Ref30]
- Discuss how MR-3 and SRD-P-002 codify the ninety-second access window requirement and how the triangular simulation substantiates compliance.[Ref4][Ref5][Ref29]
- Explain operations and maintenance obligations (MR-5 through MR-7) and how they translate into command latency, delta-v budgets, and robustness expectations, highlighting the evidence sets that demonstrate compliance.[Ref4][Ref7][Ref29]
- Illustrate configuration control processes: how scenario updates propagate to documentation via compliance checks and tests such as `test_documentation_consistency`.[Ref7][Ref27]
- Identify where literature review must reinforce requirement derivations, e.g., by citing mission assurance standards or formation-flying theory beyond repository content.

### Literature Review Prompts
- Survey standards and guidance (NASA-STD-7009A, ECSS-E-ST-10-02C) that inform verification expectations for mission requirements, recommending where they should be cited.[Ref13]
- Compare the mission’s transient formation objective with precedent missions (TanDEM-X, GRACE, PRISMA) to contextualise requirement stringency and revisit expectations.[Ref2]
- Investigate best practices in configuration management for multi-satellite missions, linking them to the repository’s authoritative run process and ledger.

### Required Visual and Tabular Elements
- [Suggested Table 1.1] Requirement-to-evidence crosswalk summarising MR and SRD identifiers, compliance status, and citing run directories or tests.[Ref4][Ref5][Ref7]
- [Suggested Figure 1.1] Diagram illustrating requirement flow from stakeholder goals to Mission Requirements and System Requirements, adapted from the textual descriptions in `docs/system_requirements.md`.[Ref5]
- [Suggested Equation 1.1] Present the definition of \(\delta \lambda\) or another ROE-based tolerance expression to connect requirement statements with orbital mechanics foundations.[Ref19]

### Cross-Chapter Linkages
- Conclude by signalling that Chapter 2 will unpack the configuration artefacts, scenario schemas, and geometric foundations underpinning these requirements.[Ref17][Ref18]
- Reinforce that subsequent chapters will interrogate whether the evidence base sustains the compliance claims introduced here.

### Deliverable Checklist
- Confirm that all requirement IDs cited include their compliance status and evidence tags from the matrix.[Ref7]
- Ensure mission configuration values (altitude, inclination, maintenance cadence) match `config/project.yaml` verbatim.[Ref16]
- Verify that references in Subsection 5 align with the numbered citations introduced in the chapter.

## Chapter 2 – Configuration & Geometric Foundations
Analyse the configuration files and geometric constructs that shape the Tehran formation and daily-pass scenarios.

### Scope and Intent
- Decompose the mission-wide configuration captured in `project.yaml`, covering metadata, platform attributes, orbit elements, simulation settings, and output controls.[Ref16]
- Examine the Tehran triangle and daily-pass JSON scenarios, emphasising formation side length, ground tolerance, RAAN alignment, access windows, and Monte Carlo settings.[Ref17][Ref18]
- Translate configuration parameters into geometric interpretations: local-vertical local-horizontal (LVLH) offsets, plane allocations, and target facility definitions.[Ref19]
- Connect the configuration choices to requirement satisfaction, demonstrating how parameter selections support compliance.[Ref4][Ref17]
- Highlight assumptions that require literature or analytical reinforcement (e.g., drag models, Monte Carlo dispersions, contact range assumptions).

### Repository Artefacts to Cite
- `config/project.yaml` for mission constants, platform characteristics, orbit elements, simulation settings, and output policies.[Ref16]
- `config/scenarios/tehran_triangle.json` for equilateral formation settings, plane allocations, maintenance assumptions, and Monte Carlo configuration.[Ref17]
- `config/scenarios/tehran_daily_pass.json` for RAAN, access window, payload constraints, and operational timing definitions.[Ref18]
- `sim/formation/triangle.py` for the translation of configuration values into propagated states and metrics.[Ref19]
- `sim/scripts/run_scenario.py` for scenario pipeline staging and RAAN optimiser integration.[Ref21]
- `docs/tehran_triangle_walkthrough.md` for replication instructions linked to scenario configurations.[Ref9]

### Analytical Threads to Expand
- Explain how the `formation.side_length_m` and plane allocations map to the `simulate_triangle_formation` offsets and LVLH frame transformations.[Ref17][Ref19]
- Describe how the ground tolerance parameter interacts with the maximum ground distance metric in `triangle_summary.json`, noting both the 96-second window and the global 180-second propagation maxima.[Ref29]
- Discuss RAAN optimisation: initial seed, optimised value, window duration, and step size as defined in the daily-pass scenario and realised by the scenario runner.[Ref18][Ref21][Ref30]
- Analyse Monte Carlo and drag dispersion settings, including sample counts, sigma values, seeds, and how they feed into success-rate reporting.[Ref17][Ref31]
- Investigate the output controls for STK export, demonstrating how scenario metadata such as `stk_export` tags ensure interoperability.[Ref12][Ref18]

### Literature Review Prompts
- Identify sources discussing LVLH formation design, ROE interpretation, and differential drag strategies to justify configuration choices.[Ref19]
- Suggest references covering RAAN alignment techniques and repeat-ground-track theory to contextualise the daily-pass scenario.[Ref18]
- Recommend studies on Monte Carlo dispersion planning for small-satellite formations to support the configuration’s sigma values and sample sizes.

### Required Visual and Tabular Elements
- [Suggested Table 2.1] Summarise key configuration parameters for the triangle and daily-pass scenarios, including side length, duration, tolerance, RAAN, access windows, and Monte Carlo settings.[Ref17][Ref18]
- [Suggested Figure 2.1] Flow diagram linking configuration sections (metadata, orbit, formation, Monte Carlo, output) to the simulation pipeline steps that consume them.[Ref16][Ref21]
- [Suggested Equation 2.1] Present the LVLH offset vectors used to construct the equilateral triangle, referencing `_formation_offsets` in `triangle.py`.[Ref19]

### Cross-Chapter Linkages
- Transition toward Chapter 3 by signalling that the forthcoming analysis will detail how the simulation pipeline executes these configurations, including stage sequencing and exporter integration.[Ref20][Ref21]

### Deliverable Checklist
- Confirm all numeric parameters (e.g., \(350.9838169642857^{\circ}\) initial RAAN, \(350.7885044642857^{\circ}\) optimised RAAN, 90-second windows) match the configuration JSONs exactly.[Ref17][Ref18]
- Ensure references in Subsection 5 include both configuration files and implementation modules that interpret them.
- Validate that Subsection 3 items correctly associate figures and tables with their source artefacts.

## Chapter 3 – Simulation Pipeline & Toolchain
Document the computational architecture, scripts, and exporters that transform configurations into validated artefacts.

### Scope and Intent
- Outline the responsibilities of `sim/scripts/run_triangle.py`, `sim/scripts/run_scenario.py`, `sim/scripts/run_triangle_campaign.py`, and `sim/scripts/run_stk_tehran.py`, including CLI usage, output directories, and metadata capture.[Ref20][Ref21][Ref22][Ref23]
- Explain the stages executed within the scenario runner: RAAN alignment, node generation, phase synthesis, two-body propagation, J2+drag propagation, metric extraction, and STK export.[Ref21]
- Describe the implementation details of `simulate_triangle_formation`, covering LVLH transformations, maintenance estimation, command latency analysis, injection recovery, and drag dispersion Monte Carlo routines.[Ref19]
- Highlight integration with STK export utilities, emphasising ephemeris resampling, identifier sanitisation, ground-track generation, facility definitions, contact intervals, and event logging.[Ref24][Ref12]
- Capture automation aids such as the triangle campaign scheduler, history ledger updates, and rerun cadence enforcement.[Ref22][Ref32]

### Repository Artefacts to Cite
- `sim/formation/triangle.py` for core simulation algorithms and metric computations.[Ref19]
- `sim/scripts/run_triangle.py` for CLI orchestration of the triangle simulation and artefact export.[Ref20]
- `sim/scripts/run_scenario.py` for scenario pipeline stage definitions and STK export integration.[Ref21]
- `sim/scripts/run_triangle_campaign.py` for scheduled rerun governance and history tracking.[Ref22]
- `sim/scripts/run_stk_tehran.py` for STK COM automation and Connect script emission.[Ref23]
- `tools/stk_export.py` for STK file generation, interpolation logic, and naming conventions.[Ref24]
- `docs/interactive_execution_guide.md` for FastAPI and debugging workflows interfacing with the simulation scripts.[Ref16]
- `tests/integration/test_simulation_scripts.py` for regression coverage of CLI entry points and artefact expectations.[Ref27]

### Analytical Threads to Expand
- Break down how `_formation_window` isolates the validated ninety-six-second interval and distinguishes it from the broader 180-second propagation horizon.[Ref19][Ref29]
- Analyse the maintenance estimation routine’s assumptions, including burn cadence, differential acceleration averaging, and delta-v budgeting.[Ref19][Ref29]
- Detail the command latency assessment: contact probability, passes per day, maximum latency, and margin calculations derived from the Tehran ground station geometry.[Ref19][Ref29]
- Discuss Monte Carlo injection recovery metrics, including sample count, delta-v computation, success-rate aggregation, and plot generation.[Ref19][Ref29]
- Explain drag dispersion analysis, including density scaling, ballistic coefficient computation, and tolerance evaluation.[Ref19][Ref29]
- Describe STK export steps: sample ordering, ephemeris resampling, facility file structure, contact interval formatting, and scenario summary composition.[Ref24][Ref12]
- Illustrate how the triangle campaign script enforces quarterly reruns, records metadata, and writes `run_metadata.json` entries per execution.[Ref22][Ref32]
- Evaluate how integration tests verify stage sequences, STK exports, and CLI outputs to maintain pipeline integrity.[Ref27]

### Literature Review Prompts
- Recommend sources on Keplerian propagation, LVLH dynamics, and relative orbital element conversions to bolster explanations of the simulation algorithms.[Ref19]
- Suggest literature on Monte Carlo campaign design, injection dispersion modelling, and drag characterisation for LEO constellations.
- Identify references on ground contact analysis and command latency modelling to contextualise the command-window calculations.
- Highlight documentation on STK ephemeris formats and Connect automation for readers unfamiliar with the exporter conventions.

### Required Visual and Tabular Elements
- [Suggested Figure 3.1] Stage-sequence diagram of the scenario runner, mapping each stage to generated artefacts and regression checks.[Ref21][Ref27]
- [Suggested Table 3.1] Summary of Monte Carlo configurations (samples, sigmas, success rates) for injection recovery and drag dispersion routines.[Ref19][Ref29][Ref31]
- [Suggested Figure 3.2] Flowchart depicting the STK export pipeline from state histories to `.e`, `.sat`, `.gt`, `.fac`, `.int`, and `.evt` files.[Ref24][Ref12]
- [Suggested Equation 3.1] Mean motion formula \(n=\sqrt{\mu/a^3}\) or the Hill-Clohessy-Wiltshire drift expression implemented in the ROE utilities to explain propagation steps.[Ref19]

### Cross-Chapter Linkages
- Prepare the reader for Chapter 4 by emphasising that the outputs from these scripts feed directly into the authoritative runs underpinning quantitative evidence.[Ref15][Ref29][Ref30]

### Deliverable Checklist
- Verify that descriptions of CLI flags, output directories, and artefact names match the script help text and observed outputs.[Ref20][Ref21]
- Ensure Monte Carlo sample counts (300 for injection recovery, 200 for drag dispersion) and seeds (314159, 20260321) are cited accurately.[Ref17][Ref19]
- Confirm Subsection 3 explicitly references maintenance, command latency, and Monte Carlo metrics with their numerical values from `triangle_summary.json`.[Ref29]

## Chapter 4 – Authoritative Runs & Quantitative Evidence
Interrogate the archived runs, presenting deterministic and probabilistic metrics that demonstrate requirement compliance.

### Scope and Intent
- Catalogue the evidence packages: `run_20251018_1207Z` (triangle maintenance and robustness), `run_20251020_1900Z_tehran_daily_pass_locked` (locked daily pass alignment), `run_20260321_0740Z_tehran_daily_pass_resampled` (resampling study), and campaign or sweep artefacts supporting trend analyses.[Ref29][Ref30][Ref31][Ref32][Ref33]
- Extract quantitative highlights: formation duration, ground-distance maxima (windowed vs full propagation), orbital elements, maintenance metrics, command latency, Monte Carlo success rates, centroid offsets, and worst-vehicle displacements.[Ref29][Ref30][Ref31]
- Compare deterministic and Monte Carlo outputs to illustrate margin, robustness, and compliance probabilities.[Ref29][Ref31]
- Summarise auxiliary datasets such as command window CSVs, maintenance summaries, injection recovery catalogues, drag dispersion tables, solver settings, and STK export inventories.[Ref29][Ref30][Ref31]
- Highlight campaign governance data from `history.csv` and sweep outcomes from `tehran_30d.csv` to demonstrate temporal coverage and scheduling discipline.[Ref32][Ref33]

### Repository Artefacts to Cite
- `artefacts/run_20251018_1207Z/triangle_summary.json` for formation metrics, maintenance, command latency, and Monte Carlo results.[Ref29]
- `artefacts/run_20251018_1207Z/maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, and `injection_recovery_cdf.svg` for tabulated and visual evidence.[Ref29]
- `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json` for deterministic cross-track metrics and centroid evaluation.[Ref30]
- `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json` for statistical distributions, \(p_{95}\) values, and compliance probabilities.[Ref31]
- `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json` for stage sequence, node catalogue, phase durations, and STK export listings.[Ref30]
- `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/monte_carlo_summary.json` for comparison of resampled metrics and evidence of workflow extension.[Ref31]
- `artefacts/triangle_campaign/history.csv` for rerun timestamps, next-due dates, and notes.[Ref32]
- `artefacts/sweeps/tehran_30d.csv` for 30-day centroid trend data.[Ref33]

### Analytical Threads to Expand
- Present the ninety-six-second formation window with start and end timestamps, distinguishing the \(343.62\,\text{km}\) windowed maximum from the \(641.89\,\text{km}\) full-propagation maximum, explaining why both figures are reported.[Ref29]
- Detail maintenance metrics per spacecraft (delta-v per burn, annual delta-v, mean/peak differential acceleration) and relate them to MR-6 limits.[Ref29]
- Describe command latency metrics (contact probability, passes per day, maximum latency of \(1.533821385870122\,\text{h}\), margin of \(10.466178614129879\,\text{h}\)) and link to MR-5 compliance.[Ref29]
- Summarise Monte Carlo injection recovery results (mean, \(p_{95}\), maximum delta-v) and success rate of 1.0, tying them to MR-7 resilience expectations.[Ref29]
- Report drag dispersion metrics (ground-distance delta maxima, success rate) and interpret their implications for maintenance planning.[Ref29]
- Highlight deterministic centroid and worst-vehicle offsets at the evaluation midpoint (\(12.142754610722838\,\text{km}\) centroid, \(27.759459081570284\,\text{km}\) worst vehicle) and demonstrate compliance with primary and waiver thresholds.[Ref30]
- Discuss Monte Carlo centroid statistics (mean \(23.91411379156524\,\text{km}\), \(p_{95}=24.180422084370257\,\text{km}\)) and worst-vehicle distributions, emphasising the unity compliance probability.[Ref31]
- Compare resampled run outcomes with the locked baseline, noting any deviations or confirmations of robustness.[Ref31]
- Interpret campaign history data (e.g., rerun executed on 2025-10-18 with next due date 2026-01-16) and daily sweep trends to illustrate sustained coverage margins.[Ref32][Ref33]

### Literature Review Prompts
- Propose literature addressing formation maintenance delta-v budgeting, injection recovery strategies, and drag dispersion analysis to contextualise observed metrics.
- Suggest sources on ground-station scheduling and command latency modelling to complement the command-window data.
- Recommend studies on probabilistic compliance assessment and risk reporting to align Monte Carlo interpretations with best practice.

### Required Visual and Tabular Elements
- [Suggested Table 4.1] Consolidated metrics from `triangle_summary.json`, listing formation duration, ground distances, maintenance statistics, command latency, and Monte Carlo outputs.[Ref29]
- [Suggested Figure 4.1] Plot or schematic describing centroid and worst-vehicle cross-track behaviour at the evaluation midpoint, derived from deterministic and Monte Carlo summaries.[Ref30][Ref31]
- [Suggested Table 4.2] Comparison of deterministic vs Monte Carlo centroid metrics, including mean, standard deviation, and \(p_{95}\) values.[Ref30][Ref31]
- [Suggested Figure 4.2] Timeline chart summarising campaign execution history and next-due intervals using data from `history.csv`.[Ref32]
- [Suggested Table 4.3] Extract daily centroid offsets for the 30-day sweep to illustrate stability and trending margins.[Ref33]

### Cross-Chapter Linkages
- Lead into Chapter 5 by emphasising that STK validation and compliance integration rely on these artefacts, requiring a detailed discussion of importer workflows and regression coverage.[Ref10][Ref11][Ref12]

### Deliverable Checklist
- Confirm that all quantitative values replicate the JSON or CSV data exactly, including significant figures and units.[Ref29][Ref30][Ref31]
- Ensure references for Monte Carlo and deterministic datasets are clearly distinguished in Subsection 5.
- Verify that proposed figures and tables link to specific artefacts, enabling straightforward reproduction.

## Chapter 5 – STK Validation & Compliance Integration
Detail how simulation outputs are validated in STK 11.2, how compliance evidence is documented, and how regression tests enforce interoperability.

### Scope and Intent
- Describe the STK export artefacts produced by the simulation pipeline, covering ephemerides, satellite definitions, ground tracks, facilities, contact intervals, and event sets.[Ref12][Ref24]
- Outline STK import procedures for both the triangle formation and daily-pass scenarios, referencing automation scripts and manual validation guides.[Ref9][Ref11][Ref23]
- Explain how compliance documentation (e.g., scenario overview, STK guide, compliance matrix) maintains synchronisation with configuration files via regression tests.[Ref7][Ref10][Ref27]
- Highlight quality assurance mechanisms such as `tests/test_stk_export.py` and documentation consistency tests, noting how they guard against regression in exporter outputs or descriptive documents.[Ref28][Ref27]
- Show how compliance evidence is captured, catalogued, and cross-referenced within the matrix and final delivery manifest.[Ref7][Ref14]

### Repository Artefacts to Cite
- `tools/stk_export.py` for exporter classes, resampling, identifier sanitisation, and file formatting.[Ref25]
- `docs/stk_export.md` for user-facing guidance on exporter usage.[Ref12]
- `docs/how_to_import_tehran_daily_pass_into_stk.md` for step-by-step import and validation instructions.[Ref11]
- `docs/tehran_triangle_walkthrough.md` for triangle scenario reproduction and STK validation guidance.[Ref9]
- `sim/scripts/run_stk_tehran.py` for automation sequences and Connect script generation.[Ref23]
- `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/stk_export` for the exported file suite demonstrating compliance.[Ref30]
- `artefacts/run_20251018_1207Z/stk_export` for triangle formation exports.[Ref29]
- `docs/compliance_matrix.md` for evidence referencing and status reporting.[Ref7]
- `docs/final_delivery_manifest.md` for deliverable listings and reproduction instructions.[Ref14]
- `tests/test_stk_export.py` and `tests/test_documentation_consistency.py` for regression coverage of STK outputs and documentation alignment.[Ref28][Ref27]

### Analytical Threads to Expand
- Describe the exporter workflow: ordering samples, resampling ephemerides (including optional SciPy usage), writing `.e`, `.sat`, `.gt`, `.fac`, `.int`, and `.evt` files, and generating scenario metadata.[Ref25]
- Explain identifier sanitisation (e.g., converting spaces to underscores) and how regression tests ensure naming conventions persist.[Ref25][Ref28]
- Detail STK import steps: launching helper scripts, verifying epochs, checking ground tracks, confirming contact intervals, and capturing evidence (screenshots, metrics).[Ref11][Ref23]
- Highlight how `run_stk_tehran.py` automates scenario loading, Connect command dispatch, and optional dry-run output when STK is unavailable.[Ref23]
- Discuss the documentation consistency tests ensuring that RAAN values, access windows, and run identifiers remain synchronised between configuration files and narrative documents.[Ref27]
- Illustrate how compliance matrices cite specific STK exports and run directories when recording status, showing the traceability chain from requirement to artefact.[Ref7]
- Emphasise the final delivery manifest’s role in packaging STK exports, reproduction instructions, and verification tests for handover.[Ref14]

### Literature Review Prompts
- Suggest references on STK best practices, ephemeris formatting, and Connect automation to support repository guidance.
- Recommend sources on verification evidence capture and compliance reporting for space missions to align with the matrix structure.
- Identify standards or guidelines (e.g., CCSDS, ECSS) relevant to data formats, export fidelity, and validation documentation.[Ref13]

### Required Visual and Tabular Elements
- [Suggested Figure 5.1] Workflow diagram showing the path from simulation outputs to STK exports, import procedures, and compliance documentation updates.[Ref12][Ref24]
- [Suggested Table 5.1] Catalogue of STK export files per run, listing file types, descriptions, and validation status.[Ref29][Ref30]
- [Suggested Figure 5.2] Screenshot or schematic illustrating STK import verification steps, referencing the helper script outputs and guide instructions.[Ref11][Ref23]
- [Suggested Table 5.2] Mapping of documentation consistency checks to configuration parameters (RAAN, access windows, run IDs).[Ref27]

### Cross-Chapter Linkages
- Transition to Chapter 6 by noting that verification planning, testing campaigns, and future work expand upon the compliance infrastructure described here.[Ref13][Ref27]

### Deliverable Checklist
- Confirm Subsection 3 references explicit filenames and validation steps, not generic descriptions.[Ref29][Ref30]
- Ensure regression tests (`test_stk_export.py`, `test_documentation_consistency.py`) are cited alongside their safeguards.[Ref27][Ref28]
- Verify that compliance matrix entries referenced in the narrative align with the evidence sets discussed in Chapter 4.[Ref7]

## Chapter 6 – Verification, Testing, and Future Work
Consolidate verification strategy, testing coverage, roadmap milestones, resource planning, and outstanding work required to mature the mission concept.

### Scope and Intent
- Summarise the Verification and Validation Plan, including verification methods, matrices, validation activities, schedule milestones, and resource allocations.[Ref13]
- Describe regression test coverage (unit, integration, exporter, documentation) and highlight gaps requiring future automation.[Ref26][Ref27][Ref28]
- Outline roadmap milestones (VRR, simulation qualification, HIL testing, operations dry run, CDR, LRR) and their entry criteria, linking them to planned verification evidence.[Ref3][Ref13]
- Detail resource requirements (personnel, facilities, licences, budget) and procurement timelines, referencing the plan’s resource table.[Ref13]
- Identify outstanding evidence actions, future campaigns, or automation priorities noted in the compliance matrix or roadmap.[Ref7][Ref13]
- Recommend research extensions, such as high-fidelity propagation, closed-loop attitude coupling, or additional Monte Carlo analyses.[Ref3][Ref8]

### Repository Artefacts to Cite
- `docs/verification_plan.md` for verification strategy, matrices, validation activities, schedule, and resource requirements.[Ref13]
- `docs/project_roadmap.md` for staged development plan and milestone sequencing.[Ref3]
- `docs/compliance_matrix.md` for current compliance status and outstanding evidence notes.[Ref7]
- `docs/final_delivery_manifest.md` for deliverable consolidation and reproduction procedures.[Ref14]
- `docs/triangle_formation_results.md` for regression coverage references and outstanding evidence actions.[Ref8]
- `tests/unit/test_triangle_formation.py`, `tests/integration/test_simulation_scripts.py`, `tests/test_stk_export.py` for current automated coverage.[Ref26][Ref27][Ref28]
- `artefacts/triangle_campaign/history.csv` and `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled` for evidence of ongoing automation and future reruns.[Ref32][Ref31]

### Analytical Threads to Expand
- Elaborate on the verification matrix entries: list requirement IDs, methods (analysis, test, demonstration, inspection), responsible teams, artefacts, and completion criteria, linking them to the evidence catalogue.[Ref13]
- Discuss validation activities such as stakeholder scenario reviews, simulation-in-the-loop validation, field data rehearsals, and user acceptance demonstrations, noting success criteria.[Ref13]
- Present schedule milestones with planned dates, responsible owners, and entry criteria, integrating roadmap context and highlighting schedule risks (e.g., HIL availability, simulator regression).[Ref3][Ref13]
- Summarise resource requirements, distinguishing committed vs requested assets, cost estimates, and procurement lead times.[Ref13]
- Identify outstanding actions from the compliance matrix (e.g., scheduled reruns, evidence capture updates) and align them with future work recommendations.[Ref7]
- Assess current regression coverage, noting where additional tests or automation are required (e.g., Monte Carlo validation scripts, advanced propagation models, STK automation regression).[Ref26][Ref27][Ref28]
- Propose future research directions, including atmospheric density model updates, drag-sail contingencies, multi-ground-station operations, or payload alignment modelling, indicating where literature review should focus.[Ref8][Ref13]

### Literature Review Prompts
- Recommend standards and methodologies for verification planning, such as NASA-STD-7009A, ECSS verification handbooks, or ISO standards on configuration management.[Ref13]
- Suggest academic sources on mission assurance, Monte Carlo validation, and small-satellite campaign planning to reinforce plan elements.
- Encourage review of HIL testing practices and resource scheduling to support the planned hardware campaigns.

### Required Visual and Tabular Elements
- [Suggested Table 6.1] Extract key rows from the verification matrix, summarising requirement IDs, methods, teams, evidence tags, and completion criteria.[Ref13]
- [Suggested Figure 6.1] Timeline chart of roadmap milestones with verification artefact delivery points.[Ref3][Ref13]
- [Suggested Table 6.2] Resource allocation summary listing personnel, facilities, licences, budgets, and status (committed/requested).[Ref13]
- [Suggested Figure 6.2] Diagram illustrating regression coverage layers (unit, integration, exporter, documentation) and highlighting gaps.[Ref26][Ref27][Ref28]

### Cross-Chapter Linkages
- Conclude the dossier by tying future work recommendations back to requirement compliance, simulation enhancements, and STK validation pathways discussed earlier.[Ref7][Ref8][Ref12]
- Emphasise that continued evidence generation must maintain configuration control and update the compliance matrix and documentation consistently.[Ref7][Ref15]

### Deliverable Checklist
- Ensure Subsection 3 references specific verification matrix entries, milestone dates, and resource identifiers from the plan.[Ref13]
- Confirm all regression tests are cited with their scope and intended assurance coverage.[Ref26][Ref27][Ref28]
- Verify that future work recommendations align with outstanding actions noted in the compliance matrix or roadmap.

## Cross-Cutting Analytical Threads to Address Throughout the Dossier
- Emphasise the interplay between relative orbital elements, geometric tolerances, and mission assurance; explain how theoretical constructs (e.g., ROE drift, LVLH geometry) manifest in simulation outputs and requirement verification.[Ref19][Ref29]
- Highlight automation and reproducibility: describe how Makefile targets (`make triangle`, `make scenario`), CLI scripts, and campaign schedulers uphold traceability and evidence regeneration.[Ref20][Ref21][Ref22]
- Discuss data provenance practices, including storage under `artefacts/`, metadata capture (`run_metadata.json`, solver settings), and configuration-controlled documentation updates.[Ref29][Ref30][Ref32]
- Address stakeholder needs by referencing Concept of Operations scenarios, ground-segment resilience strategies, and risk management frameworks documented in the ConOps.[Ref6]
- Reinforce compliance awareness by explicitly connecting metrics to requirement thresholds and evidence tags in every chapter.[Ref4][Ref7]

## Appendices and Supplementary Modules (Optional in Dossier, Mandatory to Reference)
- Encourage the dossier author to include appendices for expanded tables (e.g., full Monte Carlo catalogues, command window logs) if the main chapters require summarisation.[Ref29][Ref31]
- Suggest documenting tooling usage examples: CLI commands, FastAPI endpoints, debug workflows, and STK automation scripts to aid reproducibility.[Ref16][Ref20][Ref23]
- Recommend an appendix summarising regression test outputs or coverage reports, referencing PyTest runs and CI expectations.[Ref27][Ref28]
- Propose including glossary entries for mission-specific terminology (ROE, LVLH, RAAN, centroid, waiver) drawing on repository documentation.

## Delivery Checklist for the Generated Dossier
- Verify that all six chapters are present, in order, and contain the mandated subsections with correctly formatted headings.
- Ensure every factual statement includes an inline numbered reference, with reference lists matching those numbers.
- Confirm quantitative values replicate repository artefacts exactly, including significant figures and units.
- Check that suggested figures, tables, and equations are explicitly tied to source artefacts, enabling future drafting or plotting.
- Validate that literature review prompts identify clear themes and external standards for further research.
- Guarantee that cross-chapter transitions are articulated, guiding the reader logically through mission framing, configuration, simulation, evidence, compliance, and future work.
- Provide an overall concluding note emphasising configuration control, reproducibility, and compliance stewardship.

## References
- [Ref1] `README.md`
- [Ref2] `docs/project_overview.md`
- [Ref3] `docs/project_roadmap.md`
- [Ref4] `docs/mission_requirements.md`
- [Ref5] `docs/system_requirements.md`
- [Ref6] `docs/concept_of_operations.md`
- [Ref7] `docs/compliance_matrix.md`
- [Ref8] `docs/triangle_formation_results.md`
- [Ref9] `docs/tehran_triangle_walkthrough.md`
- [Ref10] `docs/tehran_daily_pass_scenario.md`
- [Ref11] `docs/how_to_import_tehran_daily_pass_into_stk.md`
- [Ref12] `docs/stk_export.md`
- [Ref13] `docs/verification_plan.md`
- [Ref14] `docs/final_delivery_manifest.md`
- [Ref15] `docs/_authoritative_runs.md`
- [Ref16] `docs/interactive_execution_guide.md`
- [Ref17] `config/scenarios/tehran_triangle.json`
- [Ref18] `config/scenarios/tehran_daily_pass.json`
- [Ref19] `sim/formation/triangle.py`
- [Ref20] `sim/scripts/run_triangle.py`
- [Ref21] `sim/scripts/run_scenario.py`
- [Ref22] `sim/scripts/run_triangle_campaign.py`
- [Ref23] `sim/scripts/run_stk_tehran.py`
- [Ref24] `tools/stk_export.py`
- [Ref25] `docs/stk_export.md`
- [Ref26] `tests/unit/test_triangle_formation.py`
- [Ref27] `tests/integration/test_simulation_scripts.py`
- [Ref28] `tests/test_stk_export.py`
- [Ref29] `artefacts/run_20251018_1207Z/triangle_summary.json`
- [Ref30] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`
- [Ref31] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`
- [Ref32] `artefacts/triangle_campaign/history.csv`
- [Ref33] `artefacts/sweeps/tehran_30d.csv`

## Chapter-by-Chapter Extended Guidance
### Chapter 1 Extension – Mission Framing & Requirements Baseline
#### Detailed Evidence Extraction Tasks
- Restate MR-1 through MR-7 verbatim, including verification approaches and cross-reference identifiers from the mission requirement matrix.[Ref4]
- Quote the compliance status, evidence tag, and run identifier for each mission requirement exactly as recorded in the compliance matrix table.[Ref7]
- Extract the acceptance criteria checklists from the system requirements document and integrate them as supporting evidence in the narrative.[Ref5]
- Document the linkage between the Concept of Operations objectives and MR-5 to MR-7, citing the relevant ConOps acceptance criteria.[Ref6]
- Highlight the run catalogue entries, specifying directories, key evidence artefacts, and notes recorded for each authoritative run.[Ref15]
- Summarise the configuration maintenance strategy (cadence, tolerance, delta-v reserve fraction) from `project.yaml`, explaining how it underpins MR-6 compliance.[Ref16]
- Capture the command station assumptions (location, single-station operations) from the scenario configuration and align them with MR-5.[Ref18]
- Enumerate regression tests guarding requirement thresholds, noting the specific assertions within `test_triangle_formation_meets_requirements` for each metric.[Ref26]
- List documentation artefacts that must be updated when requirements change, referencing the roadmap and compliance governance statements.[Ref3][Ref7]
- Detail the acceptance checklists within the ConOps that relate to commissioning success criteria and disposal planning.[Ref6]
- Record the instructions for naming conventions and artefact storage outlined in the compliance matrix and authoritative runs ledger.[Ref7][Ref15]
- Include guidance on how requirement updates trigger traceability reviews, referencing the change-control notes in the system requirements document.[Ref5]

#### Expanded Literature Topics to Cover
- Review formation-flying requirement derivation methodologies from ESA and NASA mission design handbooks to contextualise MR-1 through MR-4.[Ref6]
- Survey operational readiness standards governing command latency and single-ground-station operations, linking them to MR-5.[Ref6]
- Examine propulsion budgeting literature for small-satellite constellations to justify the 15 m/s annual delta-v constraint.[Ref4]
- Explore robustness and contingency planning frameworks applicable to ±5 km and ±0.05° injection dispersion recovery.[Ref4]
- Discuss configuration management and traceability best practices from systems engineering references to support the ledger approach.[Ref5]
- Highlight academic analyses of transient formation missions to underpin the unique mission framing described in Chapter 1.[Ref2]
- Incorporate standards on documentation control and audit readiness that parallel the compliance matrix structure.[Ref7]

#### Writing Style Prompts
- Use assertive topic sentences that restate the mission objective before diving into requirement details.
- Maintain a balance between descriptive and analytical prose, ensuring each requirement discussion culminates in a compliance statement.
- Embed citations after every sentence, alternating between mission documents and artefact evidence to show traceability.
- Integrate short summarising sentences that tie requirement satisfaction to upcoming configuration analysis.
- Employ transitional phrases that emphasise continuity between requirement framing and simulation evidence.

### Chapter 2 Extension – Configuration & Geometric Foundations
#### Detailed Evidence Extraction Tasks
- Tabulate all metadata fields in `project.yaml`, including project name, version, authoring team, and last updated date.[Ref16]
- List platform parameters (mass, dimensions, power margin, propulsion system, total delta-v) and explain their implications for formation maintenance.[Ref16]
- Extract payload constraints, communications parameters, and ground network entries from the configuration to inform operations discussions.[Ref16]
- Itemise orbit elements, formation design identifiers, and maintenance strategy values, linking each to simulation outputs.[Ref16]
- Document simulation settings (time bounds, step size, integrator tolerances, force models) to prepare readers for pipeline analysis.[Ref16]
- Summarise Monte Carlo dispersion settings, including sigma values, sample counts, seeds, and budgets.[Ref17]
- Record command station coordinates, contact ranges, and Monte Carlo recovery assumptions embedded in the triangle scenario.[Ref17]
- List access window timings, payload constraints, and operational limits from the daily-pass scenario metadata.[Ref18]
- Extract cross-track limits, RAAN alignment parameters, and propagation margins from the daily-pass configuration.[Ref18]
- Document payload duty cycle, power constraints, and thermal requirements for the daily-pass scenario to support ConOps linkages.[Ref18]
- Highlight `validated_against_stk_export` flags and alignment validation run IDs within scenario metadata.[Ref17][Ref18]
- Enumerate scenario output controls such as included products, reporting intervals, and STK export options.[Ref16]

#### Expanded Literature Topics to Cover
- Explore LVLH frame utilisation and equilateral formation design methods to justify the `_formation_offsets` implementation.[Ref19]
- Investigate RAAN alignment and repeat-ground-track theories that underpin the scenario RAAN optimiser assumptions.[Ref21]
- Review atmospheric drag modelling literature relevant to the NRLMSISE-00 model and drag dispersion parameters.[Ref16]
- Examine Monte Carlo planning strategies for formation-flying missions to substantiate sample sizes and sigma selections.[Ref17]
- Study command-and-control range planning for LEO constellations to validate the 2200 km contact range assumption.[Ref17]
- Survey payload thermal and duty-cycle considerations for dawn-dusk imaging missions to contextualise operational constraints.[Ref18]

#### Writing Style Prompts
- Provide precise definitions for each configuration term before explaining its role in the simulation pipeline.
- Use comparative sentences to highlight differences between triangle and daily-pass scenarios.
- Anchor each paragraph with explicit references to configuration keys and values.
- End subsections with reflections on how configuration choices satisfy or challenge requirement thresholds.
- Incorporate descriptive language that helps readers visualise the formation geometry and scenario timings.

### Chapter 3 Extension – Simulation Pipeline & Toolchain
#### Detailed Evidence Extraction Tasks
- Break down the CLI arguments for `run_triangle.py`, noting defaults, output directories, and logging behaviour.[Ref20]
- Summarise the CLI options for `run_scenario.py`, including metrics filters, output handling, and scenario selection mechanisms.[Ref21]
- Document the cadence enforcement logic, command-line switches, and metadata recording for `run_triangle_campaign.py`.[Ref22]
- Extract automation options (`--visible`, `--dry-run`, `--formation-side-length-km`) from `run_stk_tehran.py`.[Ref23]
- List the stage sequence names produced by the scenario runner and map each to generated artefacts.[Ref21]
- Describe the data structures (`StateSample`, `PropagatedStateHistory`, `GroundTrack`, `GroundContactInterval`, `SimulationResults`) utilised by the exporter.[Ref24][Ref12]
- Enumerate metric outputs from `simulate_triangle_formation`, including triangle stats, ground metrics, formation window, maintenance, command latency, injection recovery, and drag dispersion.[Ref19]
- Capture the JSON serialisation format of triangle results, noting the geometry structure and sample records.[Ref29]
- Detail the CSV column headings for maintenance, command windows, injection recovery, and drag dispersion outputs.[Ref29]
- Record the plotting routine for injection recovery CDF, including file format (SVG) and location.[Ref29]
- List the scenario summary artefacts produced by the daily-pass runner, including deterministic and Monte Carlo CSVs.[Ref30][Ref31]
- Document the solver settings JSON contents, highlighting RAAN search parameters and convergence metrics.[Ref30]

#### Expanded Literature Topics to Cover
- Review numerical integration methods (RKF78) and tolerance selection for orbit propagation.[Ref16]
- Discuss Monte Carlo sampling theory and result interpretation for spacecraft formation robustness analysis.[Ref29]
- Explore command latency modelling and ground network scheduling literature applicable to single-station operations.[Ref19]
- Investigate differential drag estimation techniques and their implications for maintenance planning.[Ref29]
- Summarise best practices in STK automation via Connect scripting to contextualise `run_stk_tehran.py`.[Ref23]
- Examine methodologies for campaign scheduling and cadence enforcement in mission assurance contexts.[Ref22]

#### Writing Style Prompts
- Structure paragraphs to follow the data flow from configuration ingestion to artefact export.
- Use active voice when describing script behaviours and pipeline stages.
- Provide explicit references to function names and classes when detailing algorithmic steps.
- Employ comparative phrases to distinguish deterministic and Monte Carlo processing paths.
- Conclude sections with notes on how automation supports reproducibility and compliance.

### Chapter 4 Extension – Authoritative Runs & Quantitative Evidence
#### Detailed Evidence Extraction Tasks
- Itemise all metrics in `triangle_summary.json`, including mean, minimum, and maximum values for area, aspect ratio, and side lengths.[Ref29]
- Document centroid latitude, longitude, and altitude time series references included in the geometry samples.[Ref29]
- Record min and max command distances, contact probabilities, passes per day, and latency margins reported in the command latency metrics.[Ref29]
- Summarise maintenance per-spacecraft statistics, including differential acceleration values and delta-v per burn figures.[Ref29]
- Extract injection recovery aggregate metrics and assumptions (position sigma, velocity sigma, recovery time, delta-v budget).[Ref29]
- Capture drag dispersion aggregate metrics and assumptions, noting success rates and delta values.[Ref29]
- List deterministic cross-track maxima and minima per vehicle, as well as centroid minima, from the daily-pass summary.[Ref30]
- Enumerate Monte Carlo cross-track statistics for each vehicle and the centroid, including mean, standard deviation, and \(p_{95}\).[Ref31]
- Document the compliance probabilities (primary, waiver, relative) and run count from the Monte Carlo summary.[Ref31]
- Record the STK export file names and scenario metadata from the daily-pass scenario summary.[Ref30]
- Extract resampled run statistics to compare with the locked baseline, noting any differences in centroid or worst-vehicle metrics.[Ref31]
- Summarise sweep data trends, highlighting centroid offsets and compliance flags across the 30-day period.[Ref33]
- Capture campaign history entries, including timestamps, next due dates, scenario paths, and notes.[Ref32]

#### Expanded Literature Topics to Cover
- Investigate statistical reporting standards for Monte Carlo campaigns to contextualise success rates and percentile metrics.[Ref31]
- Review methods for presenting maintenance and delta-v budgets in mission assurance documentation.[Ref29]
- Explore literature on access window trending and long-term coverage assessments to interpret sweep data.[Ref33]
- Examine robustness analysis techniques for nodal alignment and cross-track compliance to support deterministic vs stochastic comparisons.[Ref30]
- Discuss best practices for documenting command latency and ground contact performance in mission design reports.[Ref29]

#### Writing Style Prompts
- Use precise numerical descriptions with appropriate significant figures for every metric.
- Introduce tables with contextual sentences explaining their relevance to requirements.
- Contrast deterministic and Monte Carlo findings explicitly, noting margins and compliance probabilities.
- Integrate references to artefact filenames when discussing data sources.
- Conclude sections with interpretations that connect metrics to requirement satisfaction.

### Chapter 5 Extension – STK Validation & Compliance Integration
#### Detailed Evidence Extraction Tasks
- List each file type generated by the STK exporter (`.e`, `.sat`, `.gt`, `.fac`, `.int`, `.evt`) and describe its role in the STK scenario.[Ref24][Ref12]
- Document the scenario metadata fields (scenario name, start epoch, stop epoch, frame, step size) produced during export.[Ref24][Ref12]
- Summarise the import steps outlined in the STK guide, including helper script invocation, graphics inspection, and contact verification.[Ref11]
- Capture the validation checklist items required after importing the daily-pass scenario (ground-track alignment, contact windows, RAAN verification).[Ref11]
- Record the triangle walkthrough reproduction steps, including artefact review, runner invocation, and STK validation actions.[Ref9]
- Enumerate the regression assertions in `tests/test_stk_export.py`, noting checks on ephemeris ordering, file contents, and identifier sanitisation.[Ref28]
- Document the documentation consistency checks verifying RAAN values, window times, and path existence within key documents.[Ref27]
- Extract compliance matrix entries referencing STK exports, noting evidence tags and notes.[Ref7]
- Summarise final delivery manifest instructions for regenerating STK artefacts and running verification tests.[Ref14]
- List STK automation script outputs, including export directories, Connect command files, and metrics summaries.[Ref23]

#### Expanded Literature Topics to Cover
- Review STK ephemeris formatting requirements and recommended sample spacing to support exporter explanations.[Ref25]
- Examine Connect scripting and automation best practices relevant to mission replay.[Ref23]
- Explore standards for validation evidence capture and archival in mission assurance frameworks.[Ref7]
- Investigate documentation control methodologies for keeping configuration files and descriptive documents synchronised.[Ref27]

#### Writing Style Prompts
- Provide step-by-step descriptions of validation workflows, emphasising reproducibility.
- Use terminology consistent with STK documentation (scenario, facility, interval list) when describing artefacts.
- Highlight checks and balances ensuring exports remain compliant with STK 11.2 requirements.
- Conclude sections with notes on how validation outputs support compliance reporting.
- Maintain a formal tone when discussing regression tests and quality assurance mechanisms.

### Chapter 6 Extension – Verification, Testing, and Future Work
#### Detailed Evidence Extraction Tasks
- Extract the verification matrix table entries, listing requirement IDs, methods, teams, artefacts, and completion criteria.[Ref13]
- Document validation activities, including stakeholder reviews, simulation-in-the-loop tests, field rehearsals, and acceptance demonstrations, noting success criteria.[Ref13]
- Summarise the schedule milestones with planned dates, owners, entry criteria, and notes on dependencies or risks.[Ref13]
- Record resource allocations, distinguishing committed vs requested assets and associated cost or effort estimates.[Ref13]
- Capture procurement lead times and mitigation strategies for schedule risks identified in the plan.[Ref13]
- List outstanding evidence actions and rerun schedules noted in the compliance matrix and triangle campaign history.[Ref7][Ref32]
- Document regression test coverage per layer (unit, integration, exporter, documentation) and identify gaps for future automation.[Ref26][Ref27][Ref28]
- Summarise future work recommendations, including high-fidelity modelling, additional Monte Carlo campaigns, and STK automation enhancements.[Ref13]

#### Expanded Literature Topics to Cover
- Review verification planning standards (NASA-STD-7009A, ECSS verification guidelines) to frame strategy discussions.[Ref13]
- Investigate resource planning and budgeting practices for V&V campaigns in small-satellite missions.[Ref13]
- Explore automation and regression testing literature applicable to mission analysis pipelines.[Ref27]
- Examine methodologies for stakeholder engagement and user acceptance testing in space mission contexts.[Ref6]
- Discuss lessons learned from prior formation-flying missions regarding maintenance of compliance artefacts and rerun schedules.[Ref8]

#### Writing Style Prompts
- Present verification strategy elements as structured narratives leading into actionable recommendations.
- Use chronological ordering when describing schedule milestones to emphasise project flow.
- Align paragraphs with verification themes (analysis, test, demonstration, inspection) for clarity.
- Close sections with forward-looking statements that reinforce the importance of continued evidence generation.
- Maintain a strategic tone that underscores the mission’s readiness trajectory.

## Annex A – Repository Artefact Summaries
- Provide brief descriptions for each directory under `artefacts/`, including content types, key files, and their role in compliance.[Ref29][Ref30][Ref31]
- Summarise the purpose of `artefacts/debug`, `artefacts/conops_baseline`, and `artefacts/triangle_campaign`, noting how they support investigations.[Ref29][Ref32]
- Describe the function of `artefacts/run_20251018_1424Z` and how it relates to quarterly reruns and drag-inclusive studies.[Ref32]
- List the file naming conventions within `artefacts/run_20251020_0813Z_tehran_daily_pass` and related directories to illustrate historical data capture.[Ref30]
- Explain the contents of `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled`, highlighting differences from the locked dataset.[Ref31]
- Summarise `artefacts/sweeps` and `artefacts/triangle_campaign/history.csv` to demonstrate longitudinal analysis capabilities.[Ref32][Ref33]
- Document the presence of `run_metadata.json` files and their role in preserving execution context for each campaign.[Ref22]
- Mention the `artefacts/triangle_run` curated snapshot and its relationship to the authoritative `run_20251018_1207Z` dataset.[Ref15]

## Annex B – Stepwise Drafting Workflow
1. Read Chapters 1–6 of this prompt to understand mandatory structure and scope.[Ref2][Ref3]
2. Assemble source materials for each chapter, prioritising configuration files, mission documents, and authoritative artefacts.[Ref7][Ref15]
3. Extract quantitative metrics from JSON and CSV artefacts, double-checking against compliance matrices.[Ref29][Ref30]
4. Outline chapter narratives following the prescribed subsections before drafting prose.
5. Draft each chapter sequentially, embedding citations at the end of every sentence.[Ref4][Ref7]
6. Populate suggested figures and tables with placeholders referencing source artefacts.[Ref29][Ref31]
7. Complete chapter-specific reference lists, ensuring numbering aligns with inline citations.
8. Review transitions between chapters, inserting connective sentences that reinforce narrative continuity.
9. Audit the entire dossier for citation accuracy, numerical fidelity, and compliance emphasis.[Ref7]
10. Prepare appendices or supplementary materials as needed, referencing annex guidance.

## Annex C – Validation Gate Checklist
- Confirm that every chapter references at least one configuration file, one mission document, and one artefact dataset.[Ref16][Ref29]
- Ensure all metrics tied to requirements cite both the requirement document and the validating artefact.[Ref4][Ref29]
- Verify that STK validation steps are documented for every scenario discussed.[Ref11][Ref30]
- Check that regression tests are cited in chapters covering simulation or export tooling.[Ref26][Ref27][Ref28]
- Validate that Monte Carlo statistics include mean, \(p_{95}\), and compliance probability references.[Ref31]
- Confirm that maintenance and command latency metrics are quoted with margins relative to MR thresholds.[Ref29]
- Ensure future work recommendations correspond to outstanding actions or roadmap milestones.[Ref7][Ref13]
- Review reference lists to avoid duplication or missing sources.

## Annex D – Terminology and Abbreviations
- ROE – Relative Orbital Elements, defined in `sim/formation/triangle.py` and `src/constellation/roe.py` (include citation when discussed).[Ref19]
- LVLH – Local-Vertical Local-Horizontal frame, used to construct the equilateral formation offsets.[Ref19]
- RAAN – Right Ascension of the Ascending Node, optimised by the scenario runner for Tehran alignment.[Ref18][Ref21]
- MR – Mission Requirement, numbered MR-1 through MR-7 in the requirement matrix.[Ref4]
- SRD – System Requirements Document, detailing SRD-F/P/O/R classes.[Ref5]
- STK – Systems Tool Kit, version 11.2, targeted by exporter utilities and validation guides.[Ref12][Ref24]
- CCB – Configuration Control Board, referenced in compliance and ConOps documentation.[Ref6][Ref7]
- TMOC – Tehran Mission Operations Centre, described in the Concept of Operations.[Ref6]
- HIL – Hardware-in-the-Loop, referenced in the verification plan’s schedule.[Ref13]
- VRR/CDR/LRR – Verification Readiness Review, Critical Design Review, Launch Readiness Review; include definitions when used.[Ref3][Ref13]

## Annex E – Future Dataset Hooks
- Note placeholders for upcoming high-fidelity propagations that will augment the current Keplerian model, ensuring the dossier anticipates their integration.[Ref3]
- Identify areas where atmospheric drag model updates or SRP inclusion will modify maintenance analyses.[Ref16]
- Highlight planned extensions to Monte Carlo campaigns (e.g., increased sample counts, additional dispersion axes) and reserve space for future citation.[Ref31]
- Mention expected additions to ground-station modelling, such as multi-station support or outage simulations.[Ref6]
- Flag potential new regression tests covering advanced exporters or closed-loop attitude simulations.[Ref27]
- Anticipate repository updates introducing new run directories and describe how to integrate them into the compliance narrative.[Ref15]

## Annex F – Citation Formatting Rules
- Use bracketed numerical citations (e.g., `[1]`) aligned with chapter-specific reference lists and the repository reference set.[Ref4]
- Place citations at the end of sentences, inside punctuation, to maintain consistency.
- Reference multiple sources using combined citations (e.g., `[2][5]`) when necessary for clarity.[Ref2][Ref5]
- Ensure every citation corresponds to an entry in the chapter’s reference list and, if applicable, the global reference appendix.
- Avoid citing non-existent artefacts or speculative sources; all references must originate from the repository or approved literature.


## Annex G – Editorial Quality Checks
- Perform a spelling audit ensuring British English conventions (e.g., "optimisation", "colour") are applied consistently.[Ref1]
- Verify paragraph lengths remain manageable, with transitions linking consecutive topics smoothly.
- Check that figure and table references align with their numbering and source artefacts.[Ref29][Ref31]
- Confirm that equations are rendered using inline LaTeX syntax and tied to relevant discussions.[Ref19]
- Ensure appendices or annex references within the dossier point to the correct supplementary sections.
- Review headings for sequential numbering and consistent title case.
- Validate that cross-references to future chapters or annexes are accurate after final ordering.
- Conduct a final read-through to remove redundant statements while preserving compliance emphasis.
- Inspect hyperlinks (if any) to ensure they refer to repository-relative paths without typos.[Ref7]
- Document any deviations or editorial decisions in a change log for traceability.

## Annex H – Suggested Figure and Table Catalogue
- Figure 1.1 – Requirement flow diagram from stakeholder goals to SRD entries.[Ref5]
- Table 1.1 – Requirement-to-evidence crosswalk summarising MR and SRD compliance.[Ref4][Ref7]
- Figure 2.1 – Configuration flow diagram linking project metadata to simulation inputs.[Ref16][Ref21]
- Table 2.1 – Comparison of triangle vs daily-pass scenario parameters.[Ref17][Ref18]
- Equation 2.1 – LVLH offset definitions for the equilateral formation.[Ref19]
- Figure 3.1 – Scenario runner stage sequence with artefact outputs.[Ref21]
- Table 3.1 – Monte Carlo configuration summary for injection and drag dispersions.[Ref19][Ref29]
- Figure 3.2 – STK export pipeline workflow.[Ref24][Ref12]
- Figure 4.1 – Cross-track compliance plot comparing deterministic and Monte Carlo results.[Ref30][Ref31]
- Table 4.1 – Maintenance and command latency metrics with requirement margins.[Ref29]
- Figure 4.2 – Campaign history timeline showing rerun cadence.[Ref32]
- Table 4.2 – 30-day centroid sweep statistics.[Ref33]
- Figure 5.1 – STK validation process overview with importer checkpoints.[Ref11]
- Table 5.1 – STK export artefact inventory per run.[Ref29][Ref30]
- Figure 6.1 – Verification schedule and milestone timeline.[Ref13]
- Table 6.1 – Verification matrix excerpt for high-priority requirements.[Ref13]
- Figure 6.2 – Regression coverage layers and planned enhancements.[Ref26][Ref27][Ref28]
- Table 6.2 – Resource allocation and procurement status summary.[Ref13]
- Additional placeholders may be added for future datasets; ensure numbering remains sequential when expanded.

## Annex I – Response Packaging Instructions
- Compile the completed dossier into a single document with clearly delineated chapters and annexes.
- Provide a front-matter summary outlining mission context, methodology, and evidence structure.[Ref2]
- Include a table of contents referencing all chapter headings, subsections, and annexes.
- Append chapter-specific reference lists immediately after each chapter before transitioning to the next.
- Insert the global reference appendix (derived from this prompt) at the end of the dossier for quick cross-checking.
- Package supplementary artefacts (e.g., tables, figures, plots) with filenames mirroring the suggested catalogue entries.[Ref29]
- Maintain a version history noting drafting dates, editors, and key changes aligned with configuration management practices.[Ref15]
- Deliver the dossier in a reviewable format (e.g., Markdown or PDF) accompanied by a checksum for verification.
- Archive the response and supporting artefacts under a new run identifier if additional simulations are executed.[Ref32]
- Notify stakeholders of any deviations from the prompt’s instructions, providing rationale and remediation plans.

## Annex J – Glossary of Quantitative Targets
- \(96\,\text{s}\) minimum simultaneous access duration mandated by MR-3, evidenced by `run_20251018_1207Z`.[Ref4][Ref29]
- \(\pm30\,\text{km}\) primary and \(\pm70\,\text{km}\) waiver centroid cross-track limits enforced at the access midpoint.[Ref4][Ref30]
- \(14.04\,\text{m/s}\) maximum annual delta-v recorded for SAT-3, remaining within the 15 m/s budget.[Ref29]
- \(1.533821385870122\,\text{h}\) maximum command latency with \(10.466178614129879\,\text{h}\) margin to MR-5.[Ref29]
- 100% Monte Carlo injection recovery success rate with \(p_{95}\,\Delta v = 0.04117037812182684\,\text{m/s}\).[Ref29][Ref31]
- \(350.7885044642857^{\circ}\) optimised RAAN ensuring centroid alignment above Tehran.[Ref18][Ref30]
- 1000 Monte Carlo runs executed during the locked daily-pass campaign, yielding unity compliance probability.[Ref31]
- 300 samples executed for injection recovery and 200 for drag dispersion within the triangle simulation.[Ref17][Ref19]
- 30-day sweep showing centroid offsets decreasing from \(7.647491\,\text{km}\) to \(2.681807\,\text{km}\) over the campaign window.[Ref33]
- Next rerun scheduled for 2026-01-16T14:24:25.333551Z following the October 2025 campaign execution.[Ref32]
