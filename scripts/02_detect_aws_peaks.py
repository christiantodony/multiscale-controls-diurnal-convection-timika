"""Detect AWS peak-event dates; raw station data are not distributed here."""

from __future__ import annotations

import argparse
from pathlib import Path

from timika_diurnal.io import aws_precipitation_30min, read_aws
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
    parser.add_argument("--input", required=True, help="authorized AWS text file")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--groups", nargs="+", default=list(GROUP_SLICES))
    parser.add_argument("--prefix", default="peak_OBS")
    parser.add_argument("--utc-offset-hours", type=int, default=9)
    parser.add_argument("--missing-policy", choices=("zero", "error"), default="zero")
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
    frame = read_aws(args.input, args.utc_offset_hours)
    series = aws_precipitation_30min(frame, args.start, args.end, args.missing_policy)
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
