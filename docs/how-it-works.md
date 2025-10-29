# Tehran Triangle Formation – How It Works

## 1. Purpose and Scope
This document explains, in an end-to-end manner, how newcomers can reproduce the final Tehran triangular-formation scenario, interpret the resulting artefacts, and understand the modelling logic that demonstrates when and why the three spacecraft establish the required formation window. The emphasis is on reproducibility, Systems Tool Kit (STK 11.2) compatibility, and the analytical checkpoints that confirm the mission requirements are satisfied.[Ref4][Ref5]

## 2. Prerequisites and Environment Preparation
1. **Establish the Python toolchain.** Execute `make setup` (or equivalently create and activate a Python ≥3.10 virtual environment, then run `pip install -r requirements.txt`) within the repository root to install the pinned dependencies.[Ref5]
2. **Review scenario inputs.** Open `config/scenarios/tehran_triangle.json` to familiarise yourself with the orbital epoch, geometric tolerances, plane assignments, Monte Carlo settings, and drag-dispersion parameters that the simulation consumes.[Ref1]
3. **Prepare artefact directories.** Ensure the `artefacts/` tree is writable so the simulation can record JSON summaries, CSV tables, SVG plots, and STK exports under timestamped run directories.[Ref2][Ref3]

## 3. Configuration Overview
The Tehran triangle configuration encapsulates every assumption needed to regenerate the ninety-second access window:
- **Reference orbit.** A 6898.137 km semi-major axis, 97.7° inclination, zero-eccentricity orbit at epoch 2026-03-21T07:40:10Z defines the leader trajectory that the deputies reference.[Ref1]
- **Formation geometry.** A 6 km side length, 1 s sampling cadence across a 180 s horizon, and 350 km ground-distance tolerance enforce the access window definition, while the aspect-ratio tolerance of 1.02 guarantees near-equilateral geometry.[Ref1]
- **Plane assignments.** SAT-1 and SAT-2 occupy Plane A; SAT-3 occupies Plane B, ensuring two vehicles share the leader plane while the third provides the out-of-plane offset required for an equilateral projection.[Ref1]
- **Maintenance and commanding.** Weekly 32 s corrective burns, a 15 m/s annual Δv budget, and a 2200 km single-station contact radius define the formation-keeping and communications envelope.[Ref1]
- **Monte Carlo studies.** Injection recovery (300 samples) and drag dispersion (200 samples) specify statistical spreads, seeds, and evaluation horizons so robustness evidence is reproducible.[Ref1]

