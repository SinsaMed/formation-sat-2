# Mission Research Prompt – Orbital Design and Mission Analysis of a Three‑Satellite LEO Constellation for Repeatable, Transient Triangular Formation Over a Mid‑Latitude Target

## Preface and Usage Notes

This prompt serves as the formal specification for a comprehensive **Mission Research & Evidence Compendium** on the design and analysis of a three‑satellite low Earth orbit (LEO) constellation that achieves a **repeatable, transient equilateral triangle** formation above a fixed mid‑latitude target. It synthesises methodological expectations, literature‑review requirements, simulation workflows, and validation criteria drawn from configuration‑controlled artifacts in the reference repository as well as from contemporary formation‑flying scholarship. The following usage rules apply:

1.  **Academic tone:** Compose all prose in clear academic English using British spelling and an accessible but technical style suitable for multidisciplinary reviewers. Avoid colloquialisms and maintain consistent terminology throughout.
2.  **Sequential chapters:** Complete each chapter in numerical order without omitting any subsection. Do not interleave commentary or meta‑discussion; treat this document as a contract for the final report’s structure.
3.  **Citation scheme:** Cite repository artifacts (e.g., configuration files, scripts, run directories) and external sources using numbered brackets (e.g., `[Ref1]`). Each chapter concludes with a reference list mapping those numbers to actual documents. New external sources must fall within the 2019–2025 window unless they represent classic foundational works.
4.  **Figures, tables, and equations:** When the prompt suggests an illustration or table, include a labelled placeholder (e.g., `[Suggested Figure 2.1]`) and describe the data, format, and transformation pipeline required. These descriptions will guide later implementation.
5.  **STK interoperability:** Any section that references ephemerides, ground tracks, or contact intervals must reaffirm compatibility with Systems Tool Kit (STK 11.2) exports and mention the exporter routine used. Validation procedures should cite the appropriate guides.
6.  **Version control:** Treat configuration files and run directories as immutable evidence snapshots. Any deviation (e.g., re‑running a simulation) must follow the run‑naming convention `run_YYYYMMDD_hhmmZ` and record seeds, solver tolerances, and validation outcomes inside the report body and appendices.
7.  **Appendices:** Do not omit the appendices. They house reusable literature‑review prompts, data extraction templates, and quality assurance checklists. These appendices are integral to reproducibility and will be referenced by multiple chapters.

## Chapter 1 – Mission Framing, Requirements Baseline, and Literature Review Scope

### 1.1 Mission Overview Anchors

1.  **Mission intent:** Summarise the overall objective: deploy three identical satellites into two sun‑synchronous orbital planes such that once per day they form a transient equilateral (or deliberately near‑isosceles) triangle for approximately **90 s** above a selected mid‑latitude target such as Tehran. Highlight that the formation window must be repeatable with minimal drift to enable coordinated sensing. Reference the mission overview document for the primary motivation and any derived stakeholder requirements \[Ref1\].
2.  **Stakeholder motivations:** Identify the stakeholder communities (e.g., disaster management agencies, infrastructure monitors, scientific payload teams) and map their needs to specific mission requirements (MR‑1 through MR‑7) recorded in the Mission Requirements Document. Explain why rapid revisit, resilient operations, and low‑cost maintenance budgets are critical for these users \[Ref2\].
3.  **Baseline architecture:** Describe the dual‑plane constellation design: two orbital planes separated in right‑ascension of the ascending node (RAAN) such that two satellites occupy one plane and the third occupies the second plane. Explain how this arrangement enables daily access to the target while maintaining Sun‑synchronous conditions. Include orbital elements (semi‑major axis, inclination, eccentricity, RAAN) from the baseline configuration file and note their tolerances \[Ref3\].
4.  **Reference phenomena:** Relate the equilateral‑triangle concept to notable missions. For example, NASA’s Laser Interferometer Space Antenna (LISA) will employ three spacecraft forming an equilateral triangle with million‑mile arms for gravitational‑wave detection; this demonstrates the feasibility of triangular formations and the need for precise separation control \[Ref4\]. Similarly, NASA’s Magnetospheric Multiscale (MMS) mission uses tetrahedral formations in highly elliptical orbits; their experience with formation maintenance informs maintenance budgeting and control strategies \[Ref5\].
5.  **Operational cadence:** Capture the expected daily sequence: repeated ground‑track alignment, formation build‑up, data collection during the 90 s window, downlink operations, and maintenance manoeuvres. Explain the cadence drivers such as sun‑synchronous orbital precession, ground station contact availability, and Δv constraints.

### 1.2 Literature Review Mandates – Mission Architecture and Requirements Traceability

Conduct a structured literature review that bridges the mission architecture to contemporary research. The review must cover the following themes and map each source to relevant mission requirements:

1.  **Formation design taxonomy and selection rationale:** Survey recent research (2019–2025) spanning diverse formation sizes and geometries—ranging from satellite pairs, linear strings, rings, tetrahedra, to large clusters. Compare sensing performance, control effort, navigation requirements, and communications burden for each topology. Conclude the review by explicitly arguing why a three‑satellite transient triangle is adopted for this mission, citing drivers such as balanced coverage, manageable Δv, cost containment, and compatibility with the repository’s dual‑plane architecture.
2.  **Repeat ground‑track orbits:** Examine the theory and design of repeating ground tracks, including RAAN drift mitigation under $`J_{2}`$ perturbations. Note techniques such as adjustment of semi‑major axis and orbital inclination to achieve a desired ground‑track period. Capture any analytical or optimisation methods applied to target revisit problems.
3.  **Relative orbital elements and safety:** Review modern ROE formulations and their use in formation design and passive safety assessment. For instance, Barbour et al. (2023) present an ROE‑based method for validating passive safety using ellipse constraints; they highlight the geometric insight provided by ROEs and their computational efficiency \[Ref6\].
4.  **Formation maintenance strategies:** Investigate low‑thrust and differential‑drag techniques for maintaining small separations among satellites with Δv budgets below $`15\text{m/s}`$ per annum. Compare cold‑gas versus electric propulsion systems and note their propellant efficiencies.
5.  **Command and ground segment architectures:** Assess case studies of formation‑flying missions managed from a single ground station. Discuss latency budgets (e.g., 12‑hour command windows) and strategies for redundancy such as cross‑support between geographically separated stations.
6.  **Monte Carlo robustness validation:** Identify literature on robust mission design under injection errors and atmospheric uncertainties. Summarise methods for Monte Carlo analysis with respect to along‑track dispersions of ±5 km and inclination errors of ±0.05°, linking to MR‑7 resilience requirements.
7.  **Comparative mission analogues and design simplifications:** Catalogue prior formation‑flying missions (e.g., TanDEM‑X, GRACE/GRACE‑FO, PRISMA, CanX‑4/5, MMS) and summarise how their navigation sensors, crosslink strategies, and maintenance philosophies informed this project’s modelling choices (point‑mass spacecraft, perfect state knowledge, dual‑plane architecture). Ensure that each analogue is assessed within the broader formation taxonomy above, noting when alternative topologies were favoured and why those lessons still support the selection of a transient three‑satellite triangle for Tehran.
8.  **Urban target comparatives and Tehran selection:** Review remote‑sensing and formation‑flying missions that prioritised urban targets worldwide (e.g., Mexico City, Istanbul, Los Angeles, Delhi). Extract each city’s geographic coordinates, spatial extent, topographical or atmospheric challenges, and mission objectives. Use these findings to justify the Tehran focus by contrasting its latitude, land area, pollution or seismic monitoring needs, and operational constraints with those precedents, and spell out how these characteristics influenced formation geometry, ground contact planning, and data cadence decisions.

After completing the review, distil the findings into a synthesis subsection that connects external lessons to repository decisions (e.g., reliance on analytical ROE design, assumption of identical buses, use of transient formation windows). Explicitly record the trade study that narrows broader formation typologies down to the adopted three‑satellite transient triangle and summarise the comparative city evidence that culminates in Tehran’s selection. Highlight any simplifications retained for conceptual analysis and note where later chapters will revisit them.

### 1.3 Launch and Deployment Considerations

Establish a launch and early deployment evidence base that anchors the constellation design in realistic rideshare conditions. The analysis must integrate industry practices for dispenser sequencing and post-separation phasing so that Monte Carlo assumptions and robustness tasks remain credible.

1.  **Rideshare deployment literature review:** Survey 2019–2025 low Earth orbit rideshare campaigns and launch provider documentation covering dispenser architectures, separation sequencing, and relative phasing for clustered payloads. Highlight how dispenser design constraints influence achievable separation velocities and initial relative geometry, and cite works that document coordination between primary payload operations and secondary formation-building activities.
2.  **Deployment data extraction:** For each precedent formation mission (e.g., TanDEM-X, Planet’s SuperDove constellations, OneWeb cluster releases, SpaceX Transporter-series deployments), extract documented injection dispersions, RAAN targeting strategies, and timeline milestones from separation through the first phasing manoeuvre. Explicitly map these dispersions to the Monte Carlo assumptions enumerated earlier in Chapter 1 (e.g., along-track ±5 km, inclination ±0.05°) and flag any adjustments required for the robustness verification tasks outlined in Chapter 4.
3.  **Launch vehicle and dispenser trade table:** Compile candidate launch vehicles and compatible dispenser options capable of accommodating the three-spacecraft stack. For each pairing, record mass margins, available deployment slots, deployment geometry (stack order, dispenser port orientation, relative ejection vectors), separation delta‑v envelopes, rideshare policy constraints, and published injection accuracy statistics. Use this trade to justify which combinations align with the constellation’s RAAN targeting needs and post-separation phasing timeline.
4.  **Post-separation phasing synthesis:** Outline phasing strategies (e.g., differential drag, finite-burn trims, staged orbit-raising) used in the surveyed missions to achieve desired relative spacing. Link these strategies to prospective command timelines and maintenance windows, explaining how the resulting error budgets will feed Chapter 4 alignment-maintenance analyses.
5.  **Deliverable integration:** Capture the preceding outputs in \[Suggested Figure 1.3\], \[Suggested Table 1.4\], and \[Suggested Table 1.5\], ensuring that each product records data provenance, STK-export validation considerations, and explicit cross-references to later robustness evaluations.

