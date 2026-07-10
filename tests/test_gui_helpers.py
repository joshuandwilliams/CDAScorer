"""
test_gui_helpers.py

Tests for the pure, non-Tkinter helper logic in the GUI modules: value
scaling, even-rounding, and the bounding-box squaring/clamping maths in
MainWindow._make_square_coords (exercised without constructing a window).
"""

from types import SimpleNamespace

from cdascorer import cdascorer_gui, rescore_gui
from cdascorer.cdascorer_gui import MainWindow, _round_to_even, _scale_val


class TestScaleVal:
    def test_scales_and_floors(self):
        # int(floor(val * scale * 0.75))
        assert _scale_val(30, 1.0) == 22
        assert _scale_val(40, 1.0) == 30

    def test_returns_int(self):
        assert isinstance(_scale_val(30, 0.5), int)

    def test_rescore_gui_scale_val_matches(self):
        # The rescore GUI defines its own copy — behaviour must match.
        assert rescore_gui._scale_val(30, 1.0) == cdascorer_gui._scale_val(30, 1.0)


class TestRoundToEven:
    def test_rounds_up_to_nearest_even(self):
        assert _round_to_even(5) == 6
        assert _round_to_even(3) == 4
        assert _round_to_even(1) == 2

    def test_even_input_unchanged(self):
        assert _round_to_even(6) == 6
        assert _round_to_even(0) == 0

    def test_returns_int(self):
        assert isinstance(_round_to_even(3.2), int)


class TestMakeSquareCoords:
    """
    _make_square_coords only touches self.coords and self.img_tk width/height,
    so we can drive it with a lightweight fake instead of a real window.
    """

    def _square(self, coords, img_w=500, img_h=500):
        fake = SimpleNamespace(
            coords=list(coords),
            img_tk=SimpleNamespace(width=lambda: img_w, height=lambda: img_h),
        )
        MainWindow._make_square_coords(fake)
        return fake.coords

    def test_wider_than_tall_expands_vertically(self):
        # [x1, x2, y1, y2]
        result = self._square([0, 100, 0, 40])
        assert result[1] - result[0] == result[3] - result[2]  # square
        assert result == [0, 100, 0, 100]

    def test_taller_than_wide_expands_horizontally(self):
        result = self._square([0, 40, 0, 100])
        assert result[1] - result[0] == result[3] - result[2]
        assert result == [0, 100, 0, 100]

    def test_already_square_unchanged(self):
        assert self._square([10, 50, 10, 50]) == [10, 50, 10, 50]

    def test_clamps_and_shifts_at_right_edge(self):
        # Expanded box would run off the right edge; it shifts left instead.
        result = self._square([150, 250, 100, 120], img_w=200, img_h=200)
        assert result[1] <= 200
        assert result[0] >= 0
        assert result[1] - result[0] == result[3] - result[2]

    def test_result_is_all_ints(self):
        result = self._square([0, 101, 0, 40])
        assert all(isinstance(c, int) for c in result)
