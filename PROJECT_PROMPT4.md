# Project Prompt: Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

## Preface and Authorial Positioning
- You are commissioned as the lead researcher for the Formation Satellite Programme's Phase 2 Tehran campaign.
- Adopt an academic tone aligned with British English spelling conventions and the mission-governance documentation already baselined in this repository.
- Write every chapter as though it will appear in a systems-engineering dissertation that must withstand independent verification and configuration control audits.
- Maintain explicit traceability to configuration files, analytical scripts, regression tests, and archived run artefacts stored under `artefacts/`.
- Each chapter you draft must interleave literature synthesis, repository evidence, and open research questions so that the resulting dossier is both scholarly and actionable.

## Document Conventions and Quality Gates
- Structure the dossier with sequential chapter headings (`#`, `##`, `###`) to reflect the hierarchy employed across `docs/`.
- End each chapter with a checklist confirming that literature coverage, analytical reproduction, and STK interoperability considerations have all been addressed.
- Reference repository artefacts using the run identifier notation `run_YYYYMMDD_hhmmZ` and include directory paths relative to the repository root.
- When proposing new analyses or experiments, cite the enabling script or configuration key (for example, `sim/scripts/run_triangle.py`, `config/scenarios/tehran_daily_pass.json`).
- Reserve `[RefX]` tags for external literature; cite repository artefacts inline using backticks and precise filenames to simplify peer review.
- Highlight any dependency on STK 11.2 exports by stating "validated against `tools/stk_export.py`" to preserve interoperability assurances.

## Chapter 1: Literature Review Strategy and Theoretical Framework
### 1.1 Mission Context Recapitulation
- Restate the mission problem using the framing in `docs/project_overview.md`, emphasising the need for a daily 90-second triangular formation above Tehran.
- Summarise the mission objectives MR-1 through MR-7 as tabulated in `docs/mission_requirements.md`, noting the geometric, operational, and robustness constraints.
- Explain how the Concept of Operations in `docs/concept_of_operations.md` links single-station commanding (MR-5) to the delta-v budgeting (MR-6) and robustness (MR-7) objectives.

### 1.2 Core Literature Pillars
- Survey classical formation-flying theory focusing on relative orbital elements, referencing D'Amico et al. (2005) as cited in `docs/triangle_formation_results.md`.
- Examine repeat-ground-track design methodologies relevant to the RAAN alignment captured in `docs/tehran_daily_pass_scenario.md`.
- Review mission assurance doctrines concerning command latency and contingency recovery to contextualise the evidence from `artefacts/run_20251018_1207Z/`.
- Investigate Systems Tool Kit interoperability practices, drawing on exporter expectations described in `docs/stk_export.md` and `docs/how_to_import_tehran_daily_pass_into_stk.md`.

### 1.3 Literature Review Work Packages
- **WP1 – Formation Geometry Foundations.** Compile sources on equilateral formation synthesis in local-vertical local-horizontal (LVLH) frames, linking to the ROE calculations implemented in `sim/formation/triangle.py`.
- **WP2 – Perturbation Environment.** Identify studies on \(J_2\), drag, and solar radiation pressure impacts on low Earth triangular formations, tying back to the maintenance strategy summarised in `docs/triangle_formation_results.md`.
- **WP3 – Ground Segment Responsiveness.** Evaluate communications scheduling literature that supports the 12-hour latency requirement recorded in `docs/mission_requirements.md` and `docs/compliance_matrix.md`.
- **WP4 – Monte Carlo Recovery Protocols.** Research injection-dispersion mitigation techniques that parallel the 300-case recovery catalogue archived in `artefacts/run_20251018_1207Z/injection_recovery.csv`.
- **WP5 – STK Validation Methodologies.** Review best practices for text-ephemeris interchange and scenario verification, aligning with the process codified in `docs/how_to_import_tehran_daily_pass_into_stk.md`.

