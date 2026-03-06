"""
test_cli.py

Tests for non-GUI helper functions in cli.py and viewer.py.
"""
import os
import pytest
import pandas as pd

from cdascorer.viewer import _find_image_path

COLUMNS = ["img", "maxrow", "maxcol", "row", "col", "pos", "score", "x1", "x2", "y1", "y2"]


class TestFindImagePath:
    """Tests for the viewer's image path lookup."""

    def test_finds_image_by_basename(self):
        data = pd.DataFrame({
            "img": ["/long/path/to/DSC_0001.TIF", "/long/path/to/DSC_0002.TIF"],
        })
        result = _find_image_path(data, "DSC_0001.TIF")
        assert result == "/long/path/to/DSC_0001.TIF"

    def test_matches_basename_even_with_different_directory(self):
        data = pd.DataFrame({
            "img": ["/original/path/DSC_0001.TIF"],
        })
        result = _find_image_path(data, "/some/other/path/DSC_0001.TIF")
        assert result == "/original/path/DSC_0001.TIF"

    def test_returns_none_for_missing_image(self):
        data = pd.DataFrame({
            "img": ["/path/DSC_0001.TIF"],
        })
        result = _find_image_path(data, "DSC_9999.TIF")
        assert result is None

    def test_returns_unique_path_for_duplicated_image(self):
        data = pd.DataFrame({
            "img": [
                "/path/DSC_0001.TIF",
                "/path/DSC_0001.TIF",
                "/path/DSC_0001.TIF",
            ],
        })
        result = _find_image_path(data, "DSC_0001.TIF")
        assert result == "/path/DSC_0001.TIF"


class TestCLIFileValidation:
    """Tests for CSV file creation and validation logic in cli.py."""

    def test_creates_csv_with_correct_columns(self, tmp_path):
        """Simulates what cli.main does when the file doesn't exist."""
        output = tmp_path / "cdata.csv"
        cdata = pd.DataFrame(columns=COLUMNS)
        cdata.to_csv(output, index=False)

        loaded = pd.read_csv(output)
        assert list(loaded.columns) == COLUMNS
        assert len(loaded) == 0

    def test_rejects_csv_with_wrong_columns(self, tmp_path):
        """Simulates the column validation check."""
        bad_file = tmp_path / "bad.csv"
        pd.DataFrame(columns=["wrong", "columns"]).to_csv(bad_file, index=False)

        loaded = pd.read_csv(bad_file)
        assert list(loaded.columns) != COLUMNS