Conclude this subsection by articulating how realistic launch dispersion data conditions the repository’s Monte Carlo campaigns and by stating any gaps that subsequent simulation work must close.

### 1.4 Repository Artefact Integration Tasks

1.  **Mission requirements traceability:** Tabulate every mission requirement (MR‑1 – MR‑7) from the compliance matrix and note the compliance status and supporting evidence (EV‑1 through EV‑5). Include columns for requirement description, threshold, margin, evidence tag, and associated run directories \[Ref7\].
2.  **Configuration snapshot:** Summarise the baseline configuration parameters from the primary YAML file, including project metadata (name, version, author), global constants (Earth radius, μ, $`J_{2}`$ ), platform properties (mass, cross‑sectional area, drag coefficient), orbital elements, simulation controls (time step, propagation span), and output directives.
3.  **Scenario metadata:** Document key fields in the scenario JSON files (e.g., `tehran_daily_pass.json`, `triangle_formation.json`). Highlight RAAN values, access windows, Monte Carlo sample counts, maintenance cadence, and alignment validation flags.
4.  **Authoritative runs:** Map run identifiers (e.g., `run_20251018_1207Z`, `run_20251020_1900Z_daily_pass_locked`) to their purpose (baseline, locked, exploratory) and summarise the metrics captured (window duration, aspect ratio, centroid distances, delta‑v consumption). Cross‑link to the compliance matrix and note which runs serve as evidence for each requirement.
5.  **STK compatibility:** State the procedure for exporting ephemerides and ground tracks via the `stk_export.py` script, including the names of the classes used (`StateSample`, `PropagatedStateHistory`, `GroundTrack`, `GroundContactInterval`) and the sanitisation of identifiers to satisfy STK import rules \[Ref8\].

### 1.5 Literature Review Prompt Blocks

To organise the literature review, prepare discrete search blocks with guiding questions. For each block, identify at least five sources and construct a matrix capturing key findings, repository alignment, identified gaps, and a proposed citation tag.

1.  **Block A – Mission Geometry Foundations:** Survey repeating‑ground‑track theory, ROE formulations, and equilateral geometry metrics. Include derivations of Hill–Clohessy–Wiltshire (HCW) or Lambert solutions and discuss perturbation effects such as $`J_{2}`$ and atmospheric drag. Map sources to mission requirements MR‑1 through MR‑4.
2.  **Block B – Operations and Ground Segment:** Investigate command architectures and latency modelling. Compare single‑station operations with dual‑station cross‑support (e.g., NASA–ESA collaborations). Relate findings to MR‑5 (command latency) and identify cases where command cycles exceed 12 hours.
3.  **Block C – Maintenance and Robustness:** Evaluate control strategies for maintaining small formations. Compare ROE‑based control (leader–follower, quasi‑nonsingular E/I separation) with differential‑drag and continuous thrust techniques. Summarise delta‑v budgeting methodologies and maintenance cadence trade‑offs.
4.  **Block D – Triangular Formation Applications:** Review missions employing triangular formations for science or sensing (e.g., LISA for gravitational waves, MMS for magnetospheric studies). Extract lessons on side‑length selection, station‑keeping, and tolerance requirements. Identify gaps in literature addressing short‑baseline (5–10 km) triangular formations in LEO.
5.  **Block E – Comparative Mission Case Studies and Design Translation:** Perform an exhaustive review of formation‑flying programmes that parallel the Tehran concept, including radar interferometry pairs, gravity mapping tandems, and technology demonstrators. For each, summarise propulsion systems, relative navigation payloads (GPS, Galileo, differential carrier‑phase), operational cadences, and any transient formation experiments. Translate lessons into concrete design choices for this project—such as adopting point‑mass spacecraft models, prioritising daily repeatability over continuous formations, and selecting equilateral versus near‑isosceles geometry. Document outstanding gaps that motivate bespoke analysis in later chapters.
6.  **Block F – Urban Target Benchmarking and Tehran Trade Study:** Compile literature on spaceborne monitoring campaigns focused on major metropolitan areas. For each cited project, record the city name, latitude/longitude bounds, land area, dominant hazards or monitoring priorities, and any orbital constraints reported (e.g., revisit frequency, lighting conditions, regulatory limitations). Use this block to synthesise a defensible rationale for prioritising Tehran, explicitly linking its geographic footprint, seismic and air‑quality challenges, and political or regulatory context to the three‑satellite triangular formation choice and ground segment strategy.

### 1.6 Narrative Flow Outline

Begin Chapter 1 with a concise mission statement and stakeholder summary. Transition into the requirement hierarchy, emphasising traceability to stakeholder motivations. Introduce the literature‑review themes and summarise the repository artefacts that motivate each theme. Ensure the narrative explicitly reports how the literature synthesis justifies modelling simplifications and geometry selections, then conclude with a roadmap preview of how subsequent chapters operationalise the mission framing through simulation, analysis, validation, and recommendations.

### 1.7 Chapter 1 Deliverable Checklist

1.  Mission overview narrative aligned with repository intent and stakeholder drivers.
2.  Literature review synthesis covering geometry, operations, maintenance, and triangular formation applications.
3.  Compliance traceability table linking mission requirements to evidence tags and run directories.
4.  Configuration and scenario snapshot tables summarising parameters and metadata.
5.  Discussion of run identifiers and configuration governance conventions.
6.  Launch and deployment literature review dossier capturing rideshare precedents, dispenser sequencing, and post-separation phasing practices, with explicit cross-references to Chapter 4 robustness tasks.
7.  Candidate launch vehicle and dispenser trade table logging mass margins, slot availability, separation delta‑v envelopes, injection accuracy, and RAAN targeting suitability (populate \[Suggested Table 1.4\]).
8.  Post-separation phasing and error-budget register linking deployment timelines, injection dispersions, and Monte Carlo assumptions to the alignment-maintenance activities scheduled for Chapter 4 (populate \[Suggested Figure 1.3\] and \[Suggested Table 1.5\]).
9.  References section enumerating all cited artefacts and external sources.
10. A literature‑review matrix with at least five entries per block summarising key findings and gaps.
11. Comparative mission analogue digest capturing justification statements for geometry choices, modelling assumptions, and operational cadences derived from the literature review.
12. Formation taxonomy decision brief articulating why the three‑satellite transient triangle is selected after surveying alternate topologies, including cost, control, and sensing considerations.
13. Urban target benchmarking dossier detailing precedent city studies, geographic descriptors, operational challenges, and the resulting justification for adopting Tehran as the primary target.

### 1.8 Chapter 1 Suggested Figures, Tables, and Equations

- **\[Suggested Figure 1.1\]** A timeline schematic illustrating project roadmap stages mapped to mission phases (e.g., preliminary design, prototype runs, locked baseline, exploratory analyses).
- **\[Suggested Figure 1.2\]** A schematic showing the dual‑plane constellation geometry relative to the target latitude and the equilateral formation built at conjunction.
- **\[Suggested Figure 1.3\]** Launch-to-phasing timeline diagram mapping dispenser release order, RAAN targeting actions, post-separation phasing manoeuvres, and the handover to alignment-maintenance tasks referenced in Chapter 4.
- **\[Suggested Table 1.1\]** Mission requirement versus compliance status matrix derived from the compliance matrix file, including deterministic and Monte Carlo metrics.
- **\[Suggested Table 1.2\]** Baseline configuration parameters grouped by subsystem (platform, orbit, simulation). Provide columns for parameter name, value, units, rationale, downstream consumer, and STK dependency.
- **\[Suggested Table 1.3\]** Comparative urban target attributes summarising precedent missions (city name, latitude/longitude span, land area, dominant hazards, mission goals, cited formation topology) alongside the Tehran case to evidence the target selection rationale.
- **\[Suggested Table 1.4\]** Candidate launch vehicles and dispenser configurations documenting payload accommodation, mass margins, deployment geometry (stack order, dispenser orientation, ejection vectors), separation sequencing, injection accuracy, RAAN targeting notes, and cited references for each rideshare option.
- **\[Suggested Table 1.5\]** Post-separation error budget ledger itemising injection dispersions, phasing strategy corrections, residual alignment errors, Monte Carlo assumption linkages, and Chapter 4 robustness cross-references.
- **\[Suggested Equation 1.1\]** The Hill–Clohessy–Wiltshire relative motion relations used to compute relative orbital element offsets.
- **\[Suggested Equation 1.2\]** The great‑circle distance formula used for converting angular centroid errors into ground distances.

### 1.9 Chapter 1 References

1.  **Mission Overview Document** – Contains mission intent statements and stakeholder rationale \[Ref1\].
2.  **Mission Requirements Document (MRD)** – Defines MR‑1 through MR‑7 and associated thresholds and margins \[Ref2\].
3.  **Baseline Configuration File (**`project.yaml`**)** – Captures configuration parameters and version identifiers \[Ref3\].
4.  **Laser Interferometer Space Antenna (LISA) Overview** – NASA description of three spacecraft forming an equilateral triangle with million‑mile arms for gravitational‑wave detection \[Ref4\].
5.  **Magnetospheric Multiscale (MMS) Formation Flight Dynamics Results** – NASA SpaceOps paper discussing tetrahedral formation maintenance and manoeuvre design \[Ref5\].
6.  **AAS 23‑155 Passive Safety Using Relative Orbital Elements** – Describes an ROE‑based technique for passive safety assessment and notes the geometric insight of ROEs \[Ref6\].
7.  **Compliance Matrix File** – Provides requirement compliance status and evidence tags \[Ref7\].
8.  **STK Exporter Documentation** – Describes exporter classes and validation procedures \[Ref8\].

### 1.10 Extended Task Breakdown – Chapter 1

