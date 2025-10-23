# Mission design project on “Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over Tehran”

## Project Overview

Before drafting the report, restate the mission title exactly as above and confirm that the engineering discipline is **Aerospace Engineering** with a focus on distributed Earth observation formations. Summarise the project goal using `docs/project_overview.md` and `docs/mission_requirements.md`, explaining that the aim is to deliver a repeatable 90 s equilateral imaging opportunity above Tehran while maintaining compliance with MR-1 through MR-7 plus the added communications and payload mandates. Define the problem statement by drawing on `docs/concept_of_operations.md` and `docs/triangle_formation_results.md`, highlighting the challenge of sustaining transient triangular geometry, daily access, and resilient downlink capacity over a complex megacity.

Justify the project’s significance through references to Tehran’s environmental, seismic, and socio-technical pressures as captured in `docs/tehran_daily_pass_scenario.md` and `docs/tehran_triangle_walkthrough.md`. Detail the mission benefits—improved situational awareness, responsive environmental monitoring, and regional risk mitigation—and identify stakeholders who rely on the constellation. Provide a catalogue of “raw materials” that mirrors the repository assets: configuration baselines (`config/project.yaml`, `config/scenarios/tehran_daily_pass.yaml`), simulation scripts (`sim/scripts/run_scenario.py`, `sim/scripts/run_triangle.py`, `run.py`, `run_debug.py`), analysis notebooks or reports under `docs/`, authoritative artefacts (`artefacts/run_20251018_1207Z/` etc.), and validation tooling such as `tools/stk_export.py`. Note the provenance and parameter ranges of each asset so Chapter 2 can treat them as experimental inputs.

## Content Generation Guidelines

- All reasoning must be justified with evidence from peer-reviewed literature, agency reports, or authoritative repository data. When invoking established orbital mechanics principles (e.g., HCW, ROE), cite canonical sources alongside recent corroborating studies.
- Present quantitative data using tables, figures, and graphs. Employ Suggested Tables (e.g., Tables 2.1, 4.1, 5.1) to summarise configuration parameters, performance metrics, and validation results. Describe any figures so readers can reproduce them from repository artefacts.
- Maintain a critical tone when assessing methodologies and results. Discuss uncertainties, sensitivities, and known limitations. Record any deviations from configuration baselines and their implications for reproducibility.
- Highlight innovation: emphasise the transition from generic formation flying literature to a Tehran-specific transient triangle, and explain how communications throughput expansion, payload processing guidance, and the environmental dossier differentiate this mission from antecedents.
- Document any mathematical models (e.g., Monte Carlo propagation, link budgets) and statistical analyses (confidence intervals, compliance probabilities). State assumptions, boundary conditions, and validation status against `tools/stk_export.py`.
- Adhere to standards referenced in the repository (ISO/IEC 23555-1:2022, ESA-GSOP-OPS-MAN-001) and any additional ASTM/ISO norms uncovered during the literature review. Explain how these standards inform the experimental design and data handling procedures.

## Chapter 1: Theory—Literature Review

Conduct an exhaustive literature review spanning 2020–2025 (supplemented by seminal works where indispensable) to map the evolution of distributed satellite missions. Progress through tandem pairs (e.g., GRACE/GRACE-FO), linear strings, tetrahedral clusters (e.g., MMS), swarms, and responsive cubesat formations. Compare sensing performance, geometric stability, propulsion demand, autonomy requirements, and mission risk for each topology so that the trade-space clearly justifies adopting a **three-satellite, transient equilateral triangle** as the optimum balance between sensing diversity, controllability, and lifecycle cost for this project.[Ref1][Ref8]

Examine theoretical frameworks governing repeat ground-track orbits, sun-synchronous design, and intersecting-plane architectures. Synthesise derivations for Relative Orbital Elements (ROEs), Hill–Clohessy–Wiltshire (HCW) dynamics, differential nodal drift, and perturbation management (\(J_2\), atmospheric drag, solar radiation pressure) to establish the predictive toolkit used later in the thesis. Highlight comparative studies between analytical, semi-analytical, and numerical propagation methods, and explain why the repository’s hybrid analytical–Monte Carlo methodology remains the reference approach.[Ref2][Ref4][Ref6][Ref9]

Review global case studies of city-focused observation campaigns (e.g., Mexico City, Istanbul, Los Angeles, Jakarta). For each city, document latitude/longitude, metropolitan footprint, elevation span, seismicity, air-quality indices, and climatological challenges that influence access geometry and payload scheduling. Use this comparative dataset to articulate the **Tehran selection rationale**, emphasising how its seismic hazard, inversion-prone air quality, 730 km² urban footprint, and 35.6892°N, 51.3890°E coordinates create a demanding yet high-impact target for transient formation imaging. Explicitly connect these attributes to the mission’s need for daily 90 s coordinated passes and the geometry embedded in the repository scenarios.[Ref1][Ref3][Ref10][Ref11]

