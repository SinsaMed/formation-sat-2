# Mission design project on “Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over Tehran”

## Global Mandates / Preface

Before drafting any chapter, review the entire repository tree—`docs/`, `config/`, `sim/`, `src/`, `tests/`, and `artefacts/`—so that every instruction issued below is grounded in the actual assets. Confirm that Systems Tool Kit (STK 11.2) interoperability requirements, test harness coverage, and configuration baselines remain unchanged since the last evidence acquisition; log any deviations for Configuration Control Board (CCB) review prior to writing.

- **Chapter framing.** Every major section must adopt the exact heading pattern `## Chapter X – Title`, where `X` is the sequential chapter number used throughout the document. Under each chapter heading, produce the five mandatory subsections listed below, retaining the numeric prefixes so reviewers can trace material unambiguously:
  1. `### X.1 Objectives and Success Criteria` – restate mission drivers, stakeholder expectations, and the compliance thresholds that the chapter addresses.
  2. `### X.2 Inputs and Assumptions` – catalogue all configuration files, simulation runs, datasets, and literature sources consumed by the chapter, referencing the Evidence Catalogue table mandated in Section “Evidence Catalogue Overview”.
  3. `### X.3 Methods and Toolchain` – describe analytical techniques, software modules, and validation workflows (including `tools/stk_export.py` checks) employed to transform the inputs.
  4. `### X.4 Results and Interpretation` – present quantitative outcomes, sensitivity narratives, and limitations; explicitly identify which artefacts substantiate each claim.
  5. `### X.5 Compliance and Forward Actions` – interpret how the results satisfy or challenge Mission Requirements (MR) and System Requirements (SRD) items, and specify any follow-on actions to be raised with the SERB/CCB.

- **Narrative discipline.** Within each subsection, follow the pattern *Context → Evidence → Discussion → Conclusions* so that reviewers can reconstruct analytical logic without consulting external notes.
- **Standards acknowledgement.** Reference applicable standards (ISO/IEC 23555-1:2022, ESA-GSOP-OPS-MAN-001, ASTM or ISO derivatives) when defining methods or evidence acceptance criteria.

## Project Overview

Before drafting the report, restate the mission title exactly as above and confirm that the engineering discipline is **Aerospace Engineering** with a focus on distributed Earth observation formations. Summarise the project goal using `docs/project_overview.md` and `docs/mission_requirements.md`, explaining that the aim is to deliver a repeatable 90 s equilateral imaging opportunity above Tehran while maintaining compliance with MR-1 through MR-7 plus the added communications and payload mandates. Define the problem statement by drawing on `docs/concept_of_operations.md` and `docs/triangle_formation_results.md`, highlighting the challenge of sustaining transient triangular geometry, daily access, and resilient downlink capacity over a complex megacity.

Justify the project’s significance through references to Tehran’s environmental, seismic, and socio-technical pressures as captured in `docs/tehran_daily_pass_scenario.md` and `docs/tehran_triangle_walkthrough.md`. Detail the mission benefits—improved situational awareness, responsive environmental monitoring, and regional risk mitigation—and identify stakeholders who rely on the constellation. Provide a catalogue of “raw materials” that mirrors the repository assets: configuration baselines (`config/project.yaml`, `config/scenarios/tehran_daily_pass.yaml`), simulation scripts (`sim/scripts/run_scenario.py`, `sim/scripts/run_triangle.py`, `run.py`, `run_debug.py`), analysis notebooks or reports under `docs/`, authoritative artefacts (`artefacts/run_20251018_1207Z/` etc.), and validation tooling such as `tools/stk_export.py`. Note the provenance and parameter ranges of each asset so Chapter 2 can treat them as experimental inputs.

## Evidence Catalogue Overview

Construct and maintain **Table 0 – Repository Evidence Catalogue** before composing Chapter 2. The table must remain configuration-controlled alongside the compliance matrix and should be updated whenever new runs, documents, or test suites are baselined. Use it to brief technical reviewers on where each dataset resides, the governing configuration, and the validation status. Treat the entries below as the current baseline; extend or amend them if the repository evolves.

Table 0 – Repository Evidence Catalogue