1.  **Mission Synopsis:** Write a 250–300 word mission synopsis referencing the Mission Overview Document and MRD. Include the target latitude, dual‑plane architecture, 90‑second formation window, and stakeholder motivations. Maintain academic tone and cite relevant references.
2.  **Traceability Table:** Construct a table linking MR‑1 through MR‑7 to stakeholder motivations, thresholds, margins, evidence tags, and run identifiers. Use columns for requirement identifier, description, driver, threshold, margin, evidence tag, and status (compliant/non‑compliant/waiver).
3.  **Configuration Lifecycle:** Draft paragraphs explaining run naming conventions (`run_YYYYMMDD_hhmmZ`), semantic versioning (major.minor.patch), and STK validation logging. Emphasise the need to update configuration version numbers when parameters change and to record solver seeds and tolerances.
4.  **Literature Review Matrix:** For each block (A–F), create a matrix with columns: Topic, Key Findings, Repository Alignment, Identified Gap, Proposed Citation Tag. Populate at least five rows per block. Identify which gaps will be addressed by additional simulation or future work.
5.  **Cross‑Discipline Implications:** Provide bullet points summarising implications for payload design (e.g., imaging swath width, pointing stability), ground segment staffing (e.g., command windows), and regulatory considerations (e.g., frequency coordination). Note where these implications will be treated in later chapters.
6.  **Artefact Review:** Catalogue the contents of each authoritative run directory (maintenance summaries, command windows, injection recovery, drag dispersion, deterministic and Monte Carlo summaries). Identify which files provide windowed metrics versus full‑propagation metrics and explain how to interpret the difference.
7.  **Exploratory vs Locked Runs:** Distinguish between exploratory runs (e.g., resampled daily passes) and locked evidence runs. Document the purpose of each and any cautionary notes on using exploratory results for compliance statements.
8.  **Glossary Compilation:** Begin compiling a glossary of terms (e.g., ROE, RAAN, LVLH, HCW) to be included in the appendices. Provide concise definitions and cross‑references to relevant chapters.
9.  **Formation Taxonomy Synthesis:** Draft a concise narrative that weighs the benefits and drawbacks of alternative formation geometries, references key literature sources, and culminates in the decision to adopt a three‑satellite transient triangle for Tehran. Highlight implications for sensing coverage, control authority, and cost.
10. **Urban Target Comparative Analysis:** Assemble quantitative descriptors (latitude/longitude bounds, land area, population density if available, hazard profile) for each precedent city in the literature review. Summarise how these factors influenced mission design choices and articulate the unique challenges that make Tehran the preferred focus.

## Chapter 2 – Configuration, Methods, and Simulation Foundation

Chapter 2 dives into the configuration parameters, simulation scripts, and methodological foundations that underpin the mission analysis. It combines a detailed exposition of the input files and software interfaces with literature prompts on modelling assumptions.

### 2.1 Configuration Catalogue

1.  **Parameter breakdown:** Produce a table (see \[Suggested Table 2.1\]) that lists every parameter in the baseline configuration file, grouped by subsystem (platform, orbit, propagation, Monte Carlo, outputs). Include columns for name, value, units, rationale, downstream consumer, and STK dependency.
2.  **Scenario schema:** Draft JSON‑schema descriptions for each scenario file. Specify mandatory versus optional keys, data types, validation rules, and example snippets. For instance, fields like `raan_alignment`, `maintenance_strategy`, `alignment_validation`, and `monte_carlo.samples` should be defined and commented.
3.  **Parameter crosswalk:** Create a crosswalk mapping configuration parameters to simulation outputs. For example, `simulation.time_step_seconds` maps to the sampling cadence used in triangle summaries; `propagation.span_days` determines the length of deterministic and Monte Carlo runs.
4.  **Metadata alignment report:** Compare scenario alignment validation fields with actual run directories and entries in the authoritative run ledger. Note any mismatches (e.g., scenario claims alignment validated but the run ledger marks it exploratory) and propose corrective actions.
5.  **Configuration update policy:** Explain when configuration version numbers should be incremented, how scenario files are duplicated for new runs, and how versioning interacts with the compliance matrix. Outline the review process for approving configuration changes.
6.  **Modelling assumption ledger:** Document simplifying assumptions inherited from the literature synthesis (point‑mass spacecraft, perfect state knowledge via GNSS, neglect of detailed payload or attitude dynamics) and note any compensating analyses planned in later chapters. Cross‑reference the justification narrative compiled in Chapter 1.

### 2.2 Geometry and Frame Conventions

1.  **Relative orbital elements implementation:** Describe the algorithms used to generate equilateral formations from the baseline orbit. Reference functions in the simulation code (e.g., `triangle.py`, `frames.py`) that convert LVLH offsets into orbital elements. Explain how the Hill–Clohessy–Wiltshire linearised equations are applied or replaced by more accurate models when needed.
2.  **LVLH coordinate transformations:** Summarise transformations between Earth‑centred inertial (ECI) coordinates and local LVLH frames. Explain how these transformations are used to compute formation side lengths, aspect ratios, centroid offsets, and ground distances.
3.  **Great‑circle distance calculations:** Present the formula used to convert angular separations into ground distances. Note that this metric appears in both deterministic and windowed outputs. Clarify how Earth’s oblateness affects the calculation and whether corrections are included.
4.  **Aspect ratio and centroid metrics:** Define the aspect ratio (ratio of maximum to minimum side lengths) and centroid ground distance metrics used to judge formation quality. Describe thresholds (e.g., aspect ratio ≤ 1.02) and waiver values (e.g., centroid distance tolerance of 70 km). Explain why near‑unity aspect ratios are necessary for cooperative sensing and cite the corresponding unit test that enforces this tolerance.
5.  **Maintenance budgeting:** Explain how delta‑v budgets are estimated within the simulator. Distinguish between impulsive manoeuvre budgets and continuous drag‑modulation estimates. Note where mission requirements specify annual delta‑v limits and how these limits relate to maintenance frequency.

### 2.3 Script Interfaces and Simulation Pipelines

1.  **Scenario runner (**`run_scenario.py`**):** Describe the sequential stages: RAAN alignment optimisation, access node discovery, mission phase synthesis, two‑body propagation, high‑fidelity propagation with $`J_{2}`$ and drag, metric extraction, optional Monte Carlo sampling, and STK export. Highlight the roles of the `Node` and `Phase` data classes and how deterministic versus probabilistic outputs are structured.
2.  **Triangle simulator (**`run_triangle.py`**):** Outline the execution path: configuration loading, LVLH transformation, metric calculation, maintenance estimation, Monte Carlo campaigns, drag dispersion analysis, and export generation. Explain how CSV artefacts (`maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`) and plots (e.g., injection recovery CDF) are produced.
3.  **Campaign orchestrator (**`run_triangle_campaign.py`**):** If applicable, summarise the campaign script that iterates over multiple triangles or scenario variations. Note command‑line arguments for sample counts, random seeds, and run naming.
4.  **FastAPI service (**`run.py`**):** Describe the web interface that exposes triangle and scenario runs. Include the request models (`TriangleRunRequest`, `ScenarioRunRequest`) and job management functions. Explain how asynchronous job status and log streaming are handled and how results are persisted under `artefacts/web_runs`.
5.  **Debug scripts:** Summarise `run_debug.py` and any plotting utilities. Explain how they assist in diagnosing simulation outputs, generating additional CSVs, and visualising metrics. Mention limitations or recommended use cases (e.g., small sample runs for debugging).

### 2.4 Data Management and Artefact Inventory

1.  **Filesystem inventories:** For each authoritative run directory, produce a structured bullet list of filenames, file types, data volumes, and verification status. Indicate which files provide raw metrics, processed summaries, or visualisations.
2.  **Versioned artefacts:** Explain how new runs generate separate directories named by timestamp and identifier. State policies for storing or compressing large outputs, generating checksum manifests, and cleaning up intermediate files.
3.  **Raw vs processed data:** Define conventions for raw data (e.g., sample‑by‑sample CSV files) versus processed summaries (e.g., JSON metrics, CSV aggregates). Note where units are stored and how to avoid confusion across output formats.
4.  **Data retention:** Outline retention periods for various artefacts (e.g., keep all JSON summaries indefinitely, purge intermediate CSVs after final compendium assembly). Provide recommendations for archiving data used for published results.
5.  **Safety and security:** Mention any sensitive information (e.g., proprietary instrument models, restricted ground station locations) and note handling requirements. Ensure that public releases remove or mask sensitive fields while preserving scientific integrity.

### 2.5 Geometry‑Focused Literature Review Prompts

In addition to the repository documentation, direct further reading as follows:

1.  **LVLH frame transformations:** Survey contemporary research (2019–2025) on LVLH transformations and their application to formation flying. Compare the repository’s implementation with alternative formulations and note any advantages or simplifications.
2.  **Triangle stability metrics:** Review studies defining stability measures for triangular formations, such as aspect ratio tolerance, centroid drift, or triangle area variation. Identify metrics that can be adopted or adapted for the current mission.
3.  **Command latency modelling:** Investigate modelling approaches for command latency and ground station scheduling. Summarise frameworks that link contact duration to orbital period and describe how they inform command window design.
4.  **Drag dispersion modelling:** Examine methods for estimating drag dispersion and atmospheric density variations. Compare simplified models with high‑fidelity density estimations (e.g., NRLMSISE‑00) and discuss trade‑offs between computational cost and accuracy.
5.  **Low‑thrust maintenance control:** Read recent literature on low‑thrust control strategies for formation maintenance. Highlight algorithms that ensure passively safe trajectories while minimizing fuel consumption.

### 2.6 Suggested Analytical Assets

- **\[Suggested Table 2.1\]** Configuration catalogue table grouped by subsystem, with columns for parameter name, value, units, rationale, downstream consumer, and STK dependency.
- **\[Suggested Figure 2.1\]** Visualisation of the LVLH equilateral triangle derived from a representative triangle summary JSON file. Depict side lengths, centroid location, and aspect ratio. Mention the script or function used to generate the plot.
- **\[Suggested Figure 2.2\]** Histogram of command latency windows generated from `command_windows.csv`. Indicate bin sizes, sample counts, and reference lines for MR‑5 thresholds.
- **\[Suggested Equation 2.1\]** Great‑circle distance formula used in the simulation code.
- **\[Suggested Equation 2.2\]** Approximation linking command latency to orbital period, used in the command latency analysis function.

