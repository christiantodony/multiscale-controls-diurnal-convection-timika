from pathlib import Path

from timika_diurnal.comparison import hourly_matching_matrix


def test_hourly_intersection(tmp_path: Path):
    (tmp_path / "peak_GPM_00.txt").write_text("2001-01-01\n2001-01-02\n")
    (tmp_path / "peak_OBS_00.txt").write_text("2001-01-02\n2001-01-03\n")
    matrix, gpm, aws = hourly_matching_matrix(tmp_path, tmp_path)
    assert matrix.iloc[0, 0] == 1
    assert gpm[0] == 2
    assert aws[0] == 2
    assert matrix.to_numpy().sum() == 1

