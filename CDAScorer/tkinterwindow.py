'''
tkinterwindow.py
'''
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox
import math
import pandas as pd
from importlib_resources import files
import io
import cdascorer

def _round_to_even(val: int):
    return math.ceil(val/2.)*2

class MainWindow:
    '''
    MainWindow

    A class to contain the GUI Tkinter window for CDAScorer.

    Contains three window states:
    1. Initial state defined in __init__. This contains blank objects to define the window structure.
    2. Grid state. Here the user will input the number of rows and columns of the image displayed.
    3. Scoring state. Here the user will record the coordinates and score of the CDA matching the metadata provided in the left panel.

    The Grid state only occurs if the current metadata is Row:1, Col:1, Pos:1, otherwise it is the scoring state.

    The Initial state is never seen, since objects from the Grid or Scoring states are placed on top of it.

    Each time the state changes (including updating from Scoring to Scoring), the previous objects are destroyed and new objects placed.

    '''
    def __init__(self, root, cdata, metadata, window_width: int, num_spots: int):
        '''
        MainWindow()

        Some global variables:
        :ivar root: The Tkinter root within which the objects are packed
        :ivar dataframe: The Pandas dataframe to contain the CDA metadata.
        :ivar metadata: The metadata of the current focal CDA.
        :ivar window_width: User inputted value defining the width of the image (and therefore size of the application)
        :ivar num_spots: The number of spots per leaf.
        :ivar img_path: The path of the image containing the current focal CDA.
        :ivar raw_bytes: If loading from package data, images must be loaded in a bytes format
        :ivar img: The image containing the current focal CDA in PIL format.
        :ivar img_tk: The image containing the current focal CDA in Tkinter format.
        :ivar scale_factor: The value by which the self.img width needs to be scaled to match self.window_width
        :ivar resized_img: self.img scaled up or down by self.scale_factor in PIL format
        :ivar resized_img_tk: self.resized_img in Tkinter format.
        :ivar key_bytes, key, key_tk, key_scale_factor, resized_key, resized_key_tk: Equivalent to above with img, just for scoring key.
        :ivar scoring_frame: A frame to contain or hide the scoring key, depending on the window state (bottom panel).
        :ivar scoring_width: Assigning self.scoring_frame the same width as self.resized_img_tk
        :ivar scoring_label: If image='', scoring key is hidden. If image='self.resized_key_tk', scoring key is shown.
        :ivar info_frame: A frame to contain information to direct the user (left panel).
        :ivar info_height, info_width: The height and width to assign the info_frame.
        :ivar image_frame, image_height, image_width: Equivalent to above, but for the image frame (central panel)
        :ivar input_frame, input_height, input_width: Equivalent to above, but for the input frame used to record info (right panel)


        Variables specific to the initial state:
        :ivar temp_img: An image of same size as self.img but blank (placeholder)
        :ivar info_init: A blank label of the same size as info_frame (placeholder)
        :ivar temp_img_label: A label containing the temp_image (placeholder)
        :ivar input_init: A blank label of the same size as input_frame (placeholder)

        '''

        self.root = root
        self.dataframe = cdata
        self.metadata = metadata
        self.window_width = window_width
        self.num_spots = num_spots

        # Loading current image and lesion score key into memory
        self.img_path = self.metadata.img
        if self.img_path == "test_cda_img.jpg":
            self.raw_bytes = files('cdascorer-data').joinpath(self.img_path).read_bytes()
            self.img = Image.open(io.BytesIO(self.raw_bytes))
        else:
            self.img = Image.open(self.img_path)

        self.img_tk = ImageTk.PhotoImage(self.img)
        self.scale_factor = self.window_width/self.img.width # 500 arbitrary size - just means it fits on screen
        self.resized_img = self.img.resize((round(self.img.width*self.scale_factor), round(self.img.height*self.scale_factor)))
        self.resized_img_tk = ImageTk.PhotoImage(self.resized_img)

        self.key_bytes = files('cdascorer-data').joinpath("lesion_score_key.jpg").read_bytes()
        self.key = Image.open(io.BytesIO(self.key_bytes))
        self.key_tk = ImageTk.PhotoImage(self.key)
        self.key_scale_factor = self.window_width/self.key.width
        self.resized_key = self.key.resize((round(self.key.width*self.key_scale_factor), round(self.key.height*self.key_scale_factor)))
        self.resized_key_tk = ImageTk.PhotoImage(self.resized_key)

        self.temp_img = tk.PhotoImage()

        # Initialise bottom panel to contain key
        self.scoring_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.scoring_width = self.resized_key_tk.width()

        self.scoring_label = tk.Label(self.scoring_frame, image='')
        self.scoring_label.pack(side=tk.BOTTOM)
        self.scoring_frame.pack(side=tk.BOTTOM, anchor=tk.SE, expand=True)

        # Initialise central panel to have info placed over it
        self.image_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.image_height = self.resized_img_tk.height()
        self.image_width = self.resized_img_tk.width()
        self.temp_img_label = tk.Label(self.image_frame, image=self.temp_img, height=self.image_height, width=self.image_width)
        self.temp_img_label.pack()
        self.image_frame.pack(side=tk.RIGHT, anchor=tk.NE, expand=True)

        # Initialise left panel to have info placed over it
        self.info_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.info_width = 30
        self.info_height = 20
        self.info_init = tk.Label(self.info_frame, text="", width=self.info_width, height=self.info_height)
        self.info_init.pack()
        self.info_frame.pack(side=tk.TOP, anchor=tk.NW, expand=True)

        # Initialise right panel to have info placed over it
        self.input_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.input_width = 30
        self.input_height = 20
        self.input_init = tk.Label(self.input_frame, text="", width=self.input_width, height=self.input_height)
        self.input_init.pack()
        self.input_frame.pack(side=tk.TOP, anchor=tk.NW, expand=True)

        for score in range(0, 7):
            self.root.bind(score, lambda event, score=score: self._enter_score(score))

        # Load the first state
        if self.metadata.end_of_data == True:
            print("End of data")
            self._save_and_quit()
        elif self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
            self._scoring_to_grid()
        else:
            self._grid_to_scoring()


    def _scoring_to_grid(self):
        '''
        MainWindow._scoring_to_grid()

        The Grid state, which allows the user to input the number of rows and columns of the current image.

        Variables specific to the Grid state:
        :ivar img_label: Label to contain the self.img. Placed over self.temp_img_label.
        :ivar grid_input_info: Label containing directions for Grid state. Placed over self.info_init.
        :ivar row_info: Label for row entry box. Placed over self.input_init.
        :ivar row_input: Entry box for row count. Placed over self.input_init.
        :ivar col_info, col_input: Label and entry box for column. Placed over self.input_init.
        :ivar input_submit: Button to submit contents of self.row_input and self.col_input. Input must be digit.

        '''

        # Remove previous placed objects
        if hasattr(self, "scoring_info_label"):
            self.coords_info_label.destroy()
            self.button_prev.destroy()
            self.button_next.destroy()
            self.button_leaf.destroy()
            self.scoring_info_label.destroy()
            self.button_0.destroy()
            self.button_1.destroy()
            self.button_2.destroy()
            self.button_3.destroy()
            self.button_4.destroy()
            self.button_5.destroy()
            self.button_6.destroy()
            self.canvas.destroy()
            self.button_exit.destroy()
        if hasattr(self, "row_info"):
            self.img_label.destroy()
            #self.grid_input_info.destroy()
            self.row_info.destroy()
            self.row_input.destroy()
            self.col_info.destroy()
            self.col_input.destroy()
            self.input_submit.destroy()
            self.button_exit.destroy()

        # If metadata.img has been updated, load the new images.
        if self.metadata.end_of_data == True:
            print("End of data")
            self.root.quit()

        if not self.metadata.img == self.img_path:
            self.img_path = self.metadata.img
            self.img = Image.open(self.img_path)
            self.img_tk = ImageTk.PhotoImage(self.img)
            self.scale_factor = self.window_width/self.img.width # 500 arbitrary size - just means it fits on screen
            self.resized_img = self.img.resize((round(self.img.width*self.scale_factor), round(self.img.height*self.scale_factor)))
            self.resized_img_tk = ImageTk.PhotoImage(self.resized_img)

        # Bottom panel containing (or not containing) key
        self.scoring_label.config(image='')

        # Left panel containing info
        self.scoring_info = tk.Label(self.info_frame, text="""
Please enter the number
of rows and columns in
this image.
        """, width=self.info_width, justify=tk.CENTER, font=("Arial", 20))

        self.scoring_info.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        self.button_exit=tk.Button(self.info_frame, text="Exit", command=self._save_and_quit, font=("Arial", 20), height=1, width=4)
        self.button_exit.place(x=0, y=0, anchor=tk.NW)

        # Central panel containing static image
        self.img_label = tk.Label(self.image_frame, image=self.resized_img_tk)
        self.img_label.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        # Right panel containing input boxes