### 2.7 Narrative Flow Outline

Open Chapter 2 by recounting the configuration governance and parameter breakdown. Transition into geometric modelling concepts and highlight code functions that implement them. Then explore the simulation script interfaces, emphasising how inputs flow through each stage to produce artefacts. Conclude by motivating the geometry‑focused literature review and linking it to gaps identified in Chapter 1.

### 2.8 Chapter 2 Deliverable Checklist

1.  Configuration catalogue and crosswalk tables.
2.  JSON schema descriptions for scenario files with validation rules.
3.  Parameter alignment report comparing configuration fields to run ledger entries.
4.  Script interface documentation summarising inputs, outputs, and pipeline stages.
5.  Geometric derivation explanations anchored in source code.
6.  Artefact inventories with provenance notes and retention policies.
7.  Geometry‑centric literature review summary with identified gaps.
8.  References section listing all cited artefacts and external works.

### 2.9 Chapter 2 References

1.  **Baseline Configuration File (**`project.yaml`**)** – Complete list of parameters and version identifiers \[Ref3\].
2.  **Scenario Definitions** – JSON files for daily pass and triangle formation scenarios \[Ref9\].
3.  **Triangle Summary (**`triangle_summary.json`**)** – Contains metrics and samples for equilateral formation runs \[Ref10\].
4.  **Run Directories** – Authoritative run outputs capturing deterministic and Monte Carlo results \[Ref11\].
5.  **Formation Dynamics Code (**`triangle.py`**,** `frames.py`**)** – Implements LVLH conversions and triangle geometry algorithms \[Ref12\].
6.  **Simulation Scripts (**`run_scenario.py`**,** `run_triangle.py`**,** `run_triangle_campaign.py`**)** – Execute scenario and triangle simulations and generate artefacts \[Ref13\].
7.  **FastAPI Service (**`run.py`**)** – Exposes web endpoints for running simulations \[Ref14\].
8.  **Debug Scripts and Utilities (**`run_debug.py`**,** `render_debug_plots.py`**)** – Support interactive execution and visualisation \[Ref15\].
9.  **LVLH and Drag Dispersion Literature (2019–2025)** – External sources identified in Block A and C \[Ref16\].

### 2.10 Extended Task Breakdown – Chapter 2

1.  **Configuration Catalogue Preparation:** Use the configuration file to populate \[Suggested Table 2.1\]. Provide context for each parameter, including why it was chosen, its impact on simulations, and any links to mission requirements.
2.  **Schema Drafting:** Write JSON schema fragments for each scenario file. Include comments explaining each field’s purpose, allowable ranges, and dependencies. Provide example JSON snippets demonstrating proper usage.
3.  **Crosswalk Construction:** Map configuration parameters to simulation outputs and identify how changes propagate through the pipeline. Explain how modifications to time step or propagation span affect output sampling and Monte Carlo sample sizes.
4.  **Transformation Pipeline Analysis:** Document the order of operations in the triangle simulation code, from LVLH offsets to metric extraction. Provide pseudo‑code or flowcharts illustrating data flows and highlight where random seeds enter the process.
5.  **Artefact Inventory Compilation:** For each run directory, create bullet lists capturing filenames, file types, data volumes, and verification status. Note any anomalies (e.g., missing fields, unusual file sizes) and propose remediation steps.
6.  **Regeneration Instructions:** Draft instructions for re‑running simulations, including commands (e.g., `make triangle`, `python -m sim.scripts.run_scenario`), environment preparation steps (virtual environment activation, dependency checks), and expected outputs. Suggest estimated runtime ranges and hardware requirements.
7.  **Dual Reporting Identification:** List metrics requiring both windowed and full propagation reporting (e.g., centroid distance, side length, delta‑v). For each, indicate where values appear (CSV vs JSON) and how to contextualise them.
8.  **Alignment Validation Audit:** Compare `alignment_validation` fields in scenario JSON files with actual run directories and ledger entries. Identify discrepancies and update scenario metadata or run ledger as needed.
9.  **Reviewer Questionnaire:** Prepare a list of questions to guide configuration walkthrough meetings with systems engineers. Focus on assumptions, tolerances, data retention, and potential points of contention. Include prompts on RAAN sensitivity, maintenance cadences, and ground station scheduling assumptions.
10. **Coordinate Frame Appendix:** Draft an appendix summarising coordinate frame conventions used across code modules. Define ECI, Earth‑fixed (ECEF), LVLH, Radial‑In‑Track‑Cross‑Track (RIC), and orbital element frames. Provide diagrams and reference transformations.

## Chapter 3 – Simulation Pipeline, Toolchain, and Execution Protocols

Chapter 3 details the simulation workflows, automation tools, and continuous integration safeguards that support reproducible mission analysis. It is divided into execution protocols, regression tests, literature prompts, and quality assurance tasks.

### 3.1 Scenario Runner Workflow Description

1.  **Stage sequencing:** Describe each stage executed by the scenario runner script (`run_scenario.py`): (a) RAAN alignment optimisation, (b) access node discovery for the target site, (c) mission phase synthesis (pre‑access, access, post‑access), (d) two‑body propagation, (e) high‑fidelity propagation including $`J_{2}`$ and atmospheric drag, (f) metric extraction, (g) Monte Carlo sampling (if enabled), and (h) STK export. Highlight input and output files at each stage and note where solver seeds and tolerances are recorded.
2.  **RAAN optimisation summary:** Explain how the RAAN solver uses an initial RAAN guess and searches for the value that maximises daily access time while satisfying Sun‑synchronous constraints. Summarise the RAAN optimisation block recorded in the scenario summary JSON (initial vs optimised RAAN, centroid cross‑track magnitude, convergence criteria). Identify associated mission requirements.
3.  **Node and Phase dataclasses:** Introduce these internal data structures that encapsulate temporal segments of the mission. Explain how they enable downstream reporting, facilitate STK export, and differentiate deterministic and Monte Carlo outcomes.
4.  **Deterministic vs Monte Carlo outputs:** Describe the fields included in deterministic summaries (mean formation window, aspect ratio, side length, centroid distance, maintenance delta‑v) versus those in Monte Carlo summaries (probability distributions, confidence intervals, compliance fractions). Discuss how the simulation stores each and how analysts should interpret them.
5.  **High‑fidelity propagation:** Detail the integration scheme used for the high‑fidelity propagation stage (e.g., Runge–Kutta with perturbation models). Clarify the order of operations when applying $`J_{2}`$ effects, drag, and optionally solar radiation pressure. Mention any third‑party libraries or ephemeris models used.

### 3.2 Triangle Simulation Workflow

1.  **Execution path:** Outline the major steps of `run_triangle.py`: reading configuration, computing LVLH offsets and ROE values, propagating the nominal formation, calculating metrics, estimating maintenance delta‑v, executing Monte Carlo campaigns, performing drag dispersion analysis, and exporting results. Explain how each step writes to CSV, JSON, and SVG outputs.
2.  **Metric definitions:** Define key metrics computed by the simulator: formation window duration, aspect ratio, minimum and maximum side lengths, centroid ground distances, maintenance budgets, command latency margins, injection recovery success rates, and drag dispersion statistics. Map each metric to mission requirements and acceptance criteria.
3.  **Monte Carlo campaigns:** Describe how Monte Carlo sampling is configured (number of samples, random seed, dispersion distributions). Explain how injection errors in along‑track position, inclination, and RAAN are sampled and how resulting metrics are aggregated.
4.  **Drag dispersion analysis:** Explain the method for simulating atmospheric drag variability and its impact on maintenance budgets. Note the scaling factors and perturbations applied and how results inform robustness assessments.
5.  **STK export:** Reiterate the process for exporting ephemerides and other artefacts to STK. Summarise file formats (.e, .sat, .gt, .int) and mention the validation guide used to import them successfully.

### 3.3 Automation and Interactive Interfaces

1.  **FastAPI service:** Provide an overview of the web service exposed by `run.py`. List endpoints for running triangle and scenario simulations (`/triangle`, `/scenario`), retrieving job status, and streaming logs. Describe payload models and optional parameters (e.g., number of Monte Carlo samples, random seed, export flags).
2.  **Interactive execution guide:** Summarise the steps in `interactive_execution_guide.md` for running simulations manually. Include environment activation, dependency installation, configuration selection, command execution, and log monitoring. Note recommended hardware (CPU cores, memory) and approximate run times for baseline scenarios.
3.  **Debugging:** Explain how analysts can use the debug CLI (`run_debug.py`) to run small test cases, extract CSV outputs, and generate additional plots. Provide examples of debug commands and explain how to interpret their outputs.
4.  **Job management:** Describe how jobs are queued, executed, and persisted. Explain where log files are stored, how to inspect them, and how to cancel or restart a job if needed. Mention any concurrency limitations or thread safety considerations.
5.  **Notification hooks:** If applicable, discuss integration with continuous integration (CI) systems to notify analysts of job completion or failures. Suggest Slack or email notifications for long‑running runs.

### 3.4 Regression Safeguards and Continuous Integration

1.  **Unit tests:** Outline the key unit tests safeguarding geometry calculations (`test_triangle_formation.py`), maintenance budgeting, command latency, and exporter behaviour. Note specific assertions (e.g., aspect ratio ≤ 1.02, Monte Carlo sample count matches configuration) and how they prevent regression.
2.  **Integration tests:** Summarise integration tests (`test_simulation_scripts.py`, `test_stk_export.py`) that run complete simulations with default parameters and verify outputs exist and conform to expected schema. Explain how these tests are invoked via CI.
3.  **Makefile targets:** List relevant Makefile targets (`make triangle`, `make scenario`, `make simulate`, `make docs`). Explain what each target does, which scripts it calls, and where outputs are stored. Encourage use of these targets to ensure repeatability.
4.  **Continuous integration workflow:** Describe how CI pipelines (e.g., GitHub Actions) are configured to run linting, unit tests, integration tests, and simulation smoke tests on pull requests. Note how simulation runs in CI may use reduced sample counts to save time.
5.  **Compliance verification:** Explain how the CI system checks compliance against mission requirements by comparing simulation outputs to acceptance thresholds. Describe how failures are reported and how analysts should respond.

