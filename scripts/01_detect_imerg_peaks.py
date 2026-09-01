"""Detect IMERG peak-event dates with the traceable uploaded-code profile."""

from __future__ import annotations

import argparse
from pathlib import Path

from timika_diurnal.io import open_netcdf, precipitation_point_series, require_regular_steps
from timika_diurnal.peak_selection import (
    GROUP_SLICES,
    PeakSelectionSettings,
    dates_from_result,
    select_legacy_events,
    to_daily_matrix,
    write_date_list,
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="IMERG NetCDF file")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--variable", default="precipitation")
    parser.add_argument("--latitude", type=float, default=-4.55)
    parser.add_argument("--longitude", type=float, default=136.89)
    parser.add_argument("--latitude-name", default="lat")
    parser.add_argument("--longitude-name", default="lon")
    parser.add_argument("--start", default="2001-01-01")
    parser.add_argument("--end", default="2022-12-31")
    parser.add_argument("--groups", nargs="+", default=list(GROUP_SLICES))
    parser.add_argument("--prefix", default="peak_GPM")
    parser.add_argument("--daily-percentile", type=float, default=50.0)
    parser.add_argument("--rolling-points", type=int, default=7)
    parser.add_argument("--savgol-points", type=int, default=7)
    parser.add_argument("--savgol-order", type=int, default=3)
    parser.add_argument("--prominence-ratio", type=float, default=0.20)
    parser.add_argument("--peak-count", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dataset = open_netcdf(args.input).sel(time=slice(args.start, f"{args.end} 23:59:59"))
    series = precipitation_point_series(
        dataset,
        args.variable,
        args.latitude,
        args.longitude,
        args.latitude_name,
        args.longitude_name,
    )
    require_regular_steps(series.time, 30)
    daily = to_daily_matrix(series.values, 48)
    settings = PeakSelectionSettings(
        daily_percentile=args.daily_percentile,
        rolling_points=args.rolling_points,
        savgol_points=args.savgol_points,
        savgol_order=args.savgol_order,
        prominence_ratio=args.prominence_ratio,
        peak_count=args.peak_count,
    )
    for group in args.groups:
        result = select_legacy_events(daily, group, settings)
        dates = dates_from_result(result, args.start, args.end)
        hour = group.removeprefix("group")
        path = output / f"{args.prefix}_{hour}.txt"
        write_date_list(dates, str(path))
        print(f"{group}: {len(dates)} dates -> {path}; P50={result.daily_threshold:.6g}")


if __name__ == "__main__":
    main()
