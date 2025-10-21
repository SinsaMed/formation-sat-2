# Authoritative Simulation Runs

## Purpose
This register consolidates the simulation and analysis run identifiers that underpin the current compliance baseline. Keeping a single ledger prevents divergence between documentation, archived artefacts, and regression tests while providing reviewers with a quick reference to the governing evidence packages.

## Run Catalogue
| Run ID | Scenario | Directory | Key Evidence | Notes |
| --- | --- | --- | --- | --- |
| `run_20251018_1207Z` | Tehran triangular formation maintenance and responsiveness study | `artefacts/run_20251018_1207Z/` | `triangle_summary.json`, `maintenance_summary.csv`, `command_windows.csv`, `injection_recovery.csv`, `drag_dispersion.csv`, `injection_recovery_cdf.svg` | Captures the ninety-six-second window, distinguishes the \(343.62\,\text{km}\) windowed and \(641.89\,\text{km}\) full-propagation ground-distance maxima, and provides the MR-5 to MR-7 evidence stack documented in `docs/triangle_formation_results.md`.[Ref1] |
| `run_20251020_1900Z_tehran_daily_pass_locked` | Locked Tehran daily-pass alignment | `artefacts/run_20251020_1900Z_tehran_daily_pass_locked/` | `scenario_summary.json`, `deterministic_summary.json`, `monte_carlo_summary.json`, `stk/` export set | Establishes the \(350.7885044642857^{\circ}\) optimised RAAN with the 07:39:25–07:40:55Z imaging window and the 20:55:00–21:08:00Z downlink, forming the authoritative evidence cited across the compliance matrix and STK validation guide.[Ref2][Ref3] |
| `artefacts/triangle_run/` snapshot | Curated triangle formation rerun | `artefacts/triangle_run/` | Mirrors the `run_20251018_1207Z` data products together with `run_metadata.json` | Provides a convenient analyst-ready bundle for familiarisation and demonstrations; the underlying evidence remains the `run_20251018_1207Z` dataset listed above.[Ref1] |
| `run_20260321_0740Z_tehran_daily_pass_resampled` | Exploratory resampling of the locked daily pass | `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/` | `scenario_summary.json`, `monte_carlo_summary.json`, `stk/` export set | Retains the locked geometry while exercising the resampling workflow; marked as non-baseline but kept for methodological comparison.[Ref4] |

## Maintenance Guidance
1. Update this ledger whenever a new run supersedes an existing compliance reference. Note whether the previous dataset remains available for historical comparison.
2. When introducing exploratory reruns, flag their status explicitly (as in the table above) so that compliance documentation cannot accidentally cite non-baseline evidence.
3. Cross-reference this register from scenario and results memoranda to ensure downstream readers always resolve the latest authoritative run without manual searching.

## References
- [Ref1] `docs/triangle_formation_results.md` – Tehran triangular formation analysis memorandum and compliance summary.
- [Ref2] `docs/tehran_daily_pass_scenario.md` – Tehran daily-pass scenario overview and validation record.
- [Ref3] `docs/how_to_import_tehran_daily_pass_into_stk.md` – STK 11.2 validation workflow aligned with the locked daily-pass artefacts.
- [Ref4] `artefacts/run_20260321_0740Z_tehran_daily_pass_resampled/scenario_summary.json` – Exploratory resampled daily-pass dataset for methodological comparison.
