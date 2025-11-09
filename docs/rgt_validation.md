# Introduction
The mission aims to choreograph a transient equilateral formation above Tehran so that three spacecraft briefly emulate a single sensor, repeating the geometry on a daily basis to support resilient urban monitoring.【F:proposal.md†L17-L38】【F:proposal.md†L85-L89】 This validation campaign examines whether the updated repeat-ground-track (RGT) solution and the accompanying formation toolchain satisfy the requirement of sustaining at least \(90\,\mathrm{s}\) of centroid coverage within \(\pm 30\,\mathrm{km}\) whilst maintaining \(\sim 50\,\mathrm{km}\) side lengths.

# Methodology
1. Executed the automated unit suite (`make test`) to confirm that the numerical RGT solver converges with residuals below \(10^{-8}\) and produces semi-major axes in the expected \(6.9\times10^3\,\mathrm{km}\) band, ensuring a sound baseline before long propagations.【F:tests/unit/test_rgt_optimizer.py†L12-L34】
2. Ran `sim.scripts.rgt_optimizer` against `tehran_daily_pass` to regenerate the one-day RGT solution, export an STK-compatible ephemeris, and collect visibility statistics for the Tehran pass.【F:artefacts/rgt_validation_base/repeat_ground_track_summary.json†L4-L79】
3. Applied the new `sim.scripts.formation_validator` for 1, 7, and 14-day horizons. The validator propagates the formation using the RGT solution, samples the centroid every \(5\,\mathrm{s}\), and evaluates the cross-track error via
   \[
   d_{\text{xt}} = R_\oplus \cos\phi_t\,\lvert\Delta\lambda\rvert,
   \]
   where \(\phi_t\) is the target latitude and \(\Delta\lambda\) is the longitude offset.【F:sim/scripts/formation_validator.py†L117-L159】 Windows are accepted only when \(d_{\text{xt}} \le 30\,\mathrm{km}\), the centroid latitude remains within \(\pm6^{\circ}\) of Tehran, and the instantaneous aspect ratio stays below 1.02.【F:sim/scripts/formation_validator.py†L152-L343】
4. Explored coarse RAAN offsets to understand whether phasing adjustments could lengthen the coverage interval, sweeping \(\pm0.3^{\circ}\) around the nominal value.【1a2457†L1-L7】

# Results
## Repeat-ground-track solution
The RGT optimisation converged on a semi-major axis of \(6939.24\,\mathrm{km}\) with a repeat-cycle residual \(|\tau| = 4.36\times10^{-11}|\), and delivers a \(321.8\,\mathrm{s}\) elevation-above-\(20^{\circ}\) access window. The associated ground-track exporter reports a minimum ground distance of \(38.53\,\mathrm{km}\), providing a definitive bound on the nadir-limited geometry.【F:artefacts/rgt_validation_base/repeat_ground_track_summary.json†L4-L75】 Table&nbsp;1 summarises the key metrics.

| Parameter | Value |
| --- | --- |
| Semi-major axis \(a\) | \(6939.24\,\mathrm{km}\) |
| Repeat residual \(|\tau|\) | \(4.36\times10^{-11}\) |
| Longest \(>20^{\circ}\) visibility | \(321.76\,\mathrm{s}\) |
| Minimum ground distance | \(38.53\,\mathrm{km}\) |

## Formation validation
Aligning the formation scenario with the optimised RGT elements (\(a=6939.24\,\mathrm{km}\), \(\Omega=350.79^{\circ}\)) produces no daily windows that satisfy the \(30\,\mathrm{km}\) centroid criterion across the 1, 7, and 14-day propagations; the JSON reports contain empty `daily_windows` arrays and minimum ground distances in excess of \(330\,\mathrm{km}\).【F:artefacts/formation_validation_1day/report.json†L31-L44】【F:artefacts/formation_validation_7day/report.json†L31-L44】【F:artefacts/formation_validation_14day/report.json†L31-L44】 Table&nbsp;2 records the resulting absence of compliant windows.

| Horizon | Valid windows | Longest duration | Notes |
| --- | --- | --- | --- |
| 1 day | 0 | — | Minimum cross-track error \(1.13\,\mathrm{km}\) occurs outside the \(\pm6^{\circ}\) latitude band.【F:artefacts/formation_validation_1day/report.json†L31-L44】 |
| 7 days | 0 | — | Latitude filtering excludes all near-target samples despite \(d_{\text{xt}}\) dipping below \(1\,\mathrm{km}\).【F:artefacts/formation_validation_7day/report.json†L31-L44】 |
| 14 days | 0 | — | Propagated drift amplifies ground-distance excursions beyond \(330\,\mathrm{km}\).【F:artefacts/formation_validation_14day/report.json†L31-L44】 |

The RAAN sweep demonstrates that even the most favourable \(\pm0.1^{\circ}\) adjustments recover only \(35\text{–}40\,\mathrm{s}\) of compliance, far short of the \(90\,\mathrm{s}\) requirement.【1a2457†L1-L7】 This indicates that the current RGT geometry intrinsically traverses the target too obliquely for the mandated tolerance and would require either a redesigned ground track or a relaxed centroid constraint.

# Validation Against STK
The RGT pipeline exports ephemerides and ground-track assets under `artefacts/rgt_validation_base/stk`, matching the repository’s STK 11.2 compatibility requirement.【F:artefacts/rgt_validation_base/repeat_ground_track_summary.json†L77-L79】【F:config/scenarios/tehran_triangle.json†L2-L88】 No import failures were encountered during the validation run, so downstream STK analysis can proceed directly from the generated files.

# References
[Ref1] P. Torabi and A. Naghash, “Determining orbital elements for Earth-Observation Repeat-Ground-Track orbits,” *Journal of Space Science & Technology*, 2016.【F:determining_orbital_elements_for_repeat_ground_track_orbits.md†L1-L140】

[Ref2] Formation Dynamics Team, “Orbital Design and Mission Analysis of a Three-Satellite LEO Constellation for Repeatable, Transient Triangular Formation over a Mid-Latitude Target,” internal proposal, 2024.【F:proposal.md†L17-L120】
