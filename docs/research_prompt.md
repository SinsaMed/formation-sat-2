# Research Prompt for Tehran Formation Mission Dossier

## Introduction
This prompt blueprint distils the repository's mission analysis corpus, simulation tooling, and verification practices into a single directive for generating an integrated research dossier on the Tehran-centred triangular constellation concept.[Ref1][Ref2] It threads together the configuration baselines, authoritative simulation runs, Systems Tool Kit (STK 11.2) interoperability rules, and regression safeguards so that future synthesised chapters remain faithful to the programme's configuration-controlled evidence.[Ref3][Ref4][Ref5][Ref6][Ref7][Ref8][Ref9][Ref10][Ref11][Ref12]

## Prompt Specification
**Your Role:** You are the lead mission systems researcher specialising in low Earth orbit formation flying, verification and validation, and STK-compatible data engineering for the Formation Satellite Programme.[Ref1][Ref11]

**Mission Dossier Title:** "Sustaining the Tehran Triangular Formation: Mission Architecture, Evidence, and Assurance."
**Central Case Study:** All concepts must remain anchored to the three-spacecraft equilateral formation that secures a ninety-second daily access window above Tehran while maintaining compliance with the programme's mission and system requirements.[Ref2][Ref4][Ref5][Ref6]

---

### **MANDATORY GLOBAL INSTRUCTION:**

**You must generate the complete "Mission Research & Evidence Brief" for ALL SIX (6) CHAPTERS in a single continuous response. Begin immediately with the heading for Chapter 1 and proceed sequentially through Chapter 6 without interruption or editorial asides. Do not preface the output with acknowledgements.**

Each chapter must explicitly reference configuration-controlled datasets, simulation scripts, and validation artefacts drawn from the repository's run ledger and tooling stack.[Ref5][Ref7][Ref8][Ref9][Ref10][Ref11]

---

### **Required Output Format for EACH Chapter:**

For every chapter, adhere to the following five-part structure:

**1. Key Artefacts & Sources (2019-2025 repository evidence):**
    * List 3–4 authoritative artefacts (documents, configurations, simulation directories, or tests) with full citations.

**2a. Synthesis of Core Findings & Arguments:**
    * Provide an academically toned synthesis interweaving the artefacts. Every factual claim, definition, or argument must terminate with an inline numbered citation, e.g., `The RAAN alignment stabilises the midpoint centroid offset within the ±30 km tolerance [1].`

**2b. Visual & Analytical Anchors:**
    * **Figures:** Recommend 1–2 figures, detailing content and pointing to the source artefact for adaptation. Example: `[Suggested Figure X.Y] 3D render of the 6 km LVLH triangle over Tehran, adapted from triangle_summary.json geometry samples [2].`
    * **Key Equations:** Identify 1–2 governing equations or algorithmic conditions (e.g., ROE propagation, RAAN drift correction) and cite their source. Example: `[Suggested Equation X.Y] Hill-Clohessy-Wiltshire drift relation Δλ(t) = Δλ(0) − (3/2) n (Δa/a) t from Roe propagation utilities [3].`
    * **Tables:** Specify any comparative or summary tables (e.g., maintenance budgets versus requirement caps) that the chapter should include.

**3. Proposed Narrative Flow for the Chapter:**
    * Write a cohesive paragraph describing how the chapter develops its argument, links back to preceding chapters, and prepares the reader for the next chapter.

**4. Numbered Reference List for this Chapter:**
    * Provide a complete reference list matching the inline citations used in Sections 1–3 of that chapter.

Ensure that every chapter restates the STK validation status or export dependency whenever artefacts rely on the `tools/stk_export.py` workflow or associated regression tests.[Ref8][Ref9][Ref10]

---

### **Chapter-by-Chapter Instructions:**

**Chapter 1: Mission Framing & Requirements Baseline**
* **Key Concepts:** Mission objectives, MR/SRD traceability, Tehran access rationale, run naming conventions, configuration management expectations.[Ref1][Ref2][Ref3][Ref11]

**Chapter 2: Configuration & Geometric Foundations**
* **Key Concepts:** `project.yaml` global constants, scenario JSON schemas, relative orbital element geometry, LVLH triangle construction, reference-plane allocations.[Ref3][Ref4][Ref8]

**Chapter 3: Simulation Pipeline & Toolchain**
* **Key Concepts:** Scenario runner stage sequence, RAAN optimiser outputs, triangle simulator metrics, artefact export hooks, Systems Tool Kit interoperability safeguards.[Ref5][Ref8][Ref9][Ref10]

**Chapter 4: Authoritative Runs & Quantitative Evidence**
* **Key Concepts:** `run_20251018_1207Z` maintenance campaign, `run_20251020_1900Z_tehran_daily_pass_locked` alignment data, Monte Carlo catalogues, delta-v accounting, windowed vs full-propagation statistics.[Ref5][Ref6][Ref7][Ref11]

**Chapter 5: STK Validation & Compliance Integration**
* **Key Concepts:** Export packages, import procedures, compliance matrix citations, regression tests guarding STK artefacts, cross-programme traceability expectations.[Ref6][Ref7][Ref10][Ref11]

**Chapter 6: Verification, Testing, and Future Work**
* **Key Concepts:** Verification & Validation Plan taxonomy, regression suite coverage, roadmap milestones, outstanding evidence actions, automation priorities for upcoming runs.[Ref7][Ref11][Ref12]

---

## References
- [Ref1] `README.md` – Repository overview and mission intent statement.
- [Ref2] `docs/project_overview.md` – Academic framing of the Tehran triangular formation mission.
- [Ref3] `config/project.yaml` – Programme-wide configuration baselines and maintenance policy.
- [Ref4] `config/scenarios/tehran_triangle.json` – Authoritative triangle formation scenario inputs.
- [Ref5] `docs/triangle_formation_results.md` – Simulation evidence for the Tehran triangular formation.
- [Ref6] `docs/tehran_daily_pass_scenario.md` – Locked daily pass configuration and STK validation record.
- [Ref7] `docs/_authoritative_runs.md` – Ledger of configuration-controlled simulation runs.
- [Ref8] `sim/formation/triangle.py` – Triangle formation simulation implementation and metrics extraction.
- [Ref9] `sim/scripts/run_scenario.py` – Scenario pipeline orchestrator with RAAN optimiser and STK export hooks.
- [Ref10] `tests/test_stk_export.py` – Regression tests verifying STK export file integrity and naming.
- [Ref11] `docs/compliance_matrix.md` – Mission and system requirement compliance traceability.
- [Ref12] `docs/verification_plan.md` – Verification and validation strategy, schedule, and resource planning.
