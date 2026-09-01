"""Input helpers with explicit coordinate and time conventions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

AWS_COLUMNS = [
    "SID",
    "Year",
    "Julian Date",
    "Time",
    "Temperature (degC)",
    "Relative Humidity (%)",
    "Precipitation (mm)",
    "Solar Radiation Density (W/m2)",
    "Solar Radiation Total (cal/cm2)",
    "Wind Speed (mps)",
    "Wind Direction (degree)",
    "Std Deviation WS/WD",
    "Pressure (mmbar)",
    "Battery (Volt)",
]


def open_netcdf(path: str | Path) -> xr.Dataset:
    """Open one NetCDF file and sort it along its time coordinate."""
    dataset = xr.open_dataset(path)
    for candidate in ("time", "valid_time"):
        if candidate in dataset.coords:
            return dataset.sortby(candidate)
    raise ValueError("dataset has neither 'time' nor 'valid_time' coordinate")


def precipitation_point_series(
    dataset: xr.Dataset,
    variable: str,
    latitude: float,
    longitude: float,
    latitude_name: str = "lat",
    longitude_name: str = "lon",
) -> xr.DataArray:
    """Select the nearest precipitation grid point."""
    return dataset[variable].sel(
        {latitude_name: latitude, longitude_name: longitude}, method="nearest"
    ).squeeze(drop=True)


def read_aws(path: str | Path, utc_offset_hours: int = 9) -> pd.DataFrame:
    """Read the restricted Timika AWS layout and convert WIT timestamps to UTC."""
    frame = pd.read_csv(path, header=0, names=AWS_COLUMNS, na_values=-9999.0)
    date = pd.to_datetime(
        frame["Year"].astype(int) * 1000 + frame["Julian Date"].astype(int),
        format="%Y%j",
    )
    time_text = frame["Time"].astype(int).astype(str).str.zfill(4)
    hour = time_text.str[:-2].astype(int)
    minute = time_text.str[-2:].astype(int)
    next_day = hour.eq(24)
    hour = hour.mask(next_day, 0)
    date = date + pd.to_timedelta(next_day.astype(int), unit="D")
    local = date + pd.to_timedelta(hour, unit="h") + pd.to_timedelta(minute, unit="m")
    frame["datetime_utc"] = local - pd.Timedelta(hours=utc_offset_hours)
    return frame


def aws_precipitation_30min(
    frame: pd.DataFrame,
    start: str,
    end: str,
    missing_policy: str = "zero",
) -> pd.Series:
    """Aggregate 15-minute AWS precipitation to a regular 30-minute UTC series.

    ``missing_policy='zero'`` matches the uploaded notebook. It must not be
    interpreted as evidence that every missing observation was a dry interval.
    """
    precipitation = (
        frame.set_index("datetime_utc")["Precipitation (mm)"]
        .resample("30min")
        .sum(min_count=1)
    )
    axis = pd.date_range(f"{start} 00:00", f"{end} 23:30", freq="30min")
    precipitation = precipitation.reindex(axis)
    if missing_policy == "zero":
        return precipitation.fillna(0.0)
    if missing_policy == "error" and precipitation.isna().any():
        raise ValueError(f"AWS series contains {int(precipitation.isna().sum())} missing bins")
    if missing_policy != "keep":
        raise ValueError("missing_policy must be one of: zero, error, keep")
    return precipitation


def require_regular_steps(time: xr.DataArray, minutes: int = 30) -> None:
    values = pd.DatetimeIndex(time.values)
    if len(values) < 2:
        raise ValueError("time coordinate contains fewer than two values")
    differences = np.diff(values.view("i8"))
    expected = pd.Timedelta(minutes=minutes).value
    if not np.all(differences == expected):
        raise ValueError(f"time coordinate is not regular at {minutes}-minute intervals")

