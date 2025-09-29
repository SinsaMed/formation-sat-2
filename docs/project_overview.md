# Project Overview

## Introduction
This document reframes the mission brief into an academic context for the conceptual design of a three-satellite low Earth orbit (LEO) constellation. The design seeks to produce a transient triangular formation above a city-scale target such as Tehran, thereby enabling cooperative sensing or communication experiments that require simultaneous spatial diversity.

## Mission Problem Statement
The mission must employ two satellites within Orbital Plane A and a third satellite in Orbital Plane B. The planes intersect above the target city, ensuring that a symmetric triangular geometry is achieved immediately before and after the shared nodal crossing. The formation must be recoverable on a daily schedule with a minimum guaranteed overlap window of approximately 90 seconds during which the triangle satisfies prescribed edge-length and angular tolerances.

## Key Objectives
1. Synthesise orbital elements that deliver the required ground-track convergence above the target city while maintaining acceptable coverage elsewhere.
2. Define relative orbital element (ROE) offsets that yield the transient triangular geometry near the nodal intersection.
3. Quantify perturbation-driven drift and devise maintenance strategies that preserve the repeatability of the formation.
4. Establish performance metrics—including access duration, geometric fidelity, and pointing constraints—that support downstream trade studies.

## Deliverables
- A catalogue of baseline Keplerian elements for the three spacecraft, annotated with rationales and sensitivity notes.
- A maintenance concept describing delta-v expenditures or drag modulation policies necessary for keeping the formation within tolerance.
- Simulation artefacts illustrating access windows, relative kinematics, and robustness analyses.
- Documentation templates for future experiment briefs and verification protocols, including [`concept_of_operations.md`](concept_of_operations.md), [`system_requirements.md`](system_requirements.md), [`compliance_matrix.md`](compliance_matrix.md), and [`verification_plan.md`](verification_plan.md).

## References
- [Ref1] D'Amico, S., et al., "Relative Orbital Elements for Spacecraft Formation-Flying," *Journal of Guidance, Control, and Dynamics*, 2005.