## 4. Running the Final Scenario
1. **Invoke the triangle runner.** From the repository root, run `python -m sim.scripts.run_triangle --output-dir artefacts/run_YYYYMMDD_hhmmZ`, replacing the suffix with an ISO-8601-style timestamp. The CLI loads the Tehran configuration by default, propagates the formation, and prints the formation-window timing once complete.[Ref2]
2. **Inspect console feedback.** Confirm the terminal reports the formation start/end times and the summary path so you know where artefacts were written.[Ref2]
3. **Review generated artefacts.** Open the new run directory to examine `triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, and `injection_recovery_cdf.svg`. These outputs encode the metrics enforced by mission requirements MR-5 through MR-7.[Ref3][Ref4]
4. **Validate against STK.** Import the automatically produced STK export bundle (under `stk/`) into STK 11.2 to replay the trajectories, formation contacts, and Tehran facility geometry without manual conversions.[Ref3][Ref4]

## 5. Supplementary Execution Interfaces
1. **Debug CLI replay.** Execute `python run_debug.py --triangle` to stream detailed logs to `debug.txt` and export per-satellite CSV state histories, which are invaluable when teaching the propagation flow step-by-step.[Ref6]
2. **Interactive web runner.** Start `uvicorn run:app --host 127.0.0.1 --port 6000` to launch the single-page interface. The browser lets analysts choose stored scenarios, trigger runs, watch ground-track and 3D visualisations, and stream logs while maintaining the same artefact structure under `artefacts/web_runs`.[Ref6]
3. **Scenario pipeline diagnostics.** When the wider daily-pass pipeline is relevant, call `python run_debug.py --scenario tehran_daily_pass` to capture the ordered stage sequence and JSON summary that underpin the triangle’s contextual mission planning.[Ref6][Ref7]

## 6. Simulation Mechanics
### 6.1 Propagation Framework
The runner loads the configuration, instantiates classical orbital elements, and propagates the reference spacecraft using a Keplerian model at one-second resolution across the 180-second horizon.[Ref3] For each sample it constructs a local-vertical, local-horizontal (LVLH) frame, applies the analytical equilateral offsets, and transforms the positions into Earth-centred inertial (ECI) and Earth-centred Earth-fixed (ECEF) coordinates so both inertial and geodetic viewpoints are captured.[Ref3]

### 6.2 Geometry and Ground Tests
At each epoch the code computes triangle area, side lengths, and aspect ratio directly from the inertial vertices, and simultaneously records the centroid latitude, longitude, and altitude. Tehran-relative ground distances are obtained via haversine metrics, enforcing the 350 km tolerance, while the minimum command-station range is captured to quantify communications opportunities.[Ref3]

### 6.3 Formation-Window Detection
A boolean mask compares every sample’s ground distance and aspect ratio against the stored tolerances. The algorithm extracts the longest contiguous block that satisfies both limits, returning its start, end, and duration—96 s for the validated run—which the CLI surfaces to the operator.[Ref3][Ref4]

### 6.4 Maintenance and Command Analysis
Differential accelerations relative to the centroid estimate the per-spacecraft Δv required for weekly formation-keeping burns, yielding the annual totals published in the CSV summary. The command-latency model scans the minimum station range series, constructs contact windows, and maps them to passes per day, maximum latency, and MR-5 margin (10.47 h).[Ref3][Ref4]

### 6.5 Robustness Campaigns
Two Monte Carlo engines run automatically:
- **Injection recovery.** Random position/velocity dispersions (σ = 250 m, 5 mm/s) feed an analytic Δv estimator to confirm that 100% of 300 trials remain within the 15 m/s budget, with \(p_{95}\) at 0.041 m/s.[Ref1][Ref3][Ref4]
- **Drag dispersion.** Density and drag-coefficient perturbations integrate secular semi-major-axis decay over twelve orbits, reporting along-track drift, ground-distance growth, and the probability of staying below the 350 km tolerance.[Ref1][Ref3]

### 6.6 STK Export Integration
Once propagation and analytics finish, the tool serialises ECI state histories, ground tracks, and contact intervals into STK-compatible `.e`, `.gt`, `.sat`, `.fac`, and `.int` products. Identifiers are sanitised to avoid import errors, and scenario metadata records the TEME frame, epoch, and time step so analysts can replay the window directly in STK.[Ref3][Ref4]

## 7. Orbital Plane Reconstruction
To document the two-plane architecture, the simulator samples the midpoint of the formation window and converts each spacecraft’s Cartesian state into classical elements. The resulting table shows SAT-1 and SAT-2 sharing Plane A (semi-major axis 6891.215 km, RAAN 18.881°), while SAT-3 occupies Plane B (semi-major axis 6912.017 km, RAAN 18.881°, argument of perigee 36.065° offset), preserving the equilateral geometry in LVLH coordinates.[Ref3][Ref4]

## 8. Evidence Review and Teaching Flow
1. **Walk through archived runs.** Start with the curated `artefacts/triangle_run` package to demonstrate each artefact before generating new data, explaining how the summary JSON links to CSV diagnostics and STK exports.[Ref5]
2. **Regenerate and compare.** Run the simulation live, then contrast the new outputs against the archival baseline to highlight deterministic fields (e.g., geometry samples) versus stochastic ones (Monte Carlo draws governed by stored seeds).[Ref3][Ref4]
3. **Demonstrate external validation.** Import the STK package, show the 96 s simultaneous-contact interval, and verify that triangle side lengths remain 6.00 km within machine precision, reinforcing confidence in the analytical pipeline.[Ref3][Ref4]
4. **Conclude with maintenance insights.** Discuss how the differential acceleration analysis and command-latency windows underpin mission operations planning, emphasising the comfortable margins against the MR-5 to MR-7 thresholds.[Ref3][Ref4]

## References
- [Ref1] `config/scenarios/tehran_triangle.json` – Mission configuration detailing orbital elements, formation tolerances, and Monte Carlo settings.【F:config/scenarios/tehran_triangle.json†L1-L68】
- [Ref2] `sim/scripts/run_triangle.py` – Command-line interface for executing the triangle scenario and reporting formation-window timings.【F:sim/scripts/run_triangle.py†L1-L62】
- [Ref3] `sim/formation/triangle.py` – Propagation, metric computation, Monte Carlo analysis, and STK export implementation for the triangular formation.【F:sim/formation/triangle.py†L1-L1023】
- [Ref4] `docs/triangle_formation_results.md` – Validated metrics, orbital-element table, and maintenance evidence for the Tehran triangular formation campaign.【F:docs/triangle_formation_results.md†L1-L55】
- [Ref5] `docs/tehran_triangle_walkthrough.md` – Stepwise reproduction guide referencing archival artefacts and STK verification workflow.【F:docs/tehran_triangle_walkthrough.md†L1-L28】
- [Ref6] `docs/interactive_execution_guide.md` – Web and debug execution instructions, including artefact management guidance.【F:docs/interactive_execution_guide.md†L1-L54】
- [Ref7] `run_debug.py` – Debugging CLI producing detailed logs and CSV exports for instructional walk-throughs.【F:run_debug.py†L1-L199】