Survey formation-maintenance strategies, including differential drag, cold-gas and electric propulsion, inter-satellite ranging, and autonomous guidance algorithms. Evaluate Δv envelopes, navigation accuracy, and fault tolerance reported in recent missions and academic prototypes. Conclude why a maintenance allocation of ≤15 m/s per spacecraft with Monte Carlo validation is appropriate for this concept, and identify gaps that motivate future adaptive control research.[Ref2][Ref4][Ref8]

Compile literature on communications architectures for small formations, covering X-/S-band links, optical crosslinks, and inter-satellite networking. Derive a **communications throughput requirement** that ensures the Tehran mission can offload a full day of tri-stereo optical and coherent radar payload data plus housekeeping telemetry within the evening downlink window. Anchor the requirement to the 9.6 Mbps X-band baseline documented in the ConOps and project growth margins (e.g., scalability to 25–45 Mbps) needed to accommodate higher-resolution sensors or additional data products. Address link budgets, ground-station availability, latency constraints, and regulatory considerations.[Ref3][Ref12]

Investigate payload sensing modalities relevant to coordinated imaging (tri-stereo optical, InSAR, thermal, atmospheric sounding). For each modality, document achievable ground sampling distance, swath width, signal-to-noise ratios, and raw/compressed data volumes. Translate these findings into **payload data product and processing guidance** that justifies the repository’s Level-0 → Level-1B → analysis-ready pipeline, compression factors, and four-hour delivery objective.[Ref3][Ref4][Ref13]

Catalogue prior academic and agency projects tackling transient formation events or city-targeted constellations. Summarise their modelling assumptions, simplifications, and validation approaches, then contrast them with the repository’s insistence on STK 11.2 interoperability and repeatable Monte Carlo campaigns. Use this review to reinforce why the project leans on configuration-controlled scenario files, authoritative run ledgers, and reproducible toolchains.[Ref4][Ref5][Ref6][Ref7]

Throughout this chapter, articulate how each literature thread influences the thesis methodology, culminating in a clear statement: **because the surveyed studies show that transient equilateral formations maximise sensing value while containing risk and resource consumption, this project formalises a Tehran-focused three-satellite implementation**. Close the chapter with a consolidated mapping between literature-derived insights and the mission requirements (MR-1 to MR-7 plus communications throughput and payload handling mandates). Document which references were extracted and which were used in this chapter to maintain traceability into Chapter 5.[Ref2][Ref3]

## Chapter 2: Experimental Work

Document every repository asset that constitutes the mission “materials”. Begin with `config/project.yaml` and the scenario catalogue under `config/scenarios/`, detailing gravitational constants, spacecraft physical properties, orbital elements, solver tolerances, and Monte Carlo seeds. Present these parameters in a structured table (Suggested Table 2.1) grouped by subsystem (orbital design, spacecraft bus, payload, communications, ground segment) so analysts can cross-reference assumptions against mission requirements and ConOps statements.[Ref2][Ref3][Ref6]

Map the simulation pipeline orchestrated by `sim/scripts/run_scenario.py`, `sim/scripts/run_triangle.py`, `run.py`, and `run_debug.py`. For each stage—RAAN alignment optimisation, access window detection, high-fidelity propagation, metric extraction, Monte Carlo sampling, STK export—explain the algorithms employed, configuration inputs, verification hooks, and how they align with literature-derived methodologies. Include diagrams or sequence descriptions (e.g., Suggested Figure 2.1) showing data flow from configuration files to post-processing outputs.[Ref4][Ref6][Ref7]

Enumerate the **communications throughput requirements** within the configuration context: specify downlink/uplink rates, contact durations, modulation schemes, coding gains, and antenna parameters necessary to guarantee daily data evacuation. Provide equations linking payload generation rates to ground-segment capacity, highlighting margins or required upgrades. Embed cross-references to MR-5 responsiveness metrics and to ConOps risk mitigations that rely on redundant ground support.[Ref2][Ref3]

Detail the **payload data product and processing guidance** operationalised in the codebase: describe file formats emitted by the simulations (`triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`), how they translate to Level-0 packets, Level-1B imagery, and analysis-ready datasets, and what preprocessing (radiometric calibration, geometric co-registration, coherence filtering) must occur before stakeholder delivery. Clarify storage, compression, and checksum practices to maintain data integrity and trace back to ISO/IEC 23555-1:2022.[Ref3][Ref4][Ref13]

Audit all authoritative artefacts under `artefacts/` and `docs/` to ensure traceability. Summarise how `_authoritative_runs.md`, `triangle_formation_results.md`, `tehran_daily_pass_scenario.md`, and `tehran_triangle_walkthrough.md` interlink run identifiers, configuration files, and validation procedures. Verify that every script, dataset, and documentation asset is cross-referenced so that future analysts can reproduce historical results without ambiguity.[Ref4][Ref5][Ref6][Ref7]

