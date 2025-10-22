# Research Blueprint Prompt

**Project:** *Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target*

## Your Role

You are an expert academic research assistant specializing in aerospace engineering and you are the **lead mission systems researcher** specialising in LEO formation flying, guidance-navigation-control, verification & validation (V&V), and **STK 11.2**-compatible data engineering. You will produce a single integrated dossier (“**Mission Research & Evidence Brief**”) that others can typeset directly into a thesis/manuscript without further clarification.

## Mandatory Global Instruction

Generate the complete “Mission Research & Evidence Brief” for **all six chapters** in one continuous deliverable: begin directly with **Chapter 1** and proceed to **Chapter 6** without prefaces or asides. Every factual statement must be linked to **configuration-controlled evidence** and/or literature via inline numeric references (e.g., `[1]`) and a per-chapter numbered reference list. Retain the repository’s run-naming convention `run_YYYYMMDD_hhmmZ` in text.

## Global Output Expectations

* **Scope & depth:** Six fully developed chapters (each >1,000 words) + appendices as needed. Use a British-English analytical voice emphasising **traceability, reproducibility, and mission assurance**.
* **Evidence discipline:** Anchor assertions to **configuration-controlled artefacts** (e.g., `triangle_summary.json`, `deterministic_summary.json`, ledgered run IDs) and **declare** STK 11.2 validation status wherever exported ephemerides/contacts are consumed.
* **Reproducibility:** When quoting any metric (Δv, centroid offsets, triangle aspect ratios, window durations), restate the exact figure **as captured** in the artefact and record seeds, perturbations, and cadence settings used to produce it.
* **Governance:** Maintain cross-references to mission requirements (MR-#) and derived system requirements (SRD-###) using the compliance matrix; position recommendations within programme governance (SERB/CCB, V&V milestones).

## Required Chapter Structure (use verbatim in every chapter)

Under each `## Chapter X – Title`, include the following **five** subsections:

1. **Key Artefacts & Sources (2019–2026 repository evidence)** — 3–5 bullets naming the most relevant config files, docs, directories, or tests; end each bullet with an inline reference tag.
2. **Synthesis of Core Findings & Arguments** — 1–2 dense academic paragraphs; **every sentence ends with an inline numeric citation**.
3. **Visual & Analytical Anchors** — bulletised **[Suggested Figure/Table/Equation]** items; each ends with a source reference.
4. **Proposed Narrative Flow for the Chapter** — one paragraph showing how this chapter advances the dossier and sets up the next.
5. **Numbered Reference List for this Chapter** — ordered list matching the inline tags; do **not** invent sources outside the evidence base and literature you actually cite.

> **Why this structure?** It enforces a uniform, automatable scaffold across chapters, with built-in traceability and V&V hooks aligned to the project prompts.

## Source Fidelity, STK Interoperability, and Traceability (apply everywhere)

* Quote only **archived** artefacts; preserve run IDs and exact values; **never** round beyond the precision used in the artefact unless the artefact states a rounding rule.
* When referencing RAAN/centroid/geometry derived from daily-pass alignment or triangle runs, tie claims to the specific **authoritative run** and its export/validation logs.
* Explicitly note **STK 11.2** exporter versioning, file naming, and import workflow whenever simulation outputs feed visualisation/assurance.

## Literature & Standards Harvest (2019–2025+, engineering focus)

For chapters that integrate literature, search and cite peer-reviewed **2019–2025** sources (plus earlier seminal works) on: relative motion and ROE, formation-keeping in LEO with J2/drag/SRP, constellation operations and ground segment latency, autonomy/onboard maintenance filters, and V&V frameworks for learning-enabled systems if applicable. Tie each citation to a specific analytical gap surfaced by the repository (e.g., drag dispersion envelopes, revisit-to-delta-v tradeoffs).

## Repository Familiarisation (what to use as evidence anchors)

* **docs/**: mission overview, requirements, compliance, verification, scenario walkthroughs.
* **config/**: global constants and scenario definitions (your geometric/maintenance starting point).
* **sim/** & **src/**: formation dynamics and ROE utilities (equations & transforms to cite).
* **artefacts/**: authoritative run directories with JSON/CSV summaries and STK exports.
* **tests/**: regression harness that underpins reproducibility claims.

# Chapter-by-Chapter Blueprint (use these as binding instructions)

## Chapter 1 – **Mission Framing & Literature Review Foundations**

**Purpose:** Establish the mission intent and research axes for a *repeatable, transient equilateral formation* above a **mid-latitude** target. Frame stakeholder drivers, requirement hierarchy, and literature pillars that justify the architecture.

**1) Key Artefacts & Sources (pick 3–5 and cite)**

* `README.md`, `docs/project_overview.md` for mission framing and thesis voice.
* `docs/mission_requirements.md`, `docs/system_requirements.md`, `docs/compliance_matrix.md` for MR→SRD traceability and evidence tags.
* `config/project.yaml` for global constants (Earth model, nominal altitude, cadence).
* `docs/stk_export.md` and STK import how-to for interoperability statements.

**2) Synthesis of Core Findings & Arguments**
Write 1–2 dense paragraphs that: (a) state the mission problem (revisit + formation geometry over a mid-latitude target); (b) position the two-plane/three-sat constellation as a tractable architecture; (c) assert that all claims will be bound to configuration-controlled runs and STK-validated exports; (d) preview research threads (geometry, operations, maintenance, V&V). End **every sentence** with an inline numeric tag pointing to the above artefacts and to 2019–2025 literature you include.

**3) Visual & Analytical Anchors**

* **[Suggested Figure 1.1]** Programme roadmap swimlane aligned to V&V milestones and evidence refresh cycles. Source: `docs/project_roadmap.md`.
* **[Suggested Table 1.1]** MR→SRD→Evidence cross-reference (IDs + run IDs). Source: `docs/compliance_matrix.md`.
* **[Suggested Equation 1.1]** HCW/ROE relations that map LVLH offsets to element differences (cite repo ROE utilities).

**4) Proposed Narrative Flow**
Start from user/stakeholder drivers → formal MR/SRD → architecture sketch → where the repository already provides evidence and where literature fills gaps → signpost Chapter 2 (configuration baselines & geometry).

**5) Numbered Reference List**
Include all repository documents you cited and the external literature you integrated (2019–2025+). Keep numbering local to Chapter 1.

## Chapter 2 – **Configuration Baselines & Geometric Design Constructs**

**Purpose:** Freeze programme constants and define geometric constructs for an **equilateral LVLH triangle** that repeats transiently over the target; map scenario JSON → inertial states.

**1) Key Artefacts & Sources**

* `config/project.yaml` (Earth model, altitude, window targets, propulsion budgets).
* Scenario definitions for triangle/daily-pass (adapt to your mid-latitude target city/region).
* `sim/formation/triangle.py`, `src/constellation/orbit.py` (offset→state pipeline).

**2) Synthesis of Core Findings & Arguments**
Explain how global constants constrain feasible triangle size, access window, and maintenance cadence; describe the LVLH-to-ECI transform and propagation assumptions; justify parameter choices (time step, tolerances) against MR/SRD and literature on LEO perturbations (J2, drag). End each sentence with a numeric citation to artefacts and literature.

**3) Visual & Analytical Anchors**

* **[Suggested Figure 2.1]** LVLH-frame equilateral triangle and its inertial mapping across a 180-s window (adapt from formation generator and summary JSON).
* **[Suggested Equation 2.1]** LVLH offsets ((-\sqrt{3}L/6,\pm L/2,0)) → ECI via frame pipeline; annotate steps and assumptions.
* **[Suggested Table 2.1]** Sensitivity of access duration and centroid compliance to scenario parameters (time step, ground tolerance, contact range).

**4) Proposed Narrative Flow**
From constants → scenario encoding → geometry derivation → sensitivity triggers that lead directly into Chapter 3’s simulation pipeline and data engineering.

**5) Numbered Reference List**
List repository configs/code you cited plus geometry/perturbation literature (include classic sources for HCW/ROE and modern LEO modelling).

## Chapter 3 – **Simulation Pipeline, Toolchain, and Data Engineering**

**Purpose:** Make the data trail auditable: entry points, artefact schemas, exporter rules, tests, notebook standards, and automation for documentation refresh.

**1) Key Artefacts & Sources**

* Python entry points and Make targets (`sim.scripts.*`), exporter `tools/stk_export.py`.
* Tests/fixtures and CLI smoke tests for regression coverage.
* Documentation automation plan (MkDocs/Sphinx/Pandoc) and “notebook standards”.

**2) Synthesis of Core Findings & Arguments**
Describe how simulations are orchestrated end-to-end, how artefacts are versioned and validated (schema checksums, unit handling), how STK exports are produced and verified, and how notebooks generate controlled figures/tables with provenance headers. Cite repository policies prohibiting binary artefacts and define a **data pipeline checklist** (schema validation, rounding, outliers, cross-verification with raw artefacts).

**3) Visual & Analytical Anchors**

* **[Suggested Figure 3.1]** Block diagram of pipeline from scenario → run → JSON/CSV → STK export → figures.
* **[Suggested Table 3.1]** Notebook metadata header fields (run ID, scenario path, seed, expected outputs).
* **[Suggested Equation 3.1]** Error-budget propagation sketch (rounding and unit conversions) to bound reported metrics.

**4) Proposed Narrative Flow**
Outline orchestration, exporter usage, validation steps, and documentation automation; end by priming the reader for Chapter 4’s **authoritative runs** and quantitative synthesis.

**5) Numbered Reference List**
Include exporter docs, tests, automation notes, and any data-engineering literature cited.

## Chapter 4 – **Authoritative Runs & Quantitative Evidence Synthesis**

**Purpose:** Present curated runs and their **quantitative** evidence: windows, geometry, Δv, compliance probabilities, plus STK validation status.

**1) Key Artefacts & Sources**

* Authoritative run ledger and curated run directories in `artefacts/` with JSON/CSV summaries and screenshots.
* Visual evidence repository (SVG plots, annotated captures) and validation logs.

**2) Synthesis of Core Findings & Arguments**
Summarise each authoritative run: what changed, what was measured, how it maps to MR/SRD, and whether STK 11.2 validation has been completed. Reproduce metrics **exactly as archived** and link uncertainties to seeds/perturbations recorded in JSON. Tie maintenance budgets and centroid compliance to requirement ceilings; contrast deterministic vs Monte Carlo summaries. Every sentence ends with a numeric citation to specific run artefacts and, where appropriate, comparative literature.

**3) Visual & Analytical Anchors**

* **[Suggested Figure 4.1]** Access window distribution over the target for the selected month (SVG). Source: curated run.
* **[Suggested Table 4.1]** Run-by-run compliance matrix (metric, value, requirement ID, pass/fail, evidence path).
* **[Suggested Equation 4.1]** Δv aggregation across maintenance events, with unit and rounding rules stated.

**4) Proposed Narrative Flow**
Move from individual run results → cross-run synthesis → requirement compliance narrative; prepare the reader for Chapter 5’s **interpretation & cross-target adaptation**.

**5) Numbered Reference List**
List all runs/artefacts referenced and any comparative studies you cited.

## Chapter 5 – **Results Interpretation, Discussion, and Cross-Target Adaptation**

**Purpose:** Explain what the results mean, why they matter, and how to port the method to **any** mid-latitude target (not just the original case study).

**1) Key Artefacts & Sources**

* Results docs and scenario templates; compliance matrix entries used earlier.
* Comparative mission notes (e.g., formation-flying heritage) for context.

**2) Synthesis of Core Findings & Arguments**
Interpret revisit/geometry/Δv trade-offs, robustness to density/space-weather variability, and implications for single-station commanding. Provide a **transfer recipe** for retargeting: coordinate transforms, RAAN selection, and maintenance cadence tweaks. Support claims with your run evidence and current literature (2019–2025).

**3) Visual & Analytical Anchors**

* **[Suggested Figure 5.1]** Before/after plots showing adaptation from Target A to Target B (centroid & access deltas).
* **[Suggested Table 5.1]** Benchmark against selected comparator missions (baseline length, revisit, Δv).
* **[Suggested Equation 5.1]** RAAN drift/selection condition ensuring repeatable daily geometry under J2.

**4) Proposed Narrative Flow**
From explanation of results → operational implications → porting method → segue to Chapter 6’s **conclusions & recommendations** (roadmap, risks, and future work).

**5) Numbered Reference List**
Include repository and literature sources used for interpretation and benchmarking.

## Chapter 6 – **Conclusions, Recommendations, and Future Research Directions**

**Purpose:** Close the loop with decisions, actions, and research backlog aligned to programme governance and V&V milestones.

**1) Key Artefacts & Sources**

* `docs/project_roadmap.md`, `docs/verification_plan.md`, `docs/compliance_matrix.md`.

**2) Synthesis of Core Findings & Arguments**
State what is **proven**, what is **probable**, and what requires **further evidence**. Make **risk-adjusted recommendations** (ops, geometry, autonomy, ground segment), each tied to a requirement and an evidence source. Note TRL assumptions and propose next-run campaigns and QA gates.

**3) Visual & Analytical Anchors**

* **[Suggested Table 6.1]** TRL assessment with advancement actions and owners.
* **[Suggested Figure 6.1]** Roadmap overlay highlighting additional analyses and decision points before CDR/LRR.

**4) Proposed Narrative Flow**
Concise restatement of verified outcomes → concrete programme decisions → specific future-work items with owners/dates → closing remarks on reproducibility and open-science posture.

**5) Numbered Reference List**
List all plan/roadmap/verification documents and any standards/regulatory sources cited.

# Cross-Cutting Authoring Toolkit (use throughout)

## Evidence Integration Checklist (append to the end of each chapter)

* All claims end with numeric inline citations.
* Figures/tables/equations declared with **[Suggested …]** tags and source artefacts.
* Run IDs reproduced verbatim on first mention; seeds, perturbations, cadence recorded.
* STK 11.2 export/import status stated where relevant.
* MR/SRD links and compliance status updated.

## Style & QA Gates

Adopt house style (British English; neutral academic tone). Enforce pre-submission QA gates: **completeness**, **citation integrity**, **technical accuracy**, **traceability**; define escalation workflow for issues.

## Collaboration, Versioning, and Onboarding

Document review cycles, branching/pull-request expectations, and merge criteria; maintain an onboarding guide with a training exercise to **reproduce a full run** and **perform an STK import**.

## Appendices Guidance (optional but recommended)

* **Derivations:** lay out assumptions → steps → validation checks; cross-reference main text.
* **Extended tables/data listings:** specify captioning, footnotes, pagination; verify checksums and schema.
* **Code & algorithms:** include pseudocode/snippets with reproducibility notes (dependencies, steps, expected outputs).

# Literature & Standards Prompts (drop-in blocks your student can reuse)

* **Perturbation & Propagation Primer:** Summarise LEO perturbations (J2, drag), osculating elements, and HCW/ROE relations; cite a modern celestial-mechanics reference for Lagrange/Gaussian equations and drag modelling.
* **Numerical Methods Box:** Briefly review Runge–Kutta/Nyström, step-size control, and reliability concerns (close encounters aren’t your case, but include accuracy control best practices).
* **Operations & Ground Segment:** Survey single-station operations and latency assurance approaches; map to MR latency expectations and repository governance.
* **Autonomy & Onboard Processing (optional):** Review onboard maintenance and distributed control for formation-keeping; sketch a prototype algorithm plan that can plug into your pipeline for future work.

## Final Notes to the Author

* Keep prose in the body; use tables **only** for short labels/figures/IDs.
* Do not fabricate or interpolate numbers; quote exactly from artefacts.
* If a chapter needs external standards/regulatory references (e.g., debris mitigation, spectrum), include them in that chapter’s numbered list and tie them to specific compliance statements.
