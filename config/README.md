# Configuration Directory Overview
## Purpose
This directory collates structured mission configuration artefacts that inform modelling, simulation, and Systems Tool Kit (STK) exports. The material is curated to give contributors a single source of truth for programme-wide constants and scenario-specific references.

## Using `project.yaml`
The `project.yaml` file is the authoritative schema describing the baseline configuration. Each section captures a coherent set of parameters:

### Metadata
- `metadata.project_name` records the formal programme title to maintain consistent nomenclature across documentation.
- `metadata.configuration_version` applies semantic versioning so that downstream consumers can manage compatibility.
- `metadata.authoring_team` identifies the group accountable for maintaining the configuration.
- `metadata.last_updated` gives the ISO 8601 date to aid traceability audits.

### Global
- `global.earth_model` specifies the geodetic datum used by all coordinate transformations.
- `global.gravitational_parameter_km3_s2` lists the gravitational parameter (μ) used in dynamical models when kilometres and seconds are the working units.
- `global.nominal_altitude_km` sets the reference altitude for design calculations and quick-look analyses.
- `global.window_targets` enumerates observation or contact windows that drive coverage assessments. Each entry defines the target coordinates, an altitude constraint, and the revisit cadence requirement.
- `global.scenario_references` maps mission phases to the canonical STK scenario files generated via `tools/stk_export.py`.

### Platform
- `platform.bus` aggregates mass, lifetime, power, and envelope data for the spacecraft bus. These values inform subsystem budgets and launch compatibility assessments.
- `platform.payload` captures the sensing payload architecture. The listed parameters describe the primary multispectral instrument and the secondary GNSS occultation payload.
- `platform.communications` details the communications subsystem, including the band plan, achievable downlink rate, antenna gain, and the certified ground network.
- `platform.propulsion` outlines the propulsion approach, including total ΔV, thrust level, and expected specific impulse.

### Orbit
- `orbit.reference_epoch_utc` fixes the epoch for the orbital elements so that propagation runs start from a consistent temporal anchor.
- `orbit.central_body` confirms that the dynamics are Earth-centric.
- `orbit.classical_elements` provides the Keplerian parameters describing the leader spacecraft trajectory.
- `orbit.formation_design` defines the leader and deputy identifiers alongside their relative geometry offsets, supporting formation-keeping analyses.
- `orbit.maintenance_strategy` states the manoeuvre cadence, permitted separation tolerance, and ΔV reserve fraction guiding routine maintenance.

### Simulation
- `simulation.start_time_utc` and `simulation.stop_time_utc` bound the simulation horizon.
- `simulation.time_step_seconds` sets the numerical integrator step size for propagations.
- `simulation.integrator` characterises the propagation algorithm and its tolerances.
- `simulation.force_models` toggles perturbation models, including J2, drag, and solar radiation pressure (SRP) parameters.
- `simulation.attitude_profile` documents the nominal attitude mode and control law applied during analyses.
- `simulation.monte_carlo` configures dispersion studies, detailing whether Monte Carlo trials are enabled, the number of runs, and the statistical spreads applied to key variables.

### Output
- `output.directory` points to the default repository location for generated artefacts.
- `output.file_naming` defines the templated naming convention so exported files can be parsed systematically.
- `output.include_products` lists which product families (e.g., ephemerides, ground tracks, contact windows) should be emitted.
- `output.reporting_interval_seconds` establishes the cadence for summarised outputs.
- `output.stk_export` governs the creation of STK-compatible products, including the scenario tag and list of embedded facilities.
- `output.data_retention_days` mandates the minimum period for retaining mission data products.
- `output.quality_checks` records the checksum algorithm and schema version to support verification workflows.

## Maintenance Process
When updating `project.yaml`, contributors should:
1. Review the metadata to ensure the version and update date reflect the proposed change.
2. Validate that the global constants remain consistent with current Earth models and mission-level requirements.
3. Confirm that platform, orbit, simulation, and output sections align with the latest design baselines and STK interoperability needs.
4. Regenerate affected scenario files through `tools/stk_export.py` if any configuration change impacts exported products.