#        self.grid_input_info = tk.Label(self.input_frame, text="""
#Enter the row and column
#counts below.
#        """, justify=tk.CENTER, font=("Arial", 20))
#        self.grid_input_info.place(x=135, y=0, anchor=tk.N)

        self.row_info = tk.Label(self.input_frame, text="""
Number of rows:
        """, justify=tk.CENTER, font=("Arial", 20), height=1)
        self.row_info.place(x=135, y=60, anchor=tk.S)

        self.row_input = tk.Entry(self.input_frame)
        self.row_input.place(x=135, y=110, anchor=tk.S)

        self.col_info = tk.Label(self.input_frame, text="""
Number of columns:
        """, justify=tk.CENTER, font=("Arial", 20), height=1)
        self.col_info.place(x=135, y=180, anchor=tk.S)

        self.col_input = tk.Entry(self.input_frame)
        self.col_input.place(x=135, y=230, anchor=tk.S)

        self.input_submit = tk.Button(self.input_frame, text="Submit", command=self._get_entry_values, font=("Arial", 20), height=1, width=4)
        self.input_submit.place(x=80, y=300, anchor=tk.S)

    # Functions relating to "Grid" layout

    def _get_entry_values(self):
        '''
        MainWindow._get_entry_values()

        Updates metadata maxrow and maxcol values with input from self.row_input and self.col_input when submit button pressed.

        If the values entered are not digits, rejects and reloads window.

        '''

        self.metadata.maxrow, self.metadata.maxcol = self.row_input.get(), self.col_input.get()

        if self.metadata.maxrow.isdigit() == False or self.metadata.maxcol.isdigit() == False:
            print("Please only enter integers into the row and column boxes")
            self._scoring_to_grid()
        else:
            self.metadata.maxrow, self.metadata.maxcol = int(self.metadata.maxrow), int(self.metadata.maxcol)
            #print(f"Number of rows: {self.metadata.maxrow}\nNumber of columns: {self.metadata.maxcol}")
            self._grid_to_scoring()




    def _grid_to_scoring(self):
        '''
        MainWindow._grid_to_scoring()

        The Scoring state, which allows the user to record the bounding box and score of the focal CDA.

        Variables specific to the Scoring state:
        :ivar canvas: Canvas containing img.self. Users can left-click and drag to draw bounding box. Placed over self.temp_img_label.
        :ivar coords_info_label: Label containing directions for recording coordinate data for the focal CDA. Placed over self.info_init.
        :ivar scoring_info_label: Label containing directions for recording score data for the focal CDA. Placed over self.input_init.
        :ivar button_prev: Button to return to the previous image metadata recorded, allowing it to be overwritten. Placed over self.info_init.
        :ivar button_next: Button to skip current focal CDA. Placed over self.info_init.
        :ivar button_leaf: Button to skip to Pos=1 of next leaf. Placed over self.info_init.
        :ivar button_0, button_1, button_2, button_3, button_4, button_5, button_6: Button to record score for focal CDA. Placed over self.input_init.

        '''

        # Remove previous placed objects
        if hasattr(self, "row_info"):
            self.img_label.destroy()
            #self.grid_input_info.destroy()
            self.row_info.destroy()
            self.row_input.destroy()
            self.col_info.destroy()
            self.col_input.destroy()
            self.input_submit.destroy()
            self.button_exit.destroy()
        if hasattr(self, "scoring_info_label"):
            self.coords_info_label.destroy()
            self.button_prev.destroy()
            self.button_next.destroy()
            self.button_leaf.destroy()
            self.scoring_info_label.destroy()
            self.button_0.destroy()
            self.button_1.destroy()
            self.button_2.destroy()
            self.button_3.destroy()
            self.button_4.destroy()
            self.button_5.destroy()
            self.button_6.destroy()
            self.canvas.destroy()
            self.button_exit.destroy()

        # Check if correct image
        if not self.metadata.img == self.img_path:
            self.img_path = self.metadata.img
            self.img = Image.open(self.img_path)
            self.img_tk = ImageTk.PhotoImage(self.img)
            self.scale_factor = self.window_width/self.img.width # 500 arbitrary size - just means it fits on screen
            self.resized_img = self.img.resize((round(self.img.width*self.scale_factor), round(self.img.height*self.scale_factor)))
            self.resized_img_tk = ImageTk.PhotoImage(self.resized_img)

        # Bottom panel containing key
        self.scoring_label.config(image=self.resized_key_tk)

        # Left panel containing current CDA metadata and navigation buttons
        self.coords_info_label = tk.Label(self.info_frame, text=f"""
STEP 1:
Left-click and drag
a box around the
following CDA:
\nRow: {self.metadata.row}
\nColumn: {self.metadata.col}
\nPosition: {self.metadata.pos}
        """, width=self.info_width, justify=tk.CENTER, font=("Arial", 20))

        self.coords_info_label.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        self.button_prev=tk.Button(self.info_frame, text="Prev", command=self._prev_CDA, font=("Arial", 20), height=1, width=4)
        self.button_prev.place(x=42, y=320, anchor=tk.S)

        self.button_next=tk.Button(self.info_frame, text="Next", command=lambda: self._skip_spots(num_skip=1), font=("Arial", 20), height=1, width=4)
        self.button_next.place(x=125, y=320, anchor=tk.S)

        self.button_leaf=tk.Button(self.info_frame, text="Skip Leaf", command=lambda: self._skip_spots(num_skip=self.num_spots), font=("Arial", 20), height=1, width=6)
        self.button_leaf.place(x=220, y=320, anchor=tk.S)

        self.button_exit=tk.Button(self.info_frame, text="Exit", command=self._save_and_quit, font=("Arial", 20), height=1, width=4)
        self.button_exit.place(x=0, y=0, anchor=tk.NW)

        # Central canvas panel for selectROI
        self.rect_start_x, self.rect_start_y = None, None
        self.rect_end_x, self.rect_end_y = None, None

        self.canvas_width = self.resized_img_tk.width()
        self.canvas_height = self.resized_img_tk.height()

        self.canvas = tk.Canvas(self.image_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.resized_img_tk)
        self.canvas.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

        # Right panel for clicking score
        self.scoring_info_label = tk.Label(self.input_frame, text="""
STEP 2:
Enter a score below.
        """, width=self.input_width, justify=tk.CENTER, font=("Arial", 20))
        self.scoring_info_label.place(x=135, y=0, anchor=tk.N)

        self.button_0=tk.Button(self.input_frame, text="0", font=("Arial", 30), command=lambda:self._enter_score(0), height=1, width=2)
        self.button_0.place(x=135, y=140, anchor=tk.S)

        self.button_1=tk.Button(self.input_frame, text="1", font=("Arial", 30), command=lambda:self._enter_score(1), height=1, width=2)
        self.button_1.place(x=95, y=190, anchor=tk.S)

        self.button_2=tk.Button(self.input_frame, text="2", font=("Arial", 30), command=lambda:self._enter_score(2), height=1, width=2)
        self.button_2.place(x=175, y=190, anchor=tk.S)

        self.button_3=tk.Button(self.input_frame, text="3", font=("Arial", 30), command=lambda:self._enter_score(3), height=1, width=2)
        self.button_3.place(x=95, y=240, anchor=tk.S)

        self.button_4=tk.Button(self.input_frame, text="4", font=("Arial", 30), command=lambda:self._enter_score(4), height=1, width=2)
        self.button_4.place(x=175, y=240, anchor=tk.S)

        self.button_5=tk.Button(self.input_frame, text="5", font=("Arial", 30), command=lambda:self._enter_score(5), height=1, width=2)
        self.button_5.place(x=95, y=290, anchor=tk.S)

        self.button_6=tk.Button(self.input_frame, text="6", font=("Arial", 30), command=lambda:self._enter_score(6), height=1, width=2)
        self.button_6.place(x=175, y=290, anchor=tk.S)

    # Functions relating to "Scoring" layout
    def _on_button_press(self, event):
        '''
        MainWindow._on_button_press()

        When the user left-clicks on the image canvas, record the starting coordinates.

        :ivar rect_start_x, rect_start_y: The starting x and y coordinate values (will become x1 and y1 after scaling and make_square_coords()).

        '''

        self.rect_start_x, self.rect_start_y = event.x, event.y

    def _on_move_press(self, event):
        '''
        MainWindow._on_move_press()

        When the user drags the mouse whilst still holding the left mouse button, store the ending coordinates.

        :ivar rect_end_x, rect_end_y: The end x and y coordinate values (will become x2 and y2 after scaling and make_square_coords()).

        '''

        if self.rect_end_x and self.rect_end_y:
            self.canvas.delete("rectangle")
        self.rect_end_x, self.rect_end_y = event.x, event.y
        self.canvas.create_rectangle(self.rect_start_x, self.rect_start_y, self.rect_end_x, self.rect_end_y, outline="red", tags="rectangle")

    def _on_button_release(self, event):
        '''
        MainWindow._on_button_release()

        When the user releases the left mouse button, store the coordinates, scale them, and make the selection square.

        :ivar coords: A list to contain the four scaled, square selection coordinates.
        '''
        if not (self.rect_end_x == None and self.rect_end_y == None):
            self.coords = [_round_to_even(self.rect_start_x/self.scale_factor), _round_to_even(self.rect_end_x/self.scale_factor), _round_to_even(self.rect_start_y/self.scale_factor), _round_to_even(self.rect_end_y/self.scale_factor)]

            self._make_square_coords()

            self.metadata.x1, self.metadata.x2, self.metadata.y1, self.metadata.y2 = int(self.coords[0]), int(self.coords[1]), int(self.coords[2]), int(self.coords[3])
        #print(f"Coordinates selected: {self.metadata.x1}, {self.metadata.x2}, {self.metadata.y1}, {self.metadata.y2}")

    def _make_square_coords(self):
        '''
        MainWindow._make_square_coords()

        Given a set of coordinates collected on self.canvas, make them square.
        This is done by increasing the length of the smaller side to match the larger, adding half the difference to each coordinate.

        '''

        hlen = self.coords[1] - self.coords[0] # Horizontal length
        vlen = self.coords[3] - self.coords[2] # Vertical length
        diff = abs(hlen-vlen) # Difference
        # Add half the difference between them to the greater of the shorter axis
        # Subtract half the difference between them to the lesser of the shorter axis
        if hlen == max(hlen, vlen): # If wider than tall
            self.coords[3] = self.coords[3] + (diff / 2)
            self.coords[2] = self.coords[2] - (diff / 2)
        else: # If taller than wide
            self.coords[1] = self.coords[1] + (diff / 2)
            self.coords[0] = self.coords[0] - (diff / 2)

        # Dealing with values outside of the image
        # Image boundaries = [0, raw_img.shape[1], 0, raw_img.shape[0]]
        if self.coords[0] < 0:
            self.coords[1] = self.coords[1] - self.coords[0]
            self.coords[0] = 0

        if self.coords[1] > self.img_tk.width():
            self.coords[0] = self.coords[0] - (self.coords[1] - self.img_tk.width())
            self.coords[1] = self.img_tk.width()

        if self.coords[2] < 0:
            self.coords[3] = self.coords[3] - self.coords[2]
            self.coords[2] = 0

        if self.coords[3] > self.img_tk.height():
            self.coords[2] = self.coords[2] - (self.coords[3] - self.img_tk.height())
            self.coords[3] = self.img_tk.height()

    def _enter_score(self, score: int):
        '''
        MainWindow._enter_score()

        When a score button or key is pressed by the user, record the score.
        If no coordinates have been selected, reject and reload window.

        Then, update the metadata and then the window state accordingly.

        '''
        if not (self.metadata.maxrow == None or self.metadata.maxcol == None):
            if not self.metadata.x1 == None:
                self.metadata.score = score
                #print(f"Score entered: {self.metadata.score}")
                self.dataframe = pd.concat([self.dataframe, self.metadata._make_pandas()], ignore_index=True)
                self.metadata = self.metadata._update(8)
                if self.metadata.end_of_data == True:
                    self._save_and_quit()
                elif self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
                    self._scoring_to_grid()
                else:
                    self._grid_to_scoring()
            else:
                if hasattr(self, "scoring_info_label"):
                    print("Please select the ROI before selecting the score")

    def _skip_spots(self, num_skip: int):
        '''
        MainWindow._skip_spots()

        When "Next" or "Skip Leaf" buttons pressed, update the metadata until the condition is met.
        Then, update the window state accordingly.

        :cvar num_skips: If 1, just move to next CDA. If self.num_spots, move to start of next leaf.

        '''

        print("Skipping")
        # Update once
        self.metadata._update(self.num_spots)
        if self.metadata.end_of_data == True:
            self._save_and_quit()
        for skip in range(0, num_skip-1): # If num_spots == 1, do nothing, else repeat 7 more times, stopping if start of next leaf
            # Test if end of data, if so save and quit
            if self.metadata.end_of_data == True:
                self._save_and_quit()
            elif num_skip == self.num_spots:
                if self.metadata.pos == 1:
                    break
                else:
                    self.metadata._update(self.num_spots)
                    if self.metadata.end_of_data == True:
                        self._save_and_quit()
        try:
            if self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
                self._scoring_to_grid()
            else:
                self._grid_to_scoring()
        except:
            pass

    def _prev_CDA(self):
        '''
        MainWindow._prev_CDA()

        Go to the previous stored metadata and overwrite it.

        '''

        print("Removing previous CDA metadata record. Please input new metadata.")
        self.metadata = cdascorer.cdametadata.CDAMetadata(self.metadata.img_files, self.dataframe)
        self.dataframe = self.dataframe[:-1]
        if self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
            self._scoring_to_grid()
        else:
            self._grid_to_scoring()

    def _save_and_quit(self):
        '''
        MainWindow._save_and_quit()

        If user quits or end of data reached, quit, then destroy the window.

        '''

        self.root.destroy()
