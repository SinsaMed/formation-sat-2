### Active Station-Keeping Implementation Debugging Report

**Problem Statement:**
The active station-keeping functionality, implemented to maintain a three-satellite triangular formation under perturbed orbital dynamics, is not effectively achieving the desired formation duration. The unit test `test_triangle_formation_meets_requirements` consistently fails with `assert window["duration_s"] >= 90.0`, reporting a formation window duration of only 46.0 seconds, despite maneuvers being triggered. The primary symptom is an extremely large calculated delta-V during maneuvers, indicating a significant discrepancy between the actual satellite state and the calculated ideal state.

**Context:**
The goal is to implement active station-keeping for a satellite formation. The chosen strategy is a "teleport" maneuver: if the predicted formation deviation exceeds a tolerance, satellites are instantly reset to their "ideal" positions and velocities. The simulation uses `propagate_perturbed` for orbital propagation, which includes J2, atmospheric drag, and solar radiation pressure (SRP) perturbations.

**Initial State of Active Station-Keeping Implementation:**
*   **File:** `sim/formation/triangle.py`
*   **Function:** `simulate_triangle_formation` (main simulation loop) and `_plan_and_execute_maneuver` (station-keeping logic).
*   **Configuration:** `config/scenarios/tehran_triangle.json` defines `station_keeping_interval_s`, `prediction_horizon_s`, and `station_keeping_tolerance_m`.

**Debugging Steps and Findings (Chronological):**

1.  **Initial Failure (`assert 46.0 >= 90.0`):**
    *   **Observation:** The test failed, indicating the formation was not maintained for the required 90 seconds.
    *   **Hypothesis:** The `station_keeping_interval_s` (initially 21600s in config) was too long, preventing maneuvers within the short 180s simulation.
    *   **Action:** Modified `test_triangle_formation_meets_requirements` to set `station_keeping_interval_s` to 60.0s in the in-memory configuration.

2.  **Hyperbolic Trajectories during Prediction:**
    *   **Observation:** After enabling maneuvers, the test failed with `ValueError: Hyperbolic trajectories are not supported` originating from `propagate_perturbed` within `_plan_and_execute_maneuver`'s prediction step.
    *   **Hypothesis:** `propagate_perturbed` was numerically unstable or producing unphysical states when used for prediction.
    *   **Action:** Switched `propagate_perturbed` to `propagate_kepler` for prediction in `_plan_and_execute_maneuver`.
    *   **Sub-issue:** `propagate_kepler` initially returned a tuple, causing `TypeError: propagate_kepler() got an unexpected keyword argument 'return_elements'` and `AttributeError: 'tuple' object has no attribute 'semi_major_axis'`.
    *   **Fixes:** Modified `propagate_kepler` in `src/constellation/orbit.py` to accept `return_elements=True` and return `OrbitalElements` when requested. Corrected `_plan_and_execute_maneuver` to handle the `OrbitalElements` object.
    *   **Sub-issue:** `ValueError: At least one array has zero dimension` from `numpy.cross` in `triangle_area`.
    *   **Fix:** Corrected `_plan_and_execute_maneuver` to properly extract vertices for single time step geometry calculation and convert `triangle_side_lengths` output to `np.array`.
    *   **Result:** Test still failed with `assert 46.0 >= 90.0`.

