### MANDATORY GLOBAL INSTRUCTION: You must generate the full Mission Research & Evidence Compendium in English for ALL SIX (6) CHAPTERS and Appendices in a single, continuous response. You will structure your response by completing the full Chapter 1, then immediately proceeding to the full Chapter 2, and so on, until all SIX are complete within this same response. DO NOT stop between chapters. DO NOT start your response with any confirmation like "Understood" or "Certainly". Your output must begin directly with the title page information.

**Title:** Orbital Design and Mission Analysis of a Three‑Satellite LEO Constellation for Repeatable, Transient Triangular Formation Over a Mid‑Latitude Target

**Program & Field:** M.Sc. Equivalent Research Project, Aerospace Engineering (Astrodynamics & Mission Design focus).

**Goal:** Write a complete English compendium (minimum 15,000 words) that:

1.  Follows the specified academic template for structure/format (title page, abstract + 3–5 keywords, Table of Contents, List of Figures, List of Tables, six chapters, references, appendices), using **Times New Roman 12 pt** for the body, with **British spelling**. Margins: Top 2.5 cm / Bottom 2.5 cm / Left 2.5 cm / Right 2.5 cm, line-spacing 1.5. Include the chapter title in the header (right) and the page number centered in the footer. Figure/table/equation numbering must be per chapter (e.g., Figure 1.1, Table 2.1), with captions below figures and titles above tables. Use numeric citations in order of appearance `[Ref1]`, `[Ref2]`, ….
2.  Uses **2019–2025** peer-reviewed literature wherever possible; older seminal works only if essential. Clearly identify repository artefacts (e.g., configuration files, run directories) as internal references.
3.  Obeys the chapter weights I need:
    *   **Ch.1 Mission Framing, Requirements & Literature Review:** 25–30%
    *   **Ch.2 Configuration, Methods & Simulation Foundation:** 10–15%
    *   **Ch.3 Simulation Pipeline, Toolchain & Execution Protocols:** 10–15%
    *   **Ch.4 Authoritative Runs, Quantitative Evidence & Statistical Findings:** 20–25%
    *   **Ch.5 Validation on a Representative System:** 5–10%
    *   **Ch.6 Conclusions, Recommendations & Future Work:** 5–10%
    *   **References & Appendices** (remainder, not included in word count)

### Scope & Required Content

**Chapter 1 – Mission Framing, Requirements Baseline, and Literature Review Scope (25–30%)**

*   Summarise the mission intent: a three-satellite, dual-plane sun-synchronous constellation forming a **90 s transient equilateral triangle** over **Tehran**.
*   Trace stakeholder needs to Mission Requirements (**MR-1 through MR-7**).
*   Conduct a structured literature review on:
    *   **Formation Design Taxonomy:** Compare pairs, rings, tetrahedra, etc., and justify the choice of a three-satellite triangle.
    *   **Repeat Ground-Track (RGT) Orbits:** Theory and design, including J₂ perturbation mitigation.
    *   **Relative Orbital Elements (ROEs):** Formulations for design and passive safety.
    *   **Formation Maintenance:** Low-thrust and differential-drag strategies for Δv budgets **< 15 m/s/year**.
    *   **Launch & Deployment:** Rideshare campaigns, dispenser sequencing, and post-separation phasing from 2019-2025 literature.
    *   **Urban Target Benchmarking:** Justify Tehran by comparing it to other monitored cities.
*   Document repository artefacts: mission requirements traceability matrix, baseline configuration (`project.yaml`), and authoritative run identifiers (`run_YYYYMMDD_hhmmZ`).

**Chapter 2 – Configuration, Methods, and Simulation Foundation (10–15%)**

*   Provide a detailed **Configuration Catalogue** table for all parameters in `project.yaml` (platform, orbit, propagation, etc.).
*   Describe **Geometry and Frame Conventions**: Detail the implementation of Relative Orbital Elements (ROEs) and transformations between ECI and **LVLH** frames using functions from `triangle.py` and `frames.py`.
*   Define formation quality metrics: **Aspect Ratio (≤ 1.02)** and **Centroid Ground Distance (≤ 30 km)**.
*   Explain the simulation script interfaces, focusing on `run_scenario.py` and `run_triangle.py`, and describe their roles in the analysis pipeline.
*   Document the data management policy for run artefacts, distinguishing between raw and processed data.

