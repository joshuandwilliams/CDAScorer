"""
test_rescore.py

Tests for the non-GUI logic in rescore.py: extracting a scorer's CDAs from the
combined dataset, resolving image paths, and the sampling/output flow in main()
(with the GUI stubbed out).
"""

import os

import pandas as pd
import pytest

from cdascorer import rescore
from cdascorer.rescore import (
    OUTPUT_COLUMNS,
    _find_scorer_cdas,
    _resolve_image_path,
)


def _combined_row(basename, scorers, scores, centre_coords=1, median=3.0, **coords):
    """
    Build one row of the combined dataset. ``scorers``/``scores`` are 3-tuples
    for positions 1..3. Bounding-box columns default to a distinct value per
    coordinate set so we can check the right one is selected.
    """
    row = {
        "Basename": basename,
        "MaxRow": 3,
        "MaxCol": 3,
        "Row": 1,
        "Col": 1,
        "Pos": 1,
        "Median_Score": median,
        "Centre_Coords": centre_coords,
    }
    for i in (1, 2, 3):
        row[f"Scorer{i}"] = scorers[i - 1]
        row[f"Score{i}"] = scores[i - 1]
        row[f"X1_{i}"] = coords.get(f"x1_{i}", 100 * i)
        row[f"X2_{i}"] = coords.get(f"x2_{i}", 100 * i + 50)
        row[f"Y1_{i}"] = coords.get(f"y1_{i}", 200 * i)
        row[f"Y2_{i}"] = coords.get(f"y2_{i}", 200 * i + 50)
    return row


class TestFindScorerCdas:
    """Tests for _find_scorer_cdas normalisation."""

    def test_finds_scorer_in_any_position(self):
        data = pd.DataFrame(
            [
                _combined_row("a.tif", ["JoshW", "Raf", "Yux"], [2, 3, 4]),
                _combined_row("b.tif", ["Raf", "JoshW", "Yux"], [5, 6, 1]),
            ]
        )
        result = _find_scorer_cdas(data, "JoshW")
        assert len(result) == 2
        assert set(result["basename"]) == {"a.tif", "b.tif"}

    def test_old_score_is_the_scorers_own_score(self):
        data = pd.DataFrame(
            [_combined_row("a.tif", ["Raf", "JoshW", "Yux"], [5, 6, 1])]
        )
        result = _find_scorer_cdas(data, "JoshW")
        assert result.iloc[0]["old_score"] == 6

    def test_uses_centre_coords_bounding_box(self):
        # Centre_Coords=2 -> box columns X1_2/X2_2/Y1_2/Y2_2 (defaults 200/250/400/450)
        data = pd.DataFrame(
            [
                _combined_row(
                    "a.tif", ["JoshW", "Raf", "Yux"], [2, 3, 4], centre_coords=2
                )
            ]
        )
        result = _find_scorer_cdas(data, "JoshW").iloc[0]
        assert result["x1"] == 200
        assert result["x2"] == 250
        assert result["y1"] == 400
        assert result["y2"] == 450

    def test_returns_empty_for_unknown_scorer(self):
        data = pd.DataFrame(
            [_combined_row("a.tif", ["JoshW", "Raf", "Yux"], [2, 3, 4])]
        )
        assert len(_find_scorer_cdas(data, "Nobody")) == 0


class TestResolveImagePath:
    """Tests for _resolve_image_path lookup."""

    def test_exact_match(self, tmp_path):
        (tmp_path / "IMG_1.TIF").write_bytes(b"x")
        result = _resolve_image_path("IMG_1.TIF", str(tmp_path))
        assert result == str(tmp_path / "IMG_1.TIF")

    def test_case_insensitive_match(self, tmp_path):
        # On a case-sensitive FS this exercises the fallback listdir scan;
        # on a case-insensitive FS the exact-match branch already resolves it.
        # Either way the requested image must be found.
        (tmp_path / "IMG_1.tif").write_bytes(b"x")
        result = _resolve_image_path("img_1.TIF", str(tmp_path))
        assert result is not None
        assert os.path.exists(result)
        assert os.path.basename(result).lower() == "img_1.tif"

    def test_returns_none_when_absent(self, tmp_path):
        assert _resolve_image_path("nope.tif", str(tmp_path)) is None


