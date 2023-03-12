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

def round_to_even(val):
    return math.ceil(val/2.)*2

class MainWindow:
    def __init__(self, root, cdata, metadata, window_width, num_spots):
        self.root = root
        self.dataframe = cdata
        self.metadata = metadata
        self.window_width = window_width
        self.num_spots = num_spots

        # Loading current image and lesion score key into memory
        self.img_path = metadata.img
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

        self.scoring_label = tk.Label(image='')
        self.scoring_label.pack(side=tk.BOTTOM)
        self.scoring_frame.pack(anchor=tk.S, side=tk.BOTTOM, expand=True)

        # Initialise left panel to have info placed over it
        self.info_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.info_width = 30
        self.info_height = 30
        self.info_init = tk.Label(self.info_frame, text="", width=self.info_width, height=self.info_height)
        self.info_init.pack()
        self.info_frame.pack(side=tk.LEFT, expand=True)

        # Initialise central panel to have info placed over it
        self.image_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.image_height = self.resized_img_tk.height()
        self.image_width = self.resized_img_tk.width()
        self.label = tk.Label(self.image_frame, image=self.temp_img, height=self.image_height, width=self.image_width)
        self.label.pack()
        self.image_frame.pack(expand=True, side=tk.LEFT)

        # Initialise right panel to have info placed over it
        self.input_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.input_width = 30
        self.input_height = 30
        self.input_init = tk.Label(self.input_frame, text="", width=self.input_width, height=self.input_height)
        self.input_init.pack()
        self.input_frame.pack(side=tk.LEFT, expand=True)

        # Start
        if self.metadata.end_of_data == True:
            print("End of data")
            self.save_and_quit()
        elif self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
            self.scoring_to_grid(self.metadata, self.resized_key_tk)
        else:
            self.grid_to_scoring(self.metadata, self.resized_key_tk)

    def scoring_to_grid(self, metadata, key):

        # Remove previous placed objects
        if hasattr(self, "scoring_info_label"):
            self.grid_info.destroy()
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
        if hasattr(self, "grid_input_info"):
            self.img_label.destroy()
            self.grid_input_info.destroy()
            self.row_info.destroy()
            self.row_input.destroy()
            self.col_info.destroy()
            self.col_input.destroy()
            self.input_submit.destroy()

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

        # Central panel containing static image
        self.img_label = tk.Label(self.image_frame, image=self.resized_img_tk)
        self.img_label.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        # Right panel containing input boxes
        self.grid_input_info = tk.Label(self.input_frame, text="""
Enter the values below.
        """, justify=tk.CENTER, font=("Arial", 20))
        self.grid_input_info.place(x=135, y=0, anchor=tk.N)

        self.row_info = tk.Label(self.input_frame, text="""
Number of rows:
        """, justify=tk.CENTER, font=("Arial", 20))
        self.row_info.place(x=135, y=180, anchor=tk.S)

        self.row_input = tk.Entry(self.input_frame)
        self.row_input.place(x=135, y=200, anchor=tk.S)

        self.col_info = tk.Label(self.input_frame, text="""
Number of columns:
        """, justify=tk.CENTER, font=("Arial", 20))
        self.col_info.place(x=135, y=300, anchor=tk.S)

        self.col_input = tk.Entry(self.input_frame)
        self.col_input.place(x=135, y=320, anchor=tk.S)

        self.input_submit = tk.Button(self.input_frame, text="Submit", command=self.get_entry_values, font=("Arial", 20), height=2, width=6)
        self.input_submit.place(x=80, y=450, anchor=tk.S)

    # Functions relating to "grid" layout

    def get_entry_values(self):
        self.metadata.maxrow, self.metadata.maxcol = self.row_input.get(), self.col_input.get()

        if self.metadata.maxrow.isdigit() == False or self.metadata.maxcol.isdigit() == False:
            print("Please only enter integers into the row and column boxes")
            self.scoring_to_grid(self.metadata, self.resized_key_tk)
        else:
            self.metadata.maxrow, self.metadata.maxcol = int(self.metadata.maxrow), int(self.metadata.maxcol)
            #print(f"Number of rows: {self.metadata.maxrow}\nNumber of columns: {self.metadata.maxcol}")
            self.grid_to_scoring(self.metadata, self.resized_key_tk)




    def grid_to_scoring(self, metadata, key):
        # Remove previous placed objects
        if hasattr(self, "grid_input_info"):
            self.img_label.destroy()
            self.grid_input_info.destroy()
            self.row_info.destroy()
            self.row_input.destroy()
            self.col_info.destroy()
            self.col_input.destroy()
            self.input_submit.destroy()
        if hasattr(self, "scoring_info_label"):
            self.grid_info.destroy()
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

        # Check if correct image
        if not self.metadata.img == self.img_path:
            self.img_path = self.metadata.img
            self.img = Image.open(self.img_path)
            self.img_tk = ImageTk.PhotoImage(self.img)
            self.scale_factor = self.window_width/self.img.width # 500 arbitrary size - just means it fits on screen
            self.resized_img = self.img.resize((round(self.img.width*self.scale_factor), round(self.img.height*self.scale_factor)))
            self.resized_img_tk = ImageTk.PhotoImage(self.resized_img)

        # Bottom panel containing key
        self.scoring_label.config(image=key)

        # Left panel containing current CDA metadata and navigation buttons
        self.grid_info = tk.Label(self.info_frame, text=f"""
Please left-click and drag
a box around the CDA
corresponding to the
following metadata.
\nRow: {self.metadata.row}
\nCol: {self.metadata.col}
\nPos: {self.metadata.pos}
        """, width=self.info_width, justify=tk.CENTER, font=("Arial", 20))

        self.grid_info.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        self.button_prev=tk.Button(self.info_frame, text="Prev", command=self.prev_CDA, font=("Arial", 20), height=2, width=4)
        self.button_prev.place(x=0, y=0, anchor=tk.NW)

        self.button_next=tk.Button(self.info_frame, text="Next", command=lambda: self._skip_spots(num_skip=1), font=("Arial", 20), height=2, width=6)
        self.button_next.place(x=80, y=470, anchor=tk.S)

        self.button_leaf=tk.Button(self.info_frame, text="Skip Leaf", command=lambda: self._skip_spots(num_skip=self.num_spots), font=("Arial", 20), height=2, width=6)
        self.button_leaf.place(x=190, y=470, anchor=tk.S)

        # Central canvas panel for selectROI
        self.rect_start_x, self.rect_start_y = None, None
        self.rect_end_x, self.rect_end_y = None, None

        self.canvas_width = self.resized_img_tk.width()
        self.canvas_height = self.resized_img_tk.height()

        self.canvas = tk.Canvas(self.image_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.resized_img_tk)
        self.canvas.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Right panel for clicking score
        self.scoring_info_label = tk.Label(self.input_frame, text="""
Click the buttons below to
enter a score.
        """, width=self.input_width, justify=tk.CENTER, font=("Arial", 20))
        self.scoring_info_label.place(x=135, y=0, anchor=tk.N)

        self.button_0=tk.Button(self.input_frame, text="0", font=("Arial", 30), command=lambda:self.enter_score(0), height=2, width=4)
        self.button_0.place(x=135, y=170, anchor=tk.S)

        self.button_1=tk.Button(self.input_frame, text="1", font=("Arial", 30), command=lambda:self.enter_score(1), height=2, width=4)
        self.button_1.place(x=80, y=270, anchor=tk.S)

        self.button_2=tk.Button(self.input_frame, text="2", font=("Arial", 30), command=lambda:self.enter_score(2), height=2, width=4)
        self.button_2.place(x=190, y=270, anchor=tk.S)

        self.button_3=tk.Button(self.input_frame, text="3", font=("Arial", 30), command=lambda:self.enter_score(3), height=2, width=4)
        self.button_3.place(x=80, y=370, anchor=tk.S)

        self.button_4=tk.Button(self.input_frame, text="4", font=("Arial", 30), command=lambda:self.enter_score(4), height=2, width=4)
        self.button_4.place(x=190, y=370, anchor=tk.S)

        self.button_5=tk.Button(self.input_frame, text="5", font=("Arial", 30), command=lambda:self.enter_score(5), height=2, width=4)
        self.button_5.place(x=80, y=470, anchor=tk.S)

        self.button_6=tk.Button(self.input_frame, text="6", font=("Arial", 30), command=lambda:self.enter_score(6), height=2, width=4)
        self.button_6.place(x=190, y=470, anchor=tk.S)

    # Functions relating to "scoring" layout
    def _make_square_coords(self):
        '''Given a set of coordinates created by OpenCV.selectROI(), make them square by increasing smaller side to match longer'''
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

        if self.coords[1] > self.resized_img_tk.width():
            self.coords[0] = self.coords[0] - (self.coords[1] - self.resized_img_tk.width())
            self.coords[1] = self.resized_img_tk.width()

        if self.coords[2] < 0:
            self.coords[3] = self.coords[3] - self.coords[2]
            self.coords[2] = 0

        if self.coords[3] > self.resized_img_tk.height():
            self.coords[2] = selfcoords[2] - (self.coords[3] - self.resized_img_tk.height())
            self.coords[3] = self.resized_img_tk.height()

    def enter_score(self, score):
        self.metadata.score = score
        #print(f"Score entered: {self.metadata.score}")

        self.dataframe = pd.concat([self.dataframe, self.metadata._make_pandas()], ignore_index=True)

        if not self.metadata.x1 == None:
            self.metadata = self.metadata._update(8)
            if self.metadata.end_of_data == True:
                print("End of data")
                self.save_and_quit()
            elif self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
                self.scoring_to_grid(self.metadata, self.resized_key_tk)
            else:
                self.grid_to_scoring(self.metadata, self.resized_key_tk)
        else:
            print("Please select the ROI before selecting the score")
            self.grid_to_scoring(self.metadata, self.resized_key_tk)

    def on_button_press(self, event):
        self.rect_start_x, self.rect_start_y = event.x, event.y

    def on_move_press(self, event):
        if self.rect_end_x and self.rect_end_y:
            self.canvas.delete("rectangle")
        self.rect_end_x, self.rect_end_y = event.x, event.y
        self.canvas.create_rectangle(self.rect_start_x, self.rect_start_y, self.rect_end_x, self.rect_end_y, outline="red", tags="rectangle")

    def on_button_release(self, event):
        self.coords = [round_to_even(self.rect_start_x/self.scale_factor), round_to_even(self.rect_end_x/self.scale_factor), round_to_even(self.rect_start_y/self.scale_factor), round_to_even(self.rect_end_y/self.scale_factor)]

        self._make_square_coords()

        self.metadata.x1, self.metadata.x2, self.metadata.y1, self.metadata.y2 = int(self.coords[0]), int(self.coords[1]), int(self.coords[2]), int(self.coords[3])
        #print(f"Coordinates selected: {self.metadata.x1}, {self.metadata.x2}, {self.metadata.y1}, {self.metadata.y2}")
        pass

    def _skip_spots(self, num_skip):
        print("Skipping")
        # Update once
        self.metadata._update(self.num_spots)
        for skip in range(0, num_skip-1): # If num_spots == 1, do nothing, else repeat 7 more times, stopping if start of next leaf
            # Test if end of data, if so save and quit
            if self.metadata.end_of_data == True:
                self.save_and_quit()
            elif num_skip == self.num_spots:
                if self.metadata.pos == 1:
                    break
                else:
                    self.metadata._update(self.num_spots)
        if self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
            self.scoring_to_grid(self.metadata, self.resized_key_tk)
        else:
            self.grid_to_scoring(self.metadata, self.resized_key_tk)

    def prev_CDA(self):
        print("Prev CDA")
        self.metadata = cdascorer.cdametadata.CDAMetadata(self.metadata.img_files, self.dataframe)
        self.dataframe = self.dataframe[:-1]
        if self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
            self.scoring_to_grid(self.metadata, self.resized_key_tk)
        else:
            self.grid_to_scoring(self.metadata, self.resized_key_tk)

    def _save_and_quit(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