### 3.5 Literature Review Prompts – Simulation and Tooling

Identify external sources (2019–2025) that inform the simulation pipeline and tooling:

1.  **RAAN optimisation techniques:** Survey algorithms for maximising target revisit, including analytical and numerical methods. Compare them to the repository’s search‑and‑evaluate approach. Identify any machine‑learning‑based or multi‑objective optimisation methods.
2.  **High‑fidelity propagation:** Review literature describing propagation pipelines integrating $`J_{2}`$ and atmospheric drag, and discuss validation against commercial tools such as STK. Note recommended integrator step sizes and perturbation models.
3.  **Monte Carlo automation:** Investigate methodologies for automating Monte Carlo campaigns in formation flying. Focus on reproducibility, random seeding, and artefact logging.
4.  **Web services for mission analysis:** Look at examples of mission analysis dashboards or web services that allow remote job submission and monitoring. Compare their architectures to the FastAPI implementation.
5.  **Regression and CI practices:** Read recent papers or blog posts on best practices for regression testing in scientific software. Distil lessons applicable to the simulation toolchain.

### 3.6 Suggested Figures, Tables, and Equations (Chapter 3)

- **\[Suggested Figure 3.1\]** Flowchart of the scenario pipeline stages with artefact outputs annotated. Each node should display the stage name, script function(s), and resulting file types.
- **\[Suggested Table 3.1\]** Comparison of deterministic and Monte Carlo metrics extracted by the scenario runner. Include centroid offsets, worst‑vehicle offsets, compliance fractions, and confidence intervals.
- **\[Suggested Figure 3.2\]** Artefact generation tree for the triangle simulation, mapping outputs to file formats and downstream uses (maintenance, command latency, STK validation). Indicate which outputs feed into later chapters.
- **\[Suggested Equation 3.1\]** Hill–Clohessy–Wiltshire relationships or other propagation formulas referenced in RAAN optimisation. Provide variables and units.

### 3.7 Narrative Flow Guidance

Structure Chapter 3 to show how automation enforces reproducibility: start with the pipeline description, segue into solver mechanics, proceed to artefact generation, and conclude with test coverage and CI governance. Use figure and table prompts to illustrate complex flows and summarise key metrics. Conclude by linking simulation outputs to the evidence requirements established in Chapter 1 and the configuration details discussed in Chapter 2.

### 3.8 Evidence Integration Checklist

1.  Verify that RAAN alignment discussions reference both deterministic and Monte Carlo JSON fields for compliance statements.
2.  Confirm that suggested figures label actual function names or logging stages from the scripts.
3.  Ensure that tables distinguish between midpoint metrics and full‑window statistics, clarifying relevance to mission requirements (e.g., MR‑2, MR‑4).
4.  Cite integration tests that assert artefact presence and schema compliance after triangle simulation runs.
5.  Explicitly state how STK export compliance is verified, referencing exporter modules and validation guides.
6.  Check that RAAN solver seeds and tolerances are recorded for reproducibility.
7.  Confirm that the pipeline description mentions both two‑body and high‑fidelity propagation stages.
8.  Ensure that the narrative notes where delta‑v budgets and command latency metrics are computed and stored.
9.  Reference any automation scripts used to regenerate runs and highlight their invocation in the CI pipeline.
10. Verify that random seeds for Monte Carlo campaigns are specified and logged.

### 3.9 Automation Runbook Tasks

1.  **Command‑line invocations:** Document how to invoke each pipeline stage from the command line (`make scenario`, `python -m sim.scripts.run_scenario`, `python -m sim.scripts.run_triangle`). Provide example commands with typical arguments (e.g., `--scenario config/scenarios/triangle.json --samples 100`).
2.  **Environment preparation:** List steps for environment setup: create and activate a virtual environment, install dependencies from `requirements.txt`, verify STK licence availability, and confirm dataset retention policies. Explain how to update dependencies without breaking compatibility.
3.  **Logging artefacts:** Enumerate the log files, JSON summaries, CSV exports, and plots generated at each stage. Specify naming conventions and directory structures to reduce search time during review.
4.  **Rerun protocol:** Define criteria triggering reruns (e.g., configuration updates, regression failures). Explain how to update run identifiers, regenerate RAAN solutions, re‑execute triangle simulations, and rerun Monte Carlo sweeps. Reference the authoritative run ledger for precedence and avoid overwriting evidence runs.
5.  **CI integration:** Describe how CI pipelines should invoke linters, unit tests, integration tests, and simulation smoke runs. Provide guidelines for test sample sizes in CI to balance coverage and runtime. Outline notification pathways for failures and required follow‑up actions.

### 3.10 Artefact Quality Assurance Checklist

1.  **Schema validation:** Verify that all JSON summaries conform to the expected schema. Update schema documentation when new metrics are introduced.
2.  **CSV integrity:** Check CSV headers for completeness and naming consistency. Confirm presence of units and definitions to support downstream analytics.
3.  **Plot fidelity:** When generating SVG figures (e.g., Monte Carlo cumulative distribution functions), ensure axis labelling, scaling, and legend clarity meet publication standards. Embed metadata describing data provenance.
4.  **STK package review:** Inspect exported `.e`, `.sat`, `.gt`, and `.int` files for naming conformity, time span alignment, and absence of import errors. Record outcomes in the run directory README and note any anomalies.
5.  **Regression artefact archive:** Store logs and artefacts from automation runs under timestamped directories with checksum manifests. Provide guidance on compressing or archiving large datasets and documenting their origin.
6.  **Data anonymisation:** Remove sensitive information (e.g., ground station coordinates) from publicly released artefacts while maintaining scientific accuracy.
7.  **Performance notes:** Record computational performance metrics (execution time, memory usage) for each script. Note any tuning performed (e.g., adjusting integrator step size) to balance accuracy and runtime.
8.  **Manual spot checks:** Recommend manual examination of random samples from CSV outputs to catch anomalies not detected by automated tests.
9.  **Version consistency:** Confirm that version numbers in configuration files, scripts, and documentation are consistent across artefacts. Update version identifiers when changes occur.
10. **Cross‑referencing:** Ensure that each artefact has cross‑references to the configuration, scenario, and run IDs that generated it. Use these cross‑references to populate the global reference index.

### 3.11 Simulation Log Interpretation Prompts

1.  **Stage‑specific log entries:** Extract representative log entries for each pipeline stage and explain how they confirm correct execution (e.g., RAAN optimisation convergence, propagation start and end times, Monte Carlo sample counts).
2.  **Warning and info messages:** Identify messages analysts should monitor for regression detection (e.g., warnings about step size reduction, missed contact windows). Note potential causes and remedies.
3.  **Metrics in logs:** Describe how to interpret JSON metric outputs alongside log files to diagnose anomalies or confirm success criteria. Provide examples of linking log timestamps to metrics.
4.  **Annotation practices:** Suggest best practices for annotating log excerpts in documentation. Encourage adding context and references to specific run configurations.
5.  **Correlation with artefact generation:** Provide guidance on correlating log timestamps with artefact generation times when assembling evidence packages. Recommend including start and end timestamps in artefact metadata.
6.  **Archival of logs:** Suggest archival practices for preserving critical log files, including compression, checksum generation, and metadata tagging. Clarify retention periods and deletion policies.

### 3.12 GNSS and PNT Constellation Interoperability Literature Review

1.  **Mission case studies:** Survey formation‑flying missions that relied on GNSS or broader positioning constellations for relative navigation (e.g., TanDEM‑X, GRACE/GRACE‑FO, PRISMA, CanX‑4/5). For each, document sensor suites, differential carrier‑phase processing pipelines, crosslink architectures, and demonstrated navigation accuracies. Cite primary references for each mission \[Ref19\] \[Ref20\] \[Ref21\].
2.  **Beyond‑GPS techniques:** Examine literature on utilising alternative or complementary positioning sources (Galileo, GLONASS, BeiDou, LEO PNT demonstrators, inter‑satellite ranging). Summarise benefits, limitations, and environmental constraints relevant to a Tehran overflight scenario. Include examples of hybrid navigation architectures combining GNSS with laser ranging or inter‑satellite links \[Ref22\].
3.  **Communication and timing strategies:** Analyse how GNSS‑enabled formations schedule uplinks/downlinks, manage clock synchronisation, and mitigate signal occultation at low altitudes. Highlight operational patterns transferable to the daily transient formation concept.
4.  **Design translation:** Conclude the review with a synthesis that explains why the current project assumes perfect state knowledge, point‑mass spacecraft, and simplified communications during conceptual studies. Identify which GNSS‑enabled practices could be emulated in simulation (e.g., carrier‑phase noise injections) and which require future hardware development.
5.  **Gap assessment:** Flag outstanding research questions such as robustness to GNSS outages over urban targets, applicability of differential drag when GNSS support degrades, and requirements for integrating FastAPI tooling with real‑time navigation data. Note where these topics will reappear (Chapter 4 evidence discussions and Chapter 6 future work).

### 3.13 GNSS Integration Deliverables and Analysis Tasks

1.  **Architecture overlay:** Produce diagrams or tables showing how GNSS or PNT satellite data would feed into existing simulation pipelines (`run_scenario.py`, `run_triangle.py`). Highlight required configuration parameters (antenna models, measurement noise) and identify placeholders for future code integration.
2.  **Data product mapping:** Specify expected artefacts (e.g., GNSS observation logs, relative position time histories, clock bias estimates) and how they would be stored alongside current JSON and CSV outputs. Describe validation steps needed to maintain STK export compatibility.
3.  **Scenario extensions:** Outline hypothetical simulation runs that inject GNSS measurement errors, loss‑of‑signal events, or multi‑constellation availability maps. Define success metrics (navigation accuracy thresholds, command latency impacts) and reference relevant literature for benchmark values.
4.  **Stakeholder implications:** Summarise operational impacts such as ground segment staffing, hardware selection, and regulatory considerations for GNSS spectrum use. Link these implications to recommendations and future work sections.

