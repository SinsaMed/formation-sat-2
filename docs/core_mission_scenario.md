# Core Mission Scenario: Tehran Transient Triangle

## 1. Overview

The primary mission of this project is to simulate a three-satellite constellation that establishes a transient, repeating triangular formation over a target area centered on Tehran, Iran.

The core objective is to demonstrate a stable, equilateral triangle formation with a side length of 6 km for a minimum duration of 90 seconds during a daily pass over the target.

## 2. Constellation and Orbit Design

The constellation consists of three satellites deployed into two distinct low-Earth orbit (LEO) planes.

-   **Plane Configuration:**
    -   **Plane A:** Contains two satellites (SAT-1 and SAT-2).
    -   **Plane B:** Contains one satellite (SAT-3).

-   **Orbit Type:** The formation is based on a **daily repeating ground track (RGT) reference orbit**. This sun-synchronous orbit is designed to complete exactly 15 orbits in one sidereal day, ensuring a consistent daily pass over the target region.

-   **Formation Mechanics:** The formation is achieved by placing the three satellites into precisely coordinated orbits. A single reference satellite's RGT orbit is used as the baseline. The other satellites are placed in slightly different orbits, calculated as offsets in the local-vertical, local-horizontal (LVLH) frame relative to the reference. This passive, relative motion causes the desired triangular geometry to form as the constellation passes over the target. The entire formation's ground track is designed to be repeatable daily.

## 3. Mission Requirements

The simulation must verify the following key performance parameters:

-   **Formation Geometry:** An equilateral triangle with a 6 km side length. The simulation monitors aspect ratio and side length deviations.
-   **Target Coverage:** The formation must occur over Tehran, with all three satellites remaining within a 350 km ground tolerance of the city's center during the formation window.
-   **Formation Duration:** The triangular geometry must be maintained for a minimum of 90 seconds.
-   **Repeatability:** The formation event over Tehran must repeat on a daily basis.

## 4. Station-Keeping and Maintenance

The simulation accounts for the long-term stability of the formation. While the short-duration pass is modeled using ideal Keplerian motion, the project includes analysis to estimate the effects of orbital perturbations over longer periods. The simulation quantifies the required orbital corrections (delta-v) and the frequency of station-keeping maneuvers needed to maintain the formation's integrity over time.
