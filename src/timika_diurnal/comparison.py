"""GPM-IMERG versus AWS event-date comparison."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def read_dates(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text().splitlines() if line.strip()}


def hourly_matching_matrix(
    gpm_directory: str | Path,
    aws_directory: str | Path,
    gpm_pattern: str = "peak_GPM_{hour:02d}.txt",
    aws_pattern: str = "peak_OBS_{hour:02d}.txt",
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Return 24 x 24 intersections plus source event totals."""
    gpm_directory = Path(gpm_directory)
    aws_directory = Path(aws_directory)
    gpm = [read_dates(gpm_directory / gpm_pattern.format(hour=h)) for h in range(24)]
    aws = [read_dates(aws_directory / aws_pattern.format(hour=h)) for h in range(24)]
    matrix = np.array([[len(aws[row] & gpm[col]) for col in range(24)] for row in range(24)])
    labels = [f"{(hour + 9) % 24:02d}:00" for hour in range(24)]
    return (
        pd.DataFrame(matrix, index=labels, columns=labels),
        np.array([len(x) for x in gpm]),
        np.array([len(x) for x in aws]),
    )