### 3.14 Chapter 3 References

1.  **TanDEM‑X Autonomous Formation Flying Experiment Report** – Documents dual‑frequency GPS processing and crosslink concepts enabling close formation maintenance \[Ref19\].
2.  **GRACE‑FO Laser Ranging and GNSS Navigation Summary** – Describes integrated GNSS and laser ranging solutions for tandem gravity missions \[Ref20\].
3.  **PRISMA Mission Navigation Performance Study** – Details differential GPS techniques and autonomous manoeuvre execution for nanosatellite formations \[Ref21\].
4.  **CanX‑4/5 Formation Flying Experiment Results** – Presents carrier‑phase GNSS navigation accuracy and autonomous control lessons from micro‑sat formations \[Ref22\].
5.  **Multi‑Constellation GNSS for LEO Formation Control White Paper** – Evaluates the use of Galileo, GLONASS, and emerging LEO PNT systems for formation flying scenarios similar to the Tehran concept \[Ref23\].

## Chapter 4 – Authoritative Runs, Quantitative Evidence, and Statistical Findings

Chapter 4 presents the quantitative evidence underpinning the mission’s compliance statements. It interprets the outputs of authoritative run directories, summarises key statistics, and links them to mission requirements.

### 4.1 Run Ledger Interpretation

1.  **Run classification:** Summarise the authoritative run register, explaining the status of each listed run (baseline, locked, exploratory) and how it underpins compliance statements. Highlight the baseline run (`run_20251018_1207Z`), the locked daily pass run (`run_20251020_1900Z_daily_pass_locked`), and the curated triangle summary snapshot (`artefacts/triangle_run`). Describe any exploratory runs (e.g., resampled daily passes) and note that they support sensitivity analyses rather than compliance statements.
2.  **Evidence mapping:** Explain how each mission requirement maps to specific runs. For example, MR‑1 (geometric formation) may be satisfied by metrics in the triangle summary; MR‑2 (target access) by the daily pass run; MR‑3 and MR‑4 (aspect ratio and side lengths) by triangle metrics; MR‑5 (command latency) by command window analyses; MR‑6 (maintenance budget) by maintenance summaries; MR‑7 (robustness) by Monte Carlo outcomes.
3.  **Run metadata:** Present key metadata for each run: creation date, scenario name, random seed, maintenance strategy, alignment validation status, and STK export flags. Note any differences between baseline and locked runs (e.g., adjustments to RAAN or sample counts).

### 4.2 Triangle Formation Metrics

1.  **Formation window and aspect ratio:** Analyse the formation window duration and aspect ratio metrics from the triangle summary. Report mean, minimum, and maximum values, and compare them against threshold (90 s target window, aspect ratio ≤ 1.02). Discuss any variability across deterministic and Monte Carlo results.
2.  **Side lengths and centroid distances:** Summarise side‑length statistics (minimum, maximum, standard deviation) and centroid ground distances. Convert angular metrics to ground distances and interpret their significance relative to mission requirements (e.g., centroid ground distance ≤ 30 km, waiver up to 70 km). Note differences between full‑propagation and windowed metrics.
3.  **Maintenance budgets:** Present delta‑v budgets estimated for each spacecraft. Provide mean and maximum values, compare them to the annual delta‑v cap (e.g., 15 m/s per annum), and discuss whether budgets differ across satellites due to plane separation.
4.  **Command latency:** Interpret command latency metrics from `command_windows.csv`. Report minimum, maximum, and mean latencies, and compare them to the 12‑hour command deadline. Identify any outliers and assess whether they impact mission operations.
5.  **Injection recovery and drag dispersion:** Summarise results from `injection_recovery.csv` and `drag_dispersion.csv`. Report injection recovery success rates, recovery times, and drag dispersion statistics. Discuss how these results inform robustness assessments and maintenance planning.

### 4.3 Daily Pass Alignment Evidence

1.  **Centroid and vehicle offsets:** Present deterministic and Monte Carlo findings from the locked daily pass run. Report centroid cross‑track offsets and worst‑vehicle offsets, including mean, maximum, and percentile values. Compare them to thresholds (e.g., ±30 km primary, ±70 km waiver) and note compliance fractions.
2.  **Pass fractions and RAAN values:** Provide the fraction of the orbital period during which the target is within the access window. Compare the RAAN before and after optimisation and note drift over the propagation span. Report the distribution of access times across Monte Carlo samples.
3.  **Compliance probabilities:** Compute compliance probabilities for MR‑2 and SRD‑P‑001 (a supporting requirement) based on Monte Carlo outcomes. Present them in a table or plot and discuss whether they meet the required probability thresholds (e.g., ≥ 95%).

### 4.4 Exploratory Runs and Sensitivity Analyses

1.  **Resampled daily passes:** Briefly document the purpose and limitations of exploratory runs that resample daily passes. Describe the resampling method (e.g., varying RAAN or time offsets) and summarise key metrics. Note that these runs are for sensitivity analysis only and should not replace authoritative evidence.
2.  **Altitude or inclination variations:** If any exploratory runs vary altitude or inclination, summarise their metrics and identify trends (e.g., how increasing altitude affects formation window or maintenance budget). Suggest whether these variations warrant further investigation.
3.  **Limitations:** Acknowledge limitations of exploratory runs, such as reduced sample counts, incomplete STK exports, or missing metadata. Recommend caution in interpreting their results.

### 4.5 Figure, Table, and Equation Prompts (Chapter 4)

- **\[Suggested Figure 4.1\]** Bar chart comparing formation window durations across baseline, locked, and exploratory runs. Indicate deterministic and Monte Carlo means and error bars.
- **\[Suggested Figure 4.2\]** Box plots of centroid ground distances for each run, separated into deterministic and Monte Carlo distributions.
- **\[Suggested Table 4.1\]** Summary of maintenance budgets (mean, median, maximum) per spacecraft and run. Include annualised delta‑v estimates and compare them to mission caps.
- **\[Suggested Equation 4.1\]** Relationship used to compute delta‑v budgets from thrust accelerations and time intervals.
- **\[Suggested Figure 4.3\]** Cumulative distribution function of command latency from `command_windows.csv`, with lines indicating the 12‑hour limit.
- **\[Suggested Equation 4.2\]** Formula converting angular centroid offsets into ground distances (reprise of Equation 1.2 for context).

### 4.6 Narrative Flow Outline

Organise Chapter 4 by walking the reader through the run ledger: first describe the baseline run and its metrics, then the locked daily pass run, followed by the triangle run, and finally exploratory runs. For each, summarise key statistics, relate them to mission requirements, and interpret compliance status. Use figures and tables to visualise metric distributions. Conclude by synthesising insights and identifying where further analysis is needed (e.g., altitude sensitivity, maintenance budget trade‑offs).

### 4.7 Evidence Integration Checklist

1.  Cross‑reference each mission requirement with the metrics presented in Chapter 4.
2.  Confirm that all key metrics (window duration, aspect ratio, side lengths, centroid distances, delta‑v budgets, command latency, injection recovery, drag dispersion) are reported for baseline and locked runs.
3.  Verify that Monte Carlo results include confidence intervals and compliance probabilities.
4.  Ensure that figures and tables clearly label run identifiers and deterministic vs Monte Carlo distinctions.
5.  Cite sources for any external formulas or thresholds used in metric calculations (e.g., delta‑v formulas).
6.  Include commentary on variations between full‑propagation and windowed metrics.
7.  Check that references to run directories and scenario files match their actual names.
8.  Note any anomalies or unexpected findings and suggest possible causes or follow‑up analyses.
9.  Confirm that exploratory runs are clearly distinguished from authoritative runs in both text and visuals.
10. Ensure that the narrative flow explains how Chapter 4 builds on Chapters 1–3 and sets up validation and recommendations in subsequent chapters.

### 4.8 Extended Task Breakdown – Chapter 4

1.  **Metric extraction:** Write scripts or use existing tools to extract metrics from JSON and CSV files. Automate summarisation to compute means, medians, maxima, minima, and percentiles.
2.  **Plot generation:** Produce the suggested figures (bar charts, box plots, cumulative distribution functions) using the extracted metrics. Ensure plots follow publication quality standards and annotate thresholds.
3.  **Table creation:** Assemble the suggested tables summarising maintenance budgets, compliance probabilities, and other statistics. Ensure units are consistent and include footnotes explaining thresholds.
4.  **Comparative analysis:** Compare metrics across runs to identify trends and trade‑offs. Discuss how differences in RAAN alignment or maintenance strategies influence outcomes.
5.  **Sensitivity assessment:** If exploratory runs vary parameters (e.g., altitude), summarise their effects on metrics. Propose which variations merit further study.
6.  **Monte Carlo interpretation:** Explain how to interpret probability distributions and confidence intervals. Discuss the meaning of compliance probabilities and how they contribute to risk assessments.
7.  **Limitations:** Acknowledge uncertainties in the simulations (e.g., atmospheric model accuracy, drag coefficient assumptions) and their impact on metrics. Suggest how future work might reduce these uncertainties.
8.  **Integration with STK:** If STK exports are available, describe how to import them into STK and verify metric alignment. Provide instructions or reference the STK validation guide.
9.  **Reporting templates:** Create templates for figures and tables so that analysts can quickly update them when new runs are performed. Encourage use of consistent colours, scales, and labelling conventions.
10. **Quality control:** Implement checks to ensure metric computations and visualisations are reproducible and accurate. Use unit tests where appropriate.

## Chapter 5 – Validation on a Representative System

In Chapter 5 the mission analysis is validated on a real or representative platform. The goal is to demonstrate that the candidate constellation and formation design perform as expected when interfaced with realistic tools and operational constraints.

