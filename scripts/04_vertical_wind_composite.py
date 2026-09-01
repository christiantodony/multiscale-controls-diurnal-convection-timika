"""Compare event-day and non-event-day mean meridional-wind profiles."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr

from timika_diurnal.comparison import read_dates
from timika_diurnal.io import open_netcdf


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="ERA5 NetCDF")
    parser.add_argument("--event-files", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--variable", default="v")
    parser.add_argument("--time-name", default="valid_time")
    parser.add_argument("--pressure-name", default="pressure_level")
    parser.add_argument("--latitude-name", default="latitude")
    parser.add_argument("--longitude-name", default="longitude")
    parser.add_argument("--lat-min", type=float, default=-5.5)
    parser.add_argument("--lat-max", type=float, default=-3.5)
    parser.add_argument("--lon-min", type=float, default=136.5)
    parser.add_argument("--lon-max", type=float, default=137.5)
    return parser.parse_args()


def coordinate_slice(coordinate: xr.DataArray, low: float, high: float) -> slice:
    return slice(low, high) if coordinate.values[0] < coordinate.values[-1] else slice(high, low)


def main() -> None:
    args = arguments()
    dataset = open_netcdf(args.input)
    data = dataset[args.variable].sel(
        {
            args.latitude_name: coordinate_slice(dataset[args.latitude_name], args.lat_min, args.lat_max),
            args.longitude_name: coordinate_slice(dataset[args.longitude_name], args.lon_min, args.lon_max),
        }
    ).mean((args.latitude_name, args.longitude_name))
    event_dates = set().union(*(read_dates(Path(path)) for path in args.event_files))
    dates = pd.DatetimeIndex(data[args.time_name].values).strftime("%Y-%m-%d")
    event_mask = xr.DataArray(
        [date in event_dates for date in dates],
        dims=(args.time_name,),
        coords={args.time_name: data[args.time_name]},
    )
    event_profile = data.where(event_mask, drop=True).mean(args.time_name)
    other_profile = data.where(~event_mask, drop=True).mean(args.time_name)

    fig, axis = plt.subplots(figsize=(6, 8))
    axis.plot(event_profile, event_profile[args.pressure_name], label="event days")
    axis.plot(other_profile, other_profile[args.pressure_name], label="other days")
    axis.axvline(0, color="0.5", linewidth=0.8)
    axis.invert_yaxis()
    axis.set_xlabel("Meridional wind (m s-1)")
    axis.set_ylabel("Pressure (hPa)")
    axis.legend()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    print(f"Wrote {args.output}; event dates found: {len(event_dates)}")


if __name__ == "__main__":
    main()
