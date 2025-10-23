# Literature Review Mandate

## Purpose
Provide a self-contained brief that governs all research and literature review activity supporting the mission entitled "Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over Tehran". The mandate ensures every investigative thread produces evidence that justifies methodology, demonstrates novelty, and sustains compliance with mission requirements and oversight boards.

## Research Governance

### Evidence Quality and Innovation Controls
1. Justify every analytical statement with peer-reviewed literature, official agency reports, or authoritative mission data. Combine canonical orbital mechanics references with contemporary (2020–2025) corroborating studies whenever HCW or ROE principles are invoked.
2. Emphasise how the proposed transient triangular formation advances beyond prior formation-flying missions, contrasting Tehran-specific objectives with generic constellations to foreground innovation.
3. Identify applicable international standards (e.g., ISO/IEC 23555-1:2022, ESA-GSOP-OPS-MAN-001, relevant ASTM/ISO norms) uncovered during the review and explain how they inform modelling, data handling, and operations.

### Citation Governance Protocol
1. Maintain a master reference ledger with immutable numeric identifiers assigned upon first citation. Subsequent mentions must reuse the same identifier to preserve repository-wide traceability.
2. Append chapter-specific reference lists that repeat only the sources cited in that chapter while keeping the master numbering intact.
3. Log every new source addition by updating the master ledger, propagating identifiers into all affected chapters, and recording the change in the formal change log for oversight review.
4. Apply the same identifier scheme to mission artefacts, simulation runs, and test evidence so documentary and empirical references remain synchronised across the thesis.

### Citation Style and Currency Rules
1. Use IEEE-style numeric citations `[n]` in order of first appearance. Acceptable sources include peer-reviewed articles, scholarly books, and agency or industry publications.
2. Prioritise works published between 2020 and 2025; use earlier seminal sources only when indispensable.
3. Keep a running record distinguishing between references extracted for potential use and those actually cited so downstream traceability into the concluding references chapter remains auditable.
4. There is no upper bound on the number of references. Expand the bibliography aggressively to capture the full state of the art.

## Sequential Research Threads
Conduct the following threads in order. Each entry lists the motivation for the literature review and the expected analytical product.

### 1. Distributed Constellation Trade Space
- **Rationale:** Establish why a three-satellite, transient equilateral triangle offers the optimal balance of sensing diversity, controllability, and lifecycle cost compared with tandem pairs, linear strings, tetrahedral clusters, swarms, and responsive cubesat formations.
- **Expected Outcome:** A trade-space analysis that quantifies sensing performance, geometric stability, propulsion demand, autonomy requirements, and mission risk for each topology, culminating in a justification for the selected architecture.

### 2. Paradigm Shift to Formation Flying
- **Rationale:** Document the historical progression from monolithic spacecraft to distributed constellations in order to frame the mission’s novelty.
- **Expected Outcome:** A narrative demonstrating how formation flying has transformed Earth observation capabilities, highlighting operational and scientific gains that motivate the transient Tehran triangle.

### 3. Metropolitan Overpass Duration Analysis
- **Rationale:** Validate the feasibility of achieving at least a 90 s continuous observation window over a megacity.
- **Expected Outcome:** Statistical models of LEO pass durations over major cities—explicitly including Tehran—that confirm the 90 s requirement. Reproduce the corridor calculation for a 6,890 km semi-major axis orbit travelling at approximately 7.60 km·s⁻¹, showing that maintaining cross-track displacement \(D \leq \sqrt{350^2 - (0.5 \times 90 \times 7.60)^2} \approx 74\,\text{km}\) retains the spacecraft within a 350 km ground-radius corridor.

### 4. Justification of the LEO Mission Class
- **Rationale:** Demonstrate that a sun-synchronous LEO at roughly 550 km best serves imaging, communications, and responsiveness goals.
- **Expected Outcome:** Comparative evidence against alternative altitude regimes, covering atmospheric drag management, revisit frequency, propulsion implications, and sensing performance.

### 5. Cross-Track Tolerance Derivation
- **Rationale:** Explain the origin of the ±30 km primary cross-track tolerance and the ±70 km waiver band that safeguard daily target access.
- **Expected Outcome:** A synthesis of corridor geometry, dwell-time analysis, and precision targeting literature that proves maintaining the formation centroid within ±30 km during the 90 s window guarantees compliance, while ±70 km is acceptable only for exceptional handling. Clarify measurement definitions using great-circle geometry and percentile-based checks.