| Asset ID | Path | Category | Purpose / Content | Data Type / Format | Validation / Notes |
|----------|------|----------|-------------------|--------------------|--------------------|
| DOC-PO | `docs/project_overview.md` | Documentation | Mission context and deliverables synopsis supporting Chapter 1 framing. | Markdown | Reviewed during SERB 2025-Q4 update; cite for Chapter 1 literature scoping. |
| DOC-MR | `docs/mission_requirements.md` | Documentation | Configuration-controlled mission requirements MR-1…MR-7. | Markdown | Traceable to SRD baseline FS-REQ-001 v1.0. |
| DOC-SRD | `docs/system_requirements.md` | Documentation | Derived system requirements informing architecture constraints. | Markdown | Synchronise with MR↔SRD mapping in Traceability Architecture section. |
| DOC-CM | `docs/compliance_matrix.md` | Documentation | Current MR/SRD compliance ledger with evidence references. | Markdown | Update after every SERB/CCB decision. |
| DOC-CONOPS | `docs/concept_of_operations.md` | Documentation | Operational modes, communications throughput assumptions, and payload workflows. | Markdown | Provides primary inputs for communications analyses. |
| DOC-TFR | `docs/triangle_formation_results.md` | Documentation | Authoritative triangle maintenance metrics and STK validation narrative. | Markdown | Contains EV-3 interpretation; ensure figures remain reproducible. |
| CFG-BASE | `config/project.yaml` | Configuration | Global simulation parameters, spacecraft properties, and solver settings. | YAML | Lock prior to each evidence campaign. |
| CFG-SCEN | `config/scenarios/tehran_daily_pass.yaml` | Configuration | Scenario-specific geometry and schedule for Tehran daily pass runs. | YAML | Used by `sim/scripts/run_scenario.py`; record version in Chapter 2 inputs. |
| SIM-SCEN | `sim/scripts/run_scenario.py` | Simulation | Deterministic and Monte Carlo scenario generation for daily pass analysis. | Python | Validated through `tests/integration/test_simulation_scripts.py`. |
| SIM-TRI | `sim/scripts/run_triangle.py` | Simulation | Formation propagation script generating triangle evidence packages. | Python | Emits artefacts consumed by EV-1/EV-3; ensure STK exports pass importer. |
| TOOL-STK | `tools/stk_export.py` | Tooling | STK 11.2 export interface enforcing interoperability constraints. | Python | Mandatory in every Methods subsection when data leaves Python stack. |
| APP-RUN | `run.py` | Simulation | FastAPI automation service orchestrating scenario execution. | Python | Reference when documenting automated execution pipelines. |
| TEST-STK | `tests/test_stk_export.py` | Test | Regression coverage for STK export interface. | Python (pytest) | Cite when asserting interoperability compliance. |
| TEST-SIM | `tests/integration/test_simulation_scripts.py` | Test | Integration verification for scenario and triangle pipelines. | Python (pytest) | Demonstrates repeatability of Monte Carlo runs. |
| TEST-DOC | `tests/test_documentation_consistency.py` | Test | Ensures documentation metadata and references remain synchronised. | Python (pytest) | Run before final manuscript submission. |
| TEST-TRI | `tests/unit/test_triangle_formation.py` | Test | Validates geometry, command latency, and Δv metrics for the triangle formation. | Python (pytest) | Guards MR-5…MR-7 compliance statistics. |
| ART-TRI | `artefacts/triangle_run/` | Artefact | Baseline triangle simulation package (EV-1) with summary JSON and STK exports. | JSON, CSV, SVG | Confirm checksums before citing. |
| ART-MAINT | `artefacts/run_20251018_1207Z/` | Artefact | Maintenance and responsiveness study covering MR-5…MR-7 (EV-3). | CSV, JSON, SVG | Includes Monte Carlo catalogues; log STK validation timestamp. |
| ART-DAILYPASS | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` | Artefact | Deterministic + Monte Carlo Tehran daily pass alignment evidence (EV-5). | CSV, JSON, STK exports | Capture RAAN solution provenance in Chapter 3 narrative. |
| ART-STK | `artefacts/run_20251018_1308Z_tehran_daily_pass/` | Artefact | STK 11.2 import package verifying daily pass geometry (EV-4). | `.e`, `.sat`, `.gt`, `.int` | Note ingestion outcomes in Compliance subsections. |

Augment the catalogue with any new datasets (e.g., communications analyses, cost models) and cross-reference the corresponding MR/SRD identifiers. Use the catalogue as the authoritative index when completing `### X.2 Inputs and Assumptions` across all chapters.

## Requirements Traceability Architecture

Introduce a dedicated **Traceability Diagram + Compliance Commentary** block immediately after presenting Table 0 and before commencing Chapter 2. This block must:

- Depict the MR↔SRD↔Evidence relationships using a diagrammatic form (Mermaid, TikZ, or SVG) that explicitly maps each Mission Requirement (`docs/mission_requirements.md`) to its derived System Requirements (`docs/system_requirements.md`) and to the authoritative evidence tags maintained in `docs/compliance_matrix.md` and `_authoritative_runs.md`. Include automation hooks (e.g., `tests/test_stk_export.py`, `tests/integration/test_simulation_scripts.py`) as terminal nodes so reviewers can see which regression tests protect each link.
- Present **Table T.1 – Traceability Summary** with columns `MR ID`, `SRD IDs`, `Evidence Tags (EV-x)`, `Primary Artefact Path`, `Validation Status`, and `Change Control Notes`. Populate the table using artefacts such as `artefacts/run_20251018_1207Z/`, `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/`, and `artefacts/run_20251018_1308Z_tehran_daily_pass/`, ensuring every row records the latest SERB decision date and whether the Configuration Control Board has ratified the evidence package.
- Provide a narrative paragraph describing the governance chain: how analysts propose updates, how SERB validates provenance and statistical sufficiency, how CCB adjudicates configuration deltas, and how the Verification and Validation Plan checkpoints (V&V-1 requirements definition, V&V-2 analytical validation, V&V-3 STK confirmation) trigger updates to the compliance matrix and Table 0.

