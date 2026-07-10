"""
test_cdametadata.py

Tests for the CDAMetadata class, focusing on the _update cascade
(pos → col → row → image → end_of_data) and the _make_pandas output.
"""

import pandas as pd

from cdascorer.cdametadata import CDAMetadata

COLUMNS = [
    "img",
    "maxrow",
    "maxcol",
    "row",
    "col",
    "pos",
    "score",
    "x1",
    "x2",
    "y1",
    "y2",
]


def _empty_df():
    return pd.DataFrame(columns=COLUMNS)


def _make_metadata(files, df=None, maxrow=2, maxcol=2):
    """Helper to create a CDAMetadata with maxrow/maxcol already set."""
    if df is None:
        df = _empty_df()
    m = CDAMetadata(files, df)
    m.maxrow = maxrow
    m.maxcol = maxcol
    return m


class TestInit:
    """Tests for CDAMetadata.__init__."""

    def test_empty_dataframe_uses_first_file(self):
        m = CDAMetadata(["img_a.tif", "img_b.tif"], _empty_df())
        assert m.img == "img_a.tif"
        assert m.row == 1
        assert m.col == 1
        assert m.pos == 1
        assert m.score is None
        assert m.end_of_data is False

    def test_resumes_from_last_row_of_dataframe(self):
        df = _empty_df()
        row = pd.DataFrame(
            [
                {
                    "img": "img_b.tif",
                    "maxrow": 3,
                    "maxcol": 2,
                    "row": 2,
                    "col": 1,
                    "pos": 4,
                    "score": 3,
                    "x1": 10,
                    "x2": 50,
                    "y1": 10,
                    "y2": 50,
                }
            ]
        )
        df = pd.concat([df, row], ignore_index=True)

        m = CDAMetadata(["img_a.tif", "img_b.tif"], df)
        assert m.img == "img_b.tif"
        assert m.maxrow == 3
        assert m.maxcol == 2
        assert m.row == 2
        assert m.col == 1
        assert m.pos == 4
        assert m.score == 3
        # x/y coords are always reset
        assert m.x1 is None


class TestUpdate:
    """Tests for the _update cascade: pos → col → row → image → end."""

    def test_increments_pos(self):
        m = _make_metadata(["img.tif"])
        assert m.pos == 1
        m._update(num_spots=8)
        assert m.pos == 2
        assert m.col == 1
        assert m.row == 1

    def test_pos_wraps_to_next_col(self):
        m = _make_metadata(["img.tif"])
        m.pos = 3
        m._update(num_spots=3)
        assert m.pos == 1
        assert m.col == 2

    def test_col_wraps_to_next_row(self):
        m = _make_metadata(["img.tif"], maxrow=2, maxcol=2)
        m.pos = 3
        m.col = 2
        m._update(num_spots=3)
        assert m.pos == 1
        assert m.col == 1
        assert m.row == 2

    def test_row_wraps_to_next_image(self):
        m = _make_metadata(["img_a.tif", "img_b.tif"], maxrow=2, maxcol=2)
        m.pos = 3
        m.col = 2
        m.row = 2
        m._update(num_spots=3)
        assert m.img == "img_b.tif"
        assert m.pos == 1
        assert m.col == 1
        assert m.row == 1
        assert m.end_of_data is False

    def test_end_of_data_on_last_image(self):
        m = _make_metadata(["img.tif"], maxrow=1, maxcol=1)
        m.pos = 3
        m._update(num_spots=3)
        assert m.end_of_data is True

    def test_score_and_coords_cleared_after_update(self):
        m = _make_metadata(["img.tif"])
        m.score = 5
        m.x1, m.x2, m.y1, m.y2 = 10, 50, 10, 50
        m._update(num_spots=8)
        assert m.score is None
        assert m.x1 is None
        assert m.x2 is None
        assert m.y1 is None
        assert m.y2 is None

    def test_full_traversal_single_image(self):
        """Walk through an entire 2x2 grid with 2 spots per leaf on one image."""
        m = _make_metadata(["img.tif"], maxrow=2, maxcol=2)
        num_spots = 2

        # Expected sequence: (row, col, pos)
        expected = [
            # After each _update call:
            (1, 1, 2),  # second spot on first leaf
            (1, 2, 1),  # next col
            (1, 2, 2),
            (2, 1, 1),  # next row
            (2, 1, 2),
            (2, 2, 1),  # last leaf
            (2, 2, 2),
        ]

        for exp_row, exp_col, exp_pos in expected:
            m._update(num_spots)
            assert (m.row, m.col, m.pos) == (exp_row, exp_col, exp_pos), (
                f"Expected ({exp_row}, {exp_col}, {exp_pos}), "
                f"got ({m.row}, {m.col}, {m.pos})"
            )
            assert m.end_of_data is False

        # One more update should hit end of data
        m._update(num_spots)
        assert m.end_of_data is True

    def test_full_traversal_multiple_images(self):
        """Walk through two images, each 1x1 grid with 2 spots."""
        m = _make_metadata(["a.tif", "b.tif"], maxrow=1, maxcol=1)
        num_spots = 2

        m._update(num_spots)
        assert (m.img, m.row, m.col, m.pos) == ("a.tif", 1, 1, 2)

        m._update(num_spots)
        assert (m.img, m.row, m.col, m.pos) == ("b.tif", 1, 1, 1)
        assert m.end_of_data is False

        m._update(num_spots)
        assert (m.img, m.row, m.col, m.pos) == ("b.tif", 1, 1, 2)

        m._update(num_spots)
        assert m.end_of_data is True


class TestMakePandas:
    """Tests for _make_pandas output format."""

    def test_output_has_correct_columns(self):
        m = _make_metadata(["img.tif"])
        m.score = 3
        m.x1, m.x2, m.y1, m.y2 = 10, 50, 20, 60
        result = m._make_pandas()
        assert list(result.columns) == COLUMNS

    def test_output_values_match_metadata(self):
        m = _make_metadata(["img.tif"], maxrow=3, maxcol=4)
        m.row, m.col, m.pos = 2, 3, 5
        m.score = 4
        m.x1, m.x2, m.y1, m.y2 = 100, 200, 150, 250
        result = m._make_pandas()
        row = result.iloc[0]
        assert row["img"] == "img.tif"
        assert row["maxrow"] == 3
        assert row["maxcol"] == 4
        assert row["row"] == 2
        assert row["col"] == 3
        assert row["pos"] == 5
        assert row["score"] == 4
        assert row["x1"] == 100
        assert row["x2"] == 200

    def test_output_is_single_row_dataframe(self):
        m = _make_metadata(["img.tif"])
        m.score = 0
        result = m._make_pandas()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestStr:
    """Tests for CDAMetadata.__str__."""

    def test_str_includes_all_fields(self):
        m = _make_metadata(["img.tif"], maxrow=2, maxcol=3)
        m.pos = 4
        m.score = 5
        m.x1, m.x2, m.y1, m.y2 = 10, 50, 20, 60
        text = str(m)
        assert "Img: img.tif" in text
        assert "Maxrow: 2" in text
        assert "Maxcol: 3" in text
        assert "Pos: 4" in text
        assert "Score: 5" in text
        assert "x1: 10" in text
        assert "y2: 60" in text
