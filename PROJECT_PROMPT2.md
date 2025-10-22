# Orbital Design and Mission Analysis Prompt: Tehran Triangular Formation Programme

## Purpose of This Prompt
This prompt defines the exhaustive brief for assembling the "Mission Research & Evidence Compendium" covering the Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation tasked with generating a repeatable, transient triangular formation above Tehran. It binds literature exploration, configuration baselines, simulation artefacts, verification evidence, and analytical narratives so that every chapter of the final compendium remains anchored to configuration-controlled data and Systems Tool Kit (STK 11.2) compliant exports.[Ref1][Ref2][Ref5][Ref11] Follow the chapter sequence precisely and complete each subsection before progressing. All prose must adopt British English spelling and cite references inline using the numerical scheme defined in the concluding References section. Do not omit the specified tables, figures, or equation prompts; they are mandatory placeholders for the writing stage.

## Global Writing Rules
1. Maintain an academic tone that remains accessible to multidisciplinary reviewers drawn from mission design, systems engineering, and ground segment operations.[Ref1][Ref5]
2. Integrate repository artefacts such as `run_20251018_1207Z` and `run_20251020_1900Z_tehran_daily_pass_locked` within each chapter's evidence narrative, confirming STK interoperability whenever exports are referenced.[Ref11][Ref14][Ref18][Ref21]
3. When specifying figures or tables, state the intended content, data source, and cross-reference identifier. These placeholders will be realised in the typeset report but must be described here in enough detail for automated rendering.
4. Reinforce mission requirement traceability in every chapter by referencing the applicable identifiers (MR-#, SRD-#) and citing the governing documentation.[Ref3][Ref4][Ref5]
5. Each chapter must close with a bullet list titled **"Evidence Integration Checklist"** containing at least five items that confirm the inclusion of figures, tables, equations, data references, requirement links, and STK validation statements relevant to that chapter.

## Repository Familiarisation Tour
### A. Directory Priorities
- **docs/** – Review mission overview, requirements, compliance, verification, and scenario walkthroughs to understand narrative context and traceability expectations.[Ref2][Ref3][Ref5][Ref7][Ref17]
- **config/** – Inspect project-wide constants and scenario definitions to see how configuration controls inform simulations and documentation.[Ref9][Ref10]
- **sim/** – Explore formation dynamics code and pipeline scripts to grasp how numerical models interface with configuration data and produce artefacts.[Ref12][Ref20]
- **artefacts/** – Navigate authoritative run directories, ensuring familiarity with JSON summaries, CSV catalogues, and STK exports referenced throughout this prompt.[Ref14][Ref16][Ref18]
- **tests/** – Review unit and integration tests to understand regression coverage and how compliance is safeguarded through automation.[Ref13][Ref20]

### B. Run Artefact Orientation Tasks
1. Open `artefacts/run_20251018_1207Z/triangle_summary.json` and annotate key metrics (window duration, aspect ratio, delta-v, command latency, injection success) that will be reused in multiple chapters.[Ref14]
2. Inspect the accompanying CSV files to note column headers, units, and data ranges, preparing to reference them in Chapter 4 and Chapter 7 discussions.[Ref14][Ref15]
3. Examine `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` summaries to understand RAAN optimisation outputs and Monte Carlo statistics relevant to MR-2 and SRD-P-001.[Ref18][Ref19]
4. Review the curated `artefacts/triangle_run/` snapshot to verify how evidence is packaged for onboarding and demonstrations.[Ref16]
5. Confirm each artefact directory contains STK exports and validation logs, noting any naming conventions or metadata patterns to maintain consistency in future runs.[Ref21][Ref22]

### C. Toolchain Entry Points
- **Simulation Commands:** Identify Python entry points (`sim.scripts.run_scenario`, `sim.scripts.run_triangle`) and Makefile targets that orchestrate analyses and generate artefacts.[Ref1][Ref20]
- **Exporter Interface:** Study `tools/stk_export.py` to understand required inputs, optional parameters, and naming sanitisation rules that guarantee STK compatibility.[Ref21]
- **Testing Harness:** Familiarise yourself with pytest fixtures and CLI smoke tests to appreciate how automation ensures reproducibility and compliance adherence.[Ref13][Ref20]

### D. Documentation Cross-Reference Map
1. Link mission requirements to compliance matrix entries, noting evidence tags that reference authoritative runs.[Ref3][Ref5][Ref16]
2. Map ConOps operational scenarios to verification activities and automation outputs, ensuring narrative cohesion across chapters.[Ref6][Ref7][Ref20]
3. Trace how the project roadmap informs verification scheduling and resource allocation, particularly for upcoming milestones.[Ref7][Ref8]
4. Identify sections in `triangle_formation_results.md` and `tehran_daily_pass_scenario.md` that supply interpretive context for quantitative findings.[Ref11][Ref17]
5. Record any documentation gaps that require augmentation during compendium drafting, scheduling updates alongside writing tasks.

### E. Collaboration and Review Norms
- Note repository guidelines on academic tone, British English spelling, and structured headings; ensure contributions conform to these expectations throughout the compendium.[Ref1]
- Track configuration control practices, including run naming conventions, metadata requirements, and archival policies, to maintain auditability.[Ref16]
- Coordinate with mission analysis, operations, and systems engineering stakeholders to validate interpretations and secure timely reviews of draft chapters.[Ref5][Ref6][Ref7]
- Establish a shared progress tracker capturing literature searches, simulation reruns, and documentation updates to prevent duplication of effort.
- Schedule periodic sync meetings to discuss findings, resolve ambiguities, and align on next steps across teams.

## Evidence Citation Strategy
### Citation Principles
1. Use numbered references exactly as defined in the References section, ensuring each citation points to a configuration-controlled artefact or governance document.[Ref5]
2. When referencing simulation results, cite both the documentation summarising the analysis and the underlying artefact directory to reinforce provenance.[Ref11][Ref14][Ref18]
3. Distinguish between deterministic and statistical evidence by citing the appropriate JSON fields or CSV tables, clarifying whether metrics represent mean, percentile, or maximum values.[Ref14][Ref19]
4. For STK validation claims, include citations to the exporter module, validation guide, and relevant scenario metadata, documenting that interoperability has been confirmed.[Ref10][Ref21][Ref22]
5. Highlight configuration baselines by referencing YAML or JSON sources whenever parameters are quoted, supporting traceability during reviews.[Ref9][Ref10]

### Citation Workflow Checklist
- Maintain a master citation spreadsheet mapping references to repository paths, document locations, and usage notes to facilitate consistency across authors.
- Cross-check citations during peer review to ensure they remain accurate after revisions or new artefact generation.
- Update the References section whenever new artefacts or documents are introduced, keeping numbering stable or clearly documenting renumbering decisions.[Ref5]
- Include inline annotations for figures, tables, and equations specifying source files and line ranges where applicable to streamline verification.
- Encourage reviewers to flag ambiguous or missing citations, resolving issues before final publication.

## Chapter 1: Mission Framing, Literature Review Scope, and Requirement Baseline
### 1.1 Contextual Overview
Explain why a transient triangular formation over Tehran enables unique sensing geometries for civil resilience, grounding the description in the mission overview and project roadmap.[Ref2][Ref8] Summarise stakeholder needs from the Concept of Operations, emphasising command latency limits, delta-v budgets, and robustness envelopes that drive later analyses.[Ref6]

### 1.2 Mission Objectives and Requirement Translation
Detail how the mission intent stated in the README and mission requirements translates into the SRD taxonomy (SRD-F, SRD-P, SRD-O, SRD-R). Explicitly reference MR-1 through MR-7 and the derived SRD entries, noting verification pathways captured in the compliance matrix and verification plan.[Ref1][Ref3][Ref4][Ref5][Ref7]

### 1.3 Literature Review Directive
Construct a literature review plan covering three thematic pillars:
- **Formation-Flying Theory:** Canonical works on Relative Orbital Elements (ROE) and local-vertical local-horizontal (LVLH) frame analyses; highlight D'Amico et al. and contemporary studies relevant to 6 km separations.[Ref11]
- **Single-Station Command and Ground Segment Operations:** Research on commanding architectures meeting ≤12 h latency, drawing parallels with TMOC procedures and risk registers.[Ref6]
- **Delta-v Budgeting and Robustness:** Studies on maintaining formation geometry under J2 and drag perturbations with annual budgets ≤15 m/s, linking to maintenance evidence from `run_20251018_1207Z`.[Ref14]
For each pillar, specify publication years (2019–2025 focus), preferred journals or conference venues, and keywords to guide database searches.

### 1.4 Literature Gap Identification
Using the compliance matrix and verification plan, outline existing gaps where repository evidence requires scholarly reinforcement (e.g., command resilience beyond Kerman station, Monte Carlo dispersion methodologies, STK export assurance). Map each gap to the chapters where new citations must appear.[Ref5][Ref7][Ref21]

### 1.5 Figure, Table, and Equation Prompts (Chapter 1)
- **[Suggested Figure 1.1]** Conceptual schematic of the Tehran transient triangle showing centroid alignment and ±30 km/±70 km tolerance bands, adapted from mission overview narratives and formation metrics.[Ref2][Ref14]
- **[Suggested Table 1.1]** Mapping between MR identifiers, SRD derivatives, and governing evidence artefacts, leveraging the compliance matrix entries.[Ref3][Ref4][Ref5]
- **[Suggested Equation 1.1]** Present the great-circle distance formula used to evaluate centroid cross-track offsets, referencing its implementation within the triangle simulator.[Ref12]

### 1.6 Narrative Flow Guidance
Draft the chapter to progress from mission motivation through requirement translation into a literature strategy. Close with a synthesis that positions the subsequent configuration and geometry chapter as the bridge between theoretical insights and repository baselines.

### 1.7 Evidence Integration Checklist
- Confirm Figure 1.1 communicates the MR-2 tolerance structure with data derived from `triangle_summary.json`.
- Verify Table 1.1 lists MR-1 to MR-7 and SRD-F/SRD-P/SRD-O/SRD-R entries alongside evidence tags.[Ref3][Ref4][Ref5]
- Ensure Equation 1.1 cites the haversine distance usage within `sim/formation/triangle.py`.[Ref12]
- Reference the literature gaps using explicit MR/SRD identifiers and cite the compliance matrix or verification plan where the gaps originate.[Ref5][Ref7]
- State explicitly whether Chapter 1 introduces any STK export dependencies; if so, cite the exporter documentation.[Ref21]

### 1.8 Source Prioritisation Protocol
1. Catalogue mission-specific peer-reviewed papers published between 2019 and 2025, prioritising journals such as *Journal of Guidance, Control, and Dynamics*, *Acta Astronautica*, and *Advances in Space Research*; log digital object identifiers alongside relevance notes.[Ref11]
2. For each mission requirement, map at least two external references that demonstrate comparable performance envelopes (e.g., latency-limited command architectures, triangular imaging constellations) and record how these sources corroborate or challenge repository assumptions.[Ref3][Ref6]
3. Develop a hierarchy of evidence: (a) primary research articles, (b) agency handbooks or standards (NASA-STD-7009A, ECSS-E-ST-10-02C), (c) technical reports from missions with single-station commanding parallels, ensuring each selection contributes to the literature gap closure identified earlier.[Ref5][Ref7]
4. Flag legacy references (pre-2019) when newer studies are unavailable, providing justification and noting whether they remain foundational citations referenced by recent work; schedule targeted follow-ups to locate updated datasets or reanalyses.[Ref11]
5. Maintain a running bibliography in a collaborative reference manager (e.g., Zotero or Mendeley) with shared tags for MR alignment, STK interoperability, and robustness methodologies so that the research team can track coverage status in real time.[Ref5][Ref21]

### 1.9 Literature Extraction Log Template
- **Entry Metadata:** Date reviewed, reviewer initials, database or archive queried, search keywords used, and filters applied (year range, document type, mission class).
- **Relevance Summary:** Two to three sentences describing the paper's contribution to triangular formation theory, command architecture validation, or robustness modelling, explicitly linking back to MR/SRD identifiers.[Ref3][Ref4]
- **Quantitative Highlights:** Capture equations, parameter ranges, or empirical findings that could inform scenario updates (e.g., drag coefficients, RAAN drift rates, communication latency distributions) with page or figure references for rapid retrieval.[Ref11][Ref14]
- **Applicability Notes:** Indicate whether the source informs baseline assumptions, validation strategies, or risk mitigations; if the source conflicts with repository data, record the discrepancy and propose investigation actions.[Ref5][Ref7]
- **Follow-up Actions:** Document pending outreach (author correspondence, dataset requests), planned incorporation into specific chapters, and whether additional cross-checking with STK export practices or configuration baselines is required.[Ref9][Ref21]

- Confirm Figure 1.1 communicates the MR-2 tolerance structure with data derived from `triangle_summary.json`.
- Verify Table 1.1 lists MR-1 to MR-7 and SRD-F/SRD-P/SRD-O/SRD-R entries alongside evidence tags.[Ref3][Ref4][Ref5]
- Ensure Equation 1.1 cites the haversine distance usage within `sim/formation/triangle.py`.[Ref12]
- Reference the literature gaps using explicit MR/SRD identifiers and cite the compliance matrix or verification plan where the gaps originate.[Ref5][Ref7]
- State explicitly whether Chapter 1 introduces any STK export dependencies; if so, cite the exporter documentation.[Ref21]

### 1.10 Chapter 1 Drafting Prompts
- Describe how mission requirements cascade into SRD clauses using concrete examples and cite both documents to reinforce traceability.[Ref3][Ref4]
- Summarise the stakeholder motivations (civil protection, infrastructure resilience) and link them to the operational needs described in the ConOps.[Ref2][Ref6]
- Present a comparative overview of literature themes, noting where repository evidence already aligns with published findings and where new research is essential.[Ref5][Ref11]
- Highlight the geopolitical and geographic factors that make Tehran an ideal case study for transient triangular formations, referencing mission problem statements and access window requirements.[Ref2][Ref3]
- Explain how configuration control practices (run naming, metadata tracking) underpin the literature review's credibility by ensuring data provenance.[Ref16]
- Outline how Chapter 1 will introduce the reader to subsequent chapters, signalling where detailed configuration, simulation, and verification discussions will occur.
- Provide a closing paragraph template that reiterates the mission framing while previewing the technical depth of Chapter 2.

## Chapter 2: Configuration Baselines and Geometric Foundations
### 2.1 Repository Configuration Assets
Summarise the `config/project.yaml` metadata, highlighting global constants, platform assumptions, and maintenance strategy parameters that anchor modelling choices. Note version control conventions (semantic versioning, authoring team) and how these support configuration audits.[Ref9]

### 2.2 Scenario Definitions
Detail the Tehran triangle scenario JSON, including metadata flags for STK validation, formation side length, plane allocations, maintenance cadence, and Monte Carlo seeds. Emphasise how this configuration enforces the 6 km equilateral geometry and aligns with mission tolerances.[Ref10]

### 2.3 Relative Orbital Element Geometry
Describe how the simulator constructs offsets in the LVLH frame to achieve the equilateral triangle. Include references to the `_formation_offsets` function and the transformation into inertial coordinates.[Ref12]

### 2.4 Access Window and Ground Track Constraints
Connect the configuration parameters (ground tolerance, command range) to the requirement thresholds. Explain how these values propagate into command latency analyses and centroid distance checks within the simulation outputs.[Ref10][Ref12][Ref14]

### 2.5 Formation Plane Allocation
Illustrate how plane assignments (Plane A vs Plane B) are encoded and validated in the simulator outputs and unit tests. Cite the metrics dictionary from `triangle_summary.json` and the assertions in `test_triangle_formation.py` that confirm plane membership counts.[Ref12][Ref13][Ref14]

### 2.6 Figure, Table, and Equation Prompts (Chapter 2)
- **[Suggested Figure 2.1]** Flow diagram of configuration inheritance from `config/project.yaml` through scenario JSON to simulation inputs.[Ref9][Ref10]
- **[Suggested Figure 2.2]** LVLH offset illustration with labelled axes and magnitude annotations derived from `_formation_offsets` outputs.[Ref12]
- **[Suggested Table 2.1]** Extract of key configuration parameters (semi-major axis, inclination, side length, maintenance cadence, Monte Carlo dispersions) with source file references.[Ref9][Ref10]
- **[Suggested Equation 2.1]** Express the transformation from LVLH offsets to inertial coordinates, linking to the `_lvlh_frame` routine.[Ref12]

### 2.7 Narrative Flow Guidance
Structure the chapter to walk the reader from high-level project configuration to the specific geometry encoded in the triangle scenario. Highlight how each configuration layer ensures reproducibility and compliance traceability for later analyses.

### 2.8 Evidence Integration Checklist
- Document how scenario metadata asserts STK validation status and reference the exporter linkage.[Ref10][Ref21]
- Confirm Figure 2.1 references both YAML and JSON sources with correct versioning.[Ref9][Ref10]
- Ensure the plane allocation discussion cites both simulation metrics and unit test coverage.[Ref12][Ref13][Ref14]
- Validate Equation 2.1 is accompanied by textual interpretation of axis conventions.[Ref12]
- State the interplay between ground tolerance parameters and MR-2/MR-5 thresholds with explicit citations.[Ref3][Ref10]

### 2.9 Configuration Trace Log Blueprint
- **Baseline Record:** Include configuration filename, git commit hash, author, and modification date to maintain full traceability during audits.[Ref9]
- **Parameter Snapshot:** Capture all key numerical parameters (semi-major axis, inclination, side length, maintenance cadence, Monte Carlo dispersions) with units and tolerance notes for quick comparison across revisions.[Ref9][Ref10]
- **Dependency Map:** List downstream scripts, tests, and documentation sections that rely on each configuration item so that updates trigger appropriate regression suites and document refreshes.[Ref12][Ref20]
- **Validation Status:** Record whether each configuration has been exercised through simulation runs, STK export, and automated tests, noting evidence directories or logs that confirm successful execution.[Ref14][Ref21]
- **Change Impact Assessment:** For any proposed modification, outline affected mission requirements, anticipated shifts in metrics, and the plan for updating compliance artefacts to maintain alignment with SRD expectations.[Ref3][Ref4][Ref5]

### 2.10 Geometry Verification Workflow
1. Ingest the scenario JSON into a notebook or script that replays the `_formation_offsets` calculations, plotting LVLH coordinates to verify equilateral geometry before propagation.[Ref10][Ref12]
2. Propagate a short-duration inertial trajectory using the reference orbit to ensure offsets align with the expected centroid path and to detect any anomalies caused by epoch misalignment.[Ref12]
3. Compare the resulting inertial states with archived simulation outputs to confirm consistency across tool versions; document tolerance thresholds for acceptable deviations (e.g., ≤10⁻⁶ relative error in position vectors).[Ref12][Ref14]
4. Cross-check plane allocation outputs with unit tests and metrics dictionaries, verifying that plane membership remains stable even if satellite identifiers or ordering change between runs.[Ref13][Ref14]
5. Conclude with an STK spot-check by exporting the scenario and visually inspecting the formation geometry against repository screenshots or guidance, noting any import warnings that require exporter adjustments.[Ref21][Ref22]

- Document how scenario metadata asserts STK validation status and reference the exporter linkage.[Ref10][Ref21]
- Confirm Figure 2.1 references both YAML and JSON sources with correct versioning.[Ref9][Ref10]
- Ensure the plane allocation discussion cites both simulation metrics and unit test coverage.[Ref12][Ref13][Ref14]
- Validate Equation 2.1 is accompanied by textual interpretation of axis conventions.[Ref12]
- State the interplay between ground tolerance parameters and MR-2/MR-5 thresholds with explicit citations.[Ref3][Ref10]

### 2.11 Parameter Consistency Questions
1. Are all orbital parameters (semi-major axis, inclination, RAAN) consistent between `config/project.yaml`, scenario JSON files, and simulation outputs? Document any discrepancies and plan reconciliations.[Ref9][Ref10][Ref14]
2. Do maintenance cadence assumptions align with delta-v budgets and ConOps procedures? Provide evidence and note required adjustments if not.[Ref6][Ref14]
3. Are Monte Carlo dispersion values supported by verification activities or external literature? Identify justification gaps.[Ref7][Ref10]
4. How do plane allocations map to mission requirements and system requirements? Confirm numbering and naming conventions remain consistent across artefacts.[Ref3][Ref4][Ref14]
5. What configuration elements require special attention when extending the mission to alternative targets? Suggest parameter ranges or sensitivity tests.[Ref9][Ref10]
6. Which configuration items trigger mandatory STK export updates? Clarify notification and approval pathways.[Ref10][Ref21]
7. Draft reviewer questions that ensure configuration updates remain aligned with compliance commitments.

## Chapter 3: Simulation Pipeline, Toolchain, and Automation Harness
### 3.1 Pipeline Stage Overview
Detail the sequential stages executed by `sim/scripts/run_scenario.py`, including RAAN optimisation, node generation, phase synthesis, two-body propagation, high-fidelity propagation, metric extraction, and optional STK export. Reference logging statements or comments that clarify each stage's intent.[Ref12][Ref20]

### 3.2 RAAN Alignment Solver
Explain how the RAAN alignment routine evaluates candidate RAAN values, citing the deterministic results captured in `run_20251020_1900Z_tehran_daily_pass_locked`. Highlight the centroid cross-track metrics, pass fractions, and convergence criteria recorded in the summary JSON.[Ref18]

### 3.3 Triangle Simulation Workflow
Summarise the dedicated triangle runner, including its artefact outputs (summary JSON, maintenance CSV, command windows CSV, injection recovery CSV, drag dispersion CSV, STK directory). Outline how the script ensures STK compliance and how tests verify artefact presence.[Ref12][Ref14][Ref20]

### 3.4 Regression and Integration Testing
Document the integration tests that validate the scenario runner, CLI smoke tests, and triangle exporter outputs. Emphasise assertions on stage sequence order, Monte Carlo statistics, and artefact existence that guard against regressions.[Ref20]

### 3.5 Automation and Continuous Integration Hooks
Describe how Makefile targets and CI workflows exercise the simulation scripts, referencing README instructions and test scaffolding. Clarify naming conventions for runs (`run_YYYYMMDD_hhmmZ`) and the policy for archiving outputs under `artefacts/`.[Ref1][Ref18]

### 3.6 Figure, Table, and Equation Prompts (Chapter 3)
- **[Suggested Figure 3.1]** Stage sequence diagram showing the progression from RAAN alignment to STK export, annotated with script function names.[Ref20]
- **[Suggested Table 3.1]** Comparison of deterministic and Monte Carlo metrics extracted by the scenario runner (centroid offsets, worst-vehicle offsets, compliance fractions).[Ref18][Ref19]
- **[Suggested Figure 3.2]** Artefact generation tree for the triangle simulation, mapping outputs to file formats and downstream uses (maintenance, command latency, STK validation).[Ref12][Ref14]
- **[Suggested Equation 3.1]** Provide the Hill-Clohessy-Wiltshire relationship or equivalent propagation condition referenced in RAAN optimisation to explain how Δλ evolves with time (cite simulation code if implemented).[Ref12]

### 3.7 Narrative Flow Guidance
Weave the narrative to show how automation enforces reproducibility: start with the pipeline description, segue into solver mechanics, proceed to artefact generation, and conclude with test coverage and CI governance.

### 3.8 Evidence Integration Checklist
- Verify the RAAN alignment discussion references both deterministic and Monte Carlo JSON fields for compliance statements.[Ref18][Ref19]
- Confirm Figure 3.1 labels correspond to actual function names or logging stages from the script.[Ref20]
- Ensure Table 3.1 distinguishes between midpoint metrics and full-window statistics, clarifying relevance to MR-2 and SRD-P-001.[Ref3][Ref18][Ref19]
- Cite the integration tests that assert artefact presence after triangle simulation runs.[Ref20]
- State explicitly how STK export compliance is verified, referencing the exporter module and validation guide.[Ref21]

### 3.9 Automation Runbook Tasks
1. Document command-line invocations for each pipeline stage (`make scenario`, direct `python -m sim.scripts.run_scenario`, `python -m sim.scripts.run_triangle`) and capture expected console outputs to streamline onboarding for new analysts.[Ref1][Ref20]
2. Define environment preparation steps, including virtual environment activation, dependency verification, and dataset retention policies before executing high-fidelity runs.[Ref1]
3. Enumerate logging artefacts (log files, JSON summaries, CSV exports) generated at each stage, specifying naming conventions and directory structures to reduce search time during reviews.[Ref14][Ref18]
4. Establish a rerun protocol that dictates when to regenerate RAAN solutions, triangle simulations, or Monte Carlo sweeps following configuration updates or regression failures, referencing the authoritative run ledger for precedence.[Ref16]
5. Integrate CI hooks by outlining how GitHub Actions or comparable systems should invoke linting, unit tests, integration tests, and simulation smoke runs on pull requests, including notification pathways for failures.[Ref1][Ref20]

### 3.10 Artefact Quality Assurance Checklist
- **Schema Validation:** Verify JSON summaries comply with expected schemas (fields, types, units) and update schema documentation if new metrics are introduced.[Ref18]
- **CSV Integrity:** Inspect CSV headers for completeness and naming consistency, confirming presence of units and metric definitions to support downstream analytics.[Ref14]
- **Plot Fidelity:** When generating SVG figures (e.g., Monte Carlo CDF), confirm axis labelling, scaling, and legend clarity meet publication standards and embed metadata describing data provenance.[Ref14]
- **STK Package Review:** Check exported `.e`, `.sat`, `.gt`, and `.int` files for naming conformity, time span alignment, and absence of import errors using the validation guide, recording outcomes in the run directory README.[Ref21][Ref22]
- **Regression Artefact Archive:** Store logs and artefacts from automation runs under timestamped directories with checksum manifests so that reviewers can reproduce results long after execution.[Ref16][Ref21]

- Verify the RAAN alignment discussion references both deterministic and Monte Carlo JSON fields for compliance statements.[Ref18][Ref19]
- Confirm Figure 3.1 labels correspond to actual function names or logging stages from the script.[Ref20]
- Ensure Table 3.1 distinguishes between midpoint metrics and full-window statistics, clarifying relevance to MR-2 and SRD-P-001.[Ref3][Ref18][Ref19]
- Cite the integration tests that assert artefact presence after triangle simulation runs.[Ref20]
- State explicitly how STK export compliance is verified, referencing the exporter module and validation guide.[Ref21]

### 3.11 Simulation Log Interpretation Prompts
- Extract representative log entries for each pipeline stage (RAAN optimisation, phase generation, propagation) and explain how they confirm correct execution.[Ref20]
- Identify warning or info messages that analysts should monitor for regression detection, noting potential causes and remedies.[Ref20]
- Describe how to interpret JSON metric outputs in conjunction with log files to diagnose anomalies or confirm success criteria.[Ref18][Ref20]
- Suggest best practices for annotating log excerpts in documentation to aid reviewers unfamiliar with the automation framework.[Ref1]
- Provide guidance on correlating log timestamps with artefact generation times when assembling evidence packages.[Ref14][Ref18]
- Recommend archival practices for preserving critical log files, including compression, checksum generation, and metadata tagging.[Ref16][Ref21]

## Chapter 4: Authoritative Runs, Quantitative Evidence, and Statistical Findings
### 4.1 Run Ledger Interpretation
Summarise the authoritative run register, explaining the status of each listed run (baseline, locked, exploratory) and how it underpins compliance statements. Highlight `run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`, and the curated `artefacts/triangle_run` snapshot.[Ref16]

### 4.2 Tehran Triangle Metrics
Analyse the key metrics from `triangle_summary.json`: formation window duration, aspect ratio, side length, centroid ground distances, maintenance budgets, command latency, injection recovery success, and drag dispersion statistics. Connect each metric to the relevant mission requirements (MR-3 through MR-7).[Ref14]

### 4.3 Maintenance and Command Datasets
Describe the CSV artefacts (maintenance summary, command windows, injection recovery, drag dispersion) generated by the triangle run. Interpret mean and peak accelerations, annual delta-v per spacecraft, contact windows, and Monte Carlo outcomes. Link these data to operational planning and risk mitigation strategies outlined in the ConOps.[Ref6][Ref14]

### 4.4 Tehran Daily Pass Alignment Evidence
Present the deterministic and Monte Carlo findings from the locked Tehran daily pass run, including centroid and worst-vehicle cross-track metrics, pass fractions, RAAN values, and compliance probabilities. Relate these metrics to MR-2 and SRD-P-001 closure.[Ref17][Ref18][Ref19]

### 4.5 Exploratory Runs and Resampling Campaigns
Briefly document the purpose and limitations of exploratory runs (e.g., resampled daily pass), clarifying that they supplement but do not replace baseline evidence. Explain how these datasets can support sensitivity analyses or future work.[Ref16]

### 4.6 Figure, Table, and Equation Prompts (Chapter 4)
- **[Suggested Table 4.1]** Consolidated metrics from `triangle_summary.json`, listing window duration, aspect ratio, max/min ground distances, annual delta-v, command latency, and injection recovery statistics.[Ref14]
- **[Suggested Figure 4.1]** Cumulative distribution function (CDF) of Monte Carlo Δv requirements derived from `injection_recovery.csv` and the SVG plot.[Ref14]
- **[Suggested Table 4.2]** Deterministic vs Monte Carlo centroid offsets from the locked daily pass run, including mean, p95, and maximum values for centroid and worst-vehicle metrics.[Ref18][Ref19]
- **[Suggested Figure 4.2]** Timeline of command windows illustrating compliance with the 12-hour latency bound using `command_windows.csv` data.[Ref14]
- **[Suggested Equation 4.1]** Express the success probability calculation for Monte Carlo trials (e.g., success count divided by sample count) as implemented in the simulator.[Ref12]

### 4.7 Narrative Flow Guidance
Construct the chapter to move from the run ledger context to detailed analysis of the triangle run, followed by daily pass evidence, and concluding with interpretation of exploratory datasets. Reinforce requirement closure statements at each step.

### 4.8 Evidence Integration Checklist
- Ensure all metrics quoted from `triangle_summary.json` and CSV artefacts include precise numeric values and confidence intervals where applicable.[Ref14]
- Confirm Table 4.2 differentiates deterministic midpoint assessments from Monte Carlo percentiles.[Ref18][Ref19]
- Reference the compliance matrix entries that rely on these runs for MR-5 to MR-7 and SRD-P-001 closure.[Ref5]
- State how the run ledger signals configuration control status for each dataset.[Ref16]
- Include STK validation confirmations for artefacts exported in these runs, citing the exporter documentation or validation guide.[Ref21][Ref22]

### 4.9 Data Interpretation Playbook
1. For each key metric, articulate the associated requirement threshold, observed value, and margin, presenting them in tabular or narrative form with citations to both documentation and artefact sources.[Ref3][Ref5][Ref14]
2. When interpreting maintenance data, calculate weekly, monthly, and annual delta-v profiles to illustrate operational planning implications and identify potential propellant-saving strategies.[Ref6][Ref14]
3. For command latency analyses, cross-reference command windows with ConOps scenarios to confirm readiness for contingency operations and to highlight any required updates to ground segment playbooks.[Ref6][Ref15]
4. Summarise Monte Carlo findings by grouping statistics (mean, standard deviation, percentiles) and discussing how robustness results influence risk posture and verification planning.[Ref7][Ref14][Ref19]
5. Highlight anomalies or edge cases observed in the datasets (e.g., unusually high drag dispersion samples) and propose follow-up simulations or analysis enhancements to address them.[Ref14][Ref16]

### 4.10 Reporting Template Snippets
- **Metric Capsules:** Provide sample paragraphs for reporting key metrics, e.g., "The validated access window spans 96 s with a maximum centroid distance of 343.62 km, satisfying MR-3 with 53.62 km margin."[Ref3][Ref14]
- **Figure Captions:** Draft caption templates for Monte Carlo CDFs, command window timelines, and maintenance bar charts, incorporating references and interpretive statements for consistent publication quality.[Ref14]
- **Table Footnotes:** Outline footnote conventions explaining data sources, interpolation methods, and rounding schemes to preserve transparency when consolidating metrics.[Ref14][Ref18]
- **Risk Commentary:** Provide language templates linking data insights to risk mitigation actions (e.g., adjusting maintenance cadence) with references to ConOps risk tables and compliance notes.[Ref5][Ref6]
- **STK Validation Notes:** Supply standardised statements confirming that exported artefacts were imported without error into STK 11.2, specifying file sets and validation logs referenced in the run directory README.[Ref21][Ref22]

- Ensure all metrics quoted from `triangle_summary.json` and CSV artefacts include precise numeric values and confidence intervals where applicable.[Ref14]
- Confirm Table 4.2 differentiates deterministic midpoint assessments from Monte Carlo percentiles.[Ref18][Ref19]
- Reference the compliance matrix entries that rely on these runs for MR-5 to MR-7 and SRD-P-001 closure.[Ref5]
- State how the run ledger signals configuration control status for each dataset.[Ref16]
- Include STK validation confirmations for artefacts exported in these runs, citing the exporter documentation or validation guide.[Ref21][Ref22]

### 4.11 Evidence Packaging Workflow
1. Compile a checklist of artefacts required for submission to governance boards (SERB, CCB), including documentation, data files, and validation logs.[Ref5][Ref16]
2. Define folder structures for packaging triangle run and daily pass evidence, ensuring readability and alignment with repository conventions.[Ref14][Ref18]
3. Outline procedures for generating executive summaries or briefing slides, referencing metrics, figures, and tables specified in this prompt.[Ref5]
4. Specify how to capture reviewer feedback and integrate it into subsequent documentation updates or reruns.[Ref16]
5. Detail sign-off requirements for each artefact bundle, including responsible roles and approval thresholds.[Ref5]
6. Recommend a versioning strategy for evidence packages, highlighting how to track updates over time and maintain historical records.[Ref16]
7. Provide tips for communicating Monte Carlo and maintenance outcomes to non-technical stakeholders while preserving scientific rigour.[Ref6][Ref14]

## Chapter 5: STK Validation, Compliance Integration, and Traceability
### 5.1 STK Export Workflow
Summarise the capabilities and constraints of `tools/stk_export.py`, including state sample handling, ground track support, contact interval definitions, and identifier sanitisation. Highlight optional SciPy dependence and naming rules that prevent import errors.[Ref21]

### 5.2 Validation Procedures
Describe the steps outlined in the STK import guide for verifying exported packages: scenario loading, ephemeris attachment, contact report generation, and evidence capture. Stress the requirement to maintain validation logs for each run.[Ref22]

### 5.3 Compliance Matrix Linkages
Explain how STK-validated artefacts are cross-referenced in the compliance matrix, focusing on MR-2, MR-3, MR-5, SRD-P-001, and SRD-O-002. Detail how evidence tags map to run directories and documentation packages.[Ref5]

### 5.4 Regression Safeguards
Discuss tests guarding STK exports (unit and integration), including assertions about file creation, header content, and CLI success. Clarify how these tests underpin continuous integration confidence.[Ref20]

### 5.5 Traceability and Configuration Control
Elaborate on how run naming conventions, metadata blocks, and configuration versioning ensure bidirectional traceability between documentation, data products, and verification evidence. Reference the system requirements and verification plan discussions on configuration control.[Ref4][Ref7][Ref18]

### 5.6 Figure, Table, and Equation Prompts (Chapter 5)
- **[Suggested Figure 5.1]** STK validation workflow diagram mapping exporter outputs to STK objects (scenario, satellites, ground tracks, contacts).[Ref21][Ref22]
- **[Suggested Table 5.1]** Crosswalk between compliance matrix entries and STK artefacts, showing requirement IDs, evidence tags, run directories, and validation status.[Ref5][Ref21]
- **[Suggested Equation 5.1]** Provide the checksum or schema validation formula applied during export integrity checks (e.g., SHA-256 verification) if documented within the exporter or workflow.[Ref21]

### 5.7 Narrative Flow Guidance
Guide the reader through exporter functionality, validation procedures, and compliance integration, culminating in a discussion on traceability safeguards and configuration control practices.

### 5.8 Evidence Integration Checklist
- Verify Figure 5.1 indicates file extensions (.e, .sat, .gt, .int) and their linkage to STK entities.[Ref21][Ref22]
- Ensure Table 5.1 lists requirement IDs alongside evidence tags and run identifiers exactly as they appear in the compliance matrix.[Ref5]
- Cite regression tests that check STK export artefacts and summarise their assertions.[Ref20]
- Confirm narrative references the metadata `validated_against_stk_export` flag within scenario configurations.[Ref10]
- State the checksum or integrity-check practice referenced by the exporter configuration and explain its implementation.[Ref9][Ref21]

### 5.9 STK Review Session Agenda
1. **Preparation:** List required artefacts (scenario files, ephemerides, ground tracks, contact intervals, validation logs) and responsible attendees (mission analyst, ground segment representative, configuration manager).[Ref21][Ref22]
2. **Walkthrough:** Define step-by-step procedures for importing the package into STK, configuring animations, generating reports, and capturing evidence (screenshots, exported tables) for archival purposes.[Ref22]
3. **Findings Log:** Provide a template for recording observed discrepancies, resolution actions, and sign-off status, ensuring traceability to requirement IDs and run identifiers.[Ref5][Ref21]
4. **Follow-up Tasks:** Specify criteria for triggering reruns or exporter updates based on review outcomes, including deadlines and ownership.[Ref16][Ref21]
5. **Approval Record:** Describe how meeting minutes, decision logs, and validation artefacts should be archived within the configuration management system to preserve audit trails.[Ref5][Ref18]

### 5.10 Traceability Matrix Maintenance Steps
- Update the compliance matrix whenever STK validation status changes, ensuring cross-references to run identifiers remain current and consistent with repository directories.[Ref5][Ref16]
- Synchronise SRD and verification plan documents with new validation evidence, adjusting verification methods or completion criteria if exporter capabilities evolve.[Ref4][Ref7]
- Maintain hyperlinks or path references in all documentation to the specific artefact directories, avoiding generic descriptions that could cause ambiguity during audits.[Ref5][Ref18]
- Implement a review cadence (e.g., monthly) for verifying that archived STK packages remain accessible, uncorrupted, and documented with checksums consistent with exporter outputs.[Ref9][Ref21]
- Record configuration control board decisions affecting STK workflows and ensure the traceability matrix reflects approved waivers, deviations, or procedural updates.[Ref5][Ref18]

- Verify Figure 5.1 indicates file extensions (.e, .sat, .gt, .int) and their linkage to STK entities.[Ref21][Ref22]
- Ensure Table 5.1 lists requirement IDs alongside evidence tags and run identifiers exactly as they appear in the compliance matrix.[Ref5]
- Cite regression tests that check STK export artefacts and summarise their assertions.[Ref20]
- Confirm narrative references the metadata `validated_against_stk_export` flag within scenario configurations.[Ref10]
- State the checksum or integrity-check practice referenced by the exporter configuration and explain its implementation.[Ref9][Ref21]

### 5.11 Compliance Audit Questions
- Which requirements have the narrowest margins and require targeted monitoring during subsequent runs? Support answers with metrics and references.[Ref5][Ref14]
- Are there any requirements relying on provisional or exploratory evidence? Describe actions needed to elevate them to authoritative status.[Ref5][Ref16]
- How do STK validation outcomes influence compliance assertions, and what additional checks are necessary before major reviews?[Ref5][Ref21]
- What documentation or artefacts must be refreshed following configuration changes or new simulation results?[Ref5][Ref7]
- How should auditors verify the completeness of evidence packages, including run directories, logs, and validation notes?[Ref16][Ref21]
- What escalation pathways exist for unresolved compliance issues, and how should they be documented?[Ref5]
- Draft sample audit questions tailored to mission design, operations, and systems engineering reviewers.

## Chapter 6: Verification, Testing, and Future Work Trajectories
### 6.1 Verification Plan Alignment
Summarise the verification strategy, matrix, and milestone schedule defined in the V&V plan. Highlight requirement-to-method mappings, responsible teams, completion criteria, and upcoming milestones relevant to triangular formation analysis.[Ref7]

### 6.2 Test Coverage Assessment
Detail the scope of unit and integration tests covering formation metrics, scenario pipelines, and metric extraction. Identify gaps requiring future automation (e.g., baseline generation placeholder) and discuss planned mitigations.[Ref13][Ref20]

### 6.3 Roadmap Dependencies
Explain how project roadmap stages align with verification activities, including preparatory documentation, orbital architecture synthesis, perturbation analysis, and compliance dossiers.[Ref8]

### 6.4 Outstanding Evidence Actions
List pending or recurring evidence acquisitions (e.g., quarterly reruns, HIL tests, stakeholder workshops) indicated in the compliance matrix and V&V resource planning. Clarify how each action will be monitored and recorded.[Ref5][Ref7]

### 6.5 Future Research Directions
Identify research opportunities that extend beyond the current repository baseline, such as incorporating solar radiation pressure modelling, multi-station command architectures, or optical navigation augmentation. Tie each opportunity to the relevant mission requirements and roadmap stages.[Ref9][Ref11][Ref8]

### 6.6 Figure, Table, and Equation Prompts (Chapter 6)
- **[Suggested Table 6.1]** Matrix of requirements versus verification methods, responsible teams, and evidence artefacts, derived from the V&V plan.[Ref7]
- **[Suggested Figure 6.1]** Timeline of planned verification milestones (VRR, simulation campaigns, HIL tests, CDR, LRR) aligned with roadmap stages.[Ref7][Ref8]
- **[Suggested Table 6.2]** Test coverage summary listing unit and integration tests, objectives, and associated artefacts.[Ref13][Ref20]
- **[Suggested Equation 6.1]** Present a representative Monte Carlo statistical measure (e.g., P95 calculation) as applied in injection recovery analyses.[Ref12]

### 6.7 Narrative Flow Guidance
Frame the chapter to move from current verification posture through testing coverage, roadmap alignment, outstanding actions, and forward-looking research prospects. Ensure the closing section sets expectations for the concluding chapter.

### 6.8 Evidence Integration Checklist
- Confirm Table 6.1 mirrors requirement IDs and evidence artefacts as listed in the V&V plan.[Ref7]
- Verify Table 6.2 references the exact test module names and directories (unit vs integration).[Ref13][Ref20]
- Cite roadmap stage descriptions when aligning milestones with programme phases.[Ref8]
- State outstanding evidence actions with reference to compliance matrix notes or V&V resource requirements.[Ref5][Ref7]
- Include a discussion on future STK export enhancements or validation tasks aligned with research directions.[Ref21]

### 6.9 Verification Activity Tracker Template
- **Activity ID:** Structured identifier combining requirement, method, and campaign (e.g., MR3-ANL-2025Q1) for consistent logging.[Ref7]
- **Scope Definition:** Narrative describing objectives, assumptions, and success criteria, referencing roadmap stages and mission requirements.[Ref3][Ref8]
- **Execution Record:** Dates executed, personnel involved, tools used, and datasets generated, including links to artefacts and git commit hashes.[Ref7][Ref20]
- **Outcome Summary:** Pass/fail status, metrics achieved, anomalies encountered, and references to compliance matrix updates triggered by the activity.[Ref5]
- **Next Actions:** Follow-up tasks, retest schedules, or documentation updates required to close outstanding observations or extend coverage.[Ref7][Ref8]

### 6.10 Future Work Prioritisation Matrix
1. List potential enhancements (SRP modelling, multi-station operations, optical navigation, expanded Monte Carlo dispersions) and categorise them by strategic value, resource demand, and alignment with roadmap milestones.[Ref8][Ref11]
2. Evaluate dependencies for each enhancement, noting required data sources, tooling upgrades, and stakeholder approvals to prevent schedule conflicts.[Ref7]
3. Assign provisional timelines (near-term, mid-term, long-term) and responsible teams, referencing existing roadmap stages and verification campaigns.[Ref8]
4. Identify success metrics and verification methods for each future work item to ensure readiness for integration into compliance artefacts.[Ref5][Ref7]
5. Capture risk considerations (technical maturity, resource availability, external coordination) and propose mitigation strategies to maintain programme agility.[Ref6][Ref8]

- Confirm Table 6.1 mirrors requirement IDs and evidence artefacts as listed in the V&V plan.[Ref7]
- Verify Table 6.2 references the exact test module names and directories (unit vs integration).[Ref13][Ref20]
- Cite roadmap stage descriptions when aligning milestones with programme phases.[Ref8]
- State outstanding evidence actions with reference to compliance matrix notes or V&V resource requirements.[Ref5][Ref7]
- Include a discussion on future STK export enhancements or validation tasks aligned with research directions.[Ref21]

### 6.11 Test Expansion Ideas
- Propose additional unit tests to cover edge cases in triangle geometry calculations, including non-equilateral offsets or perturbed time steps.[Ref12][Ref13]
- Suggest integration tests that validate STK export integrity after configuration updates or toolchain modifications.[Ref20][Ref21]
- Recommend end-to-end regression scenarios combining RAAN optimisation, triangle simulation, and Monte Carlo sweeps to ensure holistic coverage.[Ref18][Ref20]
- Identify opportunities for hardware-in-the-loop or software-in-the-loop testing aligned with V&V milestones.[Ref7]
- Outline data-driven validation exercises using external ephemeris sources or third-party simulators to cross-check results.[Ref21]
- Provide a backlog of automation enhancements (parallel Monte Carlo execution, adaptive tolerances) that improve efficiency or fidelity.[Ref11][Ref12]
- Highlight documentation or tooling updates needed to support new tests, including schema changes or logging improvements.[Ref20]

## Chapter 7: Results Synthesis, Discussion, and Recommendations
### 7.1 Integrative Summary
Synthesize how the configuration baselines, simulation outputs, and verification evidence collectively demonstrate compliance with mission objectives. Reiterate the headline metrics (access duration, centroid alignment, delta-v consumption, command latency, robustness success rates) and their linkage to MR/SRD identifiers.[Ref3][Ref4][Ref14][Ref18]

### 7.2 Sensitivity and Risk Interpretation
Discuss the sensitivity of mission performance to perturbations (e.g., drag dispersion outcomes, RAAN alignment tolerance) and the risk mitigations documented in the ConOps and compliance matrix. Highlight how the evidence supports decision-making for operations and contingency planning.[Ref5][Ref6][Ref14][Ref18]

### 7.3 Comparative Evaluation
Compare the Tehran triangle architecture with alternative mid-latitude target concepts using the global configuration options, noting how adjustments in latitude or ground tolerance may affect access windows and maintenance loads.[Ref9][Ref14]

### 7.4 Policy and Operational Recommendations
Formulate actionable recommendations for command cadence, maintenance scheduling, data handling, and validation cadence. Tie each recommendation to evidence from the run artefacts and governance documents (compliance matrix, V&V plan, ConOps).[Ref5][Ref6][Ref7][Ref14]

### 7.5 Future Work Roadmap
Outline concrete next steps such as incorporating SRP in simulations, expanding Monte Carlo dispersions, or executing hardware-in-the-loop tests. Clarify how these actions map onto roadmap stages and resource plans.[Ref7][Ref8][Ref11]

### 7.6 Figure, Table, and Equation Prompts (Chapter 7)
- **[Suggested Table 7.1]** Summary of achieved versus required performance metrics (duration, geometry, latency, delta-v, robustness) with requirement identifiers and evidence citations.[Ref3][Ref4][Ref14][Ref18]
- **[Suggested Figure 7.1]** Radar chart comparing metric margins (e.g., delta-v reserve, command latency margin, centroid tolerance margin).[Ref14][Ref18]
- **[Suggested Table 7.2]** Risk-to-mitigation mapping synthesising ConOps and compliance matrix insights.[Ref5][Ref6]
- **[Suggested Equation 7.1]** Provide the formula for margin calculation (e.g., margin = limit − observed value) used when discussing compliance headroom.[Ref14]

### 7.7 Narrative Flow Guidance
Arrange the chapter to open with a holistic synthesis, transition into risk interpretation and comparative analysis, deliver recommendations, and conclude with future work commitments that segue into the overall conclusion of the compendium.

### 7.8 Evidence Integration Checklist
- Ensure Table 7.1 references exact numeric values for each performance metric and includes requirement identifiers.[Ref3][Ref4][Ref14]
- Confirm recommendations cite the governing documents or artefacts that justify them.[Ref5][Ref6][Ref7][Ref14]
- Reference sensitivity analyses with explicit mention of drag dispersion or RAAN alignment findings.[Ref14][Ref18]
- State how the proposed future work aligns with roadmap milestones and verification activities.[Ref7][Ref8]
- Include a note on maintaining STK validation currency as part of the recommendations.[Ref21][Ref22]

### 7.9 Discussion Facilitation Notes
1. Prepare a cross-functional workshop agenda that allocates time for mission analysis, operations, and systems engineering teams to interpret results collaboratively, ensuring all perspectives on risk and opportunity are captured.[Ref5][Ref6]
2. Develop a question bank focusing on geometry robustness, command resilience, maintenance sustainability, and stakeholder impacts to stimulate critical evaluation of findings.[Ref3][Ref6][Ref14]
3. Document consensus points and dissenting opinions, linking each to specific evidence artefacts or requirements; highlight any decisions requiring CCB or SERB escalation.[Ref5][Ref18]
4. Create an action register summarising agreed recommendations, responsible owners, deadlines, and verification follow-ups, ensuring traceability to roadmap milestones.[Ref7][Ref8]
5. Capture lessons learned regarding data presentation, simulation reproducibility, and stakeholder communication for inclusion in future updates to the ConOps or V&V plan.[Ref6][Ref7]

### 7.10 Recommendation Implementation Checklist
- Translate each recommendation into discrete implementation tasks with required artefacts, approvals, and success metrics clearly defined.[Ref5][Ref7]
- Verify that operational adjustments (e.g., command cadence changes) are reflected in ConOps procedures and ground segment training materials.[Ref6]
- Update compliance matrix notes to acknowledge accepted recommendations and track their effect on requirement margins.[Ref5]
- Schedule verification activities to validate the impact of implemented recommendations, updating the V&V plan accordingly.[Ref7]
- Ensure STK validation packages are regenerated or re-reviewed when recommendations alter geometry, command profiles, or maintenance strategies.[Ref21][Ref22]

- Ensure Table 7.1 references exact numeric values for each performance metric and includes requirement identifiers.[Ref3][Ref4][Ref14]
- Confirm recommendations cite the governing documents or artefacts that justify them.[Ref5][Ref6][Ref7][Ref14]
- Reference sensitivity analyses with explicit mention of drag dispersion or RAAN alignment findings.[Ref14][Ref18]
- State how the proposed future work aligns with roadmap milestones and verification activities.[Ref7][Ref8]
- Include a note on maintaining STK validation currency as part of the recommendations.[Ref21][Ref22]

### 7.11 Executive Summary Cue Sheet
- Summarise headline achievements (geometry compliance, command responsiveness, robustness success) with explicit margins and citations.[Ref3][Ref5][Ref14]
- Articulate remaining risks or open actions, referencing drag dispersion findings, exploratory runs, or pending verification tasks.[Ref5][Ref16]
- Highlight stakeholder benefits and operational readiness indicators derived from ConOps and V&V plans.[Ref6][Ref7]
- Provide closing statements that reinforce confidence in STK interoperability and data provenance.[Ref21]
- Include a call-to-action outlining immediate next steps (e.g., schedule rerun, prepare review package) with assigned owners.[Ref7][Ref16]
- Offer optional messaging for public-facing summaries, adjusting technical depth while preserving accuracy.

## Chapter 8: Conclusion and Dissemination Plan
### 8.1 Executive Conclusion Template
Provide guidance for drafting the concluding section of the compendium, emphasising how to restate mission objectives, evidence-backed compliance statements, and strategic next steps. Encourage explicit mention of run identifiers and configuration baselines to maintain auditability.[Ref1][Ref16]

### 8.2 Dissemination and Stakeholder Engagement
Outline the dissemination plan for the final dossier, including SERB reviews, CCB briefings, stakeholder workshops, and archival procedures within the configuration management system. Link each engagement to relevant documentation or roadmap milestones.[Ref5][Ref7][Ref8]

### 8.3 Data and Artefact Archiving Protocols
Describe how final datasets, STK packages, and narrative chapters should be archived under the `artefacts/` directory, noting checksum practices, metadata requirements, and retention policies. Reference exporter documentation and project configuration for integrity controls.[Ref9][Ref21]

### 8.4 Figure, Table, and Equation Prompts (Chapter 8)
- **[Suggested Figure 8.1]** Stakeholder communication cascade chart illustrating review stages from internal teams to external partners.[Ref5][Ref7]
- **[Suggested Table 8.1]** Archiving checklist enumerating required artefacts (reports, STK exports, CSVs, validation logs) with storage locations and responsible owners.[Ref9][Ref21]
- **[Suggested Equation 8.1]** Present a checksum verification expression (e.g., SHA-256 digest comparison) to be reported when archiving data packages.[Ref21]

### 8.5 Narrative Flow Guidance
Conclude the compendium by guiding authors on crafting a concise executive summary, describing dissemination steps, and confirming archival compliance, ensuring the final paragraphs reinforce the mission's readiness trajectory.

### 8.6 Evidence Integration Checklist
- Confirm Figure 8.1 labels each stakeholder group and references the associated governance document (SERB, CCB, stakeholder workshops).[Ref5][Ref7][Ref8]
- Ensure Table 8.1 specifies storage paths and retention periods consistent with project configuration.[Ref9]
- State the checksum procedure and how it will be logged during archiving.[Ref21]
- Reference configuration control practices that govern dissemination approvals.[Ref5][Ref18]
- Mention how dissemination artefacts maintain STK validation traceability for downstream reviewers.[Ref21][Ref22]

### 8.7 Dissemination Schedule Template
- **Milestone Name:** Identify dissemination checkpoints (SERB briefing, CCB decision session, stakeholder workshop, archival release) with target dates and responsible coordinators.[Ref5][Ref7][Ref8]
- **Inputs Required:** List documents, artefacts, and validation evidence needed for each checkpoint, including run identifiers and checksum manifests.[Ref16][Ref21]
- **Review Outcomes:** Capture approval status, action items, and follow-up tasks, referencing configuration control records for transparency.[Ref5][Ref18]
- **Communication Channels:** Specify how outcomes will be communicated (meeting minutes, dashboards, controlled repositories) and who must acknowledge receipt.[Ref5]
- **Archival Actions:** Detail where final materials will be stored, retention durations, and verification logs required to confirm STK package integrity post-dissemination.[Ref9][Ref21]

### 8.8 Archival Quality Gate Checklist
1. Validate that each artefact bundle includes README files summarising contents, provenance, and validation status, along with contact points for future queries.[Ref16]
2. Run checksum verification for all exported files and document results in an auditable log stored alongside the artefact bundle.[Ref21]
3. Confirm metadata files capture mission configuration details (scenario names, run IDs, tool versions) and reference relevant documentation sections.[Ref9][Ref21]
4. Ensure archival directories are access-controlled and replicated according to data retention policies, with periodic integrity checks scheduled.[Ref9]
5. Record archival completion in the configuration management system, linking to dissemination records and ensuring traceability for audits or future reuse.[Ref5][Ref18]

- Confirm Figure 8.1 labels each stakeholder group and references the associated governance document (SERB, CCB, stakeholder workshops).[Ref5][Ref7][Ref8]
- Ensure Table 8.1 specifies storage paths and retention periods consistent with project configuration.[Ref9]
- State the checksum procedure and how it will be logged during archiving.[Ref21]
- Reference configuration control practices that govern dissemination approvals.[Ref5][Ref18]
- Mention how dissemination artefacts maintain STK validation traceability for downstream reviewers.[Ref21][Ref22]

## Stakeholder Communication Templates
### Briefing Packet Components
- Executive summary slide capturing mission objectives, current compliance status, and next milestones with cited evidence.[Ref5][Ref7]
- Metric dashboard highlighting access window performance, geometry fidelity, command latency, and delta-v consumption using data from authoritative runs.[Ref14][Ref18]
- Risk overview summarising top operational and technical risks, mitigations, and residual concerns aligned with ConOps and compliance documentation.[Ref5][Ref6]
- Action tracker table documenting outstanding tasks, owners, deadlines, and dependency notes to maintain programme momentum.[Ref7][Ref16]
- Appendix section linking to full artefact directories, validation logs, and supplementary analyses for reviewers seeking deeper context.[Ref14][Ref21]

### Communication Cadence
1. Schedule monthly mission status briefings to update stakeholders on progress, highlighting new evidence, configuration changes, and verification outcomes.[Ref5][Ref7]
2. Issue fortnightly written updates summarising completed tasks, upcoming activities, and any blockers requiring leadership intervention.
3. Coordinate ad-hoc sessions following significant simulation reruns or compliance changes to ensure decision-makers remain informed.[Ref16]
4. Maintain a persistent knowledge base (e.g., shared documentation portal) aggregating briefing materials, meeting minutes, and action registers for transparency.
5. Capture feedback promptly, integrating insights into documentation revisions, simulation adjustments, or verification plans as necessary.[Ref6][Ref7]

## Risk Register Update Workflow
- Review simulation outputs and operational scenarios to detect emerging risks or shifts in probability/impact assessments.[Ref6][Ref14]
- Update risk entries with new evidence, mitigation status, and responsible owners, ensuring consistency with ConOps risk tables and compliance notes.[Ref5][Ref6]
- Flag high-priority risks to the Configuration Control Board and SERB, documenting decisions, waivers, or additional analysis requests.[Ref5][Ref16]
- Align risk updates with verification planning by identifying tests or analyses required to reduce uncertainty or demonstrate mitigation effectiveness.[Ref7]
- Archive historical risk register versions to support trend analysis and lessons learned reviews, noting key changes and outcomes.

## Cross-Chapter Integration Tasks
### Integration Matrix Instructions
1. Build a matrix that maps each mission requirement and SRD clause to the chapter sections addressing it, ensuring no requirement lacks coverage.[Ref3][Ref4][Ref5]
2. Include columns referencing specific artefacts, figures, tables, and equations to reinforce traceability and support rapid verification during reviews.[Ref14][Ref18]
3. Highlight dependencies between chapters (e.g., Chapter 2 configuration values informing Chapter 3 simulations) and note where cross-references should be inserted in the narrative.
4. Identify potential redundancies or gaps, scheduling collaborative editing sessions to harmonise overlapping content or fill missing analyses.
5. Update the matrix whenever new evidence is introduced or existing artefacts are superseded, logging version history for audit purposes.[Ref16]

### Reviewer Coordination Checklist
- Assign chapter leads responsible for maintaining accuracy, coherence, and timeliness of content updates.
- Define peer review pairings across disciplines (mission analysis, operations, systems engineering) to encourage holistic critique.[Ref5][Ref6][Ref7]
- Establish deadlines for draft submissions, review cycles, and final approvals, integrating them with roadmap and verification milestones.[Ref7][Ref8]
- Document review comments in a central repository, linking each observation to the affected chapter and requirement.
- Track resolution status for every comment, ensuring no actionable feedback is left unaddressed before publication.

## Peer Review and Quality Assurance Plan
### Quality Gates
1. **Content Review:** Verify technical accuracy, completeness, and alignment with mission requirements using subject-matter expert reviews for each chapter.[Ref3][Ref6]
2. **Citation Audit:** Confirm all references are present, correct, and consistently formatted; ensure citations directly support the statements they accompany.[Ref5]
3. **Style Compliance:** Check adherence to British English spelling, heading hierarchy, and academic tone as mandated by repository guidelines.[Ref1]
4. **Artefact Verification:** Validate that referenced datasets, plots, and exports exist, are accessible, and include necessary metadata or validation logs.[Ref14][Ref21]
5. **Configuration Control:** Confirm updates are captured in version control with descriptive commit messages and cross-referenced in configuration management records.[Ref16]

### Review Cycle Plan
- **Draft Stage:** Conduct initial reviews focusing on structural completeness, ensuring each chapter addresses its prescribed subsections and prompts.
- **Technical Validation Stage:** Engage technical reviewers to scrutinise calculations, interpretations, and compliance assertions against artefacts.[Ref5][Ref14]
- **Editorial Stage:** Refine clarity, flow, and consistency across chapters, aligning terminology and notation.
- **Final Approval Stage:** Present the integrated dossier to governance boards (SERB, CCB) for endorsement, capturing decisions and action items.[Ref5]
- **Post-Publication Assessment:** Schedule retrospectives to evaluate review effectiveness, capture lessons learned, and update processes for future iterations.

## Appendices Guidance (Optional Inclusion)
If the final dossier requires appendices, recommend the following:
- **Appendix A:** Detailed configuration listings extracted from YAML and JSON sources with schema annotations.[Ref9][Ref10]
- **Appendix B:** Full test logs and CI outputs demonstrating regression results for scenario and triangle scripts.[Ref20]
- **Appendix C:** Expanded Monte Carlo datasets (centroid, worst-vehicle, drag dispersion) with statistical summaries.[Ref14][Ref19]
- **Appendix D:** STK validation screenshots and logs produced using the official import guide.[Ref22]

Each appendix must include its own references back to the main body and indicate whether the content is configuration-controlled or informational.

### 8.9 Final Submission Checklist
1. Verify all chapters include required figures, tables, equations, and checklists, noting any intentional deviations approved by governance bodies.[Ref5]
2. Ensure references are up to date, correctly numbered, and reflected in inline citations throughout the compendium.[Ref5]
3. Confirm all cited artefacts exist in the repository with accessible paths, current metadata, and validated checksums.[Ref16][Ref21]
4. Perform a final STK validation spot-check on representative artefacts to confirm compatibility post-compilation.[Ref21][Ref22]
5. Archive draft and final versions in accordance with configuration management policy, documenting version history and reviewer acknowledgements.[Ref5][Ref18]
6. Prepare a distribution cover letter or release note summarising contents, intended audience, and requested actions.[Ref5]
7. Schedule post-publication retrospectives to gather lessons learned and inform future iterations of the mission dossier.[Ref7]

## Change Management Sign-off Checklist
- Confirm proposed changes align with mission objectives and do not conflict with established requirements or compliance commitments; document rationale and expected benefits.[Ref3][Ref5]
- Assess impact on simulations, artefacts, and documentation, listing required reruns, updates, or regression tests.[Ref14][Ref16][Ref20]
- Secure approvals from relevant authorities (mission design lead, operations lead, configuration manager) and record decisions in configuration control logs.[Ref5][Ref16]
- Schedule and execute necessary validations (STK import checks, metric comparisons, test suites) prior to merging or publishing updates.[Ref21][Ref22]
- Communicate changes to all stakeholders through established channels, referencing updated artefacts and documentation sections to minimise confusion.[Ref6][Ref7]

## Collaboration Tools and Version Control Practices
### Workflow Coordination
- Utilise issue trackers to log tasks stemming from literature reviews, simulation reruns, and documentation updates, linking each issue to relevant chapters and artefacts.[Ref16]
- Adopt feature branches for substantial updates, ensuring commits are logically scoped and reference the objectives addressed (e.g., MR alignment, STK validation enhancements).[Ref16]
- Conduct pull request reviews with checklists verifying documentation updates, artefact regeneration, and test execution prior to merging.[Ref5][Ref20]
- Schedule regular sprint reviews or stand-ups to synchronise progress across multidisciplinary teams, identifying blockers early.[Ref6][Ref7]
- Archive decision logs and meeting minutes alongside pull requests to preserve context for future audits and onboarding.

### Documentation Integration
1. Embed change logs within key documents (mission requirements, compliance matrix, verification plan) summarising updates, rationale, and reviewers.[Ref3][Ref5][Ref7]
2. Maintain a central index of documentation files with version numbers, last update dates, and responsible authors to streamline review assignments.[Ref2][Ref6]
3. Use consistent Markdown conventions for headings, tables, and equations to facilitate automated processing and ensure readability.[Ref1]
4. Record cross-references between documents (e.g., ConOps to V&V plan) to guide readers and maintain traceability.[Ref6][Ref7]
5. Leverage templates or snippets for recurring content (checklists, figure captions, recommendation summaries) to promote uniformity across chapters.

## Data Management and Security Considerations
### Data Governance
- Enumerate data retention policies for simulation outputs, documentation drafts, and validation logs, ensuring compliance with the repository's one-year minimum retention guideline.[Ref9][Ref16]
- Define access controls for sensitive directories (artefacts, configuration files) and document approval workflows for granting or revoking access.[Ref5][Ref18]
- Specify encryption or secure transfer protocols when sharing artefacts externally, referencing organisational cybersecurity standards where applicable.[Ref6]
- Outline backup schedules and storage redundancies to protect against data loss, noting responsibility assignments for monitoring integrity checks.
- Document incident response steps for data breaches or corruption events, including escalation contacts and containment actions.

### Data Quality Assurance
1. Establish naming conventions for newly generated artefacts, aligning with `run_YYYYMMDD_hhmmZ` patterns and including scenario identifiers where relevant.[Ref16]
2. Require checksum generation for all exported datasets, storing hashes alongside artefacts and verifying them during audits.[Ref21]
3. Maintain metadata manifests capturing tool versions, configuration hashes, and environmental variables to support reproducibility.[Ref9][Ref12]
4. Implement peer review for data transformations (e.g., filtering, interpolation) to avoid inadvertent distortions of key metrics.[Ref14]
5. Schedule periodic data audits to confirm legacy artefacts remain accessible and free from bit rot or format obsolescence.

## Publication Timeline and Deliverables
- **Week 1:** Complete literature review scaffolding, compile initial configuration summaries, and populate integration matrix skeleton.[Ref3][Ref5][Ref16]
- **Week 2:** Draft Chapters 1–3 with preliminary figures and tables, conduct internal reviews focused on structural completeness and citation accuracy.[Ref2][Ref3][Ref9]
- **Week 3:** Finalise data interpretation for authoritative runs, integrate results into Chapters 4–5, and update compliance cross-references.[Ref5][Ref14][Ref18]
- **Week 4:** Address verification and future work discussions in Chapters 6–7, aligning recommendations with roadmap milestones and outstanding actions.[Ref7][Ref8]
- **Week 5:** Prepare conclusion, dissemination plan, appendices, and glossary; execute full peer review and quality assurance cycle.[Ref5][Ref6]
- **Week 6:** Finalise artefact packaging, archive datasets, and submit the dossier to governance boards with supporting evidence logs.[Ref16][Ref21]

## Documentation Sign-off Summary
- Prepare a consolidated table listing each chapter, responsible author, peer reviewer, and approval status, updating it as reviews progress.[Ref5]
- Include columns for key artefacts referenced, verification of citation completeness, and confirmation that figures/tables/equations are prepared.[Ref14][Ref18]
- Record the date of final approval and any conditions or follow-up tasks imposed by reviewers or governance boards.[Ref5][Ref16]
- Archive the sign-off table within the repository alongside the final dossier to support audit readiness and historical traceability.
- Update the table after publication to reflect post-release actions or errata, if applicable.

## Glossary Development Guidelines
- Compile a glossary of mission-specific terminology (e.g., RAAN, LVLH, centroid cross-track, maintenance cadence, Monte Carlo dispersion) to support interdisciplinary readers; provide concise definitions and cite authoritative sources.[Ref3][Ref11]
- Include acronyms for organisations, facilities, and tools (TMOC, SERB, CCB, STK) with brief descriptions of their roles within the mission architecture.[Ref5][Ref6][Ref21]
- Reference the documentation section or artefact where each term is first introduced, ensuring readers can locate detailed explanations quickly.[Ref2][Ref6][Ref11]
- Update the glossary whenever new terminology appears in later chapters or appendices, maintaining alphabetical order and consistency in formatting.
- Consider adding pronunciation or translation notes if specialised terms may be unfamiliar to stakeholders or external reviewers.

## Metrics Calculation Notebook Outline
1. **Notebook Setup:** Describe environment configuration, required libraries, and data-loading procedures for analysing triangle and daily pass artefacts.[Ref12][Ref14][Ref18]
2. **Data Ingestion Cells:** Provide code snippets or pseudocode for reading JSON summaries, CSV tables, and STK exports into analysis data frames, ensuring schema validation steps are included.[Ref14][Ref18][Ref21]
3. **Metric Reproduction:** Outline computations for key metrics (access duration, centroid offset, delta-v, command latency, success rates) to verify published values and facilitate sensitivity studies.[Ref14][Ref19]
4. **Visualisation Recipes:** Suggest plotting routines (time-series, histograms, CDFs, radar charts) that align with figures proposed in the prompt, embedding citation notes for each plot.[Ref14][Ref18]
5. **Reporting Automation:** Demonstrate how to export tables or figures directly into documentation-ready formats (Markdown, CSV, SVG) to streamline chapter production and maintain consistency.[Ref14][Ref21]
6. **Validation Hooks:** Include assertions comparing computed metrics against expected tolerances, flagging deviations and logging results for regression tracking.[Ref13][Ref14]
7. **Extension Paths:** Recommend ways to integrate additional datasets (e.g., new Monte Carlo runs, alternative target scenarios) while preserving notebook modularity and reproducibility.[Ref10][Ref16]

## Final Author Checklist
- Re-read the entire dossier for narrative coherence, ensuring transitions between chapters follow the flow prescribed in this prompt.[Ref2][Ref5]
- Confirm all figures, tables, and equations are generated or scheduled for production, with data sources validated and cited.[Ref14][Ref18]
- Validate that appendices, glossary, and supplementary materials are consistent with main body content and properly cross-referenced.[Ref2][Ref6][Ref11]
- Perform a final spell-check and style review to maintain British English usage and repository formatting standards.[Ref1]
- Prepare distribution emails or portal announcements summarising key outcomes and providing download links to the dossier and artefact packages.[Ref5][Ref7]
- Log completion in the project tracker, noting any deferred actions or planned updates for future increments.

## References
- [Ref1] `README.md`, Formation-Sat Systems Team, 2024.
- [Ref2] `docs/project_overview.md`, Formation-Sat Systems Team, 2024.
- [Ref3] `docs/mission_requirements.md`, Formation-Sat Systems Team, 2024.
- [Ref4] `docs/system_requirements.md`, Formation-Sat Systems Team, 2024.
- [Ref5] `docs/compliance_matrix.md`, Formation-Sat Systems Team, 2024.
- [Ref6] `docs/concept_of_operations.md`, Formation-Sat Systems Team, 2024.
- [Ref7] `docs/verification_plan.md`, Formation-Sat Systems Team, 2024.
- [Ref8] `docs/project_roadmap.md`, Formation-Sat Systems Team, 2024.
- [Ref9] `config/project.yaml`, Formation-Sat Systems Team, 2024.
- [Ref10] `config/scenarios/tehran_triangle.json`, Formation-Sat Systems Team, 2024.
- [Ref11] `docs/triangle_formation_results.md`, Formation-Sat Systems Team, 2025.
- [Ref12] `sim/formation/triangle.py`, Formation-Sat Systems Team, 2025.
- [Ref13] `tests/unit/test_triangle_formation.py`, Formation-Sat Systems Team, 2025.
- [Ref14] `artefacts/run_20251018_1207Z/triangle_summary.json`, Formation-Sat Systems Team, 2025.
- [Ref15] `artefacts/run_20251018_1207Z/command_windows.csv`, Formation-Sat Systems Team, 2025.
- [Ref16] `docs/_authoritative_runs.md`, Formation-Sat Systems Team, 2025.
- [Ref17] `docs/tehran_daily_pass_scenario.md`, Formation-Sat Systems Team, 2025.
- [Ref18] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json`, Formation-Sat Systems Team, 2025.
- [Ref19] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`, Formation-Sat Systems Team, 2025.
- [Ref20] `tests/integration/test_simulation_scripts.py`, Formation-Sat Systems Team, 2025.
- [Ref21] `tools/stk_export.py`, Formation-Sat Systems Team, 2025.
- [Ref22] `docs/how_to_import_tehran_daily_pass_into_stk.md`, Formation-Sat Systems Team, 2025.