Revisit the diagram and commentary whenever new evidence is generated or requirements change. Archive superseded diagrams under `docs/figures/history/` with ISO-8601 filenames so reviewers can audit the evolution of the traceability model.

## Cross-Chapter Linkages

Embed explicit transition statements so the analytical narrative flows coherently across chapters:

1. **Chapter 1 → Chapter 2.** Close Chapter 1 by enumerating the parameter rationales (e.g., RAAN targeting logic, centroid spacing tolerances, communications throughput thresholds) that Chapter 2 must instantiate in configuration tables and simulation setups.
2. **Chapter 2 → Chapter 3.** Open Chapter 3 with a synopsis of the assets catalogued and executed in Chapter 2, citing Table 2.1 (configuration baselines), Table 2.3 (traceability matrix), and any Monte Carlo campaign logs. Confirm that the datasets listed in Table 0 transition directly into Chapter 3 Stage 1 evidence selection.
3. **Chapter 3 → Chapter 4.** Introduce Chapter 4 by summarising the key findings from Chapter 3—geometry compliance, maintenance budgets, communications throughput, environmental dossier outcomes—and state which conclusions will be stress-tested through benchmarking and recommendations.
4. **Feedback loop to Chapter 5.** When compiling Chapter 5, describe how the global reference ledger underpins each chapter’s arguments and identify any evidence gaps earmarked for future work.

Use these transition notes within the opening and closing paragraphs of the mandated subsections (`### X.1` and `### X.5`) so reviewers can trace the logical hand-off between chapters without ambiguity.

## Reference Management Protocol

Maintain a repository-wide reference ledger that guarantees unique numbering across all chapters:

- **Global numbering.** Continue the numeric sequence established in Chapter 5. When adding a new source, append it to Chapter 5 and assign the next available integer; do not restart numbering within individual chapters.
- **Chapter-specific ledgers.** After completing the five mandatory subsections for each chapter, append a heading `### X.R Chapter X Reference Ledger` listing only the references cited in that chapter but preserving the global numbers (e.g., Chapter 1 cites [Ref1], [Ref3]; Chapter 2 cites [Ref2], [Ref4], [Ref14]).
- **Change control.** Whenever references are added, removed, or renumbered, update `tests/test_documentation_consistency.py` expectations and rerun the test suite to ensure automated checks remain aligned. Record the change in the compliance commentary so SERB and CCB can trace literature dependencies.
- **Cross-referencing.** When a reference supports multiple chapters, cite it with the same identifier and provide parenthetical context indicating the originating chapter (e.g., `[Ref4 – Ch2, Ch3]`) in the Chapter 5 master list to aid reviewers.

Document the numbering decisions in the project log and ensure that any appendices, annexes, or supplementary memos adopt the same global reference sequence.

## Content Generation Guidelines

- All reasoning must be justified with evidence from peer-reviewed literature, agency reports, or authoritative repository data. When invoking established orbital mechanics principles (e.g., HCW, ROE), cite canonical sources alongside recent corroborating studies.
- Present quantitative data using tables, figures, and graphs. Employ Suggested Tables (e.g., Tables 2.1, 4.1, 5.1) to summarise configuration parameters, performance metrics, and validation results. Describe any figures so readers can reproduce them from repository artefacts.
- Maintain a critical tone when assessing methodologies and results. Discuss uncertainties, sensitivities, and known limitations. Record any deviations from configuration baselines and their implications for reproducibility.
- Highlight innovation: emphasise the transition from generic formation flying literature to a Tehran-specific transient triangle, and explain how communications throughput expansion, payload processing guidance, and the environmental dossier differentiate this mission from antecedents.
- Document any mathematical models (e.g., Monte Carlo propagation, link budgets) and statistical analyses (confidence intervals, compliance probabilities). State assumptions, boundary conditions, and validation status against `tools/stk_export.py`.
- Adhere to standards referenced in the repository (ISO/IEC 23555-1:2022, ESA-GSOP-OPS-MAN-001) and any additional ASTM/ISO norms uncovered during the literature review. Explain how these standards inform the experimental design and data handling procedures.

## Chapter 1: Theory—Literature Review

Conduct an exhaustive literature review spanning 2020–2025 (supplemented by seminal works where indispensable) to map the evolution of distributed satellite missions. Progress through tandem pairs (e.g., GRACE/GRACE-FO), linear strings, tetrahedral clusters (e.g., MMS), swarms, and responsive cubesat formations. Compare sensing performance, geometric stability, propulsion demand, autonomy requirements, and mission risk for each topology so that the trade-space clearly justifies adopting a **three-satellite, transient equilateral triangle** as the optimum balance between sensing diversity, controllability, and lifecycle cost for this project.[Ref1][Ref8]

### Literature Review Protocol

Adhere to the following referencing rule before compiling sources:

- **Referencing & citation style.** Use numeric citations in order of appearance (IEEE/Vancouver-style) with bracketed numbers `[1]`, `[2]`, etc., and compile the reference list in the same sequence. Acceptable reference types follow the template examples (journal articles, books, agency or company web pages). Prioritise peer-reviewed literature from 2020–2025; include older seminal sources only when unavoidable or notably influential. Update chapter-specific bibliographies as the writing progresses and consolidate them in Chapter 5.

