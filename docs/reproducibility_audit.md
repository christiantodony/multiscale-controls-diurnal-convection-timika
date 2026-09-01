# Reproducibility audit of the supplied Paper I files

Audit date: 2026-09-01

## Files reviewed

| Supplied file | Interpreted role | Repository treatment |
|---|---|---|
| `GPM_strom_pick.ipynb` | IMERG event selection and Hovmoller preparation | Refactored into scripts 01 and 07 plus reusable package functions |
| `AWS_strom_pick.ipynb` | AWS aggregation and event selection | Refactored into script 02; restricted input excluded |
| `heat_map_IMERG_vs_AWS.ipynb` | 24 x 24 event-date comparison | Refactored into script 03 |
| `Daily_mean_meridional_wind.ipynb` | Event versus non-event vertical wind profiles | Refactored into script 04 |
| `Wind_7_days_evolution.ipynb` | Day -3 to +3 pressure-time composite | Refactored into script 05 |
| `06_03_2025_wind_area500hpa.ipynb` | Exploratory peak selection and 500-hPa wind maps | Replaced by focused scripts 01 and 06 |
| `Met04_total_1997_2000.txt` | Raw restricted AWS data | Excluded from the public package |
| `1_hour_peak/peak_GPM_*.txt` | Small derived IMERG event lists | Included with provenance note |
| `1_hour_peak/peak_OBS_*.txt` | AWS-derived event lists | Excluded pending provider permission |
| checkpoint notebooks and JPEG output | Duplicates/generated output | Excluded |

## Material gaps

The reviewed files do not contain the final implementation for:

- seasonal and ENSO classifications;
- RMM/MJO phase analysis;
- WMRG/MRG-Yanai and equatorial Rossby filtering;
- sigma-phase matrices, chi-square and Cramer's V statistics;
- bootstrap confidence intervals and FDR-adjusted permutation tests;
- all final Hovmoller propagation-speed calculations; or
- every publication figure and supporting-information result.

These scripts must be located and audited before a release is labelled
"complete Paper I reproduction."

## Parameter discrepancy requiring author confirmation

The uploaded IMERG and AWS notebooks use:

- 48 samples per day (30-minute resolution);
- 7-point centered rolling mean;
- Savitzky-Golay window of 7 points;
- polynomial order 3; and
- prominence equal to 20% of each segment's range.

The final article text describes a 3-hour moving average, an approximately
6-hour Savitzky-Golay window, fifth-order polynomial selection, and a dual
threshold including a 10% deviation criterion and the dataset mean. With
30-minute samples, a 7-point window represents 3.5 hours, so the descriptions
are not numerically identical.

For traceability, the candidate repository defaults to the settings visibly
present in the uploaded notebooks and labels them `legacy_uploaded`. Do not
publish v1.0 until the exact code used for the accepted results, or a written
parameter reconciliation, is available. Once confirmed, add a frozen
`publication_v1` configuration and regression tests against known event counts.

## Other risks corrected or documented

- Absolute JASMIN and RACC paths were removed.
- Repeated exploratory notebook cells and embedded outputs were removed.
- The old exporter created four extra date labels for an N+2 selection matrix;
  the refactor explicitly maps its two padded rows to the two days before the
  requested period and the remaining rows through the final requested day.
- Selecting dates by exact equality of floating-point rows was replaced with a
  direct Boolean index, avoiding accidental duplicate-row matches.
- UTC and WIT conversion is explicit.
- AWS missing 30-minute bins were filled with zero in the uploaded notebook.
  This behavior is retained only as an explicit `--missing-policy zero` option;
  it must not be interpreted as proof of dry conditions during data gaps.
- Large files, credentials, API configuration, generated figures, checkpoints,
  and local environment files are ignored by Git.

## Release gate for v1.0

- [ ] Recover all final scripts listed under material gaps.
- [ ] Confirm the publication peak-detection parameters.
- [ ] Verify whether AWS-derived event dates may be distributed.
- [ ] Add expected event counts and checksums as regression targets.
- [ ] Run the complete workflow in a clean environment.
- [ ] Confirm all authors/contributors and software-license choice.
- [ ] Create GitHub release `v1.0.0` and archive it with Zenodo.
