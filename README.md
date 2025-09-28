# Conceptual Design of a Three-Satellite LEO Constellation

This repository scaffolds the analytical workflow for designing a three-satellite low Earth orbit (LEO) constellation that forms a repeatable, transient triangular formation above a designated city-scale target. The initial research brief focuses on Tehran, but the methodology generalises to any urban objective located along the constellation's ground track.

## Project Intent
- Formulate a mission architecture comprising two satellites in one orbital plane (Plane A) and a third satellite in a second plane (Plane B).
- Engineer the orbital elements so that both planes intersect above the target city, enabling a geometrically symmetric triangular formation immediately before and after the ascending or descending node crossing.
- Guarantee a daily (or otherwise cyclic) access window of approximately 90 seconds during which the triangular formation satisfies predefined geometric tolerances.
- Quantify maintenance strategies that mitigate dominant low-Earth perturbations (\(J_2\), drag, and solar radiation pressure) to preserve the repeatability of the formation.

Further elaboration on the mission statement, objectives, and derived requirements is available in [`docs/project_overview.md`](docs/project_overview.md).

## Repository Layout
- `AGENTS.md` – house style and collaboration guidelines for this codebase.
- `README.md` – the document you are currently reading.
- `docs/` – detailed academic documentation, including the staged research roadmap and requirement sets.
- `tests/` – placeholder directory for forthcoming analytical or software verification assets.

## Getting Started
1. Review the staged research workflow described in [`docs/project_roadmap.md`](docs/project_roadmap.md).
2. Establish modelling assumptions and parameter baselines using the requirement tables in [`docs/mission_requirements.md`](docs/mission_requirements.md).
3. Implement analytical prototypes or simulations in your preferred environment, committing incremental progress as you validate each stage.
4. Populate the `tests/` directory with automated checks (e.g., scenario verifiers, Monte Carlo campaigns) once modelling scripts are introduced.

## Contributing
All contributions must preserve the academic tone and reference discipline specified in `AGENTS.md`. Each pull request should: 
- Summarise the mission design progress achieved,
- Document new analyses or datasets within `docs/`, and
- Reference any added or updated tests.

## License
To be determined. Add licensing information before distributing the repository beyond the core research team.