Proceed through these literature review stages to structure the chapter:

1. **Trace the paradigm shift to formation flying.** Begin with a literature review that explains how single-satellite missions evolved into multi-spacecraft constellations and demonstrates how formation flying emerged as a paradigm shift in Earth observation. Contrast historic monolithic designs with responsive formations, emphasising the operational and scientific gains that motivate the Tehran transient triangle.
2. **Quantify metropolitan overpass durations.** Examine recent studies on low Earth orbit passes above major cities (including Tehran, Istanbul, Los Angeles, and Jakarta) to establish the statistical distribution of access durations. Determine the maximum practical dwell time per pass and, using Tehran’s coordinates (35.6892°N, 51.3890°E) and metropolitan extent (~730 km²), confirm that a 90 s continuous window is realistic. Reproduce the repository corridor calculation: at a 6,890 km semi-major axis the orbital speed is approximately 7.60 km·s⁻¹, so a spacecraft covers about 684 km along-track during 90 s. Treating the “over Tehran” condition as remaining within a 350 km ground-radius corridor, enforce the constant cross-track miss constraint \(D \leq \sqrt{350^2 - (0.5 \times 90 \times 7.60)^2} \approx 74\) km. Note that this tolerance still supports ≥90 s access; beyond it, the ground track exits the corridor prematurely. Document any supplementary formulae uncovered in the literature.
3. **Justify the LEO mission class.** Survey comparable constellation missions (e.g., TanDEM-X, COSMO-SkyMed, ICEYE clusters) to evaluate altitude regimes, propulsion concepts, and sensing capabilities. Summarise why a LEO implementation best satisfies Tehran’s imaging, communications, and responsiveness goals, highlighting atmospheric drag management and revisit frequency trade-offs that influenced the project’s mission objectives.
4. **Reconstruct cross-track tolerance logic.** Review the repository documentation (`docs/tehran_daily_pass_scenario.md`, `docs/triangle_formation_results.md`) and external literature to explain how the primary tolerance (cross-track ≤ ±30 km) and waiver ceiling (≤ ±70 km) were derived. Integrate the Tehran corridor model with the 90 s access analysis to show that maintaining the formation centroid within ±30 km at the midpoint of the daily window guarantees compliance, while the ±70 km waiver is admissible only under exception handling. Clarify the measurement definition: cross-track is the great-circle distance from the formation centroid to the Tehran reference point, evaluated at the midpoint of the daily 90 s access window, with an optional 95th-percentile check within the same interval. Reaffirm that the formation maintains an equilateral ~6 km triangle for ≥90 s per day at ~550 km LEO.
5. **Characterise repeat ground-track governance.** Consolidate theoretical treatments of repeat ground-track (RGT) design, the \(J_2\) perturbation effect, and inclination/altitude selection strategies that manage right ascension of the ascending node (RAAN) drift. Compare analytic and numerical approaches and explain how the chosen semi-major axis and inclination support RAAN control for the Tehran mission.

Examine theoretical frameworks governing repeat ground-track orbits, sun-synchronous design, and intersecting-plane architectures. Synthesise derivations for Relative Orbital Elements (ROEs), Hill–Clohessy–Wiltshire (HCW) dynamics, differential nodal drift, and perturbation management (\(J_2\), atmospheric drag, solar radiation pressure) to establish the predictive toolkit used later in the thesis. Highlight comparative studies between analytical, semi-analytical, and numerical propagation methods, and explain why the repository’s hybrid analytical–Monte Carlo methodology remains the reference approach.[Ref2][Ref4][Ref6][Ref9]

Review global case studies of city-focused observation campaigns (e.g., Mexico City, Istanbul, Los Angeles, Jakarta). For each city, document latitude/longitude, metropolitan footprint, elevation span, seismicity, air-quality indices, and climatological challenges that influence access geometry and payload scheduling. Use this comparative dataset to articulate the **Tehran selection rationale**, emphasising how its seismic hazard, inversion-prone air quality, 730 km² urban footprint, and 35.6892°N, 51.3890°E coordinates create a demanding yet high-impact target for transient formation imaging. Explicitly connect these attributes to the mission’s need for daily 90 s coordinated passes and the geometry embedded in the repository scenarios.[Ref1][Ref3][Ref10][Ref11]

Survey formation-maintenance strategies, including differential drag, cold-gas and electric propulsion, inter-satellite ranging, and autonomous guidance algorithms. Evaluate Δv envelopes, navigation accuracy, and fault tolerance reported in recent missions and academic prototypes. Conclude why a maintenance allocation of ≤15 m/s per spacecraft with Monte Carlo validation is appropriate for this concept, and identify gaps that motivate future adaptive control research.[Ref2][Ref4][Ref8]

Compile literature on communications architectures for small formations, covering X-/S-band links, optical crosslinks, and inter-satellite networking. Derive a **communications throughput requirement** that ensures the Tehran mission can offload a full day of tri-stereo optical and coherent radar payload data plus housekeeping telemetry within the evening downlink window. Anchor the requirement to the 9.6 Mbps X-band baseline documented in the ConOps and project growth margins (e.g., scalability to 25–45 Mbps) needed to accommodate higher-resolution sensors or additional data products. Address link budgets, ground-station availability, latency constraints, and regulatory considerations.[Ref3][Ref12]