### 1.4 Gap Identification Matrix
| Gap ID | Description | Repository Evidence Trigger | Literature Response |
| --- | --- | --- | --- |
| LG-01 | Limited discussion of LVLH-to-inertial transformation accuracy during \(J_2\) dominated propagation. | `sim/formation/triangle.py` reliance on `propagate_kepler` and `_lvlh_frame`. | Survey LVLH linearisation validity limits and propose correction strategies. |
| LG-02 | Absence of multi-ground-station contingency doctrine beyond Kerman backup references. | `docs/concept_of_operations.md` Scenario 3 outlines Redu support without quantitative link budget. | Compile studies on dual-station architectures for LEO constellations, focusing on reliability modelling. |
| LG-03 | Need for comparative analysis between deterministic midpoint compliance and Monte Carlo percentiles. | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`. | Identify statistical assurance frameworks bridging deterministic and probabilistic evidence for regulatory sign-off. |
| LG-04 | Sparse treatment of STK text ephemeris precision versus interpolation cadence trade-offs. | `tools/stk_export.py` optional SciPy resampling and `ScenarioMetadata.ephemeris_step_seconds`. | Review AGI guidance and academic sources on sampling frequency impacts for STK ingestion fidelity. |

### 1.5 Sourcing Checklist for Chapter 1
- Extract citation metadata from each repository document referenced above to ensure alignment with configuration-controlled terminology.
- Maintain a bibliography table that differentiates between peer-reviewed sources (2019–2025 focus) and authoritative agency manuals.
- Annotate how each literature cluster informs forthcoming analytical chapters, ensuring every gap (LG-01–LG-04) maps to a proposed study.
- Confirm that at least one reference addresses delta-v budgeting in persistent formation-keeping to support MR-6 context.

### 1.6 Chapter 1 Deliverables
- Annotated literature review summarising theoretical constructs, perturbation models, and operations doctrine relevant to the Tehran formation.
- Narrative linking repository evidence (e.g., `docs/triangle_formation_results.md`, `artefacts/run_20251018_1207Z/`) with external research.
- Table cross-walking MR-1–MR-7 against proposed literature sources to guarantee traceability.
- Checklist demonstrating STK interoperability considerations have been captured when reviewing exporter-related literature.

### 1.7 Chapter 1 Exit Criteria
- [ ] Literature synthesis spans at least three peer-reviewed sources per work package.
- [ ] Each mission requirement MR-1–MR-7 is referenced within the chapter narrative.
- [ ] All repository artefacts cited in the chapter are verified for version control provenance.
- [ ] STK export and validation dependencies are explicitly acknowledged where relevant.

## Chapter 2: Mission Configuration and Geometric Foundations
### 2.1 Repository Artefact Orientation
- Provide an overview of `config/project.yaml`, highlighting global constants (e.g., WGS84 Earth model, \(398600.4418\,\text{km}^3\,\text{s}^{-2}\) gravitational parameter) and maintenance cadence assumptions.
- Describe the triangle scenario structure stored in `config/scenarios/tehran_triangle.json`, emphasising side length, duration, Monte Carlo seeds, and plane allocations.
- Summarise the Tehran daily pass scenario (`config/scenarios/tehran_daily_pass.json`) with focus on the locked RAAN \(350.7885044642857^{\circ}\) and cross-track tolerances.
- Cross-reference the mission roadmap in `docs/project_roadmap.md` to contextualise configuration updates.

### 2.2 Configuration Traceability Tasks
- Map each key-value pair in `config/project.yaml` to the subsystem narratives within `docs/system_requirements.md`.
- Document how the `formation.maintenance` block informs the delta-v assumptions used in `tests/unit/test_triangle_formation.py`.
- Explain how the `formation.monte_carlo` seed of 314159 establishes reproducibility for injection recovery metrics.
- Outline how `command.station` coordinates align with the single-station architecture described in `docs/concept_of_operations.md`.

### 2.3 Analytical Reconstruction Activities
- Re-derive the reference orbital elements in `config/scenarios/tehran_triangle.json` using the `cartesian_to_classical` routine within `sim/formation/triangle.py` and note any rounding differences.
- Validate that the epoch `2026-03-21T07:40:10Z` aligns with the deterministic midpoint captured in `artefacts/run_20251018_1207Z/triangle_summary.json`.
- Compute the LVLH offsets for each satellite using the `_formation_offsets` helper and confirm the equilateral geometry yields \(L = 6000\,\text{m}\).
- Analyse the `formation.drag_dispersion` parameters to understand how density sigma 0.25 influences the drag campaign archived in `artefacts/run_20251018_1207Z/drag_dispersion.csv`.

### 2.4 Configuration Integrity Checks
- Ensure that every scenario metadata block sets `validated_against_stk_export` to `true` when the corresponding run directories contain STK packages.
- Confirm the `command.contact_range_km` of 2200.0 is consistent with the command windows recorded in `artefacts/run_20251018_1207Z/command_windows.csv`.
- Verify that the `formation.duration_s` of 180 seconds matches the sample count logic used in `sim/formation/triangle.py` (duration/time-step + 1).
- Audit the Monte Carlo sample counts (300 for injection, 200 for drag) to ensure they exceed the coverage thresholds in `tests/unit/test_triangle_formation.py`.

### 2.5 Chapter 2 Deliverables
- Detailed explanation of scenario configuration semantics with annotated figures illustrating plane allocations and target geometry.
- Table connecting configuration parameters to code modules (e.g., `time_step_s` to propagation loops) and to run artefacts (e.g., `ground_tolerance_km` to windowed metrics).
- Commentary on configuration governance referencing the change-control workflow summarised in `docs/compliance_matrix.md` and `docs/project_roadmap.md`.

### 2.6 Chapter 2 Exit Criteria
- [ ] Each configuration file referenced is cross-checked against its latest commit hash before citation.
- [ ] The relationship between scenario metadata and simulation outputs is explicitly demonstrated.
- [ ] Plane allocation rationale is substantiated with both configuration and analytical evidence.
- [ ] STK validation status is summarised for every configuration that exports text ephemerides.

## Chapter 3: Simulation Pipeline and Toolchain Examination
### 3.1 Script Inventory
- Catalogue the core scripts in `sim/scripts/`, including `run_triangle.py`, `run_scenario.py`, `run_triangle_campaign.py`, `perturbation_analysis.py`, and `run_stk_tehran.py`.
- Describe the responsibilities of `sim/scripts/scenario_execution.py` and `sim/scripts/extract_metrics.py` as orchestrators and summarisation utilities.
- Note the placeholder status of `sim/scripts/baseline_generation.py`, which intentionally raises `NotImplementedError` pending future development.
- Acknowledge the interactive tooling described in `docs/interactive_execution_guide.md` that wraps `run.py` and `run_debug.py`.

### 3.2 Pipeline Stage Analysis
- Break down the stage sequence enforced by `tests/integration/test_simulation_scripts.py`, namely `access_nodes`, `mission_phases`, `two_body_propagation`, `high_fidelity_j2_drag_propagation`, `metric_extraction`, and optional `stk_export`.
- Explain how `scenario_execution.run_scenario` records this sequence and produces `scenario_summary.json` artefacts under timestamped directories.
- Detail the metric extraction flow that populates centroid percentiles (`centroid_abs_cross_track_km_p95`) within Monte Carlo outputs, referencing the equality checks in the test suite.
- Document how the CLI smoke tests spawn subprocesses to exercise `python -m sim.scripts.run_scenario tehran_daily_pass` and `python -m sim.scripts.run_triangle`.

### 3.3 Numerical Modelling Considerations
- Examine `sim/formation/triangle.py` to describe the use of Keplerian propagation (`propagate_kepler`) and LVLH frame construction (`_lvlh_frame`).
- Discuss how the script computes triangle area, aspect ratio, and side lengths via `constellation.geometry` utilities.
- Outline the maintenance and injection recovery metrics computed within `simulate_triangle_formation`, highlighting how annual \(\Delta v\) (`maintenance_summary.csv`) and Monte Carlo success rates (100% over 300 samples) are recorded.
- Comment on the drag dispersion modelling, noting sample count thresholds (≥50) enforced in `tests/unit/test_triangle_formation.py`.

### 3.4 Export and Interoperability Pipeline
- Summarise the STK export process implemented in `tools/stk_export.py`, focusing on `StateSample`, `PropagatedStateHistory`, `GroundTrack`, `GroundContactInterval`, `FacilityDefinition`, and `FormationMaintenanceEvent` structures.
- Describe how `export_simulation_to_stk` enforces monotonic epochs, optional resampling via SciPy, identifier sanitisation through `sanitize_stk_identifier`, and unique naming via `unique_stk_names`.
- Connect the exporter to the automation entry point `sim/scripts/run_stk_tehran.py`, which can generate Connect scripts for STK ingestion.
- Reference regression coverage in `tests/test_stk_export.py`, noting the expectation that `.e`, `.gt`, `.fac`, `.int`, and `.evt` files are produced with correct naming conventions.

### 3.5 Toolchain Risk Assessment
- Identify dependencies on optional libraries (SciPy, poliastro) and note the fallback behaviour documented in `tools/stk_export.py` for environments without these packages.
- Discuss potential numerical sensitivities (e.g., interpolation step size, integrator tolerances) and propose mitigation strategies anchored in literature from Chapter 1.
- Highlight logging and telemetry facilities (e.g., `debug.txt`, web run logs) that support reproducibility and audit trails.
- Evaluate the automation coverage of `make triangle`, `make scenario`, and `make simulate` as described in `README.md` to ensure continuous integration parity.

### 3.6 Chapter 3 Deliverables
- Narrative walkthrough of the simulation pipeline with sequence diagrams or flowcharts mapping script interactions.
- Tabulated mapping between pipeline stages, produced artefacts, and regression tests guaranteeing behaviour.
- Critical analysis of numerical methods used in propagation and metric extraction, referencing both repository code and external sources.

### 3.7 Chapter 3 Exit Criteria
- [ ] All key scripts are described with their inputs, outputs, and dependencies.
- [ ] Regression test coverage is referenced for every automation path mentioned.
- [ ] Numerical modelling assumptions are critically evaluated against literature findings.
- [ ] STK export integration is discussed with explicit mention of `tools/stk_export.py` safeguards.

## Chapter 4: Authoritative Runs and Quantitative Evidence Synthesis
### 4.1 Run Ledger Summary
- Present the authoritative run catalogue maintained in `docs/_authoritative_runs.md`, highlighting `run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`, and the curated `artefacts/triangle_run/` snapshot.
- Note the exploratory status of `run_20260321_0740Z_tehran_daily_pass_resampled` and the expectation that compliance documentation references baseline runs.
- Explain the naming convention `run_YYYYMMDD_hhmmZ` and the requirement to log assumptions, seeds, and model versions with each run.

### 4.2 Evidence Extraction Tasks
- For `run_20251018_1207Z`, summarise maintenance metrics (annual \(\Delta v = 14.04\,\text{m/s}\)), command latency (\(1.53\,\text{h}\)), and Monte Carlo recovery (100% success with \(p_{95}\ \Delta v = 0.041\,\text{m/s}\)).
- Distinguish between the windowed maximum ground distance \(343.62\,\text{km}\) and the full propagation maximum \(641.89\,\text{km}\) recorded in `triangle_summary.json`.
- For `run_20251020_1900Z_tehran_daily_pass_locked`, document the deterministic centroid offset \(12.143\,\text{km}\) and worst-spacecraft offset \(27.759\,\text{km}\) plus Monte Carlo percentiles (centroid \(p_{95} = 24.180\,\text{km}\), worst-spacecraft \(p_{95} = 39.761\,\text{km}\)).
- For `artefacts/triangle_run/`, describe how the snapshot mirrors the drag-inclusive rerun and includes CSV catalogues (`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`) and `injection_recovery_cdf.svg`.

### 4.3 Cross-Referencing with Compliance Documentation
- Tie the run evidence to the compliance statuses recorded in `docs/compliance_matrix.md`, demonstrating closure of MR-1 through MR-7 and SRD derivatives.
- Explain how `tests/unit/test_triangle_formation.py` enforces compliance margins by referencing the same metrics captured in the run artefacts.
- Detail how `docs/triangle_formation_results.md` and `docs/tehran_daily_pass_scenario.md` incorporate run metrics into narrative form for stakeholder review.
- Highlight how `docs/final_delivery_manifest.md` enumerates deliverables derived from these runs and ensures reproducibility via `make` targets.

### 4.4 Data Presentation Requirements
- Construct tables summarising run IDs, scenarios, directories, and key metrics for quick reference.
- Provide figure recommendations (e.g., reproduction of `injection_recovery_cdf.svg`) and note the expectation to convert to SVG for publication.
- Suggest how to visualise centroid offset distributions and maintenance budgets using repository CSV files.
- Outline how to capture STK screenshots per `docs/how_to_import_tehran_daily_pass_into_stk.md` for inclusion in the results chapter.

### 4.5 Chapter 4 Deliverables
- Comprehensive narrative interpreting each authoritative run and linking metrics back to mission requirements.
- Analytical commentary comparing deterministic versus statistical evidence for centroid alignment and formation stability.
- Recommendations for future run campaigns (e.g., scheduling, perturbation inclusions) based on gaps noted in `docs/_authoritative_runs.md`.

### 4.6 Chapter 4 Exit Criteria
- [ ] Every run cited is accompanied by directory paths and metric summaries.
- [ ] Compliance linkage to MR-1–MR-7 and SRD identifiers is explicitly stated.
- [ ] STK export validation status is confirmed for runs generating text ephemerides.
- [ ] Proposed figures and tables are enumerated with source artefacts.

## Chapter 5: STK Interoperability and Compliance Integration
### 5.1 Export Workflow Documentation
- Describe the exporter architecture in `tools/stk_export.py`, emphasising assumptions about TEME frames, monotonic epochs, and optional resampling.
- Explain how `sim/scripts/run_scenario.py` and `sim/scripts/run_triangle.py` invoke the exporter and populate `stk_export/` directories.
- Reference the automation guide `docs/how_to_import_tehran_daily_pass_into_stk.md` for ingestion steps, including Connect script usage.
- Summarise validation responsibilities, noting that the compliance matrix expects STK import logs for MR-2, SRD-P-001, and SRD-O-002 evidence.

### 5.2 Validation Artefact Requirements
- Identify the set of files produced for each scenario (`.sc`, `.sat`, `.e`, `.gt`, `.fac`, `.int`, `.evt`) and describe their roles in STK.
- Document the naming conventions enforced by `sanitize_stk_identifier` and `unique_stk_names` to prevent import errors.
- Outline the screenshot and metric capture expectations enumerated in `docs/how_to_import_tehran_daily_pass_into_stk.md`.
- Recommend maintaining a validation log referencing run IDs, import dates, and analysts responsible, aligning with `docs/compliance_matrix.md`.

### 5.3 Compliance Story Integration
- Explain how STK validation confirms the RAAN alignment, access windows, and facility geometry recorded in `config/scenarios/tehran_daily_pass.json` and `config/scenarios/tehran_triangle.json`.
- Discuss the interplay between Python-generated metrics and STK-measured values, emphasising the need to reconcile differences >1% as per the validation guide.
- Highlight regression safeguards like `tests/test_stk_export.py` that ensure file integrity.
- Address how STK validations feed into the Verification and Validation Plan milestones described in `docs/verification_plan.md`.

### 5.4 Chapter 5 Deliverables
- Step-by-step STK validation narrative integrated into the main text, supplemented by appendices capturing command logs and screenshot references.
- Table enumerating export files per run with notes on frame assumptions, time bounds, and facility definitions.
- Assessment of STK import results compared to Python metrics, identifying any biases or rounding differences.

### 5.5 Chapter 5 Exit Criteria
- [ ] Every export file type is described alongside its provenance and purpose.
- [ ] Validation steps explicitly cite `docs/how_to_import_tehran_daily_pass_into_stk.md` and `tools/stk_export.py`.
- [ ] Compliance matrix dependencies on STK validation are acknowledged and satisfied.
- [ ] Any discrepancies between STK and Python metrics are discussed with proposed resolutions.

## Chapter 6: Analytical Results, Discussion, and Interpretation
### 6.1 Result Structuring Guidance
- Begin with the Tehran triangular formation results summarised in `docs/triangle_formation_results.md`, restating key metrics (96-second window, aspect ratio unity, altitude 520 km).
- Present orbital element reconstruction (Table 2 in the memorandum) verifying plane allocations and RAAN separation.
- Discuss maintenance and responsiveness metrics, referencing Table 3 and emphasising margins against MR-5–MR-7 thresholds.
- Integrate Tehran daily pass alignment results to demonstrate centroid compliance and Monte Carlo robustness.

### 6.2 Comparative Analysis Requirements
- Contrast deterministic formation behaviour with Monte Carlo dispersions, illustrating how mean and \(p_{95}\) metrics support compliance cases.
- Evaluate how drag dispersion results (e.g., \(p_{95} = 3.6\,\text{m}\) along-track shift) inform maintenance scheduling.
- Compare the Tehran scenario with the global constants in `config/project.yaml` to determine how baseline assumptions translate to results.
- Critically assess the limitations of the current Keplerian propagation model and propose inclusion of higher-order perturbations where necessary.

### 6.3 Visual and Tabular Presentation
- Recommend figures derived from `artefacts/run_20251018_1207Z/injection_recovery_cdf.svg` and similar CSV datasets.
- Construct tables summarising key metrics across runs, including maintenance budgets, command latency, and centroid offsets.
- Suggest inclusion of STK visualisations (3D orbit view, ground track overlay) to complement Python-derived metrics.
- Ensure all visuals are produced as SVGs to satisfy repository guidelines.

### 6.4 Discussion Points
- Interpret how the ninety-six-second window supports mission applications (tri-stereo imaging, infrastructure monitoring) as described in `docs/concept_of_operations.md`.
- Evaluate operational resilience in light of command latency margins and Monte Carlo recovery success.
- Discuss the sufficiency of delta-v budgets relative to the 15 m/s cap, referencing maintenance schedules.
- Consider risk factors identified in `docs/concept_of_operations.md` (e.g., ground station outage, propellant margins) and relate them to simulation outcomes.

### 6.5 Chapter 6 Deliverables
- Integrated results narrative combining simulation outputs, STK validations, and operational implications.
- Critical discussion section weighing strengths and limitations of the current evidence base.
- Recommendations for additional analyses (e.g., higher fidelity perturbations, thermal modelling) informed by gaps observed in earlier chapters.

### 6.6 Chapter 6 Exit Criteria
- [ ] Result tables and figures are fully sourced with repository artefacts.
- [ ] Discussion addresses mission applicability, resilience, and maintenance implications.
- [ ] Limitations of current modelling are transparently stated with proposed remediation steps.
- [ ] Compliance with MR-1–MR-7 is reiterated with supporting evidence references.

## Chapter 7: Conclusions, Recommendations, and Future Work
### 7.1 Conclusion Framework
- Summarise mission feasibility by synthesising Chapter 6 findings with requirement satisfaction evidence from `docs/compliance_matrix.md`.
- Restate key achievements: daily 90-second geometry, STK interoperability, maintenance budget adherence.
- Articulate the residual uncertainties or assumptions requiring continued monitoring.

### 7.2 Recommendations
- Propose near-term actions, such as extending Monte Carlo campaigns with atmospheric variability or integrating solar radiation pressure models.
- Recommend documentation updates (e.g., `docs/system_requirements.md`, `docs/verification_plan.md`) to capture new evidence or assumptions.
- Suggest stakeholder engagements (e.g., Scenario review boards, SERB updates) aligned with the roadmap milestones.
- Encourage automation enhancements for baseline generation once `sim/scripts/baseline_generation.py` is implemented.

### 7.3 Future Research Directions
- Identify advanced control strategies (drag modulation, differential lift) that could be investigated using the existing toolchain.
- Highlight potential expansion to alternative targets (e.g., mid-latitude cities listed in `config/project.yaml` window targets) for comparative analysis.
- Recommend development of integrated thermal, attitude, or payload performance models to enrich mission realism.
- Advocate for data assimilation studies linking STK outputs with operational dashboards described in `docs/interactive_execution_guide.md`.

### 7.4 Chapter 7 Exit Criteria
- [ ] Conclusions directly trace back to evidence presented earlier in the dossier.
- [ ] Recommendations include responsible teams or artefact owners where applicable.
- [ ] Future work proposals cite enabling scripts or configuration pathways.
- [ ] STK interoperability considerations remain visible where recommendations affect export or validation workflows.

## Appendix A: Repository Evidence Map
- `README.md` – Orientation to mission intent, Makefile automation, and CI expectations.
- `docs/project_overview.md` – Academic framing and recent verification evidence summary.
- `docs/mission_requirements.md` – Requirement statements MR-1 to MR-7 with verification approaches.
- `docs/system_requirements.md` – Derived requirement taxonomy and compliance status references.
- `docs/compliance_matrix.md` – Cross-reference table tying requirements to evidence tags [EV-1]–[EV-5].
- `docs/triangle_formation_results.md` – Detailed memorandum of triangular formation metrics and maintenance campaign.
- `docs/tehran_daily_pass_scenario.md` – Scenario overview with RAAN alignment and STK validation notes.
- `docs/how_to_import_tehran_daily_pass_into_stk.md` – Step-by-step STK 11.2 ingestion procedure.
- `docs/verification_plan.md` – Verification strategy, matrix, schedule, and resource plan.
- `docs/interactive_execution_guide.md` – Instructions for web and debug tooling.
- `artefacts/triangle_run/` – Curated triangle formation snapshot mirroring `run_20251018_1424Z` outputs.
- `artefacts/run_20251018_1207Z/` – Maintenance and responsiveness dataset covering MR-5 through MR-7.
- `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` – Locked RAAN alignment dataset for MR-2 evidence.
- `sim/formation/triangle.py` – Formation propagation and metric computation engine.
- `sim/scripts/run_triangle.py` – CLI entry point for triangular formation simulations.
- `sim/scripts/run_scenario.py` – General scenario runner with RAAN optimisation and STK export stages.
- `tests/unit/test_triangle_formation.py` – Regression guard for formation metrics and maintenance assumptions.
- `tests/integration/test_simulation_scripts.py` – Pipeline smoke tests and artefact validation.
- `tests/test_stk_export.py` – Export-format regression coverage ensuring STK compatibility.

## Appendix B: Run Regeneration Playbooks
- **Triangular Formation Reproduction.** Execute `make setup` followed by `make triangle`; inspect `artefacts/triangle/triangle_summary.json` and compare to `artefacts/triangle_run/`.
- **Tehran Daily Pass Scenario.** Run `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ`; validate outputs per `docs/how_to_import_tehran_daily_pass_into_stk.md`.
- **Maintenance Campaign Update.** Launch `python -m sim.scripts.run_triangle_campaign --output-dir artefacts/run_YYYYMMDD_hhmmZ_campaign` to refresh drag and injection studies, updating the ledger in `docs/_authoritative_runs.md`.
- **Interactive Debug Session.** Invoke `python run_debug.py --triangle` to stream verbose logs to `debug.txt` and populate `artefacts/debug/<timestamp>/` with CSV traces.
- **STK Automation.** Use `python sim/scripts/run_stk_tehran.py --output-dir artefacts/stk_runs --dry-run` on non-Windows systems to produce Connect scripts and STK-ready exports.
- **Baseline Generation Placeholder.** Document expectations for `sim/scripts/baseline_generation.py` once implemented, referencing the raising of `NotImplementedError` enforced in `tests/integration/test_simulation_scripts.py`.

## Appendix C: Writing and Review Standards
- Apply the acceptance checklists embedded throughout `docs/system_requirements.md`, `docs/concept_of_operations.md`, and `docs/compliance_matrix.md` as templates for chapter-level peer reviews.
- Ensure every factual assertion traces to a repository artefact or peer-reviewed source published between 2019 and 2025, unless citing foundational work (e.g., D'Amico 2005) explicitly marked as enduring.
- Maintain parity with the repository's emphasis on reproducibility: include run IDs, seeds, and configuration versions alongside narrative claims.
- Document all modelling limitations, including Keplerian assumptions, STK sampling intervals, and communication availability thresholds.
- Encourage reviewers to replicate key results using the provided playbooks, logging outcomes in a review register appended to the final dossier.

## References
- [Ref1] D'Amico, S., Montenbruck, O., Ardaens, J.-S., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
- [Ref2] Wertz, J. R., Everett, D. F., Puschell, J. J. (eds.), *Space Mission Engineering: The New SMAD*, Microcosm Press, 2011.
- [Ref3] NASA-STD-7009A, *Standards for Models and Simulations*, National Aeronautics and Space Administration, 2016.
- [Ref4] ECSS-E-ST-10-02C, *Verification*, European Cooperation for Space Standardization, 2010.
- [Ref5] CCSDS 130.0-G-3, *TM Synchronization and Channel Coding*, Consultative Committee for Space Data Systems, 2017.

### 1.8 Literature Review Task Breakdown
1. Catalogue every peer-reviewed paper between 2019 and 2025 that discusses triangular or polyhedral formation flying in sun-synchronous orbits; map each paper to MR-3 or MR-4 coverage.
2. For each article identified in Task 1, record the propagation assumptions (e.g., two-body, \(J_2\), atmospheric drag) and compare them with the implementations observed in `sim/formation/triangle.py`.
3. Extract delta-v maintenance strategies from published missions such as TanDEM-X or Cartwheel, contrasting them with the annual \(14.04\,\text{m/s}\) requirement satisfaction observed in `artefacts/run_20251018_1207Z/maintenance_summary.csv`.
4. Investigate telemetry latency case studies for single-ground-station missions and benchmark them against the \(1.53\,\text{h}\) command latency recorded in `artefacts/run_20251018_1207Z/command_windows.csv`.
5. Analyse injection recovery literature to identify algorithms achieving ≥95% success at ±5 km dispersions, verifying compatibility with the 300-sample Monte Carlo archive.
6. Document STK workflow discussions in conference proceedings, especially those referencing text ephemeris ingestion, to reinforce the exporter guidance already codified in `docs/stk_export.md`.
7. Compile a comparative matrix showing how each literature source supports MR-1–MR-7, SRD-F/P/O/R classes, or STK interoperability.
8. Summarise methodological innovations discovered during the review and note whether any could be integrated into `sim/scripts/run_triangle_campaign.py` for future campaigns.
9. Record any contradictions or alternative assumptions identified in the literature and plan how to reconcile them with the repository baseline.
10. Verify that all sources are logged with DOIs or persistent identifiers to streamline referencing in the final dossier.

### 1.9 Literature Review Artefact Control
- Store annotated bibliographies within `docs/references/literature_notes/` using ISO-8601 filenames to maintain traceability.
- Include cross-references to run IDs when a literature source directly informs a reproduction attempt or scenario configuration.
- Flag any literature-driven model updates in a change proposal, ensuring the Configuration Control Board can review the impact on existing run evidence.
- Update the compliance matrix commentary if new literature strengthens or challenges existing verification claims.

### 1.10 Chapter 1 Review Gate
- Convene a peer review with the Mission Analysis Cell to validate that literature coverage supports all mission objectives.
- Document review outcomes and action items in a `docs/reviews/chapter1_review_YYYYMMDD.md` file, referencing commit hashes for transparency.
- Only progress to Chapter 2 drafting once all action items are closed or deferred with documented rationale.

### 2.7 Configuration Data Tables
- Create a table summarising each configuration parameter, including column headings for `Parameter`, `Value`, `Source File`, `Linked Script`, `Dependent Run`, and `Verification Reference`.
- Populate the table with entries such as `formation.side_length_m`, `formation.duration_s`, `command.contact_range_km`, `drag_dispersion.samples`, and `command.station.latitude_deg`.
- Reference `tests/unit/test_triangle_formation.py` and `tests/integration/test_simulation_scripts.py` within the `Verification Reference` column where relevant.
- Add narrative text explaining how the table supports traceability reviews conducted during SERB audits.

### 2.8 Configuration Sensitivity Study Prompts
- Propose sensitivity sweeps for RAAN perturbations ±0.05° to gauge centroid tolerance margins beyond the locked alignment.
- Suggest evaluations of Monte Carlo sample sizes (e.g., 300 vs 500) to determine convergence of injection recovery statistics.
- Recommend exploring variations of the command contact range to assess single-station coverage resilience.
- Document how these sweeps would be implemented via `sim/scripts/run_scenario.py` or adapted into new campaign scripts.

### 2.9 Configuration Review Workflow
- Establish a checklist for configuration updates requiring reviews: change description, impacted missions requirements, affected scripts, regression coverage updates, and STK validation obligations.
- Encourage maintainers to submit configuration updates via dedicated pull requests referencing the review checklist.
- Archive signed approval records in `docs/reviews/configuration/`, ensuring the latest decision is easily accessible.
- Require updates to `docs/_authoritative_runs.md` whenever a configuration change triggers a new authoritative run.

### 3.8 Simulation Logging Expectations
- Define logging levels for each script (`INFO` for stage start/end, `DEBUG` for detailed metric outputs, `WARNING` for convergence anomalies).
- Mandate inclusion of run IDs, seeds, configuration versions, and Git commit hashes in log headers for reproducibility.
- Encourage storing JSON run manifests capturing environment details (Python version, dependency hashes) alongside artefacts.
- Integrate logging summaries into the final dossier to demonstrate traceability and audit readiness.

### 3.9 Automation Enhancement Ideas
- Propose implementing a scheduler for `sim/scripts/run_triangle_campaign.py` to maintain quarterly rerun cadence automatically.
- Outline potential CLI enhancements (e.g., `--compare` flag) enabling automated diffing between new and authoritative run metrics.
- Suggest integration of STK Connect execution results into the scenario runner to automate validation logging.
- Recommend expanding the FastAPI service to expose endpoints for retrieving run metadata, enabling external dashboards.

### 3.10 Simulation Chapter Review Checklist
- [ ] Documented stage sequence matches `tests/integration/test_simulation_scripts.py` expectations.
- [ ] All scripts have identified logging and error-handling behaviours.
- [ ] Suggested enhancements are prioritised with responsible teams noted.
- [ ] Dependencies on optional packages (SciPy, poliastro) are accompanied by mitigation plans.

### 4.7 Detailed Run Narratives
- Draft a sub-section for each authoritative run describing setup, execution parameters, outputs, validation steps, and lessons learned.
- Include quotes or paraphrased content from `docs/triangle_formation_results.md` and `docs/tehran_daily_pass_scenario.md` to maintain alignment.
- Highlight how each run contributes to closing specific compliance items in `docs/compliance_matrix.md`.
- Record operator notes such as RAAN solver iterations or Monte Carlo convergence diagnostics if available.

### 4.8 Evidence Quality Assurance Steps
- Implement checksum verification for JSON and CSV artefacts in each run directory using the configured `sha256` algorithm from `config/project.yaml`.
- Ensure STK export directories contain consistent file counts and naming conventions before acceptance.
- Compare regenerated runs against authoritative snapshots to quantify drift in metrics, documenting acceptable tolerances.
- Archive reproduction scripts or notebooks used during the analysis alongside the run directory.

### 4.9 Run Chapter Review Checklist
- [ ] Every authoritative run has an accompanying narrative and metric summary table.
- [ ] Evidence quality checks (checksums, file counts) are logged and referenced.
- [ ] Links to compliance documentation are explicit and up to date.
- [ ] Reproduction instructions have been validated by at least one independent analyst.

### 5.6 STK Workflow Expansion
- Encourage capturing STK `scenario.log` outputs and storing them alongside the run directories for audit purposes.
- Recommend recording Connect command transcripts when using `sim/scripts/run_stk_tehran.py` to automate validation playback.
- Suggest establishing a catalogue of STK workspace templates pre-configured with Tehran facilities for rapid verification.
- Advocate for capturing screenshot metadata (camera parameters, epoch stamps) to accompany each SVG image included in the dossier.

### 5.7 STK Troubleshooting Guide Prompts
- Document common import errors (e.g., non-monotonic ephemeris, invalid identifiers) and corresponding resolutions referencing exporter code sections.
- Provide guidance on reconciling frame mismatches if analysts attempt to import ECI data with incorrect assumptions.
- Offer tips for verifying facility coordinates and ensuring ground tracks align with expected geography.
- Encourage noting STK version, licence features, and operating system details in validation logs.

### 5.8 STK Chapter Review Checklist
- [ ] All export components (.e, .sat, .gt, .fac, .int, .evt, .sc) are catalogued with descriptions.
- [ ] Validation steps include screenshot capture, metric comparison, and log archival.
- [ ] Troubleshooting guidance references actual exporter safeguards and repository instructions.
- [ ] Compliance linkages to MR-2, SRD-P-001, and SRD-O-002 are explicit.

### 6.7 Result Visualisation Matrix
| Visual ID | Description | Source Artefact | Intended Chapter Placement | Notes |
| --- | --- | --- | --- | --- |
| V-01 | Centroid cross-track time history overlaying deterministic and Monte Carlo \(p_{95}\) envelopes. | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json` | Chapter 6 results | Present deterministic mid-point markers for clarity. |
| V-02 | Maintenance \(\Delta v\) budget waterfall diagram showing weekly contributions. | `artefacts/run_20251018_1207Z/maintenance_summary.csv` | Chapter 6 results | Emphasise margin to the 15 m/s cap. |
| V-03 | Injection recovery cumulative distribution (SVG adaptation). | `artefacts/run_20251018_1207Z/injection_recovery_cdf.svg` | Chapter 6 results | Annotate \(p_{95} = 0.041\,\text{m/s}\). |
| V-04 | STK 3D view of triangular formation during midpoint epoch. | STK validation capture | Chapter 6 results | Ensure camera metadata recorded. |
| V-05 | Table summarising orbital elements for SAT-1/2/3 with plane assignments. | `docs/triangle_formation_results.md` Table 2 | Chapter 6 results | Include uncertainties if available. |

