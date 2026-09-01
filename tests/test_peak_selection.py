import numpy as np
import pytest

from timika_diurnal.peak_selection import (
    GROUP_SLICES,
    PeakSelectionSettings,
    build_padded_groups,
    centered_edge_rolling_mean,
    extended_daily_dates,
    select_legacy_events,
    to_daily_matrix,
)


def test_daily_matrix_trims_incomplete_day():
    values = np.arange(101, dtype=float)
    result = to_daily_matrix(values, 48)
    assert result.shape == (2, 48)
    np.testing.assert_array_equal(result.ravel(), values[:96])


def test_centered_rolling_mean_preserves_constant():
    result = centered_edge_rolling_mean(np.ones(30), 7)
    np.testing.assert_allclose(result, 1.0)


def test_group_shapes_match_uploaded_notebook():
    groups = build_padded_groups(np.zeros((10, 48)))
    assert set(groups) == set(GROUP_SLICES)
    assert groups["group00"].shape == (12, 78)
    assert groups["group21"].shape == (12, 80)


def test_selection_returns_day_count_plus_padding():
    rng = np.random.default_rng(42)
    daily = rng.gamma(shape=1.5, scale=0.2, size=(20, 48))
    result = select_legacy_events(daily, "group00")
    assert result.selected.shape == (22,)
    assert result.peak_counts.shape == (22,)


def test_extended_dates_align_with_group_rows():
    dates = extended_daily_dates("2001-01-01", "2001-01-20")
    assert len(dates) == 22
    assert str(dates[0].date()) == "2000-12-30"
    assert str(dates[-1].date()) == "2001-01-20"


def test_settings_reject_even_savgol_window():
    settings = PeakSelectionSettings(savgol_points=12)
    with pytest.raises(ValueError, match="odd"):
        settings.validate()
