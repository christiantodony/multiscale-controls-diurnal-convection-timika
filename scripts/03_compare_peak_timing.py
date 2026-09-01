"""Create the 24 x 24 IMERG-AWS date-intersection table and figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from timika_diurnal.comparison import hourly_matching_matrix


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpm-dir", required=True)
    parser.add_argument("--aws-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    matrix, gpm_totals, aws_totals = hourly_matching_matrix(args.gpm_dir, args.aws_dir)
    matrix.to_csv(output / "hourly_peak_date_intersections.csv")

    values = matrix.to_numpy()
    diagonal = np.diag(values)
    gpm_different = values.sum(axis=0) - diagonal
    aws_different = values.sum(axis=1) - diagonal
    gpm_unmatched = np.maximum(gpm_totals - diagonal - gpm_different, 0)
    aws_unmatched = np.maximum(aws_totals - diagonal - aws_different, 0)

    fig = plt.figure(figsize=(13, 11), constrained_layout=True)
    grid = fig.add_gridspec(4, 4)
    top = fig.add_subplot(grid[0, :3])
    main = fig.add_subplot(grid[1:, :3], sharex=top)
    right = fig.add_subplot(grid[1:, 3], sharey=main)
    image = main.imshow(values, cmap="Greys", origin="upper")
    for row in range(24):
        for column in range(24):
            main.text(column, row, str(values[row, column]), ha="center", va="center", fontsize=7)
    labels = matrix.columns.tolist()
    main.set_xticks(range(24), labels, rotation=45, ha="right")
    main.set_yticks(range(24), matrix.index.tolist())
    main.set_xlabel("IMERG peak time (WIT, UTC+9)")
    main.set_ylabel("AWS peak time (WIT, UTC+9)")
    fig.colorbar(image, ax=main, label="Matching dates")

    x = np.arange(24)
    top.bar(x, diagonal, color="0.25", label="same-hour")
    top.bar(x, gpm_different, bottom=diagonal, color="0.55", label="different-hour")
    top.bar(x, gpm_unmatched, bottom=diagonal + gpm_different, color="0.82", label="unmatched")
    top.set_ylabel("IMERG dates")
    top.legend(ncols=3, fontsize=8)
    top.tick_params(axis="x", labelbottom=False)

    right.barh(x, diagonal, color="0.25")
    right.barh(x, aws_different, left=diagonal, color="0.55")
    right.barh(x, aws_unmatched, left=diagonal + aws_different, color="0.82")
    right.set_xlabel("AWS dates")
    right.tick_params(axis="y", labelleft=False)
    fig.savefig(output / "hourly_peak_date_intersections.png", dpi=300, bbox_inches="tight")
    print(f"Wrote table and figure to {output}")


if __name__ == "__main__":
    main()
