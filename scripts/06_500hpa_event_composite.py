"""Create day -3 to +3 maps of event-composite 500-hPa meridional-wind anomalies."""

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
    parser.add_argument("--variable", default="v")
    parser.add_argument("--time-name", default="valid_time")
    parser.add_argument("--pressure-name", default="pressure_level")
    parser.add_argument("--pressure", type=float, default=500)
    parser.add_argument("--utc-hour", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dataset = open_netcdf(args.input)
    data = dataset[args.variable]
    if args.pressure_name in data.dims:
        data = data.sel({args.pressure_name: args.pressure})
    event_dates = sorted(pd.Timestamp(date) for date in read_dates(Path(args.events)))
    climatology = data.where(data[args.time_name].dt.hour == args.utc_hour, drop=True).mean(args.time_name)
    daily_maps = []
    counts = []
    for day in range(-3, 4):
        requested = [date + pd.Timedelta(days=day, hours=args.utc_hour) for date in event_dates]
        available = data.reindex({args.time_name: requested}).dropna(args.time_name, how="all")
        counts.append(available.sizes.get(args.time_name, 0))
        daily_maps.append(available.mean(args.time_name) - climatology)
    anomaly = xr.concat(daily_maps, pd.Index(range(-3, 4), name="relative_day"))
    anomaly.attrs["event_counts_by_day"] = ",".join(map(str, counts))
    anomaly.to_netcdf(output / "v500_event_anomaly_day_minus3_to_plus3.nc")

    figure, axes = plt.subplots(2, 4, figsize=(16, 8), constrained_layout=True)
    limit = float(np.nanpercentile(np.abs(anomaly.values), 98))
    levels = np.linspace(-limit, limit, 17)
    artist = None
    for axis, day in zip(axes.flat, range(-3, 4)):
        panel = anomaly.sel(relative_day=day)
        longitude = panel.coords.get("longitude", panel.coords.get("lon"))
        latitude = panel.coords.get("latitude", panel.coords.get("lat"))
        artist = axis.contourf(longitude, latitude, panel, levels=levels, cmap="RdBu_r", extend="both")
        axis.set_title(f"Day {day:+d} (n={counts[day + 3]})")
        axis.set_xlabel("Longitude")
        axis.set_ylabel("Latitude")
    axes.flat[-1].axis("off")
    figure.colorbar(artist, ax=axes, label="500-hPa v anomaly (m s-1)", shrink=0.8)
    figure.savefig(output / "v500_event_anomaly_day_minus3_to_plus3.png", dpi=300, bbox_inches="tight")
    print(f"Wrote NetCDF and figure to {output}")


if __name__ == "__main__":
    main()