### 6.8 Discussion Question Bank
- How does the ninety-six-second window support the sensor duty cycles and dwell times recorded in `config/scenarios/tehran_daily_pass.json`?
- What is the operational impact if command latency increases to the MR-5 limit of 12 hours, and how do maintenance plans adapt?
- Which environmental perturbations (e.g., solar storms) could erode centroid alignment margins, and what mitigation strategies exist?
- How resilient is the mission architecture to loss of one spacecraft, and what contingency operations are envisaged?
- In what ways could additional ground stations reduce risk without violating single-station assumptions documented in the ConOps?

### 6.9 Result Chapter Review Checklist
- [ ] Figures and tables correspond to the visualisation matrix with correct sources.
- [ ] Discussion responds to the question bank with evidence-backed arguments.
- [ ] Operational implications reference ConOps scenarios and mission requirements.
- [ ] Limitations and future enhancements are cross-referenced with recommendations in Chapter 7.

### 7.5 Recommendation Tracking
- Assign each recommendation a unique identifier (e.g., REC-01) and list responsible owners such as Mission Analysis Cell, Ground Segment Integration Team, or Systems Engineering Office.
- Document expected closure dates and review milestones for each recommendation.
- Track dependencies (e.g., new script features, updated configuration baselines) required to implement the recommendations.
- Incorporate recommendation status updates into SERB agendas and project roadmap revisions.

