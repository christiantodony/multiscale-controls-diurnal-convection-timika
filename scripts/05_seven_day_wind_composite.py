"""Build a pressure-time meridional-wind composite from day -3 to day +3."""

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
    return parser.parse_args()


def main() -> None:
    args = arguments()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = open_netcdf(args.input)[args.variable].squeeze(drop=True)
    event_dates = sorted(pd.Timestamp(date) for date in read_dates(Path(args.events)))
    offsets = pd.timedelta_range("-3D", periods=168, freq="1h")
    blocks = []
    used = []
    for date in event_dates:
        requested = date + offsets
        block = data.reindex({args.time_name: requested})
        if bool(block.notnull().all().item()):
            block = block.assign_coords({args.time_name: np.arange(168)}).rename({args.time_name: "relative_hour"})
            blocks.append(block)
            used.append(date)
    if not blocks:
        raise ValueError("no complete seven-day event windows were available")
    composite = xr.concat(blocks, dim="event").mean("event")
    composite.attrs["event_count"] = len(used)
    composite.to_netcdf(output / "seven_day_meridional_wind_composite.nc")

    figure, axis = plt.subplots(figsize=(12, 6))
    levels = np.linspace(float(composite.min()), float(composite.max()), 21)
    plot = axis.contourf(
        composite.relative_hour,
        composite[args.pressure_name],
        composite.transpose(args.pressure_name, "relative_hour"),
        levels=levels,
        cmap="RdBu_r",
        extend="both",
    )
    axis.invert_yaxis()
    axis.axvline(72, color="black", linestyle="--", linewidth=1)
    axis.set_xlabel("Relative hour (event day begins at 72)")
    axis.set_ylabel("Pressure (hPa)")
    figure.colorbar(plot, ax=axis, label="Meridional wind (m s-1)")
    figure.savefig(output / "seven_day_meridional_wind_composite.png", dpi=300, bbox_inches="tight")
    print(f"Wrote composite using {len(used)} complete events")


if __name__ == "__main__":
    main()
