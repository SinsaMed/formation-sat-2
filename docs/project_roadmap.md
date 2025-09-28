# Project Roadmap

## Introduction
The roadmap decomposes the mission brief into sequential, academically framed work packages. Each stage specifies the motivating question, the expected progress state, and the principal deliverables necessary to advance the constellation design toward completion.

## Stage 1 – Mission Context and Requirement Capture
1. **Define the core problem.** Clarify the operational scenario, target city coordinates, and mission stakeholders, yielding a concise statement of need.
2. **Catalogue assumptions.** Document orbital regimes, spacecraft class (e.g., CubeSat specifications), and communication constraints.
3. **Translate objectives into requirements.** Populate the requirement matrix in [`mission_requirements.md`](mission_requirements.md) and review traceability against stakeholder goals.

## Stage 2 – Orbital Architecture Synthesis
1. **Select baseline orbital parameters.** Determine altitude, inclination, and repeat-ground-track conditions that align the nodal intersection with the target city.
2. **Allocate satellites to planes.** Assign two spacecraft to Plane A and one to Plane B, specifying initial right ascension of the ascending node (RAAN) offsets and argument placements.
3. **Formulate relative orbital elements.** Compute \(\delta a\), \(\delta \lambda\), \(\delta e_x\), \(\delta e_y\), \(\delta i_x\), and \(\delta i_y\) for each satellite pair to shape the triangular formation during the window of interest.

## Stage 3 – Access Window Analysis
1. **Simulate ground-track convergence.** Use analytical or numerical tools to determine the temporal alignment of the three satellites above the target city.
2. **Quantify formation geometry.** Evaluate side lengths, internal angles, and centroid dynamics throughout the access interval; confirm that the 90-second requirement is met.
3. **Assess observation constraints.** Examine line-of-sight, elevation angles, and sensor pointing to ensure the formation is operationally useful.

## Stage 4 – Perturbation and Maintenance Strategy
1. **Model dominant perturbations.** Incorporate \(J_2\), atmospheric drag, and solar radiation pressure into the relative motion analysis.
2. **Design maintenance manoeuvres.** Develop delta-v budgets or drag-modulation tactics that keep the formation within tolerance over the mission duration.
3. **Plan command timelines.** Outline when and how corrections are uploaded given the single ground-station assumption.

## Stage 5 – Verification and Validation
1. **Develop automated checks.** Implement scripts or notebooks that reproduce key metrics and place them under `tests/`.
2. **Conduct sensitivity studies.** Perturb initial conditions to evaluate robustness against injection errors and environmental uncertainties.
3. **Compile final dossier.** Aggregate findings into a publishable report summarising methodology, results, and recommendations for deployment.

## References
- [Ref1] Wertz, J. R., *Mission Analysis and Design*, Microcosm Press, 2011.