### 7.6 Future Work Planning Matrix
| Future Work ID | Description | Enabling Artefacts | Proposed Owner | Target Review |
| --- | --- | --- | --- | --- |
| FW-01 | Implement higher-order perturbation models (SRP, third-body) in the triangle simulator. | `sim/formation/triangle.py`, `tests/unit/test_triangle_formation.py` | Formation Dynamics Team | Q1 2026 |
| FW-02 | Extend Monte Carlo campaigns to cover ±10 km dispersions and variable inclination offsets. | `sim/scripts/run_triangle_campaign.py` | Mission Analysis Cell | Q2 2026 |
| FW-03 | Integrate baseline generation automation once placeholder is implemented. | `sim/scripts/baseline_generation.py`, `tests/integration/test_simulation_scripts.py` | Systems Engineering Office | Q3 2026 |
| FW-04 | Develop multi-target scenario comparisons using additional window targets in `config/project.yaml`. | Mission Planning Team | Q4 2026 |
| FW-05 | Publish STK automation toolkit and Connect script library for external partners. | `sim/scripts/run_stk_tehran.py`, `docs/how_to_import_tehran_daily_pass_into_stk.md` | Ground Segment Integration Team | Q2 2026 |

### 7.7 Conclusion Chapter Review Checklist
- [ ] Conclusions succinctly restate mission feasibility backed by quantified evidence.
- [ ] Recommendations and future work items are tracked with owners and timelines.
- [ ] Dependencies on STK interoperability and configuration control are reiterated.
- [ ] Outstanding risks or assumptions are acknowledged with mitigation plans.

