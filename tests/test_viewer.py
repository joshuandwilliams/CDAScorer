"""
test_viewer.py

Tests for the non-GUI logic in viewer.py: the image-path lookup helper and
the argument validation in main() (with the GUI display stubbed out).
"""

import pandas as pd
import pytest

from cdascorer import viewer
from cdascorer.viewer import _find_image_path


class TestFindImagePath:
    """Tests for the viewer's image path lookup."""

    def test_finds_image_by_basename(self):
        data = pd.DataFrame(
            {"img": ["/long/path/to/DSC_0001.TIF", "/long/path/to/DSC_0002.TIF"]}
        )
        assert _find_image_path(data, "DSC_0001.TIF") == "/long/path/to/DSC_0001.TIF"

    def test_matches_basename_even_with_different_directory(self):
        data = pd.DataFrame({"img": ["/original/path/DSC_0001.TIF"]})
        result = _find_image_path(data, "/some/other/path/DSC_0001.TIF")
        assert result == "/original/path/DSC_0001.TIF"

    def test_returns_none_for_missing_image(self):
        data = pd.DataFrame({"img": ["/path/DSC_0001.TIF"]})
        assert _find_image_path(data, "DSC_9999.TIF") is None

    def test_returns_unique_path_for_duplicated_image(self):
        data = pd.DataFrame({"img": ["/path/DSC_0001.TIF"] * 3})
        assert _find_image_path(data, "DSC_0001.TIF") == "/path/DSC_0001.TIF"


class TestMain:
    """Tests for viewer.main argument validation (display stubbed)."""

    @pytest.fixture
    def stub_view(self, monkeypatch):
        calls = {}

        def fake_view(data, image_path):
            calls["data"] = data
            calls["image_path"] = image_path

        monkeypatch.setattr(viewer, "_view", fake_view)
        return calls

    def _run(self, monkeypatch, argv):
        monkeypatch.setattr("sys.argv", ["cdascorer-view", *argv])
        viewer.main()

    def test_rejects_missing_data_file(self, monkeypatch, stub_view):
        with pytest.raises(SystemExit) as exc:
            self._run(monkeypatch, ["--data", "/no/file.csv", "--image", "x.tif"])
        assert "does not exist" in str(exc.value)

    def test_resolves_image_by_direct_path(self, tmp_path, monkeypatch, stub_view):
        data_file = tmp_path / "scores.csv"
        image = tmp_path / "img.tif"
        image.write_bytes(b"x")
        pd.DataFrame({"img": [str(image)]}).to_csv(data_file, index=False)
        self._run(monkeypatch, ["--data", str(data_file), "--image", str(image)])
        assert stub_view["image_path"] == str(image)

    def test_resolves_image_by_basename_from_csv(
        self, tmp_path, monkeypatch, stub_view
    ):
        data_file = tmp_path / "scores.csv"
        image = tmp_path / "img.tif"
        image.write_bytes(b"x")
        # CSV references the real path; user passes only the basename.
        pd.DataFrame({"img": [str(image)]}).to_csv(data_file, index=False)
        self._run(monkeypatch, ["--data", str(data_file), "--image", "img.tif"])
        assert stub_view["image_path"] == str(image)

    def test_rejects_image_absent_from_disk_and_csv(
        self, tmp_path, monkeypatch, stub_view
    ):
        data_file = tmp_path / "scores.csv"
        pd.DataFrame({"img": ["/somewhere/other.tif"]}).to_csv(data_file, index=False)
        with pytest.raises(SystemExit) as exc:
            self._run(monkeypatch, ["--data", str(data_file), "--image", "ghost.tif"])
        assert "was not found" in str(exc.value)

    def test_rejects_csv_path_that_is_missing_on_disk(
        self, tmp_path, monkeypatch, stub_view
    ):
        data_file = tmp_path / "scores.csv"
        # CSV references a path that does not exist on disk.
        pd.DataFrame({"img": ["/gone/img.tif"]}).to_csv(data_file, index=False)
        with pytest.raises(SystemExit) as exc:
            self._run(monkeypatch, ["--data", str(data_file), "--image", "img.tif"])
        assert "does not exist on disk" in str(exc.value)
