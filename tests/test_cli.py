"""
test_cli.py

Tests for the non-GUI logic in cli.py: image discovery, the save/backup
helper, and the argument-parsing/validation flow in main() (with the GUI
launch stubbed out).
"""

import pandas as pd
import pytest

from cdascorer import cli
from cdascorer.cli import COLUMNS, _discover_images, _save_and_quit


class TestDiscoverImages:
    """Tests for _discover_images file filtering."""

    def test_finds_supported_image_extensions(self, tmp_path):
        for name in ["a.tif", "b.TIFF", "c.jpg", "d.jpeg", "e.png"]:
            (tmp_path / name).write_bytes(b"x")
        found = _discover_images(str(tmp_path))
        assert len(found) == 5
        assert all(p.startswith(str(tmp_path)) for p in found)

    def test_skips_non_image_files(self, tmp_path):
        (tmp_path / "keep.tif").write_bytes(b"x")
        (tmp_path / "notes.txt").write_text("hello")
        (tmp_path / "data.csv").write_text("a,b")
        found = _discover_images(str(tmp_path))
        assert [p.rsplit("/", 1)[-1] for p in found] == ["keep.tif"]

    def test_skips_hidden_files(self, tmp_path):
        (tmp_path / "visible.tif").write_bytes(b"x")
        (tmp_path / ".hidden.tif").write_bytes(b"x")
        found = _discover_images(str(tmp_path))
        assert [p.rsplit("/", 1)[-1] for p in found] == ["visible.tif"]

    def test_results_are_sorted(self, tmp_path):
        for name in ["c.tif", "a.tif", "b.tif"]:
            (tmp_path / name).write_bytes(b"x")
        found = _discover_images(str(tmp_path))
        assert found == sorted(found)

    def test_empty_folder_returns_empty_list(self, tmp_path):
        assert _discover_images(str(tmp_path)) == []


class TestSaveAndQuit:
    """Tests for _save_and_quit backup/save behaviour."""

    def test_writes_dataframe_to_new_file(self, tmp_path):
        out = tmp_path / "cdata.csv"
        df = pd.DataFrame(columns=COLUMNS)
        with pytest.raises(SystemExit):
            _save_and_quit(df, str(out))
        assert out.exists()
        assert list(pd.read_csv(out).columns) == COLUMNS

    def test_backs_up_existing_file(self, tmp_path):
        out = tmp_path / "cdata.csv"
        out.write_text("old,data\n1,2\n")
        df = pd.DataFrame(columns=COLUMNS)
        with pytest.raises(SystemExit):
            _save_and_quit(df, str(out))
        # The new file exists with the fresh columns ...
        assert list(pd.read_csv(out).columns) == COLUMNS
        # ... and a timestamped backup of the old content was created.
        backups = list(tmp_path.glob("backup_*cdata.csv"))
        assert len(backups) == 1
        assert "old,data" in backups[0].read_text()


class TestMain:
    """Tests for cli.main argument validation (GUI launch stubbed)."""

    @pytest.fixture
    def stub_gui(self, monkeypatch):
        """Replace _cdascorer so main() never opens a Tkinter window."""
        calls = {}

        def fake_cdascorer(source_folder, df, test, file):
            calls["source_folder"] = source_folder
            calls["df"] = df
            calls["test"] = test
            calls["file"] = file

        monkeypatch.setattr(cli, "_cdascorer", fake_cdascorer)
        return calls

    def _run(self, monkeypatch, argv):
        monkeypatch.setattr("sys.argv", ["cdascorer", *argv])
        cli.main()

    def test_creates_csv_when_missing(self, tmp_path, monkeypatch, stub_gui):
        out = tmp_path / "new.csv"
        self._run(monkeypatch, ["--test", "--file", str(out)])
        assert out.exists()
        assert list(pd.read_csv(out).columns) == COLUMNS
        assert stub_gui["test"] is True

    def test_loads_existing_valid_csv(self, tmp_path, monkeypatch, stub_gui):
        out = tmp_path / "existing.csv"
        pd.DataFrame(columns=COLUMNS).to_csv(out, index=False)
        self._run(monkeypatch, ["--test", "--file", str(out)])
        assert list(stub_gui["df"].columns) == COLUMNS

    def test_rejects_non_csv_file(self, monkeypatch, stub_gui):
        with pytest.raises(SystemExit) as exc:
            self._run(monkeypatch, ["--test", "--file", "output.txt"])
        assert "is not a CSV file" in str(exc.value)
        assert stub_gui == {}  # GUI never reached

    def test_rejects_missing_source_folder(self, monkeypatch, stub_gui):
        with pytest.raises(SystemExit) as exc:
            self._run(monkeypatch, ["--source_folder", "/no/such/folder"])
        assert "does not exist" in str(exc.value)

    def test_rejects_csv_with_wrong_columns(self, tmp_path, monkeypatch, stub_gui):
        bad = tmp_path / "bad.csv"
        pd.DataFrame(columns=["wrong", "columns"]).to_csv(bad, index=False)
        with pytest.raises(SystemExit) as exc:
            self._run(monkeypatch, ["--test", "--file", str(bad)])
        assert "incorrect column names" in str(exc.value)
