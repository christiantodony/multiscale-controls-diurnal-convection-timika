# Method and parameter notes

## Available peak-selection implementation

The reconstructed workflow follows these steps:

1. Select a nearest IMERG grid point or read authorized AWS observations.
2. Convert AWS WIT timestamps to UTC and aggregate 15-minute rain amounts into
   30-minute totals.
3. Reshape the regular series into 48 samples per UTC day.
4. Calculate daily totals and zero days below the chosen percentile (P50 by
   default).
5. Apply a centered rolling mean to the flattened continuous series.
6. Construct shifted multi-day windows for the eight UTC groups 00, 03, 06, 09,
   12, 15, 18, and 21.
7. Retain windows whose maximum lies inside the target index interval.
8. Apply a Savitzky-Golay filter and identify peaks with a relative-prominence
   threshold.
9. Retain peaks above the row mean in both the raw and filtered series.
10. Export single-peak dates by default.

This describes the supplied-code profile, not a claim that every textual detail
in the final paper has already been reconciled. See the audit.

## Defaults in `legacy_uploaded`

| Parameter | Value |
|---|---:|
| Samples per day | 48 |
| Daily threshold | P50 |
| Rolling window | 7 points |
| SG window | 7 points |
| SG polynomial order | 3 |
| Prominence | 0.20 x row range |
| Target maximum indices | 37-42 inclusive |
| Retained peak count | 1 |

## Applying the method to another region

At minimum, document and test:

- geographic point or averaging box;
- sampling interval and rain-rate/accumulation units;
- local time offset and daylight-saving behavior, if any;
- missing-data treatment;
- wet-day threshold sensitivity;
- smoothing and SG windows in physical time, not only sample count;
- peak-prominence sensitivity; and
- independent validation against gauges or radar where possible.

For a new region, preserve the configuration and output metadata used for each
run. A regional application should cite both the original QJRMS method paper and
the exact software release used.