### 6. Repeat Ground-Track Governance
- **Rationale:** Ensure that daily, repeatable passes over Tehran are theoretically defensible under dominant perturbations.
- **Expected Outcome:** Integrated coverage of repeat ground-track orbit design, \(J_2\)-driven nodal drift management, and inclination/altitude selection techniques. Compare analytical, semi-analytical, and numerical treatments to justify the adopted hybrid analytical–Monte Carlo methodology.

### 7. Core Theoretical Framework Synthesis
- **Rationale:** Assemble the predictive toolkit for relative motion and perturbation control before applying it in simulations.
- **Expected Outcome:** Consolidated derivations of Relative Orbital Elements, Hill–Clohessy–Wiltshire dynamics, differential nodal drift, atmospheric drag effects, and solar radiation pressure influences. Include parameter-derivation subsections that:
  1. Validate the \(6\,\text{km}\) equilateral separation and associated centroid spacing using ROE theory.
  2. Corroborate the baseline right ascension solutions and access window timing yielded by internal scenario analyses through published RAAN optimisation heuristics.
  3. Quantify perturbation magnitudes that necessitate \(J_2\) management and drag compensation strategies.
  4. Compare command latency findings from relevant missions against the twelve-hour turnaround requirement.

### 8. Comparative Urban Campaign Analysis
- **Rationale:** Substantiate the choice of Tehran as a high-value, high-complexity target.
- **Expected Outcome:** A comparative catalogue of urban observation campaigns (e.g., Mexico City, Istanbul, Los Angeles, Jakarta) covering geography, seismicity, atmospheric conditions, and infrastructure challenges. Use the comparison to articulate why Tehran’s characteristics demand and justify a transient formation strategy.

### 9. Formation Maintenance Strategy Review
- **Rationale:** Confirm that the annual \(\Delta v\) budget of ≤15 m/s per spacecraft is feasible.
- **Expected Outcome:** Survey findings on differential drag control, low-thrust propulsion, inter-satellite ranging, and autonomous guidance that demonstrate achievable maintenance envelopes, navigation accuracy, and fault tolerance. Identify research gaps requiring future adaptive control investigations.

### 10. Communications Architecture Baseline
- **Rationale:** Derive the data throughput necessary to downlink daily observation products and housekeeping telemetry.
- **Expected Outcome:** Literature-backed link budget analyses covering X-/S-band, optical crosslinks, and inter-satellite networking. Anchor the requirement to the 9.6 Mbps baseline and define scalability bands (25–45 Mbps) to support higher-resolution payloads, ground-station availability, latency constraints, and regulatory considerations.

### 11. Coordinated Payload Modalities
- **Rationale:** Show how the triangular geometry enables unique sensing products.
- **Expected Outcome:** Assessment of tri-stereo optical, interferometric radar, thermal, and atmospheric sounding modalities, including ground sampling distances, swath widths, signal-to-noise ratios, and raw/compressed data volumes. Translate the findings into guidance for the Level-0 → Level-1B → analysis-ready processing pipeline and the four-hour delivery objective.

### 12. Prior Transient Formation Missions
- **Rationale:** Benchmark the mission against prior transient or event-based formations to demonstrate advancement.
- **Expected Outcome:** Catalogue academic and agency efforts addressing transient formations or city-focused constellations, noting modelling assumptions, simplifications, validation approaches, and interoperability requirements. Contrast these with the project’s emphasis on reproducible toolchains and strict configuration control.

## Downstream Research Integration
1. Use the literature review outputs to justify all simulation methods and acceptance thresholds. Where thresholds (e.g., <2% metric divergence between analysis tools) lack published support, expand the literature search until a defensible value is established.
2. Pair quantitative results with published benchmarks when reporting Monte Carlo statistics, robustness findings, or data handling performance so reviewers can gauge relative performance.
3. Conduct targeted reviews for the Tehran environmental operations dossier, ensuring that geospatial, atmospheric, and socio-technical data originate from reputable datasets and align with operational procedures.
4. When benchmarking against international missions, open each comparison with a concise literature review that clarifies why each reference mission is relevant and supports the tabulated metrics.
5. Maintain a living list of emerging technologies—autonomous control, adaptive communications, advanced payload processing—to feed the Future Research Suggestions subsection with at least three literature-backed avenues.

## Expected Deliverables
1. A chapter that integrates all twelve research threads, culminating in the statement that transient equilateral formations maximise sensing value while containing risk and resource consumption for the Tehran mission.
2. A mapping that traces each literature-derived insight to mission requirements (MR-1 through MR-7 and the communications and payload mandates), demonstrating how evidence flows into subsequent methodological, simulation, and validation chapters.
3. Comprehensive traceability artefacts showing which sources were collected versus cited, enabling the concluding references chapter to reconcile the master ledger with chapter-level extracts without renumbering.
