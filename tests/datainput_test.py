import pytest
import cdataml
import numpy as np


def test_square_coords():
    print("\n")
    # [y1, x1, y2, x2] is coords format

    # Mock raw img for shape
    raw_img = np.random.randn(500, 1000, 3) # vertical length, horizontal length, channels

    # Taller than wide
    tall_coords = [100, 200, 0, 200]
    assert cdataml.datainput._make_square_coords(tall_coords, raw_img) == [50, 250, 0, 200]

    # Wider than tall
    wide_coords = [0, 200, 100, 200]
    assert cdataml.datainput._make_square_coords(wide_coords, raw_img) == [0, 200, 50, 250]

    # Already square
    square_coords = [100, 200, 100, 200]
    assert cdataml.datainput._make_square_coords(square_coords, raw_img) == square_coords

    # Goes below zero
    negative_coords_h = [0, 100, 100, 300]
    assert cdataml.datainput._make_square_coords(negative_coords_h, raw_img) == [0, 200, 100, 300]
    negative_coords_v = [100, 300, 0, 100]
    assert cdataml.datainput._make_square_coords(negative_coords_v, raw_img) == [100, 300, 0, 200]

    # Goes above image size boundary
    over_bounds_h = [950, 1050, 100, 200]
    assert cdataml.datainput._make_square_coords(over_bounds_h, raw_img) == [900, 1000, 100, 200]
    over_bounds_v = [100, 200, 450, 550]
    assert cdataml.datainput._make_square_coords(over_bounds_v, raw_img) == [100, 200, 400, 500]

    # Odd number
    #odd_coords = [0, 100, 200, 201]
    #assert cdataml.datainput._make_square_coords(odd_coords) == [0, 50, 200, 250]
