# LQR Controller Performance Report

## Introduction
This report summarizes the initial performance analysis of the Linear Quadratic Regulator (LQR) controller integrated into the three-satellite low Earth orbit (LEO) constellation simulation. The LQR controller is designed to maintain the desired triangular formation by calculating optimal control inputs (delta-V maneuvers) to correct for orbital perturbations and deviations.

## Integration and Verification
The LQR controller, implemented in `src/constellation/control/lqr.py`, has been successfully integrated into the `sim/formation/triangle.py` module. Verification was performed through unit and integration tests, which passed successfully, confirming the correctness of the implementation.

## Initial Simulation Results (Short Duration)
A short-duration simulation (180 seconds) of the "Tehran Triangle" scenario was executed with the LQR controller enabled. The primary observations from this run are:
- **Formation Stability:** The satellite formation maintained its desired triangular geometry throughout the simulation.
- **Station-Keeping:** No active LQR maneuvers were triggered during this short period. Consequently, the `total_delta_v_consumed_mps` was 0.0. This indicates that the natural orbital dynamics and initial conditions kept the formation within the defined station-keeping tolerance without requiring corrective action.
- **Formation Window:** A formation window of 98 seconds was observed over Tehran, during which the formation met the specified ground distance and geometry criteria.

## Monte Carlo Analysis
The simulation also included Monte Carlo analyses to assess the robustness of the system:
- **Injection Recovery:** The injection recovery analysis showed a 100% success rate over 300 samples, with a mean delta-V of approximately 0.026 m/s required to correct for initial position and velocity errors.
- **Drag Dispersion:** The drag dispersion analysis also yielded a 100% success rate over 200 samples, indicating the formation's ability to maintain its configuration despite variations in atmospheric drag.

## Conclusion and Future Work
The initial short-duration simulation confirms the successful integration and nominal operation of the LQR controller. The formation maintained its stability without requiring active maneuvers, and the Monte Carlo analyses demonstrate robustness against injection errors and drag variations.

To fully assess the LQR controller's performance, including its active station-keeping capabilities and fuel consumption, longer-duration simulations are required. These longer runs will allow for the observation of actual delta-V expenditures and the controller's response to accumulated perturbations over extended periods.

## Artefacts
The results of this simulation run are stored in the following directory: `artefacts/triangle_20251113T201211Z`