class TestMain:
    """Tests for rescore.main sampling and output (GUI stubbed)."""

    @pytest.fixture
    def stub_gui(self, monkeypatch):
        """Stub Tk and RescoreWindow; capture the records passed to the GUI."""
        captured = {}

        class FakeRoot:
            def title(self, *a):
                pass

            def winfo_screenwidth(self):
                return 1000

            def winfo_screenheight(self):
                return 800

            def protocol(self, *a):
                pass

            def mainloop(self):
                pass

        class FakeWindow:
            def __init__(self, root, cda_records, w, h):
                captured["records"] = cda_records
                # Pretend the user scored every CDA with a 4.
                self.results = [
                    {
                        **{k: rec.get(k) for k in OUTPUT_COLUMNS if k != "new_score"},
                        "new_score": 4,
                    }
                    for rec in cda_records
                ]

            def _save_and_quit(self):
                pass

        monkeypatch.setattr(rescore.tk, "Tk", lambda: FakeRoot())
        monkeypatch.setattr(rescore, "RescoreWindow", FakeWindow)
        return captured

    def _write_data(self, tmp_path, rows):
        data_file = tmp_path / "combined.csv"
        pd.DataFrame(rows).to_csv(data_file, index=False)
        return data_file

    def _run(self, monkeypatch, argv):
        monkeypatch.setattr("sys.argv", ["cdascorer-rescore", *argv])
        rescore.main()

    def test_excludes_median_zero_and_writes_output(
        self, tmp_path, monkeypatch, stub_gui
    ):
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        (img_dir / "a.tif").write_bytes(b"x")
        (img_dir / "b.tif").write_bytes(b"x")
        rows = [
            _combined_row("a.tif", ["JoshW", "Raf", "Yux"], [2, 3, 4], median=3.0),
            _combined_row("b.tif", ["JoshW", "Raf", "Yux"], [1, 3, 4], median=0.0),
        ]
        data_file = self._write_data(tmp_path, rows)
        out = tmp_path / "out.csv"
        self._run(
            monkeypatch,
            [
                "--data",
                str(data_file),
                "--scorer",
                "JoshW",
                "--source_folder",
                str(img_dir),
                "--output",
                str(out),
                "--num_samples",
                "10",
            ],
        )
        # median-0 CDA excluded -> only "a.tif" reaches the GUI
        assert {r["basename"] for r in stub_gui["records"]} == {"a.tif"}
        written = pd.read_csv(out)
        assert list(written.columns) == OUTPUT_COLUMNS
        assert len(written) == 1
        assert written.iloc[0]["new_score"] == 4

    def test_rejects_unknown_scorer(self, tmp_path, monkeypatch, stub_gui):
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        rows = [_combined_row("a.tif", ["JoshW", "Raf", "Yux"], [2, 3, 4])]
        data_file = self._write_data(tmp_path, rows)
        with pytest.raises(SystemExit) as exc:
            self._run(
                monkeypatch,
                [
                    "--data",
                    str(data_file),
                    "--scorer",
                    "Ghost",
                    "--source_folder",
                    str(img_dir),
                ],
            )
        assert "not found" in str(exc.value)

    def test_sampling_is_reproducible_with_seed(self, tmp_path, monkeypatch, stub_gui):
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        rows = []
        for i in range(20):
            name = f"img_{i}.tif"
            (img_dir / name).write_bytes(b"x")
            rows.append(
                _combined_row(name, ["JoshW", "Raf", "Yux"], [2, 3, 4], median=3.0)
            )
        data_file = self._write_data(tmp_path, rows)
        out = tmp_path / "out.csv"
        args = [
            "--data",
            str(data_file),
            "--scorer",
            "JoshW",
            "--source_folder",
            str(img_dir),
            "--output",
            str(out),
            "--num_samples",
            "5",
            "--seed",
            "7",
        ]
        self._run(monkeypatch, args)
        first = [r["basename"] for r in stub_gui["records"]]
        self._run(monkeypatch, args)
        second = [r["basename"] for r in stub_gui["records"]]
        assert first == second
        assert len(first) == 5
