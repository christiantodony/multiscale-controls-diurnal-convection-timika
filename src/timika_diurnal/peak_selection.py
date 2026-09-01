"""Peak-selection utilities reconstructed from the uploaded Paper I notebooks.

The ``legacy`` workflow in this module preserves the numerical settings and
day-padding logic found in the supplied IMERG and AWS notebooks. Parameters are
explicit so that a publication-verified profile can replace them once the
remaining source code and final settings have been confirmed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

GROUP_SLICES = {
    "group00": (12, 90),
    "group03": (18, 96),
    "group06": (24, 102),
    "group09": (30, 108),
    "group12": (36, 114),
    "group15": (42, 120),
    "group18": (48, 126),
    "group21": (54, 134),
}


@dataclass(frozen=True)
class PeakSelectionSettings:
    """Settings used by the uploaded notebooks."""

    steps_per_day: int = 48
    daily_percentile: float = 50.0
    rolling_points: int = 7
    savgol_points: int = 7
    savgol_order: int = 3
    prominence_ratio: float = 0.20
    maximum_index_start: int = 37
    maximum_index_end: int = 42
    peak_count: int = 1

    def validate(self) -> None:
        if self.steps_per_day <= 0:
            raise ValueError("steps_per_day must be positive")
        if self.rolling_points < 1 or self.rolling_points % 2 == 0:
            raise ValueError("rolling_points must be a positive odd integer")
        if self.savgol_points < 3 or self.savgol_points % 2 == 0:
            raise ValueError("savgol_points must be an odd integer >= 3")
        if self.savgol_order >= self.savgol_points:
            raise ValueError("savgol_order must be smaller than savgol_points")
        if not 0 <= self.daily_percentile <= 100:
            raise ValueError("daily_percentile must be in [0, 100]")


@dataclass
class PeakSelectionResult:
    selected: np.ndarray
    peak_counts: np.ndarray
    daily_threshold: float
    group_values: np.ndarray


def to_daily_matrix(values: np.ndarray, steps_per_day: int = 48) -> np.ndarray:
    """Trim a one-dimensional regular series and reshape it to day x step."""
    values = np.asarray(values, dtype=float).reshape(-1)
    complete = (values.size // steps_per_day) * steps_per_day
    if complete == 0:
        raise ValueError("input does not contain one complete day")
    return values[:complete].reshape(-1, steps_per_day)


def centered_edge_rolling_mean(values: np.ndarray, points: int) -> np.ndarray:
    """Centered mean with replicated edges, matching the supplied notebooks."""
    if points < 1 or points % 2 == 0:
        raise ValueError("points must be a positive odd integer")
    half = points // 2
    padded = np.pad(np.asarray(values, dtype=float), (half, half), mode="edge")
    return np.convolve(padded, np.ones(points) / points, mode="valid")


def build_padded_groups(daily_smoothed: np.ndarray) -> dict[str, np.ndarray]:
    """Create the eight shifted legacy event windows."""
    group = np.asarray(daily_smoothed, dtype=float)
    if group.ndim != 2:
        raise ValueError("daily_smoothed must be a two-dimensional array")
    zeros = lambda rows: np.zeros((rows, group.shape[1]), dtype=float)
    group_aa = np.vstack((zeros(2), group))
    group_bb = np.vstack((zeros(1), group, zeros(1)))
    group_cc = np.vstack((group, zeros(2)))
    joined = np.concatenate((group_aa, group_bb, group_cc), axis=1)
    return {name: joined[:, start:end] for name, (start, end) in GROUP_SLICES.items()}


def count_significant_peaks(
    rows: np.ndarray,
    savgol_points: int,
    savgol_order: int,
    prominence_ratio: float,
) -> np.ndarray:
    """Count SG peaks above the mean in both raw and filtered series."""
    rows = np.asarray(rows, dtype=float)
    counts = np.zeros(rows.shape[0], dtype=int)
    for index, row in enumerate(rows):
        if not np.isfinite(row).all() or np.ptp(row) <= 0:
            continue
        filtered = savgol_filter(row, savgol_points, savgol_order)
        prominence = np.ptp(row) * prominence_ratio
        peaks, _ = find_peaks(filtered, prominence=prominence)
        mean = row.mean()
        peaks = peaks[(filtered[peaks] > mean) & (row[peaks] > mean)]
        counts[index] = peaks.size
    return counts


def select_legacy_events(
    daily_values: np.ndarray,
    group_name: str,
    settings: PeakSelectionSettings | None = None,
) -> PeakSelectionResult:
    """Run the traceable workflow represented by the uploaded notebooks."""
    if settings is None:
        settings = PeakSelectionSettings()
    settings.validate()
    if group_name not in GROUP_SLICES:
        raise ValueError(f"unknown group {group_name!r}; choose from {sorted(GROUP_SLICES)}")

    daily = np.asarray(daily_values, dtype=float)
    if daily.ndim != 2 or daily.shape[1] != settings.steps_per_day:
        raise ValueError(f"daily_values must have shape (day, {settings.steps_per_day})")
    if not np.isfinite(daily).all():
        raise ValueError("daily_values contains NaN or infinite values")

    totals = daily.sum(axis=1)
    threshold = float(np.percentile(totals, settings.daily_percentile))
    conditioned = daily.copy()
    conditioned[totals < threshold] = 0.0

    flattened = conditioned.reshape(-1)
    smoothed = centered_edge_rolling_mean(flattened, settings.rolling_points)
    groups = build_padded_groups(smoothed.reshape(daily.shape))
    target = groups[group_name]

    maxima = np.argmax(target, axis=1)
    in_window = (
        (maxima >= settings.maximum_index_start)
        & (maxima <= settings.maximum_index_end)
    )
    peak_counts = np.zeros(target.shape[0], dtype=int)
    peak_counts[in_window] = count_significant_peaks(
        target[in_window],
        settings.savgol_points,
        settings.savgol_order,
        settings.prominence_ratio,
    )
    selected = in_window & (peak_counts == settings.peak_count)
    return PeakSelectionResult(selected, peak_counts, threshold, target)


def extended_daily_dates(start: str, end: str) -> pd.DatetimeIndex:
    """Return labels for the N+2 rows of the legacy group matrix.

    Rows zero and one represent the two days before the requested period; the
    remaining rows represent every requested day through ``end``.
    """
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    return pd.date_range(start_ts - pd.Timedelta(days=2), end_ts)


def dates_from_result(
    result: PeakSelectionResult,
    start: str,
    end: str,
) -> pd.DatetimeIndex:
    dates = extended_daily_dates(start, end)
    if result.selected.size != dates.size:
        raise ValueError(
            f"selection length {result.selected.size} does not match date length {dates.size}; "
            "check the requested period and complete-day input"
        )
    return dates[result.selected]


def write_date_list(dates: Iterable[pd.Timestamp], path: str) -> None:
    pd.Series(pd.DatetimeIndex(dates).strftime("%Y-%m-%d")).to_csv(
        path, index=False, header=False
    )
