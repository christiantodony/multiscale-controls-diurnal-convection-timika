# Multiscale controls on diurnal convection in the Maritime Continent

Code and reproducibility materials associated with:

> Christianto, D., Plant, R. S., Stein, T. H. M., & Woolnough, S. J. (2026).
> *Multiscale controls on diurnal convection in the Maritime Continent: Insights
> from high-resolution observations in Timika*. Quarterly Journal of the Royal
> Meteorological Society. <https://doi.org/10.1002/qj.70297>

## Status and scope

This is a cleaned **candidate release (v0.1.0)** reconstructed from the source
files supplied by the lead author. The available archive covers:

- peak-event selection from 30-minute GPM-IMERG precipitation;
- peak-event selection from 15-minute AWS observations aggregated to 30 minutes;
- the 24 x 24 IMERG-AWS peak-time comparison;
- vertical and seven-day meridional-wind composites; and
- a configurable 500-hPa event-anomaly composite and IMERG Hovmoller composite.

The supplied archive did **not** contain the final scripts for the seasonal,
ENSO, MJO, equatorial-wave, bootstrap, or permutation analyses. Therefore this
version must not yet be described as a complete reproduction of every result in
the paper. See [the audit](docs/reproducibility_audit.md).

## Quick start

```bash
git clone https://github.com/christiantodony/multiscale-controls-diurnal-convection-timika.git
cd multiscale-controls-diurnal-convection-timika

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
pytest
```

Windows PowerShell users activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Data

| Dataset | Availability | Repository content |
|---|---|---|
| GPM IMERG V07 Final, 2001-2022 | Public from NASA GES DISC | Small derived GPM event-date lists only |
| ERA5 hourly pressure-level data | Public under Copernicus terms | Acquisition instructions only |
| Timika AWS | Restricted; permission from PT Freeport Indonesia is required | No raw data and no AWS-derived event dates |

Large NetCDF/GRIB files are deliberately excluded. Details and expected schemas
are in [data/README.md](data/README.md).

## Workflow

1. Obtain IMERG and, if authorized, AWS and ERA5 inputs.
2. Edit paths and variable names in `config/timika_legacy_uploaded.yaml` or pass
   command-line options.
3. Generate the eight three-hour event groups with scripts 01 and 02.
4. Compare the hourly event-date files with script 03.
5. Generate wind diagnostics with scripts 04-06 and Hovmoller composites with script 07.

Example IMERG command:

```bash
python scripts/01_detect_imerg_peaks.py \
  --input /path/to/papuav720012022.nc \
  --output-dir outputs/tables/imerg_peaks \
  --start 2001-01-01 \
  --end 2022-12-31
```

Run `python scripts/01_detect_imerg_peaks.py --help` to see all configurable
region, coordinate, and method arguments. This makes the workflow reusable in
another region without editing the source code.

## Time conventions

- Analysis timestamps are stored in UTC.
- Timika local time is WIT = UTC+9.
- AWS source timestamps are treated as WIT and converted to UTC.
- File suffixes in the supplied hourly lists are UTC hours; figure labels are
  converted to WIT.

## Reusing the method elsewhere

Change the target latitude/longitude, input variable and coordinate names,
analysis period, and local UTC offset. Do not copy the Timika thresholds without
testing them for the new sampling interval and rainfall climate. The method
parameters are explicit in the CLI and configuration file so regional
sensitivity experiments can be documented.

## Citation

If you use the scientific method or results, cite the QJRMS article above. If
you use or modify this software, also cite the archived software release DOI
that will appear after the GitHub-Zenodo release. GitHub can read
[`CITATION.cff`](CITATION.cff) and display a **Cite this repository** button.

## License

Code is released under the [MIT License](LICENSE). Dataset licenses and access
restrictions remain with their providers; the software license does not grant
permission to redistribute AWS, IMERG, or ERA5 data.

## Reproducibility record

- [Method and parameter notes](docs/methods.md)
- [Audit of supplied source files](docs/reproducibility_audit.md)
- [Step-by-step GitHub and Zenodo guide](docs/github_first_release.md)
- [How to contribute](CONTRIBUTING.md)
