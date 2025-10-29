# Formation SAT How-It-Works Guide

## 1. Purpose and Audience
This guide equips new analysts with the complete workflow for reproducing the Tehran formation campaign, from configuring the environment to verifying the locked evidence run `run_20251020_1900Z_tehran_daily_pass_locked`. It supplements the existing memoranda by explaining the system logic, detailing every executable step, and clarifying how we demonstrated that three spacecraft distributed across two orbital planes achieve and maintain the required formation.

## 2. Environment Preparation
1. Install Python 3.10 (or later) and the project dependencies with `pip install -r requirements.txt`. A virtual environment is strongly recommended to isolate mission tooling.[Ref1]
2. Ensure the workstation can expose TCP port 6000, enabling the optional FastAPI runner and accompanying visual interface.[Ref1]
3. Retain access to the repository `artefacts/` directory because the authoritative evidence—JSON summaries, CSV catalogues, and STK exports—is stored under timestamped subdirectories.[Ref1]

## 3. Mission Geometry Overview
### 3.1 Daily Pass Baseline
The Tehran daily-pass scenario defines the deterministic baseline used by the RAAN alignment solver. Key elements are:
- Epoch of 2026-03-21T09:32:00Z in the TEME frame with a semi-major axis of 6,880.150 km and inclination of 97.70°.
- Optimised RAAN of 350.7885044642857° with the access window 07:39:25Z–07:40:55Z and cross-track limits of ±30 km (primary) and ±70 km (waiver).
- Propagation margins of 300 s and a 10 s step to support the high-fidelity \(J_2\)+drag model.
These parameters are codified in `config/scenarios/tehran_daily_pass.json` together with payload, power, and thermal constraints that inform downstream analysis.[Ref2]

### 3.2 Two-Plane Triangle Architecture
The three-spacecraft formation uses a reference orbit at the 2026-03-21T07:40:10Z midpoint with an equilateral target of 6 km. Spacecraft SAT-1 and SAT-2 occupy Plane A while SAT-3 rides Plane B, all sharing the same RAAN (18.880656°) but differing in argument of perigee and mean anomaly to create the along-track offsets that close the triangle. The configuration also stipulates maintenance (weekly 32 s burns with a 15 m/s annual budget), command geometry (2,200 km station range), and Monte Carlo seeds for injection and drag dispersions.[Ref3]

### 3.3 Locked Triangle Metrics
The curated triangle summary confirms the geometric and operational margins that underpin compliance:
- Formation window duration of 96 s spanning 09:31:12Z–09:32:48Z with triangle aspect ratio unity to within \(1.8\times10^{-13}\).
- Orbital elements for each spacecraft demonstrating the Plane A/Plane B split, with SAT-3 offset in argument of perigee to occupy the second plane.
- Maintenance, command, injection recovery, and drag dispersion analytics showing ≤0.057 m/s corrective manoeuvres and 100% success rates under the recorded assumptions.[Ref4]

## 4. Scenario Pipeline Logic
The scenario runner `sim/scripts/run_scenario.py` executes a deterministic sequence:
1. Load the scenario configuration from `config/scenarios` or an override file.
2. Perform RAAN alignment if the configuration declares a target window, reporting both the seed and optimised nodes.
3. Generate mission nodes (imaging and downlink windows) and derive mission phases from them.
4. Propagate the formation with a two-body model, then repeat with the \(J_2\)+drag perturbation model while capturing cross-track metrics.
5. Extract headline metrics and, when an output directory is supplied, export STK-compatible artefacts.
The script records the stage order so audits can confirm that RAAN alignment preceded propagation.[Ref5]

## 5. Replaying the Authoritative Daily-Pass Run
Follow this numbered checklist to regenerate the locked run using the documented methodology:
1. **Resolve the configuration.** Inspect `config/scenarios/tehran_daily_pass.json` to confirm the RAAN, window, and constraint values before execution.[Ref2]
2. **Launch the runner.** Execute `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir artefacts/run_YYYYMMDD_hhmmZ` from the repository root. Replace the suffix with the current timestamp while preserving the ISO-8601 pattern.[Ref5]
3. **Monitor the log.** Observe the console (or the optional `debug.txt` tail via the web interface) to see the RAAN optimisation and propagation stages complete in the documented order.[Ref1][Ref5]
4. **Review the summary.** Examine the generated `scenario_summary.json` to verify that the artefact list includes the STK export suite, the centroid cross-track at evaluation is 12.1427546 km, and the worst spacecraft offset is 27.7594591 km—matching the locked evidence.[Ref6]
5. **Check deterministic metrics.** Open `deterministic_summary.json` to confirm that each spacecraft remains inside the ±30 km primary limit at 07:40:10Z while logging per-vehicle extrema and compliance flags.[Ref7]
6. **Check Monte Carlo metrics.** Inspect `monte_carlo_summary.json` to confirm the 1.0 compliance probabilities, 23.914 km centroid mean, and 39.7606 km \(p_{95}\) worst-spacecraft offsets across the 1,000 resamples using seed 4242.[Ref8]
7. **Confirm stage sequencing.** Validate that the `stage_sequence` array lists `raan_alignment` through `stk_export` exactly once, demonstrating that the outputs are locked to the documented processing chain.[Ref6]