### 5.1 Validation Platform and Environment

1.  **Representative platform:** Identify a representative system for validation. For the Tehran study this may be a region of interest with similar latitude, orbital conditions, and ground station availability (e.g., another mid‑latitude city). Explain why this platform is selected and how it approximates the actual mission environment.
2.  **STK import:** Describe the process for importing exported ephemerides and ground tracks into STK. Reference the validation guide and specify which files to import (`.e`, `.sat`, `.gt`, `.int`). Detail steps for verifying time ranges, coordinate frame selection, and object creation.
3.  **Pre‑validation checks:** List checks to perform before running the validation (e.g., confirm that initial conditions match exported ephemerides, verify that the formation geometry is preserved, ensure that ground station locations are correctly configured). Document any discrepancies and their resolutions.
4.  **Test cases:** Define the specific test cases to be validated: formation build‑up, maintenance manoeuvres, command latency, ground contact scheduling, and injection recovery. For each, describe the expected behaviour and success criteria.
5.  **Operational constraints:** Identify constraints imposed by the validation platform (e.g., limited communication windows, scheduling conflicts with other missions, STK computational limits). Note how these constraints may differ from the simulation environment and adjust expectations accordingly.

### 5.2 Validation Execution and Results

1.  **Before–after comparison:** For each test case, perform the operation in STK (or equivalent tool) and compare results to simulation predictions. For example, measure the formation window duration and aspect ratio using STK and compare them to values from the triangle summary. Document any differences and analyse their causes.
2.  **Ground contact verification:** Validate the predicted ground contact intervals by comparing simulation `command_windows.csv` outputs to STK contact analyses. Note any mismatches in timing or duration and investigate reasons (e.g., difference in Earth models, propagation settings).
3.  **Maintenance manoeuvre replication:** Simulate representative maintenance manoeuvres (e.g., differential drag or impulsive burns) in STK. Compare fuel consumption and resulting formation geometry to simulation estimates. Discuss any discrepancies and their implications for delta‑v budgets.
4.  **Sensitivity to perturbations:** Introduce small perturbations (e.g., injection errors, atmospheric density variations) in the STK environment and observe effects on formation metrics. Assess whether the Monte Carlo distributions produced in simulation are consistent with STK outcomes.
5.  **Validation metrics:** Compile metrics from the validation runs and summarise them in tables or plots similar to those in Chapter 4. Indicate whether validation results fall within predicted ranges and whether any adjustments to simulation models are warranted.

### 5.3 Limitations of the Validation

1.  **Model fidelity differences:** Discuss differences between the simulation environment and STK (e.g., drag models, gravitational harmonics). Explain how these differences may lead to metric discrepancies.
2.  **Operational variability:** Recognise that the validation platform may introduce operational constraints not present in simulation (e.g., communication outages, scheduling conflicts). Acknowledge that these factors could affect formation performance.
3.  **Data availability:** Note any limitations in available data (e.g., missing atmospheric density updates, incomplete orbit determination). Suggest how acquiring additional data (e.g., GPS tracking) could improve validation accuracy.
4.  **Hardware limitations:** If the validation uses a hardware‑in‑the‑loop setup or a specific ground segment, mention any limitations (e.g., processor speed, memory). Explain how these limitations influence run times or data fidelity.

### 5.4 Figure, Table, and Equation Prompts (Chapter 5)

- **\[Suggested Figure 5.1\]** Screenshot from STK showing the triangular formation at the mid‑latitude target. Label the satellites, ground station, and formation geometry.
- **\[Suggested Table 5.1\]** Comparison of key metrics (formation window, aspect ratio, side length, centroid distance, maintenance delta‑v, command latency) between simulation and validation runs.
- **\[Suggested Figure 5.2\]** Plot of ground contact intervals from simulation versus STK, highlighting differences.
- **\[Suggested Equation 5.1\]** Formula for converting fuel mass to delta‑v under the rocket equation, used to cross‑check maintenance budgets.

### 5.5 Narrative Flow Outline

Start Chapter 5 by introducing the validation platform and explaining its representativeness. Then describe the validation procedure step by step (importing ephemerides, performing test cases, comparing metrics). Use the suggested figures and tables to present results. Discuss discrepancies, their causes, and potential adjustments to simulation models. Conclude by summarising the validation’s success and limitations and setting up the final conclusions and recommendations.

### 5.6 Evidence Integration Checklist

1.  Confirm that validation runs use exported ephemerides from authoritative simulation runs.
2.  Verify that all validation test cases have corresponding simulation predictions for comparison.
3.  Ensure that validation metrics are presented in the same units and formats as simulation metrics.
4.  Document any differences between simulation and validation results and provide explanations.
5.  Note any limitations or constraints encountered during validation (e.g., STK licensing, hardware issues).
6.  Reference the validation guide in citations and explain how each step adheres to it.
7.  Include screenshots or visual evidence for each validation test case.
8.  Provide a summary table comparing simulation and validation metrics.
9.  Highlight any metrics that exceed thresholds or reveal new risks.
10. Suggest changes to simulation models or operational procedures based on validation findings.

### 5.7 Extended Task Breakdown – Chapter 5

1.  **Validation Plan Drafting:** Write a detailed validation plan including objectives, test cases, tools, metrics, and success criteria. Circulate it for stakeholder review before execution.
2.  **Test Case Implementation:** Implement the test cases in STK or the chosen validation tool. Automate as much as possible to ensure repeatability.
3.  **Data Collection:** Capture results from validation runs, including screenshots, logs, and exported metrics. Organise them in a structured directory with metadata files describing run conditions.
4.  **Comparison Scripts:** Develop scripts to compare validation outputs to simulation results. Automate metric extraction and produce difference reports.
5.  **Reporting:** Prepare the suggested figures and tables. Write narrative text explaining the validation process, results, and discrepancies.
6.  **Model Adjustment:** If validation reveals systematic differences, propose adjustments to simulation models (e.g., update atmospheric density, refine $`J_{2}`$ terms). Document any changes for future simulations.
7.  **Recommendations:** Draft recommendations for operational procedures based on validation findings (e.g., adjust command windows, schedule additional maintenance manoeuvres). Record them for inclusion in Chapter 6.
8.  **Lessons Learned:** Summarise lessons from the validation process, noting what worked well, what was challenging, and how to improve future validations.
9.  **Appendix Preparation:** Compile raw validation data and scripts into an appendix or supplementary repository to support reproducibility.
10. **Stakeholder Review:** Present validation findings to stakeholders and capture feedback for incorporation into conclusions and recommendations.

## Chapter 6 – Conclusions, Recommendations, and Future Work

Chapter 6 distils the findings from literature, simulations, and validation into concise conclusions. It identifies the best mission architecture and formation design, summarises limitations, and proposes recommendations for future work.

### 6.1 Summary of Findings

1.  **Mission objectives achieved:** State whether the mission objectives (90 s triangular formation window, daily repeatability, low maintenance budget) are met by the baseline design. Use metrics from Chapter 4 and validation results from Chapter 5 to support your statements.
2.  **Triangular formation performance:** Summarise how the equilateral formation performs in terms of window duration, aspect ratio, side lengths, and centroid distances. Highlight compliance probabilities for deterministic and Monte Carlo results.
3.  **Maintenance and command:** Discuss whether maintenance delta‑v budgets and command latency margins meet mission requirements. Note any trade‑offs observed between delta‑v consumption and formation quality.
4.  **Robustness and resilience:** Evaluate the robustness of the design to injection errors and drag variations. Summarise Monte Carlo compliance probabilities and identify any weaknesses.
5.  **Validation consistency:** Compare simulation predictions to validation results. State whether differences are within acceptable bounds and discuss possible reasons for discrepancies.

### 6.2 Limitations and Uncertainties

1.  **Model assumptions:** Identify assumptions in the simulations (e.g., atmospheric density models, constant drag coefficient, linearised ROE dynamics). Discuss their potential impact on results.
2.  **Data limitations:** Note any missing or uncertain data (e.g., mass properties of satellites, thrust efficiencies, ground station availability). Discuss how these uncertainties may affect conclusions.
3.  **Tool fidelity:** Recognise differences between simulation tools and real‑world systems (e.g., differences in gravitational harmonics, drag models). Suggest caution when extrapolating results.
4.  **Scope limitations:** Acknowledge that this study focuses on a specific target and set of orbital parameters. Explain how results might change for other targets or altitudes.

### 6.3 Recommendations

1.  **Design refinements:** Recommend adjustments to orbital parameters (e.g., slight increases in altitude or adjustments to RAAN) if they improve formation window duration or maintenance budgets without violating mission constraints.
2.  **Maintenance strategy:** Suggest whether impulsive manoeuvres, differential drag, or hybrid approaches are preferred based on delta‑v budgets and control complexity. Recommend manoeuvre scheduling (e.g., weekly corrections) and propellant allocation.
3.  **Ground segment enhancements:** Propose improvements to command and ground station architectures, such as adding a second ground station to reduce latency or implementing more responsive command uplink protocols.
4.  **Validation expansion:** Encourage further validation using high‑fidelity atmospheric models, additional targets, or hardware‑in‑the‑loop simulations. Suggest obtaining flight data from similar missions (e.g., MMS) to calibrate models.
5.  **Documentation and automation:** Recommend continuing to enhance documentation, automate run generation and analysis, and integrate new metrics as they are identified. Suggest periodic audits of artefact completeness and compliance status.

### 6.4 Future Work