Include methodological guidance for quality assurance: outline regression testing (`tests/unit/test_triangle_formation.py`), configuration control practices, expectations for logging and metadata capture, and procedures for updating scenario metadata. Reference relevant standards (ESA-GSOP-OPS-MAN-001) when discussing ground-station operations and communications verification. Provide instructions for documenting deviations, rerunning Monte Carlo campaigns, and validating STK 11.2 compatibility so the workflow remains audit-ready.[Ref4][Ref5][Ref7][Ref12]

## Chapter 3: Results and Discussion

Present the analytical outputs as a three-stage narrative that mirrors the repository evidence chain, integrating quantitative analysis, figures, and tables to support each argument.

**Stage 1—Authoritative Evidence Selection.** Identify and justify the “locked” runs (`run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`, curated triangle reruns). Describe their directories, data products, validation status, and relationship to the compliance matrix. Explain how exploratory runs are archived without contaminating baseline evidence, and document any statistical sampling decisions drawn from Monte Carlo campaigns.[Ref4][Ref5][Ref6]

**Stage 2—Formation Geometry, Maintenance, and Communications Performance.** Extract quantitative metrics from `triangle_summary.json`, `maintenance_summary.csv`, and associated Monte Carlo catalogues: formation window mean (≈91.2 s), aspect ratio stability (~1.008 mean, ≤1.019 max), centroid ground-distance statistics (mean 18.7 km, 95% interval 88.5–93.9 s for window duration, ≤30 km compliance), and annual Δv budget (~8.3 m/s). Correlate these with communications throughput findings—demonstrate that the 9.6 Mbps link (or upgraded margin) can downlink the day’s payload volume within the evening window, and flag any discrepancies requiring configuration updates. Summarise the results in Suggested Table 4.1 and supporting figures.[Ref3][Ref4][Ref6]

**Stage 3—Robustness, STK Validation, and Data Handling Assurance.** Report Monte Carlo compliance probabilities (≥98.2% for ≤30 km centroid distance, 100% within waiver band), drag dispersion impacts, and STK 11.2 cross-check outcomes. Provide guidance for generating comparative tables (e.g., Suggested Table 5.1) showing <2% divergence between Python simulations and STK metrics. Confirm that exported ephemerides, ground tracks, and contact intervals ingest without error, and record any limitations or corrective actions discovered during validation. Document how communications analyses and payload processing pipelines remain coherent with STK timelines.[Ref4][Ref6][Ref7]

Develop a **Tehran environmental operations dossier** that consolidates geospatial, atmospheric, and socio-technical constraints relevant to mission planning. Include: (1) urban morphology and land-cover distribution influencing retrieval algorithms and stray-light management; (2) seasonal meteorology (dust events, inversion layers, cloud climatology) affecting payload duty cycles and link budgets; (3) air-quality and pollution metrics that motivate coordinated sensing and calibrate optical/radar processing approaches; (4) seismic and infrastructure risk profiles guiding prioritised observation corridors and contingency response planning; and (5) ground-segment considerations within Tehran (spectrum regulation, electromagnetic interference sources, power resilience). Reference reputable datasets (UN urban studies, Tehran Air Quality Control Company, Iran Meteorological Organization) and align the dossier with operational procedures outlined in the ConOps.[Ref3][Ref10][Ref11]

Conclude the chapter by synthesising how the quantified results, communications analyses, payload processing guidance, and environmental dossier collectively demonstrate compliance with MR-1 through MR-7, the added throughput mandate, and the data-handling objectives. Compare findings to existing literature, discuss limitations or sources of error, and note how future control or communications upgrades could mitigate identified risks. Record the references extracted and used here for Chapter 5 traceability.[Ref2][Ref3]

## Chapter 4: Conclusions and Recommendations

Summarise how the mission architecture—dual-plane, sun-synchronous constellation delivering a daily 90 s equilateral formation—meets stakeholder needs. Reiterate evidence for geometric fidelity, robustness, communications adequacy, payload processing readiness, and Tehran environmental responsiveness, citing the authoritative runs and validation artefacts.[Ref3][Ref4][Ref5][Ref6]

Issue actionable recommendations: maintain the current baseline design, invest in redundant ground infrastructure, refine autonomous maintenance strategies, and institutionalise the environmental dossier within operations planning. Address communications scaling options and payload processing automation enhancements needed to preserve four-hour delivery commitments under evolving data loads.[Ref3][Ref4]

Define a future work pathway that embeds a **mission cost and risk analysis framework**. Outline steps to integrate parametric cost models (e.g., NASA/Aerospace Corp CERs), lifecycle budgeting, and risk-based decision analysis with the existing simulation pipeline. Emphasise how cost and risk modelling will interact with robustness studies, communications upgrades, payload enhancements, and environmental contingencies to support future design iterations and stakeholder reviews.[Ref3][Ref12]

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
