import pytest
import cdataml
import pandas as pd

# Mock file_names object
filenames = ["Test1.tif", "Test2.tif"]

# Mock CDAMetadata object
class CDA:
    def __init__(self, img = "Test1.tif", maxrow = 2, maxcol = 4, row = 1, col = 1, pos = 1, score = None, x1 = None, x2 = None, y1 = None, y2 = None):
        self.img = img
        self.maxrow = maxrow
        self.maxcol = maxcol
        self.row = row
        self.col = col
        self.pos = pos
        self.score = score
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

# Mock cdata object
def CDAdata(finalrow = None):
    if finalrow == None: # Return empty dataframe
        return pd.DataFrame(columns=["img", "maxrow", "maxcol", "row", "col", "pos", "score", "x1", "x2", "y1", "y2"])
    else: # Return dataframe with
        assert finalrow.__class__.__name__ == "CDA"
        return pd.DataFrame({'img': [finalrow.img],
        'maxrow': [finalrow.maxrow],
        'maxcol': [finalrow.maxcol],
        'row': [finalrow.row],
        'col': [finalrow.col],
        'pos': [finalrow.pos],
        'score': [finalrow.score],
        'x1': [finalrow.x1],
        'x2': [finalrow.x2],
        'y1': [finalrow.y1],
        'y2': [finalrow.y2]})

# Create CDAMetadata test object
def create_CDAMetadata_object(img = "Test1.tif", maxrow = 2, maxcol = 4, row = 1, col = 1, pos = 1, score = None, x1 = None, x2 = None, y1 = None, y2 = None):
    cdata = CDAdata(finalrow = CDA(img, maxrow, maxcol, row, col, pos, score, x1, x2, y1, y2))
    return cdataml.cdametadata.CDAMetadata(filenames, cdata)



# Test assertions about CDAMetadata object quickly
def assert_CDAMetadata(object, img, maxrow, maxcol, row, col, pos):
    assert object.img == img
    assert object.maxrow == maxrow
    assert object.maxcol == maxcol
    assert object.row == row
    assert object.col == col
    assert object.pos == pos

# PyTest Tests
def test_initiale_CDAMetadata_object():

    # Check initialised CDAMetadata object from empty df
    empty_df = CDAdata()
    from_empty = cdataml.cdametadata.CDAMetadata(filenames, empty_df)
    assert_CDAMetadata(from_empty, "Test1.tif", None, None, 1, 1, 1)

    # Check initialised CDAMetadata object from non empty df
    non_empty_df = CDAdata(finalrow = CDA())
    from_non_empty = cdataml.cdametadata.CDAMetadata(filenames, non_empty_df)
    assert_CDAMetadata(from_non_empty, "Test1.tif", 2, 4, 1, 1, 1)


def test_update_CDAMetadata_object():

    # Check updated CDAMetadata object from first pos on img
    first_CDA = create_CDAMetadata_object()
    updated_first = first_CDA._update(8)
    assert_CDAMetadata(updated_first, "Test1.tif", 2, 4, 1, 1, 2)

    # Check updated CDAMetadata object from last pos on leaf
    end_of_leaf = create_CDAMetadata_object(pos=8)
    updated_leaf = end_of_leaf._update(8)
    assert_CDAMetadata(updated_leaf, "Test1.tif", 2, 4, 1, 2, 1)

    # Check updated CDAMetadata object from last pos on row
    end_of_row = create_CDAMetadata_object(col=4, pos=8)
    updated_row = end_of_row._update(8)
    assert_CDAMetadata(updated_row, "Test1.tif", 2, 4, 2, 1, 1)

    # Check updated CDAMetadata object from end of img
    end_of_img = create_CDAMetadata_object(row=2, col=4, pos=8)
    updated_img = end_of_img._update(8)
    assert_CDAMetadata(updated_img, "Test1.tif", 2, 4, 1, 1, 1) # Could make this change image in update - currently in cdataml-run script.