1.  **Alternative formation shapes:** Investigate whether other formation geometries (e.g., isosceles triangles, linear arrays) could offer advantages in specific sensing applications or reduce maintenance costs.
2.  **Multi‑target missions:** Explore designs that service multiple mid‑latitude targets using the same constellation. Analyse trade‑offs between orbit design and ground segment complexity.
3.  **Adaptive scheduling:** Develop adaptive scheduling algorithms that adjust RAAN alignment and maintenance based on real‑time atmospheric data and operational conditions.
4.  **Advanced control algorithms:** Research advanced control strategies (e.g., model predictive control, reinforcement learning) for formation maintenance. Evaluate their fuel efficiency and robustness.
5.  **New propulsion technologies:** Consider the impact of emerging propulsion technologies (e.g., electric propulsion, drag sails) on formation maintenance and mission lifetime.
6.  **Extended mission scenarios:** Evaluate mission extensions (e.g., raising altitude for extended lifetime or transferring to different targets) and estimate delta‑v requirements.
7.  **Public release and outreach:** Plan for publishing data and results in scientific journals and presenting at conferences. Prepare outreach materials to communicate the mission’s significance to the public.
8.  **Cross‑disciplinary collaboration:** Encourage collaboration with atmospheric scientists, control theorists, and data analysts to improve models and analyses.
9.  **Open‑source tool development:** Contribute to or develop open‑source tools for formation‑flying simulation and analysis. Ensure tools are modular, well‑documented, and reproducible.
10. **Long‑term operational planning:** Develop strategies for operational handover, satellite decommissioning, and debris mitigation at end of life.
11. **GNSS and PNT interoperability roadmap:** Using the literature synthesis from Chapter 3, outline phased approaches for integrating GNSS (GPS, Galileo, GLONASS, BeiDou, emerging LEO PNT) measurements into future revisions of the simulation pipeline and hardware design. Discuss candidate algorithms (e.g., carrier‑phase double differencing, inter‑satellite ranging augmentation) and identify triggers for transitioning from idealised navigation assumptions to hardware‑in‑the‑loop demonstrations, explicitly citing precedent missions that communicated with positioning satellites to sustain formation coherence.

### 6.5 Chapter 6 References

1.  **Baseline Simulation Results** – Summarised metrics from authoritative runs \[Ref11\].
2.  **Validation Results** – Metrics obtained from representative validation platform \[Ref17\].
3.  **MMS Formation Flight Dynamics Results** – Provides context on formation maintenance and manoeuvre design \[Ref5\].
4.  **LISA Mission Overview** – Demonstrates the feasibility of triangular formations in space \[Ref4\].
5.  **Passive Safety Using Relative Orbital Elements** – Highlights ROE applications to passive safety and robustness \[Ref6\].
6.  **Additional Literature (2019–2025)** – Sources identified throughout the literature review blocks that inform recommendations and future work \[Ref18\].

### 6.6 Extended Task Breakdown – Chapter 6

1.  **Conclusion writing:** Draft concise conclusions that summarise the key findings and clearly state whether mission requirements are met. Use evidence from previous chapters.
2.  **Recommendation drafting:** Translate analysis into actionable recommendations. Ensure recommendations are prioritised, feasible, and linked to mission requirements.
3.  **Future work roadmap:** Create a roadmap for future research, specifying tasks, responsible parties, and tentative timelines. Indicate dependencies (e.g., requiring additional data or validation).
4.  **Limitations discussion:** Elaborate on the limitations listed above, explaining how they might be addressed in future work. Provide citations for any external studies that may help overcome these limitations.
5.  **Stakeholder presentation:** Prepare a briefing summarising the conclusions and recommendations. Tailor the message to different audiences (engineers, managers, scientists) and highlight critical decisions and trade‑offs.
6.  **Document finalisation:** Ensure all chapters are cross‑referenced correctly. Update the global reference index and appendices. Perform proofreading for grammar, formatting, and consistency.
7.  **Peer review:** Arrange for peer review of the final report. Capture feedback and integrate changes before final submission.
8.  **Publication preparation:** If the report will be published externally, adjust language to meet journal or conference guidelines. Prepare abstract, keywords, and acknowledgements.
9.  **Archival:** Archive all scripts, data, and artefacts used in the analysis. Ensure that future researchers can reproduce the study.
10. **Post‑project reflection:** Document lessons learned during the project, including successes, challenges, and unexpected insights. Share these lessons with the broader organisation to improve future projects.

## Chapter 7 – Appendices and Supplementary Material

The appendices consolidate reusable prompts, templates, checklists, and glossaries referenced throughout the report. They are essential for reproducibility and must be maintained alongside the main chapters.

### 7.1 Appendix A – Literature Search Prompts and Templates

1.  **Search prompt templates:** Provide generic search prompts for each literature block (e.g., “triangular satellite formation LEO 2019–2025”, “relative orbital elements passive safety 2020–2025”). Encourage analysts to adapt these prompts to specific databases and include synonyms (e.g., “formation flying”, “repeat ground track”).
2.  **Extraction templates:** Offer table templates for extracting information from literature. Include columns for citation, year, source type (journal, conference, standard), key findings, repository alignment, gaps, and proposed use. Provide example rows.
3.  **Source quality checklist:** Include criteria for judging source quality (peer‑reviewed, publicly accessible, recency, relevance). Encourage prioritising high‑quality sources and noting when grey literature is used.

### 7.2 Appendix B – Data Extraction and Reporting Templates

1.  **Metric extraction sheets:** Provide spreadsheets or CSV templates for recording metrics from JSON and CSV outputs. Include fields for each metric, units, sample counts, and notes.
2.  **Plot templates:** Supply reusable scripts or Jupyter notebooks for generating common plots (e.g., histograms, box plots, CDFs). Include placeholders for data file paths and output file names.
3.  **Table templates:** Offer Markdown or LaTeX templates for summarising run metrics, maintenance budgets, compliance probabilities, and validation comparisons. Include guidance on where to insert footnotes and citations.

### 7.3 Appendix C – Glossary of Terms and Acronyms

Provide concise definitions for technical terms used in the report. Include at least the following entries:

- **ROE (Relative Orbital Elements):** A set of parameters describing the relative motion between spacecraft in a formation. ROEs provide geometric insight and decouple dynamics along different axes \[Ref6\].
- **LVLH (Local Vertical Local Horizontal):** A reference frame attached to a spacecraft in orbit, with axes aligned to radial, in‑track, and cross‑track directions. Used for expressing formation offsets and control laws.
- **RAAN (Right Ascension of the Ascending Node):** The angle from the reference direction to the ascending node of an orbit. Adjusting RAAN aligns orbital planes and influences ground track.
- **HCW (Hill–Clohessy–Wiltshire) Equations:** Linearised equations describing relative motion between satellites in circular orbits. Used for initial formation design and quick estimations.
- **Delta‑v:** A measure of propulsive effort needed to change a spacecraft’s velocity. Used for budgeting maintenance manoeuvres.
- **Aspect Ratio:** Ratio of the longest to shortest side lengths of a triangle. For equilateral formations, it should be close to 1.
- **Centroid Ground Distance:** Ground distance between the formation’s centroid and the target location. A measure of formation alignment.
- **Monte Carlo Simulation:** A statistical technique that samples uncertainties (e.g., injection errors, drag variations) to estimate probabilities of meeting mission requirements.
- **STK (Systems Tool Kit):** A commercial mission analysis tool used for propagating orbits and visualising trajectories. Interfaces with exported ephemerides from the simulation pipeline.
- **Compliance Matrix:** A document mapping mission requirements to evidence and indicating whether thresholds are met, waived, or pending.

### 7.4 Appendix D – Quality Assurance and Submission Checklists

1.  **Submission quality assurance:** Provide a checklist for final document preparation: spell‑check, grammar review, British English usage, internal hyperlink validation, figure and table numbering, reference consistency, metadata accuracy, accessibility considerations, and reviewer sign‑off.
2.  **Citation management:** Describe best practices for maintaining a central bibliography, tagging references with keywords, recording access dates, and ensuring persistent identifiers (DOI, URI). Encourage periodic audits to retire outdated sources and prevent duplicate citations.
3.  **Review questions:** Offer a set of review questions to challenge assumptions and check completeness in each chapter. For example, “Does the literature review cover all relevant themes?”, “Are uncertainties and limitations adequately discussed?”, “Do figures and tables clearly communicate the metrics?”.

### 7.5 Appendix E – Repository Change Control Guidelines

1.  **Code changes:** Enforce modular commits with descriptive messages referencing objectives. Require updates or additions to tests when altering simulation logic or exporter behaviour. Document new scripts in the README and relevant documentation pages.
2.  **Configuration updates:** Increment the configuration version number when baseline parameters change. Update scenario metadata (author, creation date, alignment validation) upon re‑runs. Notify compliance and verification teams when updates impact requirements.
3.  **Documentation revisions:** Maintain British English spelling and academic tone. Update appendices and reference indices when new artefacts or external sources are cited. Perform documentation consistency checks using automated tools.
4.  **Artefact management:** Store new run outputs in time‑stamped directories following naming conventions. Include metadata files (run metadata, validation logs) for traceability. Avoid committing binary artefacts; prefer text‑based formats (CSV, JSON, SVG).
5.  **Review and approval:** Submit pull requests summarising mission design progress, analytical deliverables, and testing status. Ensure reviewers validate compliance implications and regression coverage. Record approvals and follow‑up actions for auditability.

### 7.6 Appendix F – Audit Trail Requirements

1.  **Run index:** Maintain a central index of all run directories, including creation dates, responsible analysts, and associated change requests. Update this index whenever new runs are performed.
2.  **Hash digests:** Store hash digests (e.g., SHA256) for key artefacts to detect unintended modifications. Regenerate digests upon re‑runs.
3.  **Meeting records:** Archive meeting minutes and review outcomes related to mission analyses. Link them to affected artefacts or documentation sections.
4.  **Decision rationales:** Capture decision rationales when adopting new configurations, algorithms, or validation procedures. Ensure that future auditors can trace the reasoning behind key choices.
5.  **Periodic audits:** Conduct periodic audits (e.g., quarterly) verifying artefact completeness, metadata accuracy, and compliance matrix updates. Document audit outcomes and corrective actions.

## Global Reference Index

The global reference index consolidates all repository artefacts, scripts, and external standards cited across chapters and appendices. It should include hyperlinks or relative paths to each referenced file, version identifiers, commit hashes, or run timestamps where applicable. Update the index whenever new artefacts or references are introduced so that the prompt remains synchronised with repository evolution. Use this index when constructing the final report’s bibliography.