## 6. Formation Verification Logic
### 6.1 Deterministic Proof of Formation
The deterministic metrics show that at the 07:40:10Z midpoint the centroid lies 12.1427546 km from Tehran with each satellite within ±30 km. Historical minima at 07:40:05Z confirm the solver’s 39.629474 km worst-case bound across the window, matching the RAAN alignment record. Altitude spans (485.85–513.41 km) and orbital period (5,679.4704 s) confirm that the perturbation model aligns with the configuration epoch.[Ref6][Ref7]

### 6.2 Probabilistic Proof of Formation
Monte Carlo outputs demonstrate robustness: all 1,000 trials satisfy primary and waiver limits, the centroid \(p_{95}\) magnitude is 24.180 km, and worst-spacecraft \(p_{95}\) is 39.761 km. Relative-plane separation statistics show 0.200 km maximum relative cross-track dispersion, confirming that the two planes remain synchronised within tolerance.[Ref8]

### 6.3 Triangle Maintenance and Supportability
The curated triangle artefacts detail long-term maintenance. Annual \(\Delta v\) consumption remains between 9.29 and 14.04 m/s with a 32 s weekly burn, command latency margins exceed 10.47 h, and drag dispersion studies stay well inside the 350 km ground-tolerance. Injection recovery Monte Carlo trials (300 samples, seed 314159) never exceed 0.0567 m/s corrective burns.[Ref4]

## 7. Locating the Two Orbital Planes
The RAAN alignment summary tabulates the candidate RAAN sweep, showing the initial 350.9838169642857° seed and the converged 350.7885044642857° solution with centroid compliance across the 90 s window. Plane-normal vectors for Plane A and Plane B appear in the deterministic summary, quantifying the slight inclination offsets that underpin the dual-plane design. Together they prove that two near-identical planes—with minor argument-of-perigee offsets and plane-normal vectors separated by less than \(6\times10^{-5}\)—were selected to centre the formation over Tehran.[Ref6][Ref7]

## 8. STK Export and Validation
1. Confirm that `scenario_summary.json` lists the STK package (`.e`, `.sat`, `.gt`, `.fac`, `.int`, and `.sc` files). Copy these into an analysis workstation if external validation is required.[Ref6]
2. Use `tools/stk_export.py` (invoked automatically by the scenario runner) to regenerate ephemerides when rerunning the pipeline, ensuring Systems Tool Kit 11.2 remains a validation peer.[Ref5]
3. Follow the established STK ingestion procedure to animate the pass, overlay the Tehran facility, and check that contact windows match the Python outputs.[Ref1]

## 9. Optional Interactive Interface
The FastAPI service (`uvicorn run:app --host 127.0.0.1 --port 6000`) exposes a browser-based cockpit for launching the same runs, monitoring logs, and downloading artefacts under `artefacts/web_runs`. Analysts may use it to retrace the locked run visually while preserving the same evidence directories.[Ref1]

## 10. Evidence Governance
The authoritative run ledger confirms that only `run_20251020_1900Z_tehran_daily_pass_locked` is acceptable for compliance statements regarding Tehran alignment. Exploratory reruns (e.g. `run_20260321_0740Z_tehran_daily_pass_resampled`) are tracked separately to prevent accidental substitution.[Ref9]

## References
- [Ref1] `docs/interactive_execution_guide.md`.
- [Ref2] `config/scenarios/tehran_daily_pass.json`.
- [Ref3] `config/scenarios/tehran_triangle.json`.
- [Ref4] `artefacts/triangle_run/triangle_summary.json`.
- [Ref5] `sim/scripts/run_scenario.py`.
- [Ref6] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/scenario_summary.json`.
- [Ref7] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/deterministic_summary.json`.
- [Ref8] `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/monte_carlo_summary.json`.
- [Ref9] `docs/_authoritative_runs.md`.
