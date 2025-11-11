# Active Station-Keeping Implementation Plan

## 1. Objective
Implement a simplified active station-keeping mechanism within the satellite formation flying simulation to counteract orbital perturbations and maintain the desired triangular formation over extended durations. This mechanism will involve predicting future formation deviations and applying corrective maneuvers when necessary.

## 2. Proposed Approach
The approach will involve periodic checks for formation deviation, prediction of future drift, and the application of corrective delta-V maneuvers.

## 3. Key Parameters to Introduce/Modify

*   **`formation.station_keeping_interval_s` (New):** Defines how frequently the simulation checks for formation deviations and plans maneuvers (e.g., every few hours or once per day).
*   **`formation.prediction_horizon_s` (New):** Defines how far into the future the simulation predicts the formation's state to anticipate drift (e.g., 1 to 3 days).
*   **`formation.station_keeping_tolerance_m` (Existing, but will be actively used):** The maximum allowable deviation in side length before a maneuver is triggered.

## 4. Implementation Steps

### 4.1. Modify `tehran_triangle.json`
*   Add `station_keeping_interval_s` (e.g., 21600.0 seconds = 6 hours) to the `formation` section.
*   Add `prediction_horizon_s` (e.g., 86400.0 seconds = 1 day) to the `formation` section.

### 4.2. Modify `sim/formation/triangle.py`

#### 4.2.1. Introduce a `_plan_and_execute_maneuver` Function
This new function will be called periodically within the main propagation loop.

*   **Inputs:** Current orbital elements of all satellites, current time, `station_keeping_interval_s`, `prediction_horizon_s`, `station_keeping_tolerance_m`, `formation_offsets`.
*   **Logic:**
    1.  **Prediction:** For each satellite, propagate its current orbital elements forward for `prediction_horizon_s` *without* applying any control.
    2.  **Evaluate Predicted Formation:** Calculate the predicted `triangle_side_lengths` at the end of the prediction horizon.
    3.  **Check Tolerance:** Compare the predicted side lengths against `formation.side_length_m` and `station_keeping_tolerance_m`.
    4.  **Maneuver Decision:** If the predicted deviation exceeds the tolerance, a maneuver is deemed necessary.
    5.  **Calculate Corrective Delta-V (Simplified):**
        *   Determine the relative position and velocity errors at the end of the prediction horizon.
        *   Calculate a simplified delta-V to reduce these errors (e.g., by targeting zero relative velocity in the LVLH frame at the end of the prediction horizon). This will likely involve adjusting the mean anomaly or semi-major axis of individual satellites.
    6.  **Apply Maneuver:** Update the orbital elements of the satellites by applying the calculated delta-V. This will effectively "reset" their relative positions/velocities to the desired state for the next propagation segment.
    7.  **Record Maneuver:** Log the time, satellites involved, and magnitude of the applied delta-V.

#### 4.2.2. Integrate into `simulate_triangle_formation`
*   Introduce a counter or a time variable to track when the next station-keeping check is due.
*   Inside the main propagation loop (where `propagate_perturbed` is called):
    *   Before propagating for `time_step_s`, check if `station_keeping_interval_s` has elapsed since the last check/maneuver.
    *   If it has, call `_plan_and_execute_maneuver`. The `propagate_perturbed` function will then use the *updated* orbital elements.
    *   Ensure that the `current_elements` are updated correctly after a maneuver.

## 5. Metrics and Reporting
*   The `station_keeping` metrics (events, recommended delta-V) will now reflect actual applied maneuvers rather than just theoretical requirements.
*   The `maintenance_summary.csv` will be updated to include the actual delta-V consumed by active station-keeping.

## 6. Considerations
*   **Simplified Delta-V Calculation:** For initial implementation, the delta-V calculation will be simplified. More advanced methods (e.g., optimal control) could be considered later.
*   **Maneuver Application:** The delta-V will be applied instantaneously to the orbital elements.
*   **Impact on `duration_s`:** The `duration_s` will now represent the total simulation time, during which active station-keeping will occur.
