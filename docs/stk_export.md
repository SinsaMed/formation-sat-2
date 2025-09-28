# STK Exporter Usage Guide

## Introduction
This guide summarises the procedure for translating formation-flying simulation outputs into textual artefacts that can be imported into Systems Tool Kit (STK) 11.2. The exporter focuses on expressing propagated orbits, ground contact geometry, and formation-maintenance manoeuvres in formats familiar to mission analysts.

## Input Data Structures
The exporter consumes dedicated data classes defined in `tools.stk_export`. These classes ensure that input data is well-formed and chronologically ordered before serialisation.

1. `StateSample` encapsulates a single position and velocity vector expressed in kilometres and kilometres per second, respectively. The current implementation assumes the TEME frame; convert alternative frames prior to export.
2. `PropagatedStateHistory` groups an ordered sequence of `StateSample` instances belonging to a single spacecraft.
3. `GroundTrackPoint` and `GroundTrack` capture latitude, longitude, and altitude samples that define the nadir ground track for a spacecraft.
4. `GroundContactInterval` summarises access periods between a spacecraft and a defined facility.
5. `FacilityDefinition` sets the static geodetic properties of a ground asset.
6. `FormationMaintenanceEvent` records impulsive or finite-burn manoeuvres including optional \(\Delta v\) magnitudes.
7. `SimulationResults` aggregates the foregoing artefacts, while `ScenarioMetadata` declares global timing and naming parameters.

## Export Procedure
The `export_simulation_to_stk` function generates the following artefacts:

1. Produce STK ephemeris files (`*.e`) for each spacecraft using the supplied state history. When the optional `ephemeris_step_seconds` parameter is provided within `ScenarioMetadata`, SciPy interpolation ensures evenly spaced samples compatible with STK accuracy recommendations.[Ref1]
2. Emit ground-track descriptions (`*_groundtrack.gt`) that list time-tagged geodetic points in the declared inertial frame.
3. Create facility definitions (`Facility_*.fac`) describing ground sites associated with the simulation.
4. Assemble interval lists (`Contacts_*.int`) mapping visibility windows between facilities and spacecraft.
5. Capture formation-maintenance events inside an event set (`formation_events.evt`).
6. Compile a scenario summary (`<scenario>.sc`) referencing the generated assets and aligning the mission epoch bounds.

## Usage Example
1. Instantiate `SimulationResults` with propagated states, ground tracks, facility metadata, and manoeuvre events derived from your simulation pipeline.
2. Create a `ScenarioMetadata` object specifying the scenario name, start epoch, and (optionally) the ephemeris resampling cadence.
3. Call `export_simulation_to_stk(sim_results, output_directory, metadata)` to populate the target directory with STK-compatible files.
4. Within STK, load the scenario file (`File > Open > Scenario`) and import the ephemerides for each satellite asset. Associate facilities and interval lists through the object browser to confirm contact geometries.

## References
[Ref1] Anon., *STK Satellite Module User's Guide*, Analytical Graphics Inc., 2023.
