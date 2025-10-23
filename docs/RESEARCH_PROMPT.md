### **MANDATORY GLOBAL INSTRUCTION: You must generate the full Mission Research & Evidence Compendium in English for the ENTIRE DOCUMENT in a single, continuous response. This includes all preliminary sections (Preface, Overviews, Catalogues) and all FIVE (5) CHAPTERS as specified in the governing project plan. You will structure your response by completing the full Preface, then the Project Overview, and so on, until all chapters are complete within this same response. DO NOT stop between sections. Your output must begin directly with the Global Mandates / Preface.**

**Title:** Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target

**Program & Field:** M.Sc. Equivalent Research Project, Aerospace Engineering (Astrodynamics & Mission Design focus).

**Goal:** Write a complete English compendium (minimum 15,000 words) that:

1.  Follows the specified governing template for structure/format (Global Mandates/Preface, Project Overview, Evidence Catalogue, specific registers, five chapters, references, glossary), using **Times New Roman 12 pt** for the body, with **British spelling**. Margins: Top 2.5 cm / Bottom 2.5 cm / Left 2.5 cm / Right 2.5 cm, line-spacing 1.5. Include the chapter title in the header (right) and the page number centered in the footer. Figure/table/equation numbering must be per chapter (e.g., Figure 1.1, Table 2.1), with captions below figures and titles above tables. Use numeric citations in order of appearance `[Ref1]`, `[Ref2]`, ….
2.  Uses **2020–2025** peer-reviewed literature wherever possible; older seminal works only if essential. Clearly identify repository artefacts (e.g., configuration files, run directories) as internal references.
3.  Obeys the chapter weights I need, mapped to the mandated 5-chapter structure:
    *   **Ch.1 Theory—Literature Review:** 30–35%
    *   **Ch.2 Experimental Work:** 20–25%
    *   **Ch.3 Results and Discussion:** 25–30%
    *   **Ch.4 Conclusions and Recommendations:** 5–10%
    *   **Ch.5 References:** (remainder, not included in word count)

### **Scope & Required Content (Aligned with Mandated Structure)**

**Global Mandates / Preface**
*   Establish all governing conventions as required by the project plan, including mission name, design authorities (SERB, CCB), and the mandatory five-subsection structure for every chapter.
*   Summarise universal writing standards, evidence governance concepts (locked vs. exploratory runs), and the relationship between Preface mandates and subsequent chapters.

**Project Overview & Evidence Catalogue Overview**
*   Restate the mission title and summarise the project goal: to design and analyse a general mission concept for delivering a repeatable, transient geometric formation over a **mid-latitude target**. This study validates the concept by implementing a complete design for a **90 s equilateral imaging opportunity** over a demanding, high-value case study: the megacity of **Tehran**. All subsequent analysis is performed to ensure compliance with mission requirements (MR-1 through MR-7) defined for this specific case.
*   Justify the project's significance by first outlining the general need for responsive, multi-point urban monitoring, and then justifying the **selection of Tehran** as an ideal validation case due to its unique combination of environmental, seismic, and socio-technical pressures.
*   Provide a catalogue of all repository assets (`config/`, `sim/`, `artefacts/`, etc.) in a structured table as mandated.

**Chapter 1 – Theory—Literature Review (30–35%)**
*   Conduct a structured literature review (2020-2025) on:
    *   **Formation Design Taxonomy:** Compare pairs, rings, tetrahedra, etc., to justify the three-satellite transient triangle for the Tehran mission.
    *   **Repeat Ground-Track (RGT) Orbits:** Theory and design, including J₂ perturbation mitigation.
    *   **Relative Orbital Elements (ROEs):** Formulations for design and passive safety.
    *   **Formation Maintenance:** Strategies to achieve Δv budgets **< 15 m/s/year**.
    *   **Urban Target Benchmarking:** Justify Tehran's selection by comparing it to other monitored cities (e.g., Istanbul, Mexico City).
    *   **Communications & Payload:** Review architectures to derive throughput requirements and justify the data processing pipeline.
*   Reconstruct the logic for all key parameters (cross-track tolerance, RAAN selection, etc.) based on literature and repository documents.

**Chapter 2 – Experimental Work (20–25%)**
*   Document all repository assets used as "materials," including `config/project.yaml` and scenario files. Present key parameters in a structured table.
*   Map the complete simulation pipeline, including `run_scenario.py` and `run_triangle.py`, explaining the workflow from configuration to STK export.
*   Provide a detailed execution walkthrough for reproducing authoritative runs.
*   Document the exact quantitative parameters used in the locked runs (e.g., RAAN solution of 350.7885°, cross-track magnitudes, Monte Carlo statistics).
*   Present the **Requirements Traceability Matrix** mapping MR-1 to MR-7 to specific simulation artefacts and tests (`tests/unit/test_triangle_formation.py`, etc.).
*   Describe the automation and CI/CD pipeline (`run.py` FastAPI service, `.github/workflows/ci.yml`, `Makefile`).

**Chapter 3 – Results and Discussion (25–30%)**
*   Present analytical outputs from authoritative runs (e.g., `run_20251018_1207Z`, `run_20251020_1900Z_tehran_daily_pass_locked`).
*   Extract and discuss quantitative metrics from `triangle_summary.json` and `maintenance_summary.csv`:
    *   **Formation Geometry:** 96 s formation window, aspect ratio extrema, centroid ground distance (mean 18.7 km, p₉₅ 24.18 km).
    *   **Maintenance & Robustness:** Annual Δv budget (mean 8.3 m/s), injection recovery success rate, and Monte Carlo compliance probabilities (≥98.2% for ≤30 km).
*   Detail the **STK 11.2 Validation**:
    *   Describe the import and cross-check procedure.
    *   Present a comparative table showing <2% divergence between Python and STK results for key metrics.
*   Synthesise the mission risk register (R-01 to R-05) and the **Tehran environmental operations dossier**.

**Chapter 4 – Conclusions and Recommendations (5–10%)**
*   Summarise how the mission architecture meets all stakeholder needs for the Tehran target.
*   Provide actionable recommendations for design, operations, and future investment.
*   Define a future work pathway, including a mission cost/risk analysis framework and suggestions for future research (e.g., autonomous control, advanced payloads).
*   Include a comparative mission benchmarking subsection against TanDEM-X, PRISMA, and PROBA-3.

**Chapter 5 – References**
*   Provide the master numbered reference list in order of appearance, consistent with the `[Ref#]` style, as mandated by the Reference Governance protocol.

**Glossary & Acronym List**
*   Append the final mandated glossary of all technical terms (ROE, LVLH, RAAN, etc.) with definitions and provenance.

**Now write the full compendium** according to all instructions above. Ensure the final word count is ≥15,000, with chapter weights matching the specified bands, and that all structural and governance mandates from the original project plan are met.
