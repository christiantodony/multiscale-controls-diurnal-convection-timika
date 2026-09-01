# Data instructions

No large or restricted raw datasets are distributed in this repository.

## GPM IMERG V07 Final

Obtain the Final Run half-hourly precipitation product for 2001-01-01 through
2022-12-31 from NASA GES DISC. Prepare a NetCDF with a regular 30-minute `time`
coordinate, latitude and longitude coordinates, and a precipitation variable.
The command-line script accepts alternative variable and coordinate names.

The `derived/imerg_hourly` directory contains small event-date lists from the
supplied author archive. They are included as traceability material, not as a
substitute for the raw IMERG product. Before v1.0, regenerate and checksum them
with the confirmed publication settings.

## ERA5

Download hourly meridional wind from the Copernicus Climate Data Store at the
pressure levels and spatial domain required by the diagnostic. Files are not
redistributed. Script defaults recognize `valid_time`, `pressure_level`,
`latitude`, `longitude`, and variable `v`; all are configurable.

## Timika AWS

The paper states that the station data are available from PT Freeport Indonesia
and that restrictions apply. Raw AWS observations and AWS-derived event-date
lists are excluded from this public package pending explicit redistribution
permission. Authorized users can place the input outside the repository and
pass its path to script 02.

Expected columns are documented in `src/timika_diurnal/io.py`. Missing values
encoded as `-9999.0` are recognized.

## Integrity record recommended for v1.0

For every locally held input, record filename, product version, temporal range,
spatial subset, size, and SHA-256 checksum in a private manifest. Do not commit
restricted filenames or metadata if they reveal confidential information.

