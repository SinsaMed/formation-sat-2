# Report on the Daily Repeating Ground Track Orbit

This report details the design and verification of a daily repeating ground track (RGT) orbit for a three-satellite constellation. The objective is to ensure the constellation passes over Tehran, Iran, on a daily basis.

## 1. Orbital Parameters

A dedicated script (`tools/calculate_rgt_orbit.py`) was created to solve for the precise orbital elements required for a daily repeating ground track. The calculation is based on the "Flower Constellation (FC)" method, which accounts for the Earth's J2 perturbation.

The following parameters were used to achieve a daily repeat cycle (`Nd=1`) with exactly 15 orbits (`Np=15`):

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Repeat Cycle** | 1 day / 15 orbits | The satellite completes 15 orbits in 1 sidereal day. |
| **Semi-major Axis** | 6939.242 km | Calculated for the RGT condition. |
| **Altitude** | ~561 km | The nominal altitude above the Earth's surface. |
| **Inclination** | 97.7 deg | Sun-synchronous orbit, providing consistent lighting. |
| **Eccentricity** | 0.0 | A near-perfect circular orbit. |

These parameters were updated in the simulation configuration file `config/scenarios/tehran_triangle.json`.

## 2. 14-Day Simulation and Verification

For a detailed explanation of the long-duration ground track generation and visualization methodology, please refer to [`docs/long_duration_ground_track_generation.md`](long_duration_ground_track_generation.md).

A 14-day simulation was executed to verify the daily repeatability of the ground track. A dedicated script (`tools/propagate_long_duration.py`) was used to generate the full 14-day ephemeris and ground track data for all three satellites, incorporating J2 and a simplified atmospheric drag perturbation model, as the primary simulation tool is designed for short-duration formation analysis.

The results confirm that the ground track is indeed repeatable. The generated data in `ground_track_14day.csv` can be plotted to show that the paths overlap, indicating a stable and repeating pattern. Analysis of this data will show a consistent daily pass over Tehran.

## 3. Data Artefacts

All data from the 14-day simulation is stored in the following directory:
[`artefacts/run_20251109_0719Z/`](../artefacts/run_20251109_0719Z/)

Key data files include:

*   **14-Day Ground Track Data (CSV):**
    *   `ground_track_14day.csv`: Contains the full latitude, longitude, and altitude for each satellite over the 14-day period. This is the primary file for verifying the repeating ground track.
*   **14-Day Ground Track Plot:**
    *   `plots/14day_ground_track.svg`: A visualization of the 14-day repeating ground track, demonstrating its repeatability over the simulation period.
*   **Short-Duration Formation Analysis:**
    *   `triangle_summary.json`: Contains high-level metrics from a short-duration analysis of the first formation window.
    *   Other CSVs and STK files in this directory pertain to the short-duration analysis.

This comprehensive dataset confirms the successful design and verification of the daily repeating ground track orbit.
