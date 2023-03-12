'''
cdametadata.py

contains class to store metadata attributed to a particular CDA
'''

import pandas as pd

class CDAMetadata(object):
        def __init__(self, files, df):
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

        def _update(self, num_spots):
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
                            self.end_of_data = True
                        return self
            return self

        def _make_pandas(self):
            '''Turn the CDA metadata object into a pandas dataframe'''
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
