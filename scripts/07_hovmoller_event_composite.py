"""Create a latitude-time IMERG Hovmoller composite around selected events."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from timika_diurnal.comparison import read_dates
from timika_diurnal.io import open_netcdf


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--variable", default="precipitation")
    parser.add_argument("--time-name", default="time")
    parser.add_argument("--latitude-name", default="lat")
    parser.add_argument("--longitude-name", default="lon")
    parser.add_argument("--lat-min", type=float, default=-5.5)
    parser.add_argument("--lat-max", type=float, default=-3.5)
    parser.add_argument("--lon-min", type=float, default=136.5)
    parser.add_argument("--lon-max", type=float, default=137.5)
    parser.add_argument("--peak-hour-utc", type=int, required=True)
    parser.add_argument("--hours-each-side", type=int, default=18)
    return parser.parse_args()


def coordinate_slice(coordinate: xr.DataArray, low: float, high: float) -> slice:
    return slice(low, high) if coordinate.values[0] < coordinate.values[-1] else slice(high, low)


def main() -> None:
    args = arguments()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dataset = open_netcdf(args.input)
    rain = dataset[args.variable].sel(
        {
            args.latitude_name: coordinate_slice(dataset[args.latitude_name], args.lat_min, args.lat_max),
            args.longitude_name: coordinate_slice(dataset[args.longitude_name], args.lon_min, args.lon_max),
        }
    ).mean(args.longitude_name)
    event_dates = sorted(pd.Timestamp(date) for date in read_dates(Path(args.events)))
    offsets = pd.timedelta_range(
        start=f"-{args.hours_each_side}h",
        end=f"{args.hours_each_side}h",
        freq="30min",
    )
    blocks = []
    for date in event_dates:
        peak = date + pd.Timedelta(hours=args.peak_hour_utc)
        requested = peak + offsets
        block = rain.reindex({args.time_name: requested})
        if bool(block.notnull().all().item()):
            block = block.assign_coords({args.time_name: np.arange(len(offsets))}).rename(
                {args.time_name: "relative_step"}
            )
            blocks.append(block)
    if not blocks:
        raise ValueError("no complete event windows are available in the input")
    composite = xr.concat(blocks, dim="event").mean("event")
    relative_hours = np.arange(len(offsets)) * 0.5 - args.hours_each_side
    composite = composite.assign_coords(relative_hour=("relative_step", relative_hours))
    composite.attrs.update(event_count=len(blocks), peak_hour_utc=args.peak_hour_utc)
    composite.to_netcdf(output / "imerg_latitude_time_event_composite.nc")

    figure, axis = plt.subplots(figsize=(10, 6))
    artist = axis.contourf(
        composite[args.latitude_name],
        composite.relative_hour,
        composite,
        levels=16,
        cmap="Blues",
        extend="max",
    )
    axis.axhline(0, color="red", linestyle="--", linewidth=1)
    axis.set_xlabel("Latitude")
    axis.set_ylabel("Hours relative to peak window")
    axis.set_title(f"IMERG event composite (n={len(blocks)})")
    figure.colorbar(artist, ax=axis, label="Precipitation rate")
    figure.savefig(output / "imerg_latitude_time_event_composite.png", dpi=300, bbox_inches="tight")
    print(f"Wrote Hovmoller composite using {len(blocks)} complete events")


if __name__ == "__main__":
    main()