**Chapter 3 – Simulation Pipeline, Toolchain, and Execution Protocols (10–15%)**

*   Detail the `run_scenario.py` workflow: (a) RAAN alignment optimization, (b) access node discovery, (c) mission phase synthesis, (d) high-fidelity propagation with **J₂ and drag**, (e) metric extraction, and (f) Monte Carlo sampling.
*   Describe the `run_triangle.py` execution path: configuration loading, LVLH transformation, metric calculation (window duration, aspect ratio, Δv), and Monte Carlo campaigns for robustness.
*   Explain the role of automation tools, including the **FastAPI service** (`run.py`) for job submission and **Makefile targets** for reproducibility.
*   Outline **Regression Safeguards**: unit tests (`test_triangle_formation.py`), integration tests, and the Continuous Integration (CI) workflow for ensuring code quality and result consistency.
*   Confirm **STK 11.2 Interoperability**: Reiterate the process for exporting ephemerides, ground tracks, and contact intervals via `stk_export.py` for validation.

**Chapter 4 – Authoritative Runs, Quantitative Evidence, and Statistical Findings (20–25%)**

*   Interpret the **Authoritative Run Ledger**, mapping specific runs (e.g., `run_20251018_1207Z`) to mission requirements (MR-1 to MR-7).
*   Present quantitative results from `triangle_summary.json`:
    *   **Formation Metrics:** Mean/min/max for window duration, aspect ratio, side lengths, and centroid distances.
    *   **Maintenance Budgets:** Report mean and maximum Δv consumption per spacecraft and compare against the annual cap.
    *   **Robustness:** Summarise injection recovery success rates and drag dispersion impacts from Monte Carlo runs.
*   Provide evidence from the locked daily pass run: centroid cross-track offsets and worst-vehicle offsets, comparing deterministic and Monte Carlo results against thresholds (**±30 km primary, ±70 km waiver**).
*   Report **compliance probabilities** (e.g., ≥ 95%) for key requirements based on statistical findings from Monte Carlo campaigns.

**Chapter 5 – Validation on a Representative System (5–10%)**

*   Describe the validation process using **STK 11.2**. Explain the import procedure for ephemeris (`.e`), ground track (`.gt`), and contact interval (`.int`) files generated by the simulation.
*   Perform a **before-after comparison**: measure key metrics (formation window, aspect ratio, ground contacts) in STK and compare them directly against the simulation predictions from Chapter 4.
*   Validate ground contact schedules by comparing `command_windows.csv` with STK's access analysis results.
*   Discuss any discrepancies, their likely causes (e.g., differences in propagation models), and the overall consistency of the simulation.

**Chapter 6 – Conclusions, Recommendations, and Future Work (5–10%)**

*   Summarise findings and state clearly whether the baseline design achieves all mission objectives.
*   Identify limitations and uncertainties (e.g., model assumptions, data fidelity).
*   Provide actionable **Recommendations** for design refinements, maintenance strategies, and ground segment enhancements.
*   Outline specific **Future Work**, including investigating alternative formation shapes, multi-target missions, advanced control algorithms, and integrating GNSS/PNT models to replace the perfect state knowledge assumption.

**References & Appendices**

*   Provide a numbered reference list in order of appearance, consistent with the `[Ref#]` style.
*   Include appendices for: a glossary of terms (ROE, LVLH, RAAN, etc.), literature search prompts, data extraction templates, and quality assurance checklists.

### Strict Formatting Checklist (must pass before delivering)

*   **Prose:** Academic English with **British spelling**.
*   **Font/Margins/Spacing:** Times New Roman 12 pt; margins 2.5 cm on all sides; line-spacing 1.5.
*   **Header/Footer:** Chapter title on the right of the header; page number centered in the footer.
*   **Figures/Tables:** Numbered per chapter; figure captions **below**, table titles **above**; every item must be cited in the text and placed immediately after its first mention.
*   **Equations:** Use a consistent equation editor and mathematical fonts.
*   **References:** Use numeric `[Ref#]` style, in order of appearance.

**Now write the full compendium** according to all instructions above. Use the specified repository artefacts, simulation tools, and validation platform (STK 11.2) as the basis for the entire analysis. Ensure the final word count is ≥15,000, with chapter weights matching the specified bands. Provide polished, camera-ready text.