Investigate payload sensing modalities relevant to coordinated imaging (tri-stereo optical, InSAR, thermal, atmospheric sounding). For each modality, document achievable ground sampling distance, swath width, signal-to-noise ratios, and raw/compressed data volumes. Translate these findings into **payload data product and processing guidance** that justifies the repository’s Level-0 → Level-1B → analysis-ready pipeline, compression factors, and four-hour delivery objective.[Ref3][Ref4][Ref13]

### Parameter derivation literature modules

Expand Chapter 1 with a targeted literature reconnaissance that explains how each mission-critical parameter was derived before it appears in later chapters. Structure the material into clearly labelled subsections covering **ROE theory and centroid spacing**, **RAAN optimisation heuristics**, **perturbation modelling for drift control**, and **command latency studies**. Within each subsection, cite external research that validates the repository baselines—e.g., justify the \(6\,\text{km}\) equilateral separation and associated centre-of-mass spacing reported in `docs/triangle_formation_results.md` and its Table 2 orbital elements (RAAN \(18.881^{\circ}\) for Plane A, \(36.065^{\circ}\) for Plane B) by tying them to ROE formulations; corroborate the locked RAAN \(350.7885^{\circ}\) solution and 07:39:25–07:40:55Z window extracted from `docs/tehran_daily_pass_scenario.md`; quantify perturbation impacts that necessitate \(J_2\) management and atmospheric drag modelling; and compare command latency findings from agency missions that align with the MR-5 twelve-hour ceiling documented in the ConOps.[Ref3][Ref4][Ref6]

Catalogue prior academic and agency projects tackling transient formation events or city-targeted constellations. Summarise their modelling assumptions, simplifications, and validation approaches, then contrast them with the repository’s insistence on STK 11.2 interoperability and repeatable Monte Carlo campaigns. Use this review to reinforce why the project leans on configuration-controlled scenario files, authoritative run ledgers, and reproducible toolchains.[Ref4][Ref5][Ref6][Ref7]

Throughout this chapter, articulate how each literature thread influences the thesis methodology, culminating in a clear statement: **because the surveyed studies show that transient equilateral formations maximise sensing value while containing risk and resource consumption, this project formalises a Tehran-focused three-satellite implementation**. Close the chapter with a consolidated mapping between literature-derived insights and the mission requirements (MR-1 to MR-7 plus communications throughput and payload handling mandates). Document which references were extracted and which were used in this chapter to maintain traceability into Chapter 5.[Ref2][Ref3]

## Chapter 2: Experimental Work

Document every repository asset that constitutes the mission “materials”. Begin with `config/project.yaml` and the scenario catalogue under `config/scenarios/`, detailing gravitational constants, spacecraft physical properties, orbital elements, solver tolerances, and Monte Carlo seeds. Present these parameters in a structured table (Suggested Table 2.1) grouped by subsystem (orbital design, spacecraft bus, payload, communications, ground segment) so analysts can cross-reference assumptions against mission requirements and ConOps statements.[Ref2][Ref3][Ref6]

Map the simulation pipeline orchestrated by `sim/scripts/run_scenario.py`, `sim/scripts/run_triangle.py`, `run.py`, and `run_debug.py`. For each stage—RAAN alignment optimisation, access window detection, high-fidelity propagation, metric extraction, Monte Carlo sampling, STK export—explain the algorithms employed, configuration inputs, verification hooks, and how they align with literature-derived methodologies. Include diagrams or sequence descriptions (e.g., Suggested Figure 2.1) showing data flow from configuration files to post-processing outputs.[Ref4][Ref6][Ref7]

### Execution Walkthrough

Provide a step-by-step explanation of how the repository scripts operationalise the experimental workflow before presenting aggregated results:

1. **Initialise the environment and configurations.** Describe setting up the Python environment (e.g., `make setup`), reviewing `config/project.yaml`, and confirming the chosen scenario file. Explain how analysts select between stored JSON configurations and inline overrides when invoking the scripts.
2. **Execute `run_scenario.py`.** Detail the command-line arguments, expected logging, and generated artefacts (`summary.json`, propagation CSV files, STK exports) when running `python -m sim.scripts.run_scenario --config config/scenarios/tehran_daily_pass.json --output-dir <path>`. Clarify how each pipeline stage reports progress and where to locate intermediate outputs for validation.
3. **Execute `run_triangle.py`.** Walk through `python -m sim.scripts.run_triangle --config config/scenarios/tehran_triangle.json --output-dir <path>`, interpret the CLI readout of formation window duration, and reference how the JSON and CSV artefacts capture triangle geometry, centroid behaviour, and maintenance statistics. Highlight cross-links to the archived authoritative runs for comparison.
4. **Document STK outputs.** Summarise the structure of the generated STK directory (OEM ephemerides, ground-track files, facility definitions, contact intervals) and outline the import procedure using `docs/stk_export.md` and `docs/how_to_import_tehran_daily_pass_into_stk.md`. Emphasise verification steps that confirm STK 11.2 ingests the artefacts without warnings.
5. **Record validation processes.** Explain how analysts inspect log files, compare outputs with `artefacts/run_20251018_1207Z/`, and reference regression tests (`tests/unit/test_triangle_formation.py`) to demonstrate pipeline fidelity. Document any manual checks (e.g., cross-track thresholds, Monte Carlo convergence) expected after each execution.

