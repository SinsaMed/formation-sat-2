# Validating the Tehran Daily Pass STK Export

## Purpose
This guide instructs analysts on how to import the `sim.scripts.run_scenario` export products into Systems Tool Kit (STK) 11.2, verify that the orbital geometry and operational timelines remain faithful to the Tehran daily pass configuration, and capture objective evidence suitable for compliance reporting. The workflow assumes that the export artefacts were generated using a repository `run_YYYYMMDD_hhmmZ` directory so that provenance and tooling versions are traceable.

## Prerequisites
1. Install STK 11.2 with the Desktop application and Connect module enabled.
2. Generate the Tehran daily pass export package via `python -m sim.scripts.run_scenario tehran_daily_pass --output-dir run_YYYYMMDD_hhmmZ` and retain the resulting `stk_export/` directory.
3. Ensure that `tools/stk_export.py` remains unmodified relative to the repository commit used to generate the artefacts so that coordinate-frame and naming assumptions match the guidance below.

## Import Procedure
1. Launch STK 11.2 and create a new, empty workspace.
2. Use *File → Open* and select `<run_dir>/stk_export/Tehran_Daily_Pass.sc` to load the packaged scenario; accept the prompt to import all referenced objects.
3. Verify that the *Object Browser* lists `tehran_daily_pass_spacecraft` and the facility definitions `Tehran_Urban_Core` and `Svalbard`; if any objects are missing, review the export directory for incomplete transfers before proceeding.

## Geometry Verification
1. Open a 3D Graphics window and right-click the satellite to centre the camera; confirm that the orbit plane exhibits the expected \(97.7^\circ\) inclination and dawn-dusk geometry relative to the Sun vector.
2. Activate the satellite ground track and ensure that the sub-satellite point crosses Tehran within the \(09{:}24\)–\(09{:}36\) UTC window; the facility icon should be overlaid on the metropolitan coordinates provided in the configuration.
3. Inspect the *Access* tool between `tehran_daily_pass_spacecraft` and both facilities; confirm that the rise and set times match the exported intervals to within one second and that minimum elevation angles satisfy the configuration constraints.
4. Review the *Animation* timeline and execute one full orbital period; confirm that the exported ephemeris populates without interpolation warnings.

## Evidence Capture
1. Capture a screenshot of the 3D view showing the spacecraft ground track over Tehran together with the Svalbard contact geometry; save the image under `artefacts/run_YYYYMMDD_hhmmZ/stk_validation/tehran_overpass.svg`.
2. Export the *Access* report for both facilities (CSV format) and archive the files within the same `stk_validation/` directory.
3. Record a short animation (GIF or MP4) illustrating one orbital revolution with ground-track overlay if required by stakeholder review; convert the asset to SVG frames or provide a textual summary in `stk_validation/animation_log.md` to remain compliant with repository policies.

## Post-Validation Actions
1. Once the STK checks succeed, set `"validated_against_stk_export": true` within `config/scenarios/tehran_daily_pass.json` for the recorded run.
2. Update `docs/tehran_daily_pass_scenario.md` to document the validation date, evidence identifiers, and any deviations observed during the import.
3. Amend `docs/compliance_matrix.md` with a new evidence reference linking to the archived STK validation artefacts so that the Systems Engineering Review Board can trace compliance.
4. Commit the updated documentation alongside the captured evidence under a single run identifier and raise the corresponding pull request for review.

## References
No external references were required for this procedure.
