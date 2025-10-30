# Web Interface Overview

## Purpose and Scope
The web interface provides an interactive environment for executing the Tehran formation scenario directly from the repository's FastAPI service. It has been designed to expose the same simulation stack used by the Python orchestration scripts while presenting the results in a trilingual-ready Persian user interface. The page currently focuses on the equilateral triangle formation surrounding Tehran and retrieves its baseline configuration from the stored scenario files, ensuring consistency with the analytical workflows described in the broader mission documentation.

## Layout and Navigation
The interface is structured as three persistent columns rendered right-to-left. The rightmost column is a navigation sidebar exposing two entry points: the **Home** view for scenario execution and the **Settings** view for city-level configuration. The remaining two columns display control widgets, execution metadata, a tabular summary of orbital parameters, and the visualisation canvas stack. Users can switch between views without triggering a page refresh; the navigation toggle simply hides or reveals the relevant grid panels, thereby maintaining application state in memory.

## Scenario Execution Workflow
The **Home** view is wired to the `/runs/triangle` endpoint and issues JSON requests that contain inline overrides for the Tehran triangle configuration. When the user selects a scenario duration, the client clones the baseline configuration bundled in `config/scenarios/tehran_triangle.json` and updates the formation duration and sampling cadence before dispatching the request. The duration options shown in the selector are derived from:

1. The repeat ground-track cycle in the Tehran daily-pass configuration (`repeat_cycle_days = 1`).
2. The planning-horizon window defined for the same scenario (`2026-03-21` to `2026-03-28`, i.e. seven days).
3. The manoeuvre cadence published in `config/project.yaml` (`manoeuvre_cadence_days = 14`).

These values are surfaced in the sidebar alongside short explanatory notes so that operators understand the provenance of each option. The form also records contextual assumptions (duration, sampling cadence, and city identifier) in the payload, allowing downstream analytics to log the precise run inputs.

## Visualisation Components
Once the backend simulation completes, three complementary views become available:

1. **Orbital Parameter Table:** The metrics block in the simulation summary is parsed to generate a table containing the semi-major axis, eccentricity, inclination, right ascension of the ascending node, and argument of perigee for each satellite. Values are shown in kilometres or degrees, respecting the nomenclature in the analysis pipeline.
2. **Three-Dimensional Earth View:** Using Three.js, the application renders an Earth sphere normalised to the equatorial radius, overlays the propagated formation tracks, and marks Tehran's position. The renderer maintains a slow axial rotation to support depth perception during mission briefings.
3. **Two-Dimensional Ground Track and Orbital Element Trends:** A canvas-based map focuses on a ±18° latitude and ±28° longitude window around Tehran, highlighting ground tracks and the city marker. A second canvas computes orbital elements over time from the geometry time series by differentiating positions to recover velocities, applying the standard two-body formulae with the gravitational parameter from `config/project.yaml`, and plotting semi-major axis, inclination, and right ascension of the ascending node as small multiples. The sampling cadence adapts automatically to longer durations to maintain a tractable point density.

## Configuration Dependencies and Validation
The interface reads the Tehran triangle scenario directly so that any repository update to the geometry propagates to the web client on the next server restart. Gravitational constants are sourced from `config/project.yaml`, ensuring alignment with the Systems Tool Kit (STK 11.2) export assumptions. All run artefacts generated through the interface can be ingested by `tools/stk_export.py`; however, formal re-validation of the interactive pipeline against STK is scheduled for a future iteration once the extended visualisation features stabilise.

## Future Work
Planned enhancements include enabling the disabled "محاسبه پارامترهای مداری" action to trigger sensitivity analyses, exposing additional ground-station overlays, and offering CSV downloads of the computed orbital-element time series. Support for multiple cities is also envisaged once additional scenario files are introduced to the repository.

## References
[Ref1] Tehran Daily Pass scenario configuration (`config/scenarios/tehran_daily_pass.json`).

[Ref2] Tehran triangle formation specification (`config/scenarios/tehran_triangle.json`).

[Ref3] Mission-wide constants (`config/project.yaml`).