### Quantitative parameter documentation

Dedicate a subsection to reporting the exact numeric parameters used in the experiments and the derivation method for each quantity. Populate Suggested Table 2.2 with: the RAAN solution \(350.7885^{\circ}\) and 07:39:25–07:40:55Z access window from `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json`; the centroid cross-track magnitude \(12.14\,\text{km}\) and worst-spacecraft offset \(27.76\,\text{km}\) at 07:40:10Z from the deterministic Tehran pass summary; the Monte Carlo centroid \(p_{95}=24.18\,\text{km}\) statistic and unit success rate recorded in `monte_carlo_summary.json`; the formation window duration \(96\,\text{s}\), maintenance \(p_{95}\ \Delta v = 0.041\,\text{m/s}\), and command latency \(1.53\,\text{h}\) from `triangle_summary.json` and the maintenance ledger; and the per-spacecraft RAAN values (Plane A \(18.881^{\circ}\), Plane B \(36.065^{\circ}\)) extracted from the orbital element reconstruction table. For every figure, state the procedure that produced it—RAAN solver iteration, centroid geometry computation, Monte Carlo aggregation, or regression test output—so the thesis clearly links each parameter to its provenance.[Ref4][Ref6]

### Requirement traceability and governance

Insert a **requirements traceability matrix** (Suggested Table 2.3) that maps MR-1 to MR-7 and the corresponding SRD identifiers to the exact configuration files, simulation artefacts, and verification assets that demonstrate compliance. Reference the compliance ledger in `docs/compliance_matrix.md` when defining the MR-to-evidence mapping and ensure each row cites the authoritative run directory and STK export files.[Ref14] Augment the table with a dedicated column for automated checks, pointing explicitly to `tests/test_stk_export.py`, `tests/integration/test_simulation_scripts.py`, `tests/test_documentation_consistency.py`, and `tests/unit/test_triangle_formation.py`, noting which requirement each test underpins and where regression coverage exists.[Ref15][Ref16][Ref17][Ref18] Close the section by outlining the governance cadence: describe how the Systems Engineering Review Board (SERB) ratifies evidence packages, how the Configuration Control Board (CCB) approves configuration changes, and how Verification and Validation milestones (V&V-1 requirements definition, V&V-2 analytical validation, V&V-3 STK confirmation) structure progress reviews. Summarise when each board convenes, what artefacts they demand, and how decisions feed back into the repository metadata.[Ref3]

### Automation and continuous integration

Describe how automation sustains reproducibility across local and cloud executions. Explain the FastAPI runner exposed by `run.py`, including how analysts submit scenario and triangle jobs through REST endpoints and how the service logs configuration hashes for auditability.[Ref19] Summarise the GitHub Actions workflow in `.github/workflows/ci.yml`, detailing the sequence of `make setup`, `make lint`, `make test`, `make simulate`, `make baselines`, and `make docs` steps executed on every push or pull request, and clarify how artefacts are published for review.[Ref20] Link these pipelines to the local Makefile targets (`make scenario`, `make triangle`, `make clean`) to show how developers reproduce the CI stages on their workstations and how the automation hooks enforce STK export compatibility and regression integrity before evidence is accepted.[Ref21]

Enumerate the **communications throughput requirements** within the configuration context: specify downlink/uplink rates, contact durations, modulation schemes, coding gains, and antenna parameters necessary to guarantee daily data evacuation. Provide equations linking payload generation rates to ground-segment capacity, highlighting margins or required upgrades. Embed cross-references to MR-5 responsiveness metrics and to ConOps risk mitigations that rely on redundant ground support.[Ref2][Ref3]

Detail the **payload data product and processing guidance** operationalised in the codebase: describe file formats emitted by the simulations (`triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`), how they translate to Level-0 packets, Level-1B imagery, and analysis-ready datasets, and what preprocessing (radiometric calibration, geometric co-registration, coherence filtering) must occur before stakeholder delivery. Clarify storage, compression, and checksum practices to maintain data integrity and trace back to ISO/IEC 23555-1:2022.[Ref3][Ref4][Ref13]

Audit all authoritative artefacts under `artefacts/` and `docs/` to ensure traceability. Summarise how `_authoritative_runs.md`, `triangle_formation_results.md`, `tehran_daily_pass_scenario.md`, and `tehran_triangle_walkthrough.md` interlink run identifiers, configuration files, and validation procedures. Verify that every script, dataset, and documentation asset is cross-referenced so that future analysts can reproduce historical results without ambiguity.[Ref4][Ref5][Ref6][Ref7]