## Appendix D: Glossary of Repository-Specific Terms
- **Access Window:** Ninety-second minimum simultaneous observation period mandated by MR-3, validated by `artefacts/triangle_run/triangle_summary.json`.
- **Authoritative Run:** Configuration-controlled dataset listed in `docs/_authoritative_runs.md`, serving as baseline evidence for compliance.
- **Command Window:** Uplink opportunity metrics captured in `artefacts/run_20251018_1207Z/command_windows.csv`, tied to MR-5 latency checks.
- **Compliance Matrix:** Document in `docs/compliance_matrix.md` summarising requirement satisfaction status with evidence tags.
- **Formation Maintenance Event:** Entry within STK exports representing manoeuvres, produced by `tools/stk_export.py`.
- **Ground Distance Tolerance:** \(350\,\text{km}\) threshold defined in `config/scenarios/tehran_triangle.json` for centroid evaluation.
- **Injection Recovery Catalogue:** Monte Carlo dataset stored as `artefacts/run_20251018_1207Z/injection_recovery.csv` demonstrating robustness.
- **Run Ledger:** Section of `docs/_authoritative_runs.md` maintaining references to compliance-supporting runs.
- **Scenario Summary:** JSON output generated by `sim/scripts/run_scenario.py`, logging stage sequence and metrics.
- **STK Export Directory:** Folder created by simulation scripts containing `.sc`, `.sat`, `.e`, `.gt`, `.fac`, `.int`, `.evt` files for ingestion.