3.  **Investigation of Perturbation Strength:**
    *   **Hypothesis:** The perturbations were too strong, causing rapid formation breakdown.
    *   **Action:** Temporarily disabled all perturbations in `src/constellation/orbit.py` (`propagate_perturbed`'s `dynamics` function).
    *   **Observation:** `Max predicted deviation: 0.0000 m`. Maneuvers were *not* triggered because the predicted deviation was zero (below tolerance). This confirmed that the maneuver logic was not being exercised under ideal conditions.
    *   **Action:** Re-enabled perturbations in `src/constellation/orbit.py`.

4.  **Inconsistency between Prediction and Correction Models:**
    *   **Observation:** With perturbations re-enabled, the maneuver was triggered, but `Total Delta-V consumed` was ~2235 m/s, and the formation still failed (`assert 46.0 >= 90.0`).
    *   **Analysis:** The prediction step in `_plan_and_execute_maneuver` was using `propagate_perturbed` (correct for predicting drift under perturbations), but the maneuver's target state (`ideal_propagated_elements`) was being calculated using `propagate_kepler` (unperturbed ideal). This inconsistency meant the maneuver was correcting to an unperturbed ideal in a perturbed environment.
    *   **Action:** Modified `_plan_and_execute_maneuver` to use `propagate_perturbed` for calculating `ideal_propagated_elements` (the target state for the maneuver), ensuring consistency between prediction and correction models.
    *   **Sub-issue:** An `IndentationError` occurred due to a copy-paste error during the previous `replace` operation.
    *   **Fix:** Corrected the `IndentationError`.
    *   **Result:** Test still failed with `assert 46.0 >= 90.0`. Print statements showed `Max predicted deviation: 156.2679 m` (with `prediction_horizon_s` 60s) and `Total Delta-V consumed: 2235.1825 m/s`.

5.  **Current Problem Analysis (Large Delta-V):**
    *   **Observation:** The `Ideal Velocity` and `Current Velocity` values printed from `_plan_and_execute_maneuver` are vastly different (e.g., `Ideal Velocity: [-4916, -9, 5769]` vs. `Current Velocity: [-5447, 142, 5270]`). This large discrepancy directly leads to the enormous delta-V.
    *   **Hypothesis:** The way `ideal_propagated_elements` (the target state for the maneuver) is calculated is still problematic. It's currently derived by propagating the `initial_ideal_elements_for_sat` (which are Keplerian elements from the simulation start) using `propagate_perturbed`. This "ideal" perturbed trajectory is diverging significantly from the actual perturbed trajectory of the satellites.
    *   **Latest Attempt:** Modified `_plan_and_execute_maneuver` to calculate the `ideal_propagated_elements` based on the perturbed propagation of the *global `reference_elements`* (from `simulate_triangle_formation`) and then applying the `formation_offsets`. This aims to ensure the maneuver's target state is consistent with the perturbed dynamics of the reference orbit, which the formation is supposed to follow.

**Current State of the Code:**
*   `sim/formation/triangle.py`:
    *   `simulate_triangle_formation`:
        *   `reference_elements` is now always defined and passed to `_plan_and_execute_maneuver`.
        *   `station_keeping_interval_s`, `prediction_horizon_s`, `station_keeping_tolerance_m`, `last_maneuver_time`, `total_delta_v_consumed`, and `satellite_physical_properties` are initialized.
        *   The main loop includes a conditional call to `_plan_and_execute_maneuver`.
        *   `station_keeping` metrics now include `total_delta_v_consumed_mps`.
    *   `_plan_and_execute_maneuver`:
        *   Accepts `reference_elements` as an argument.
        *   Calculates `predicted_elements` using `propagate_perturbed`.
        *   Calculates `max_predicted_deviation` from `predicted_elements`.
        *   If `max_predicted_deviation > station_keeping_tolerance_m`:
            *   Propagates the global `reference_elements` using `propagate_perturbed` to the `current_epoch`.
            *   Calculates the LVLH frame at this perturbed reference state.
            *   Applies `formation_offsets` to get `ideal_perturbed_sat_pos` and `ideal_perturbed_sat_vel`.
            *   Sets `updated_elements[sat_id]` to `cartesian_to_classical(ideal_perturbed_sat_pos, ideal_perturbed_sat_vel)`.
            *   Calculates `delta_v_eci` as `ideal_perturbed_sat_vel - current_sat_vel_eci`.
*   `src/constellation/orbit.py`:
    *   `propagate_kepler`: Modified to accept `return_elements` argument.
    *   `propagate_perturbed`: Perturbations (J2, drag, SRP) are re-enabled.
*   `tests/unit/test_triangle_formation.py`:
    *   `test_triangle_formation_meets_requirements`:
        *   Loads `tehran_triangle.json`.
        *   Sets `station_keeping_interval_s = 60.0`, `prediction_horizon_s = 60.0`, `station_keeping_tolerance_m = 60.0` in the in-memory config for testing.
        *   Includes an assertion for `station_keeping["total_delta_v_consumed_mps"] >= 0.0`.

**Current Problem (Post-Latest Attempt):**
Even with the latest change to derive the ideal maneuver target from the perturbed reference orbit, the `Ideal Velocity` and `Current Velocity` still show a large discrepancy, leading to an enormous `Total Delta-V consumed` (~2235 m/s). The test still fails with `assert 46.0 >= 90.0`.

This indicates that the "ideal" perturbed formation, as calculated by propagating the reference orbit and applying static offsets, is still diverging significantly from the actual perturbed trajectories of the individual satellites.

**TODOs / Next Steps for Developer:**

1.  **Deep Dive into Velocity Discrepancy:**
    *   **Verify `perturbed_ref_vel` vs. `ideal_perturbed_sat_vel`:** The line `ideal_perturbed_sat_vel = perturbed_ref_vel` assumes zero relative velocity in the LVLH frame. This is a simplification that is likely incorrect for maintaining a dynamic formation under perturbations. The relative velocity in the LVLH frame should be calculated to maintain the desired relative positions over time, considering the perturbed dynamics. This would involve more complex relative motion dynamics (e.g., Hill's equations or a more sophisticated relative motion model).
    *   **Analyze `propagate_perturbed` behavior:** Investigate if `propagate_perturbed` is numerically stable and accurate enough for the given time steps and perturbation magnitudes. Small numerical differences in the propagation of the reference orbit versus individual satellites could accumulate rapidly.
    *   **Inspect `reference_elements` and `satellite_elements`:** Ensure that the initial `reference_elements` and the derived `satellite_elements` are truly consistent with the desired formation geometry and relative motion.

2.  **Refine Maneuver Target Calculation:**
    *   **Implement proper relative velocity calculation:** Instead of `ideal_perturbed_sat_vel = perturbed_ref_vel`, calculate the required relative velocity in the LVLH frame to maintain the `formation_offsets` over time, considering the perturbed dynamics. This is a non-trivial task and might require a dedicated relative motion model.
    *   **Consider a feedback control loop:** The current "teleport" is an open-loop correction. A closed-loop feedback control system (e.g., LQR, PID) that continuously calculates and applies small delta-Vs based on observed deviations might be more robust.

3.  **Debugging Strategy:**
    *   **Isolate Perturbations:** Temporarily disable individual perturbations (J2, drag, SRP) within `propagate_perturbed` (by commenting out their acceleration terms) to identify which perturbation is causing the most significant divergence.
    *   **Step-by-step Debugging:** Use a debugger to step through `simulate_triangle_formation` and `_plan_and_execute_maneuver` to observe the values of positions, velocities, and orbital elements at each step, especially around the maneuver points.
    *   **Plotting:** Generate plots of relative positions and velocities over time, both before and after maneuvers, to visualize the divergence and the effect of corrections.

4.  **Test Configuration Adjustments (for further debugging):**
    *   **Increase `station_keeping_tolerance_m`:** Temporarily increase the tolerance in the test (e.g., to 1000m) to see if the formation can be maintained for longer with a more relaxed requirement. This helps separate functional correctness from performance under strict conditions.
    *   **Reduce `time_step_s`:** A smaller `time_step_s` in the main simulation loop might improve the accuracy of `propagate_perturbed` and reduce numerical errors, potentially leading to more stable formation keeping.

The core problem is the large velocity discrepancy leading to an unrealistic delta-V. The solution lies in ensuring that the "ideal" state for the maneuver is truly consistent with the perturbed dynamics and the desired relative motion of the formation.