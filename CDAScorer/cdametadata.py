import pandas as pd

class CDAMetadata(object):
        '''
        CDAMetadata

        A class to contain the metadata associated with a single cell death area (CDA)

        :ivar img: The filepath of the image containing the CDA.
        :ivar maxrow: Assuming leaves in grid pattern. Total number of rows in grid.
        :ivar maxcol: Assuming leaves in grid pattern. Total number of columns in grid.
        :ivar row: The grid row containing the CDA.
        :ivar col: The grid column containing the CDA.
        :ivar pos: The position of of the CDA on the leaf. Starts top left of central vein and continues anti-clockwise.
        :ivar score: The score (0-6) attributed to the CDA.
        :cvar last_row: The final row of the existing CDA dataframe df.
        :ivar x1: The pixel position in the raw image of the left bound of the CDA image subset.
        :ivar x2: The pixel position in the raw image of the right bound of the CDA image subset.
        :ivar y1: The pixel position in the raw image of the upper bound of the CDA image subset.
        :ivar y2: The pixel position in the raw image of the lower bound of the CDA image subset.
        :ivar img_files: A list of all images in the folder given by the user.
        :ivar end_of_data: A boolean which becomes true if the CDA is the last CDA of the last image.

        '''

        def __init__(self, files, df):
            '''
            CDAMetadata()

            If the metadata dataframe (df) is empty, initialise CDAMetadata.
            Otherwise, use the values from the last row of df as the initial values.

            '''
            if len(df) == 0:
                self.img = files[0]
                self.maxrow = None
                self.maxcol = None
                self.row = 1
                self.col = 1
                self.pos = 1
                self.score = None
            else:
                last_row = df.iloc[-1]
                self.img = last_row[0]
                self.maxrow = last_row[1]
                self.maxcol = last_row[2]
                self.row = last_row[3]
                self.col = last_row[4]
                self.pos = last_row[5]
                self.score = last_row[6]
            self.x1 = None
            self.x2 = None
            self.y1 = None
            self.y2 = None
            self.img_files = files
            self.end_of_data = False

        def __str__(self):
            '''
            print(CDAMetadata)

            Prints the instance variables that will be appended to the metadata dataframe.

            '''

            return f"""----------
CURRENT METADATA:
            Img: {self.img}
            Maxrow: {self.maxrow}
            Maxcol: {self.maxcol}
            Row: {self.row}
            Col: {self.col}
            Pos: {self.pos}
            Score: {self.score}
            x1: {self.x1}
            x2: {self.x2}
            y1: {self.y1}
            y2: {self.y2}
----------
            """

        def _update(self, num_spots: int):
            '''
            CDAMetadata._update()

            Update the CDAMetadata object with the metadata of the next CDA.

            If end of leaf, move to next col.
            If end of col, move to next row.
            If end of row, move to next img.
            If end of dataset, end_of_data tag = True (program exits)

            '''
            # Check if there are any spots left on the leaf
            if not self.pos == num_spots:
                self.pos += 1
            else:
                self.pos = 1
                # Check if there are any leaves left in the row
                if not self.col == self.maxcol:
                    self.col += 1
                else:
                    self.col = 1
                    # Check if there are any columns left in the image
                    if not self.row == self.maxrow:
                        self.row += 1
                    else:
                        # Check if there are any images left
                        if not self.img == self.img_files[-1]:
                            self.img = self.img_files[self.img_files.index(self.img)+1]
                            self.pos = 1
                            self.row = 1
                            self.col = 1
                        else:
                            print("End of Data Reached")
                            self.end_of_data = True
            self.score, self.x1, self.x2, self.y1, self.y2 = None, None, None, None, None
            return self

        def _make_pandas(self):
            '''
            CDAMetadata._make_pandas()

            Turn the CDAMetadata object into a pandas dataframe.
            This can be appended to the dataframe df.

            '''
            data = {'img': self.img,
            'maxrow': self.maxrow,
            'maxcol': self.maxcol,
            'row': self.row,
            'col': self.col,
            'pos': self.pos,
            'score': self.score,
            'x1': self.x1,
            'x2': self.x2,
            'y1': self.y1,
            'y2': self.y2}
            series = pd.Series(data=data, index=["img", "maxrow", "maxcol", "row", "col", "pos", "score", "x1", "x2", "y1", "y2"])
            return series.to_frame().T