## Appendix E: Narrative Outline Template
1. **Introduction Section:** Frame mission objectives, reference `docs/project_overview.md`, and state research questions.
2. **Background:** Summarise literature findings aligned with Work Packages WP1–WP5.
3. **Methodology:** Detail configurations (`config/project.yaml`, `config/scenarios/*`), simulation scripts, and validation workflows.
4. **Results:** Present metrics, tables, and figures produced from authoritative runs and STK validation.
5. **Discussion:** Address question bank prompts, operational implications, and modelling limitations.
6. **Conclusions:** Restate evidence-backed achievements and residual uncertainties.
7. **Recommendations:** Provide actionable items referencing responsible teams and enabling artefacts.
8. **Future Work:** Align with planning matrix FW-01–FW-05.
9. **References:** Combine repository artefact citations and external literature `[RefX]` entries.
10. **Appendices:** Include reproduction instructions, validation logs, and supplementary analyses.

## Appendix F: Peer Review Log Template
- **Review ID:** PR-CHX-YYYYMMDD.
- **Chapter or Section:** Identify the chapter under review.
- **Participants:** List reviewers and roles.
- **Artefacts Examined:** Reference commit hashes, run directories, and configuration files assessed.
- **Findings:** Summarise observations, categorising them as major, minor, or informational.
- **Actions:** Detail remediation steps with owners and due dates.
- **Follow-Up:** Record closure evidence, including rerun IDs or updated documents.

## Appendix G: Integration with Verification and Validation Plan
- Map each verification method in `docs/verification_plan.md` to chapters where its evidence is reported.
- Ensure schedule milestones (VRR, Simulation Qualification Campaign, HIL tests) are referenced in relevant narrative sections.
- Note resource allocations (e.g., £120,000 HIL facility cost) when discussing future work or recommendations requiring funding.
- Align validation activities (stakeholder scenario reviews, simulation-in-the-loop exercises) with the chapter structure to avoid duplication.

## Appendix H: Risk Register Alignment
- Cross-reference operational risks (R-01 to R-05) in `docs/concept_of_operations.md` with analytic evidence or mitigation discussions.
- When discussing command latency or propellant margins, cite the corresponding risk entries and state how current analyses address them.
- Document any new risks identified during analysis and propose how they should be incorporated into the next risk register update.
- Encourage coordination with the Anomaly Response Board for risks affecting MR-4–MR-7 compliance.

## Appendix I: Artefact Archiving Checklist
- Confirm each run directory includes `run_metadata.json` summarising seeds, configuration versions, and tool versions.
- Ensure CSV files are encoded in UTF-8 with newline-terminated rows for compatibility with data processing tools.
- Verify JSON files contain ISO 8601 timestamps and explicit units in key names where applicable.
- Store STK validation screenshots as SVG files with descriptive filenames and include textual annotations where necessary.

## Appendix J: Change Control Touchpoints
- Identify chapters affected when `config/project.yaml` or scenario files are updated, ensuring cross-document consistency.
- Require updates to `docs/final_delivery_manifest.md` whenever new deliverables are introduced.
- Encourage tagging Git releases when major evidence sets (e.g., new maintenance campaigns) are baselined.
- Maintain a summary of outstanding change requests appended to the dossier for transparency.

## Appendix K: External Engagement Guidance
- Coordinate with external partners (e.g., ESA Redu, MBRSC) when discussing shared ground-station operations, referencing agreements mentioned in `docs/concept_of_operations.md`.
- Prepare briefing materials summarising the mission concept using the narrative outline template, ensuring STK visuals and key metrics are included.
- Capture stakeholder feedback and note how it influences configuration or simulation updates in subsequent revisions.
- Align external communication with compliance artefacts to avoid divulging non-baselined assumptions.

## Appendix L: Bibliography Management Notes
- Use citation management software to export references in BibTeX and CSL-JSON formats compatible with the writing workflow.
- Maintain a `docs/references/README.md` explaining filing conventions and review cycles.
- Schedule quarterly bibliography audits to ensure new literature is incorporated and obsolete references are retired.
- Include placeholder references for anticipated publications (e.g., forthcoming mission analyses) with clear annotations.

## Appendix M: Quality Assurance Metrics
- Track the number of authoritative runs referenced per chapter and ensure they meet coverage expectations.
- Monitor the ratio of external literature citations to repository artefact citations to maintain balance.
- Record peer review cycle counts and average closure times for action items.
- Document STK validation success rates and any recurring issues requiring engineering attention.

### 6.10 Integration with Mission Roadmap
- Cross-reference each analytical milestone with the stage gates defined in `docs/project_roadmap.md`, ensuring Stage 4 perturbation studies and Stage 5 verification activities are fully addressed.
- Provide timeline annotations showing when each authoritative run was executed relative to roadmap milestones.
- Identify any roadmap tasks that remain outstanding and note which chapter or appendix should capture their progress updates.
- Recommend adjustments to the roadmap if new analyses or validation steps extend beyond the original schedule.

### 7.8 Communication Plan Elements
- Draft executive summaries for senior stakeholders emphasising compliance achievements and remaining risks.
- Prepare technical briefings for engineering teams focusing on simulation upgrades, STK validation, and configuration changes.
- Craft outreach materials for external partners summarising mission objectives, run evidence, and collaborative opportunities.
- Schedule dissemination milestones aligned with review boards and delivery manifest updates.

## Appendix N: Data Schema Summary
| Artefact | Format | Key Fields | Description | Referenced In |
| --- | --- | --- | --- | --- |
| `triangle_summary.json` | JSON | `metrics`, `samples`, `geometry` | Comprehensive record of formation metrics and time series. | Chapters 3, 4, 6 |
| `maintenance_summary.csv` | CSV | `spacecraft_id`, `annual_delta_v_mps` | Aggregated maintenance budget by spacecraft. | Chapters 3, 4, 6 |
| `command_windows.csv` | CSV | `window_index`, `start_utc`, `latency_hours` | Command latency ledger underpinning MR-5 evidence. | Chapters 4, 6 |
| `injection_recovery.csv` | CSV | `sample_id`, `delta_v_mps`, `success` | Monte Carlo recovery catalogue supporting MR-7. | Chapters 4, 6 |
| `drag_dispersion.csv` | CSV | `sample_id`, `ground_distance_delta_km` | Drag sensitivity data for robustness assessments. | Chapters 3, 4 |
| `scenario_summary.json` | JSON | `stage_sequence`, `metrics`, `artefacts` | Scenario pipeline output summarising Tehran daily pass runs. | Chapters 3, 4, 5 |
| `monte_carlo_summary.json` | JSON | `centroid_abs_cross_track_km`, `worst_spacecraft_km` | Statistical evidence for centroid compliance. | Chapters 4, 5, 6 |
| `deterministic_summary.json` | JSON | `midpoint_metrics`, `ground_track` | Deterministic centroid offsets for MR-2 compliance. | Chapters 4, 6 |
| `command_windows.svg` | SVG | Visual timeline annotations | Optional figure illustrating command opportunities. | Chapter 6 |
| `run_metadata.json` | JSON | `run_id`, `seed`, `config_commit` | Reproducibility ledger for each run directory. | Appendices B, I |