Include methodological guidance for quality assurance: outline regression testing (`tests/unit/test_triangle_formation.py`), configuration control practices, expectations for logging and metadata capture, and procedures for updating scenario metadata. Reference relevant standards (ESA-GSOP-OPS-MAN-001) when discussing ground-station operations and communications verification. Provide instructions for documenting deviations, rerunning Monte Carlo campaigns, and validating STK 11.2 compatibility so the workflow remains audit-ready.[Ref4][Ref5][Ref7][Ref12]

## Chapter 3: Results and Discussion

Present the analytical outputs as a three-stage narrative that mirrors the repository evidence chain, integrating quantitative analysis, figures, and tables to support each argument. Use the structural arc **Mission Framing → Configuration → Simulation → Evidence → Discussion → Conclusions** within each subsection so readers can trace how assumptions flow into executed runs, validated outputs, and the resulting interpretation.

**Stage 1—Authoritative Evidence Selection.** Identify and justify the “locked” runs (`run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`, curated triangle reruns). Describe their directories, data products, validation status, and relationship to the compliance matrix. Explain how exploratory runs are archived without contaminating baseline evidence, and document any statistical sampling decisions drawn from Monte Carlo campaigns.[Ref4][Ref5][Ref6]

**Stage 2—Formation Geometry, Maintenance, and Communications Performance.** Extract quantitative metrics from `triangle_summary.json`, `maintenance_summary.csv`, and associated Monte Carlo catalogues: the 96 s formation window, exact aspect ratio extrema (unity within numerical precision), centroid ground-distance series with mean 18.7 km and \(p_{95}\) 24.18 km, and the annual \(\Delta v\) statistics (mean 8.3 m/s, \(p_{95}\) 0.041 m/s, 100% recovery success rate). Cross-reference these with the RAAN allocations from the orbital element reconstruction to show how Plane A and Plane B maintain differential nodal alignment. Correlate the findings with communications throughput evidence—demonstrate that the 9.6 Mbps baseline, or any proposed upgrade, clears the payload backlog within the evening window, and document configuration updates triggered by any shortfall. Summarise the results in Suggested Table 4.1 and supporting figures, annotating each metric with its derivation method (deterministic propagation, Monte Carlo aggregation, or regression test output).[Ref3][Ref4][Ref6]

**Stage 3—Robustness, STK Validation, and Data Handling Assurance.** Report Monte Carlo compliance probabilities (≥98.2% for ≤30 km centroid distance, 100% within waiver band), drag dispersion impacts, and STK 11.2 cross-check outcomes. Explain how the simulation datasets, the STK exports, and the supporting literature jointly substantiate each claim—for example, pair the Python-derived \(p_{95}\) centroid statistic with the STK contact interval confirmation and cite the literature that motivates the acceptance thresholds. Provide guidance for generating comparative tables (e.g., Suggested Table 5.1) showing <2% divergence between Python simulations and STK metrics. Confirm that exported ephemerides, ground tracks, and contact intervals ingest without error, and record any limitations or corrective actions discovered during validation. Document how communications analyses and payload processing pipelines remain coherent with STK timelines.[Ref4][Ref6][Ref7]

### Risk register synthesis

Summarise the mission risk posture by reproducing and updating the R-01 to R-05 entries from the ConOps risk register. Present the material as Suggested Table 4.2 with probability, impact, mitigation, and owner columns, and include trend commentary based on the latest simulation evidence—e.g., relate the \(\Delta v\) consumption statistics to R-02, Monte Carlo recovery outcomes to R-03, STK compatibility checks to R-05, and communications latency findings to R-01. Describe how each risk is tracked through SERB and CCB reviews, what regression tests or scenario reruns are mandated when indicators drift, and which artefacts are archived to demonstrate closure.[Ref3]

Develop a **Tehran environmental operations dossier** that consolidates geospatial, atmospheric, and socio-technical constraints relevant to mission planning. Include: (1) urban morphology and land-cover distribution influencing retrieval algorithms and stray-light management; (2) seasonal meteorology (dust events, inversion layers, cloud climatology) affecting payload duty cycles and link budgets; (3) air-quality and pollution metrics that motivate coordinated sensing and calibrate optical/radar processing approaches; (4) seismic and infrastructure risk profiles guiding prioritised observation corridors and contingency response planning; and (5) ground-segment considerations within Tehran (spectrum regulation, electromagnetic interference sources, power resilience). Reference reputable datasets (UN urban studies, Tehran Air Quality Control Company, Iran Meteorological Organization) and align the dossier with operational procedures outlined in the ConOps.[Ref3][Ref10][Ref11]

Conclude the chapter by synthesising how the quantified results, communications analyses, payload processing guidance, and environmental dossier collectively demonstrate compliance with MR-1 through MR-7, the added throughput mandate, and the data-handling objectives. Compare findings to existing literature, discuss limitations or sources of error, and note how future control or communications upgrades could mitigate identified risks. Record the references extracted and used here for Chapter 5 traceability.[Ref2][Ref3]

## Chapter 4: Conclusions and Recommendations

Summarise how the mission architecture—dual-plane, sun-synchronous constellation delivering a daily 90 s equilateral formation—meets stakeholder needs. Reiterate evidence for geometric fidelity, robustness, communications adequacy, payload processing readiness, and Tehran environmental responsiveness, citing the authoritative runs and validation artefacts.[Ref3][Ref4][Ref5][Ref6]

