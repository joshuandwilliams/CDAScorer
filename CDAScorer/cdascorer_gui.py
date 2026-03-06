"""
cdascorer_gui.py

Tkinter GUI for the CDAScorer annotation workflow.
"""
import math
import pandas as pd
import io

import tkinter as tk
from PIL import ImageTk, Image

from importlib.resources import files

from cdascorer.cdametadata import CDAMetadata


def _scale_val(val: int, scale: float) -> int:
    """Scale a value by a factor (used for font sizes and widget dimensions)."""
    return int(math.floor(val * scale * 0.75))


def _round_to_even(val: float) -> int:
    """Round a value up to the nearest even integer."""
    return int(math.ceil(val / 2.0) * 2)


class MainWindow:
    """
    MainWindow

    A class to contain the GUI Tkinter window for CDAScorer.

    Contains three window states:
    1. Initial state defined in __init__. This contains blank objects to define the window structure.
    2. Grid state. Here the user will input the number of rows and columns of the image displayed.
    3. Scoring state. Here the user will record the coordinates and score of the CDA matching
       the metadata provided in the left panel.

    The Grid state only occurs if the current metadata is Row:1, Col:1, Pos:1, otherwise
    it is the scoring state.

    The Initial state is never seen, since objects from the Grid or Scoring states are placed
    on top of it.

    Each time the state changes (including updating from Scoring to Scoring), the previous
    objects are destroyed and new objects placed.
    """

    # Names of widgets created in the grid state
    _GRID_WIDGETS = [
        "img_label", "scoring_info", "row_info", "row_input",
        "col_info", "col_input", "count_info", "count_input",
        "input_submit", "button_exit",
    ]

    # Names of widgets created in the scoring state
    _SCORING_WIDGETS = [
        "coords_info_label", "scoring_info_label", "canvas",
        "button_prev", "button_next", "button_leaf", "button_exit",
        "button_0", "button_1", "button_2", "button_3",
        "button_4", "button_5", "button_6",
    ]

    def __init__(self, root, cdata, metadata, window_width: int, window_height: int):
        """
        Initialise the MainWindow.

        :param root: The Tkinter root within which the objects are packed.
        :param cdata: The Pandas dataframe to contain the CDA metadata.
        :param metadata: The metadata of the current focal CDA.
        :param window_width: The width of the screen in pixels.
        :param window_height: The height of the screen in pixels.
        """

        # Window parameters
        self.root = root
        self.dataframe = cdata
        self.metadata = metadata
        self.window_width = window_width
        self.window_height = window_height

        # What percentage of the window should be covered by the image
        self.window_cover = 0.65

        # Scale for text
        self.scale = self.window_width / 2500

        # Determines when 0-6 scores can be inputted by keyboard
        self.allow_scorekeypress = False

        # Number of spots per leaf (set during grid entry)
        self.num_spots = None

        # Loading current image and lesion score key into memory
        self.img_path = self.metadata.img
        if self.img_path == "test_cda_img.jpg":
            raw_bytes = files('cdascorer.data').joinpath(self.img_path).read_bytes()
            self.img = Image.open(io.BytesIO(raw_bytes))
        else:
            self.img = Image.open(self.img_path)
        self.img_tk = ImageTk.PhotoImage(self.img)

        # Scale image size so that it always fits inside the screen
        self._scale_image()

        # Load in the scoring key from the package files and scale it to the width of the image
        key_bytes = files('cdascorer.data').joinpath("lesion_score_key.jpg").read_bytes()
        self.key = Image.open(io.BytesIO(key_bytes), formats=["JPEG"])
        self.key_tk = ImageTk.PhotoImage(self.key)
        self._scale_key()
        self.temp_img = tk.PhotoImage()

        # Initialise right panel to contain image and key
        self.right_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        self.scoring_label = tk.Label(self.right_frame, image='', highlightthickness=0)
        self.scoring_label.pack(side=tk.BOTTOM)
        self.image_height = self.resized_img_tk.height()
        self.image_width = self.resized_img_tk.width()
        self.temp_img_label = tk.Label(
            self.right_frame, image=self.temp_img,
            height=self.image_height, width=self.image_width,
        )
        self.temp_img_label.pack(side=tk.BOTTOM)
        self.right_frame.pack(side=tk.RIGHT, anchor=tk.W, expand=True)
        self.root.update()

        # Initialise left panel to have info placed over it
        self.left_frame = tk.Frame(
            self.root,
            width=_scale_val(500, self.scale),
            height=self.right_frame.winfo_height(),
            bd=2, relief=tk.GROOVE,
        )
        self.left_frame.pack_propagate(0)
        self.left_width = self.left_frame.winfo_width()
        self.left_height = self.left_frame.winfo_height()
        self.left_init = tk.Label(self.left_frame, text="", width=self.left_width, height=self.left_height)
        self.left_init.pack()
        self.left_frame.pack(side=tk.RIGHT, anchor=tk.E, expand=True)

        # Whenever number keys 0 to 6 are pressed, count as entering score
        for score in range(0, 7):
            self.root.bind(str(score), lambda event, s=score: self._enter_score(s))

        # Load the grid state (checking whether previous image was completed or not)
        if self.metadata.end_of_data:
            print("End of data")
            self._save_and_quit()
        else:
            self._scoring_to_grid()

    # ──────────────────────────────────────────────
    # Image scaling helpers
    # ──────────────────────────────────────────────

    def _scale_image(self):
        """Scale the current image to fit within the window."""
        width_ratio = self.img.width / self.window_width
        height_ratio = self.img.height / self.window_height
        if width_ratio > height_ratio:
            self.img_scale = (self.window_width / self.img.width) * self.window_cover
        else:
            self.img_scale = (self.window_height / self.img.height) * self.window_cover
        self.resized_img = self.img.resize((
            round(self.img.width * self.img_scale),
            round(self.img.height * self.img_scale),
        ))
        self.resized_img_tk = ImageTk.PhotoImage(self.resized_img)

    def _scale_key(self):
        """Scale the scoring key image to match the width of the current image."""
        self.key_scale = self.resized_img.width / self.key.width
        self.resized_key = self.key.resize((
            round(self.key.width * self.key_scale),
            round(self.key.height * self.key_scale),
        ))
        self.resized_key_tk = ImageTk.PhotoImage(self.resized_key)

    def _load_new_image_if_needed(self):
        """If metadata points to a different image, load and scale it."""
        if self.metadata.img != self.img_path:
            self.img_path = self.metadata.img
            self.img = Image.open(self.img_path)
            self.img_tk = ImageTk.PhotoImage(self.img)
            self._scale_image()
            self._scale_key()
            self.temp_img_label.config(
                width=round(self.img.width * self.img_scale),
                height=round(self.img.height * self.img_scale),
            )

    # ──────────────────────────────────────────────
    # Widget cleanup
    # ──────────────────────────────────────────────

    def _clear_state_widgets(self):
        """Destroy all widgets belonging to the current grid or scoring state."""
        for name in self._SCORING_WIDGETS + self._GRID_WIDGETS:
            widget = getattr(self, name, None)
            if widget is not None:
                try:
                    widget.destroy()
                except tk.TclError:
                    pass  # Already destroyed
                setattr(self, name, None)

    # ──────────────────────────────────────────────
    # State: Grid (enter rows, cols, num spots)
    # ──────────────────────────────────────────────

    def _scoring_to_grid(self):
        """
        The Grid state, which allows the user to input the number of rows
        and columns of the current image.
        """
        self._clear_state_widgets()
        self.allow_scorekeypress = False

        if self.metadata.end_of_data:
            print("End of data")
            self.root.quit()
            return

        self._load_new_image_if_needed()

        # Right frame — image label containing current image
        self.img_label = tk.Label(self.right_frame, image=self.resized_img_tk)
        self.img_label.place(x=0, y=0, anchor=tk.NW, relwidth=1.0, relheight=1.0)
        self.root.update()
        # Hide scoring key in grid state
        self.scoring_label.config(image='')

        # Left frame
        self.root.update()
        self.left_frame.config(height=self.right_frame.winfo_height())

        font = ("Arial", _scale_val(30, self.scale))

        self.scoring_info = tk.Label(
            self.left_frame, width=self.left_width, font=font,
            text="\nPlease enter the number\nof rows and columns in\nthis image.\n",
        )
        self.scoring_info.place(relx=0.5, rely=0.05, anchor=tk.N, relwidth=1.0)

        self.button_exit = tk.Button(
            self.left_frame, text="Save and Exit",
            command=self._save_and_quit, font=font,
        )
        self.button_exit.place(relx=0, rely=0, anchor=tk.NW)

        self.row_info = tk.Label(
            self.left_frame, text="\nNumber of rows:\n",
            justify=tk.CENTER, font=font, height=1,
        )
        self.row_info.place(relx=0.5, rely=0.3, anchor=tk.S)

        self.row_input = tk.Entry(self.left_frame, font=font)
        self.row_input.place(relx=0.5, rely=0.4, anchor=tk.S, relwidth=0.5)

        self.col_info = tk.Label(
            self.left_frame, text="\nNumber of columns:\n",
            justify=tk.CENTER, font=font, height=1,
        )
        self.col_info.place(relx=0.5, rely=0.5, anchor=tk.S)

        self.col_input = tk.Entry(self.left_frame, font=font)
        self.col_input.place(relx=0.5, rely=0.6, anchor=tk.S, relwidth=0.5)

        self.count_info = tk.Label(
            self.left_frame, text="\nNumber of CDAs per leaf:\n",
            justify=tk.CENTER, font=font, height=1,
        )
        self.count_info.place(relx=0.5, rely=0.7, anchor=tk.S)

        self.count_input = tk.Entry(self.left_frame, font=font)
        self.count_input.place(relx=0.5, rely=0.8, anchor=tk.S)

        self.input_submit = tk.Button(
            self.left_frame, text="Submit",
            command=self._get_entry_values, font=font,
        )
        self.input_submit.place(relx=0.5, rely=0.9, anchor=tk.S)

    # ──────────────────────────────────────────────
    # Grid state: submission handler
    # ──────────────────────────────────────────────

    def _get_entry_values(self):
        """
        Updates metadata maxrow and maxcol values with input from entry boxes.
        If the values entered are not digits, rejects and reloads window.
        """
        maxrow_str = self.row_input.get()
        maxcol_str = self.col_input.get()
        num_spots_str = self.count_input.get()

        if not maxrow_str.isdigit() or not maxcol_str.isdigit() or not num_spots_str.isdigit():
            print("Please only enter integers into the entry boxes")
            self._scoring_to_grid()
            return

        self.metadata.maxrow = int(maxrow_str)
        self.metadata.maxcol = int(maxcol_str)
        self.num_spots = int(num_spots_str)

        if self.metadata.score is not None:
            # Resuming from a previous session — this CDA was already scored,
            # so advance to the next one.
            self.metadata._update(self.num_spots)
            self._route_to_state()
        else:
            self._grid_to_scoring()

    # ──────────────────────────────────────────────
    # State: Scoring (draw bounding box, enter score)
    # ──────────────────────────────────────────────

    def _grid_to_scoring(self):
        """
        The Scoring state, which allows the user to record the bounding box
        and score of the focal CDA.
        """
        self._clear_state_widgets()
        self._load_new_image_if_needed()
        self.allow_scorekeypress = True

        # Initialise bounding box coordinates
        self.rect_start_x, self.rect_start_y = None, None
        self.rect_end_x, self.rect_end_y = None, None

        # Canvas containing image
        self.canvas = tk.Canvas(
            self.right_frame,
            width=self.resized_img_tk.width(),
            height=self.resized_img_tk.height(),
            highlightthickness=0, bg="white",
        )
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.resized_img_tk)
        self.canvas.place(x=2, y=2, anchor=tk.NW)
        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

        # Display scoring key
        self.scoring_label.config(image=self.resized_key_tk)

        # Left frame
        self.root.update()
        self.left_frame.config(height=self.right_frame.winfo_height())

        font = ("Arial", _scale_val(30, self.scale))
        font_large = ("Arial", _scale_val(40, self.scale))

        self.coords_info_label = tk.Label(
            self.left_frame, highlightthickness=0,
            width=self.left_width, font=font,
            text=(
                f"\nSTEP 1:\nLeft-click and drag\na box around the\nfollowing CDA:"
                f"\n\nRow: {self.metadata.row}"
                f"\n\nColumn: {self.metadata.col}"
                f"\n\nPosition: {self.metadata.pos}\n"
            ),
        )
        self.coords_info_label.place(relx=0.5, rely=0.05, anchor=tk.N, relwidth=1.0)

        self.button_prev = tk.Button(
            self.left_frame, text="Prev",
            command=self._prev_CDA, font=font,
        )
        self.button_prev.place(relx=1, rely=1, anchor=tk.SE)

        self.button_next = tk.Button(
            self.left_frame, text="Next",
            command=lambda: self._skip_spots(num_skip=1), font=font,
        )
        self.button_next.place(relx=0, rely=1, anchor=tk.SW)

        self.button_leaf = tk.Button(
            self.left_frame, text="Skip Leaf",
            command=lambda: self._skip_spots(num_skip=self.num_spots), font=font,
        )
        self.button_leaf.place(relx=0.5, rely=1, anchor=tk.S)

        self.button_exit = tk.Button(
            self.left_frame, text="Save and Exit",
            command=self._save_and_quit, font=font,
        )
        self.button_exit.place(relx=0, rely=0, anchor=tk.NW)

        self.scoring_info_label = tk.Label(
            self.left_frame, width=self.left_width,
            justify=tk.CENTER, font=font,
            text="\nSTEP 2:\nEnter a score below.\n",
        )
        self.scoring_info_label.place(relx=0.5, rely=0.55, anchor=tk.S, relwidth=1.0)

        # Score buttons
        score_positions = [
            (0, 0.5, 0.60),
            (1, 0.35, 0.70), (2, 0.65, 0.70),
            (3, 0.35, 0.80), (4, 0.65, 0.80),
            (5, 0.35, 0.90), (6, 0.65, 0.90),
        ]
        for score_val, rx, ry in score_positions:
            btn = tk.Button(
                self.left_frame, text=str(score_val), font=font_large,
                command=lambda s=score_val: self._enter_score(s),
            )
            btn.place(relx=rx, rely=ry, anchor=tk.S)
            setattr(self, f"button_{score_val}", btn)

    # ──────────────────────────────────────────────
    # Scoring state: mouse event handlers
    # ──────────────────────────────────────────────

    def _on_button_press(self, event):
        """Record starting coordinates when the user clicks on the canvas."""
        self.rect_start_x, self.rect_start_y = event.x, event.y

    def _on_move_press(self, event):
        """Update the rectangle as the user drags the mouse."""
        if self.rect_end_x is not None and self.rect_end_y is not None:
            self.canvas.delete("rectangle")
        self.rect_end_x, self.rect_end_y = event.x, event.y
        self.canvas.create_rectangle(
            self.rect_start_x, self.rect_start_y,
            self.rect_end_x, self.rect_end_y,
            outline="red", tags="rectangle",
        )

    def _on_button_release(self, event):
        """When the mouse is released, scale coordinates and make the selection square."""
        if self.rect_end_x is not None and self.rect_end_y is not None:
            self.coords = [
                min(_round_to_even(self.rect_start_x / self.img_scale), _round_to_even(self.rect_end_x / self.img_scale)),
                max(_round_to_even(self.rect_start_x / self.img_scale), _round_to_even(self.rect_end_x / self.img_scale)),
                min(_round_to_even(self.rect_start_y / self.img_scale), _round_to_even(self.rect_end_y / self.img_scale)),
                max(_round_to_even(self.rect_start_y / self.img_scale), _round_to_even(self.rect_end_y / self.img_scale)),
            ]
            self._make_square_coords()
            self.metadata.x1 = int(self.coords[0])
            self.metadata.x2 = int(self.coords[1])
            self.metadata.y1 = int(self.coords[2])
            self.metadata.y2 = int(self.coords[3])

    def _make_square_coords(self):
        """
        Given a set of bounding box coordinates, make them square by expanding
        the shorter axis equally on both sides.
        """
        hlen = self.coords[1] - self.coords[0]
        vlen = self.coords[3] - self.coords[2]
        diff = abs(hlen - vlen)

        if hlen >= vlen:  # Wider than tall — expand vertically
            self.coords[3] = self.coords[3] + (diff / 2)
            self.coords[2] = self.coords[2] - (diff / 2)
        else:  # Taller than wide — expand horizontally
            self.coords[1] = self.coords[1] + (diff / 2)
            self.coords[0] = self.coords[0] - (diff / 2)

        # Clamp to image boundaries
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

        self.coords = [int(c) for c in self.coords]

    # ──────────────────────────────────────────────
    # Scoring state: score entry and navigation
    # ──────────────────────────────────────────────

    def _enter_score(self, score: int):
        """
        Record a score for the current CDA, then advance to the next one.
        Rejects if no bounding box has been drawn yet.
        """
        if not self.allow_scorekeypress:
            return

        if self.metadata.maxrow is None or self.metadata.maxcol is None:
            return

        if self.metadata.x1 is None:
            print("Please select the ROI before selecting the score")
            return

        self.metadata.score = score
        self.dataframe = pd.concat(
            [self.dataframe, self.metadata._make_pandas()],
            ignore_index=True,
        )
        self.metadata._update(self.num_spots)
        self._route_to_state()

    def _skip_spots(self, num_skip: int):
        """
        Skip one or more CDA positions.
        If num_skip == 1, move to the next CDA.
        If num_skip == self.num_spots, skip to the start of the next leaf.
        """
        self.metadata._update(self.num_spots)
        if self.metadata.end_of_data:
            self._save_and_quit()
            return

        for _ in range(num_skip - 1):
            if self.metadata.end_of_data:
                self._save_and_quit()
                return
            # When skipping a whole leaf, stop if we've landed on pos 1
            # (meaning we've already reached the next leaf)
            if num_skip == self.num_spots and self.metadata.pos == 1:
                break
            self.metadata._update(self.num_spots)
            if self.metadata.end_of_data:
                self._save_and_quit()
                return

        self._route_to_state()

    def _prev_CDA(self):
        """
        Go back to the previous CDA and allow it to be re-scored.
        Removes the last row from the dataframe and reconstructs metadata
        from what remains.
        """
        if len(self.dataframe) == 0:
            print("No previous CDA to go back to.")
            return

        print("Removing previous CDA metadata record. Please input new metadata.")

        # Remove the last row FIRST, then reconstruct metadata from what remains.
        self.dataframe = self.dataframe.iloc[:-1]
        self.metadata = CDAMetadata(self.metadata.img_files, self.dataframe)

        # Clear the score so the grid/scoring flow treats this as a fresh CDA
        # to be annotated, not one to advance past.
        self.metadata.score = None

        self._route_to_state()

    def _route_to_state(self):
        """
        Decide which state to transition to based on current metadata.
        If at the start of a new image (row=1, col=1, pos=1), go to grid state.
        Otherwise go directly to scoring state.
        """
        if self.metadata.end_of_data:
            self._save_and_quit()
        elif self.metadata.row == 1 and self.metadata.col == 1 and self.metadata.pos == 1:
            self._scoring_to_grid()
        else:
            self._grid_to_scoring()

    def _save_and_quit(self):
        """If user quits or end of data reached, destroy the window."""
        self.root.destroy()