## Appendix O: Writing Schedule and Deliverable Timeline
- Week 1: Complete Chapter 1 literature review drafting, gather bibliographic assets, schedule peer review.
- Week 2: Draft Chapters 2 and 3 focusing on configurations and simulation pipeline; execute reproduction checks for key scripts.
- Week 3: Compile Chapter 4 run evidence, verify metrics against authoritative artefacts, refresh compliance cross-links.
- Week 4: Prepare Chapter 5 STK validation narrative and gather required screenshots and logs.
- Week 5: Draft Chapter 6 results and discussion, generating tables and figures using curated data.
- Week 6: Finalise Chapter 7 conclusions and recommendations; integrate appendices and peer review logs.
- Week 7: Conduct comprehensive quality assurance review, reconcile action items, and prepare final submission package referencing `docs/final_delivery_manifest.md`.

## Appendix P: Editorial Standards Checklist
- [ ] Consistent use of British English spelling across all chapters and appendices.
- [ ] Tables and figures include captions, source citations, and units.
- [ ] All inline code references use backticks and accurate relative paths.
- [ ] Mathematical expressions employ inline LaTeX syntax where appropriate.
- [ ] Acronyms are expanded on first use in each chapter.
- [ ] Footnotes or endnotes reference `[RefX]` entries where external literature is cited.

## Appendix Q: Stakeholder Mapping
| Stakeholder | Interest | Relevant Chapters | Key Artefacts |
| --- | --- | --- | --- |
| Mission Analysis Cell | Propagation fidelity, formation metrics | Chapters 1–4, 6 | `sim/formation/triangle.py`, `artefacts/triangle_run/` |
| Ground Segment Integration Team | Command latency, STK validation | Chapters 3, 4, 5, 6 | `artefacts/run_20251018_1207Z/command_windows.csv`, STK exports |
| Systems Engineering Office | Requirement traceability | Chapters 2, 4, 5, 7 | `docs/system_requirements.md`, `docs/compliance_matrix.md` |
| Flight Dynamics Team | Maintenance strategies | Chapters 3, 4, 6, 7 | `artefacts/run_20251018_1207Z/maintenance_summary.csv` |
| External Partners (ESA, MBRSC) | Ground-station coordination | Chapters 5, 7, Appendices K, Q | `docs/concept_of_operations.md`, STK visuals |

## Appendix R: Review Artefact Distribution Plan
- Publish draft chapters to the internal documentation portal with access controls aligned to stakeholder roles.
- Provide zipped bundles of relevant artefacts (`triangle_run`, `run_20251020_1900Z_tehran_daily_pass_locked`) for reviewers requiring offline access.
- Include STK packages and screenshots in review kits to facilitate independent validation.
- Require reviewers to acknowledge receipt and confirm environment readiness before review deadlines.

## Appendix S: Metrics for Continuous Improvement
- Establish baseline turnaround time for reproducing `run_20251018_1207Z` and monitor for regressions.
- Track frequency of STK validation issues and categorise root causes (export errors, configuration drift, analyst oversight).
- Monitor citation diversity across chapters to ensure balanced coverage of external sources.
- Record number of automated tests executed per release (`pytest`, `make lint`, `make simulate`) and tie them to documentation updates.

## Appendix T: Change Impact Assessment Template
- **Change Description:** Summarise proposed modification (e.g., updated drag model).
- **Affected Artefacts:** List configuration files, scripts, tests, and runs impacted.
- **Verification Plan Updates:** Identify new activities required in `docs/verification_plan.md`.
- **Compliance Impact:** Note requirements potentially affected and evidence needing refresh.
- **STK Validation:** State whether new exports or re-validation is necessary.
- **Approval Status:** Capture decision, approvers, and date.

## Appendix U: Archive and Publication Strategy
- Store final dossier and supporting artefacts under `docs/deliverables/mission_research_brief/` with versioned filenames.
- Generate a checksum manifest for the publication package and archive it with the final delivery manifest.
- Coordinate with configuration management to tag a repository release corresponding to the dossier submission.
- Prepare a public-facing summary (if authorised) that removes sensitive configuration details while highlighting mission achievements.

## Appendix V: Compliance Status Dashboard Outline
- Create a dashboard summarising MR and SRD compliance statuses using data from `docs/compliance_matrix.md`.
- Include visual indicators for evidence freshness (e.g., days since last run) and upcoming verification milestones.
- Integrate links to run directories and STK exports for quick access.
- Plan updates to the dashboard following each major run or documentation revision.

## Appendix W: Scenario Extension Prompts
- Explore modelling alternative targets listed in `config/project.yaml` (AuroraScience, EquatorialEnergy) to demonstrate methodology portability.
- Outline modifications required in scenario JSON files to retarget the formation while preserving baseline tolerances.
- Identify new literature or datasets needed to justify additional targets, such as regional weather patterns or infrastructure priorities.
- Recommend updating documentation to reflect any expanded mission scope.

## Appendix X: Data Integrity Validation Scripts
- Develop Python notebooks or scripts to automatically compare regenerated runs against authoritative baselines, highlighting deviations.
- Integrate these scripts into CI pipelines to trigger alerts when metrics drift beyond acceptable thresholds.
- Document usage instructions within the dossier to encourage adoption by analysts.
- Archive validation script outputs alongside run artefacts for audit purposes.

## Appendix Y: Lessons Learned Capture
- After completing the dossier, facilitate a retrospective with representatives from analysis, simulation, and operations teams.
- Record successes, challenges, and improvement opportunities in `docs/reviews/lessons_learned_YYYYMMDD.md`.
- Translate lessons into actionable updates for scripts, configurations, or documentation templates.
- Share outcomes with stakeholders to reinforce continuous improvement culture.

## Appendix Z: Final Submission Checklist
- [ ] All chapters and appendices reviewed and approved by designated stakeholders.
- [ ] Compliance matrix updated with references to the new dossier.
- [ ] STK validation logs and screenshots archived alongside the publication package.
- [ ] Bibliography cross-checked for completeness and formatting consistency.
- [ ] Final document converted to desired distribution format (e.g., PDF) with bookmarks reflecting chapter structure.
- [ ] Repository release tagged and noted in project communication channels.

## Appendix AA: Figure Caption Template
1. **Title:** Concise descriptor of the visual (e.g., "Centroid Offset Over Time").
2. **Source:** Cite the artefact or run directory used to generate the figure.
3. **Description:** Summarise the insight communicated, referencing mission requirements where applicable.
4. **Assumptions:** List key modelling or processing assumptions.
5. **Validation:** Note whether the figure has been cross-checked against STK or other independent tools.
6. **Revision History:** Track updates to the figure across drafts with dates and responsible analysts.

## Appendix AB: Citation Format Guidance
- Use numeric bracketed references `[RefX]` for external literature consistent with the repository's documentation style.
- Cite repository artefacts inline using backticks and relative paths (e.g., `artefacts/run_20251018_1207Z/triangle_summary.json`).
- Include access dates for online references and note version numbers for standards or manuals.
- Maintain a separate bibliography section for proprietary or internal documents if necessary.
- Ensure each reference is mentioned in the text; remove unused entries before final submission.

## Appendix AC: Data Processing Workflow Notes
- Standardise units during data processing (kilometres, metres per second) to match configuration files and STK exports.
- Use Pandas for CSV manipulation and maintain notebooks in `notebooks/` with explanatory markdown cells.
- Store intermediate datasets under `artefacts/analysis_working/` with clear naming conventions if needed.
- Document any data cleaning steps (e.g., outlier removal, smoothing) in the dossier to preserve transparency.
- Verify that processed data reproduces key metrics before inclusion in tables or figures.