### Comparative mission benchmarking

Add a subsection that contrasts the Tehran constellation outcomes with international reference missions such as TanDEM-X, PRISMA, and PROBA-3. Quantitatively compare formation maintenance envelopes, command latency practices, payload data handling throughput, and risk postures. Highlight where the Tehran design meets or exceeds these benchmarks and where further optimisation is required, drawing on literature cited in Chapter 1 and any newly reviewed mission reports. Close the subsection by interpreting how these comparisons influence the strategic recommendations delivered to stakeholders.

Issue actionable recommendations: maintain the current baseline design, invest in redundant ground infrastructure, refine autonomous maintenance strategies, and institutionalise the environmental dossier within operations planning. Address communications scaling options and payload processing automation enhancements needed to preserve four-hour delivery commitments under evolving data loads.[Ref3][Ref4]

Define a future work pathway that embeds a **mission cost and risk analysis framework**. Outline steps to integrate parametric cost models (e.g., NASA/Aerospace Corp CERs), lifecycle budgeting, and risk-based decision analysis with the existing simulation pipeline. Emphasise how cost and risk modelling will interact with robustness studies, communications upgrades, payload enhancements, and environmental contingencies to support future design iterations and stakeholder reviews.[Ref3][Ref12]

Augment the chapter with a dedicated subsection titled **Future Research Suggestions**. Conduct a fresh literature review focused on emerging formation-flying technologies, autonomous maintenance, adaptive communications, and advanced payload processing relevant to post-Tehran deployments. Summarise at least three research avenues, explaining how each could expand the mission’s capability envelope or mitigate identified risks, and articulate the analytical steps required to investigate them in follow-on studies.

## Evaluation Criteria

Use the following criteria to assess the completed report:

- **Completeness:** All chapters fully address the mission objectives, literature scope, configuration assets, analytical results, and future pathways.
- **Accuracy:** Information is technically correct, consistent with repository artefacts, and supported by credible references or validated simulations.
- **Clarity:** Writing maintains an academic yet accessible tone, with coherent structure and precise terminology.
- **Organisation:** The narrative follows the mandated chapter sequence, with clear transitions and cross-references between mission requirements, literature findings, and simulation evidence.
- **Critical Analysis:** Discussions evaluate limitations, uncertainties, and alternative approaches, demonstrating mastery of formation-flying scholarship.
- **Adherence to Standards:** Formatting, referencing, STK interoperability, and data handling comply with repository guidelines and cited standards.
- **Proper Referencing:** Each chapter specifies which references were extracted and used, culminating in Chapter 5 with a comprehensive, consistently formatted list.

## Chapter 5: References

- [Ref1] `docs/project_overview.md` – Mission overview and academic framing of the Tehran transient formation concept.
- [Ref2] `docs/mission_requirements.md` – Configuration-controlled mission requirements MR-1 through MR-7.
- [Ref3] `docs/concept_of_operations.md` – Operational architecture, communications throughput baseline, and payload processing workflow.
- [Ref4] `docs/triangle_formation_results.md` – Authoritative simulation results and maintenance budget analysis.
- [Ref5] `docs/_authoritative_runs.md` – Ledger of baseline run identifiers and evidence packages.
- [Ref6] `docs/tehran_daily_pass_scenario.md` – Scenario configuration, RAAN alignment evidence, and Monte Carlo outputs.
- [Ref7] `docs/tehran_triangle_walkthrough.md` – Procedural guide for reproducing Tehran formation simulations and STK validation.
- [Ref8] Barbour, A. et al. (2023). “Passive Safety Using Relative Orbital Elements,” AAS 23-155.
- [Ref9] D’Amico, S., Montenbruck, O. (2020). “Proximity Operations in Low Earth Orbit,” *Acta Astronautica* 176: 206–223.
- [Ref10] United Nations Department of Economic and Social Affairs (2022). *World Urban Prospects: Tehran Metropolitan Profile*.
- [Ref11] Tehran Air Quality Control Company (2024). *Annual Air Quality and Meteorological Report*.
- [Ref12] European Space Agency (2021). *Ground Station Operations Manual*, ESA-GSOP-OPS-MAN-001.
- [Ref13] ISO/IEC 23555-1:2022. *Data product specification for Earth observation – Part 1: General requirements*.
- [Ref14] `docs/compliance_matrix.md` – Verification ledger detailing SERB, CCB, and V&V evidence mapping.
- [Ref15] `tests/test_stk_export.py` – Regression coverage for STK export compatibility.
- [Ref16] `tests/integration/test_simulation_scripts.py` – Integration tests for scenario and triangle execution pipelines.
- [Ref17] `tests/test_documentation_consistency.py` – Automated checks on documentation metadata and references.
- [Ref18] `tests/unit/test_triangle_formation.py` – Formation geometry and maintenance regression tests.
- [Ref19] `run.py` – FastAPI automation service for mission scenario execution.
- [Ref20] `.github/workflows/ci.yml` – Continuous integration pipeline invoking linting, testing, and simulation targets.
- [Ref21] `Makefile` – Local automation targets mirroring the CI workflow.