## Appendix AD: Accessibility Considerations
- Provide text alternatives for all figures and diagrams to support accessible dissemination.
- Ensure tables use header rows and avoid merged cells for screen-reader compatibility.
- Select colour palettes that remain legible in grayscale reproductions and for colour-vision deficiencies.
- Offer hyperlinks to interactive artefacts (e.g., Plotly outputs) where appropriate while maintaining static equivalents.

## Appendix AE: Translation and Localisation Notes
- Prepare executive summaries in multiple languages if required by stakeholders, ensuring technical accuracy is preserved.
- Maintain glossaries of mission-specific terminology to support translators.
- Highlight sections containing culturally sensitive or region-specific references for careful adaptation.
- Coordinate localisation reviews with regional partners familiar with Tehran mission objectives.

## Appendix AF: Backup and Recovery Plan for Documentation
- Schedule automated backups of the `docs/` directory and key artefact snapshots to secure storage.
- Keep off-site copies of final deliverables and critical run artefacts in compliance with organisational policies.
- Document restoration procedures to ensure rapid recovery in the event of data loss.
- Test backup integrity quarterly, recording outcomes in configuration management logs.

## Appendix AG: Alignment with Institutional Standards
- Verify that the dossier complies with institutional formatting guidelines (fonts, margins, citation style).
- Confirm adherence to data security policies when referencing run artefacts or STK outputs.
- Ensure legal or export-control considerations are reviewed when discussing ground station partnerships or mission capabilities.
- Coordinate with institutional review boards if human factors or stakeholder interviews are included.

## Appendix AH: Checklist for Future Updates
- [ ] Review new simulation runs for inclusion in Chapter 4 and update metrics accordingly.
- [ ] Audit configuration changes since the last publication and revise Chapter 2 narratives.
- [ ] Incorporate newly published literature and refresh Chapter 1 citations.
- [ ] Update STK validation notes to reflect changes in workflow or tooling.
- [ ] Reassess recommendations and future work items, closing those completed and adding new actions as needed.

## Appendix AI: Communication Artefact Inventory
| Artefact | Purpose | Owner | Update Frequency |
| --- | --- | --- | --- |
| Mission brief slides | Executive summary for leadership reviews | Project Manager | Quarterly |
| Technical white paper | Detailed analysis for engineering stakeholders | Mission Analysis Cell | As required |
| STK demonstration files | Interactive validation for external partners | Ground Segment Integration Team | After each major run |
| FAQ document | Rapid responses to common stakeholder queries | Systems Engineering Office | Semi-annually |

## Appendix AJ: Knowledge Transfer Plan
- Schedule onboarding sessions for new analysts covering repository layout, configuration files, and simulation tooling.
- Develop recorded tutorials demonstrating key workflows (e.g., running `sim/scripts/run_triangle.py`, importing into STK).
- Pair new team members with experienced mentors for their first reproduction exercise.
- Maintain a question-and-answer log to capture clarifications for future reference.

## Appendix AK: Compliance Audit Preparation
- Assemble a binder (digital or physical) containing compliance matrix extracts, run summaries, STK validation logs, and peer review records.
- Pre-stage responses to anticipated auditor questions regarding reproducibility, configuration control, and validation coverage.
- Conduct internal mock audits to verify readiness and refine documentation.
- Track auditor findings and ensure corrective actions are recorded with closure evidence.

## Appendix AL: Sustainability and Resource Considerations
- Document computational resources required for simulations (CPU hours, memory) to inform future capacity planning.
- Monitor data storage usage for artefacts and plan archival strategies to prevent repository bloat.
- Evaluate energy consumption or environmental impacts of high-frequency simulations if relevant to institutional goals.
- Consider leveraging cloud resources for intensive campaigns, ensuring compliance with data policies.

## Appendix AM: Ethical and Societal Impact Notes
- Reflect on potential civil applications (disaster response, infrastructure monitoring) emphasised in `docs/concept_of_operations.md`.
- Consider privacy implications of persistent imaging and outline mitigation strategies within policy constraints.
- Note any international regulatory frameworks or bilateral agreements relevant to the mission scope.
- Encourage inclusion of ethical discussions in stakeholder briefings and final conclusions.

## Appendix AN: Continuous Integration Hooks
- Integrate documentation linting or spell-checking into CI pipelines to maintain quality standards.
- Automate generation of documentation digests (`make docs`) following major updates to ensure artefact parity.
- Set up notifications when CI runs detect regressions in simulation scripts or STK exporter tests.
- Document CI status in the dossier to demonstrate ongoing quality control.

## Appendix AO: Open Questions Tracker
- Maintain a list of unresolved questions emerging from literature review, simulation analysis, or stakeholder feedback.
- Assign owners and due dates for resolving each question, referencing relevant artefacts.
- Update the tracker as questions are answered, linking to sections in the dossier where resolutions are documented.
- Use the tracker to inform future research priorities and roadmap adjustments.

## Appendix AP: Template for Future Scenario Additions
1. Define mission objective and target region, citing relevant stakeholders.
2. Draft configuration JSON skeleton with metadata, orbital elements, access windows, and operational constraints.
3. Identify required literature or data sources to justify scenario assumptions.
4. Outline simulation and validation steps, including STK export expectations.
5. Plan integration into compliance documentation and update `docs/_authoritative_runs.md` upon baseline establishment.

## Appendix AQ: Summary of Key Metrics
| Metric | Value | Evidence Source | Requirement |
| --- | --- | --- | --- |
| Formation window duration | \(96\,\text{s}\) | `artefacts/triangle_run/triangle_summary.json` | MR-3 |
| Maximum aspect ratio | 1.00000000000018 | `docs/triangle_formation_results.md` | MR-4 |
| Maximum validated ground distance | \(343.62\,\text{km}\) | `artefacts/triangle_run/triangle_summary.json` | MR-2 |
| Annual formation-keeping \(\Delta v\) | \(14.04\,\text{m/s}\) | `artefacts/run_20251018_1207Z/maintenance_summary.csv` | MR-6 |
| Command latency | \(1.53\,\text{h}\) | `artefacts/run_20251018_1207Z/command_windows.csv` | MR-5 |
| Injection recovery \(p_{95}\ \Delta v\) | \(0.041\,\text{m/s}\) | `artefacts/run_20251018_1207Z/injection_recovery.csv` | MR-7 |
| Centroid \(p_{95}\) offset | \(24.180\,\text{km}\) | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json` | SRD-P-001 |

## Appendix AR: Author Responsibilities Matrix
| Author | Chapter Responsibilities | Supporting Artefacts |
| --- | --- | --- |
| Lead Mission Analyst | Chapters 1, 2, 3 | `docs/project_overview.md`, `config/project.yaml`, simulation scripts |
| Formation Dynamics Specialist | Chapters 3, 4, 6 | `sim/formation/triangle.py`, run artefacts |
| Ground Segment Engineer | Chapters 5, 6, 7 | STK exports, command latency data |
| Systems Engineer | Chapters 2, 4, 7, Appendices | `docs/system_requirements.md`, `docs/compliance_matrix.md` |
| Technical Writer | Appendices, editorial coordination | Review logs, style guides |

## Appendix AS: Final Review Sign-Off Sheet
- **Chapter 1:** Reviewer signature, date, notes.
- **Chapter 2:** Reviewer signature, date, notes.
- **Chapter 3:** Reviewer signature, date, notes.
- **Chapter 4:** Reviewer signature, date, notes.
- **Chapter 5:** Reviewer signature, date, notes.
- **Chapter 6:** Reviewer signature, date, notes.
- **Chapter 7:** Reviewer signature, date, notes.
- **Appendices:** Reviewer signature, date, notes.

## Appendix AT: Document Distribution List
| Recipient | Role | Distribution Date | Format |
| --- | --- | --- | --- |
| Systems Engineering Review Board | Oversight | TBD | PDF, STK package |
| Mission Planning Team | Operations | TBD | PDF, artefact bundle |
| External Partners | Collaboration | TBD | Sanitised PDF |
| Archive | Records management | TBD | PDF, zipped artefacts |

## Appendix AU: Post-Publication Maintenance Plan
- Schedule periodic reviews (e.g., biannual) to ensure the dossier remains aligned with evolving mission evidence.
- Establish triggers for immediate updates (e.g., major run completion, requirement change, new validation workflow).
- Maintain version history documenting significant revisions and rationale.
- Communicate updates to all stakeholders listed in the distribution list.
