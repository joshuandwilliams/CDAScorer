"""
rescore_gui.py

A simplified Tkinter GUI for rescoring previously annotated CDAs.

Shows the full image with the bounding box pre-drawn and only asks
the user to enter a score (0-6). No bounding box drawing is needed.
"""
import math
import io

import tkinter as tk
from PIL import ImageTk, Image, ImageDraw

from importlib.resources import files


def _scale_val(val: int, scale: float) -> int:
    """Scale a value by a factor (used for font sizes and widget dimensions)."""
    return int(math.floor(val * scale * 0.75))


class RescoreWindow:
    """
    A GUI window for rescoring CDAs.

    Displays the full source image with the bounding box highlighted,
    the scoring key, and score buttons (0-6). Cycles through a list
    of CDA records to be rescored.

    :param root: The Tkinter root window.
    :param cda_records: A list of dicts, each containing: basename, row, col,
        pos, x1, x2, y1, y2, old_score, median_score, scorer, image_path.
    :param window_width: Screen width in pixels.
    :param window_height: Screen height in pixels.
    """

    def __init__(self, root, cda_records: list, window_width: int, window_height: int):
        self.root = root
        self.cda_records = cda_records
        self.window_width = window_width
        self.window_height = window_height
        self.window_cover = 0.65
        self.scale = self.window_width / 2500

        self.current_index = 0
        self.results = []

        # Determines when 0-6 scores can be inputted by keyboard
        self.allow_scorekeypress = False

        # Load scoring key from package data
        key_bytes = files('cdascorer.data').joinpath("lesion_score_key.jpg").read_bytes()
        self.key = Image.open(io.BytesIO(key_bytes), formats=["JPEG"])

        # Build the persistent frame structure
        self.right_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        self.right_frame.pack(side=tk.RIGHT, anchor=tk.W, expand=True)

        self.scoring_label = tk.Label(self.right_frame, image='', highlightthickness=0)
        self.scoring_label.pack(side=tk.BOTTOM)

        self.canvas = None  # Will be created per-CDA

        self.left_frame = tk.Frame(
            self.root,
            width=_scale_val(500, self.scale),
            height=window_height,
            bd=2, relief=tk.GROOVE,
        )
        self.left_frame.pack_propagate(0)
        self.left_frame.pack(side=tk.RIGHT, anchor=tk.E, expand=True)

        # Bind keyboard shortcuts for scores 0-6
        for score in range(0, 7):
            self.root.bind(str(score), lambda event, s=score: self._enter_score(s))

        # Show the first CDA
        self._show_current_cda()

    # ──────────────────────────────────────────────
    # Image handling
    # ──────────────────────────────────────────────

    def _load_and_scale_image(self, image_path: str):
        """Load an image, draw the bounding box on it, and scale to fit the window."""
        record = self.cda_records[self.current_index]

        img = Image.open(image_path).copy()

        # Draw the bounding box onto the image
        draw = ImageDraw.Draw(img)
        x1, x2 = int(record["x1"]), int(record["x2"])
        y1, y2 = int(record["y1"]), int(record["y2"])
        for offset in range(3):  # Draw a few pixels thick
            draw.rectangle(
                [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                outline="red",
            )

        # Scale to fit window
        width_ratio = img.width / self.window_width
        height_ratio = img.height / self.window_height
        if width_ratio > height_ratio:
            self.img_scale = (self.window_width / img.width) * self.window_cover
        else:
            self.img_scale = (self.window_height / img.height) * self.window_cover

        resized = img.resize((
            round(img.width * self.img_scale),
            round(img.height * self.img_scale),
        ))
        self.resized_img_tk = ImageTk.PhotoImage(resized)

        # Scale the scoring key to match image width
        key_scale = resized.width / self.key.width
        resized_key = self.key.resize((
            round(self.key.width * key_scale),
            round(self.key.height * key_scale),
        ))
        self.resized_key_tk = ImageTk.PhotoImage(resized_key)

    # ──────────────────────────────────────────────
    # Widget management
    # ──────────────────────────────────────────────

    _LEFT_WIDGETS = [
        "info_label", "progress_label", "scoring_info_label",
        "button_0", "button_1", "button_2", "button_3",
        "button_4", "button_5", "button_6",
        "button_skip", "button_exit",
    ]

    def _clear_widgets(self):
        """Destroy all dynamically created widgets."""
        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None
        for name in self._LEFT_WIDGETS:
            widget = getattr(self, name, None)
            if widget is not None:
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
                setattr(self, name, None)

    # ──────────────────────────────────────────────
    # Display current CDA
    # ──────────────────────────────────────────────

    def _show_current_cda(self):
        """Display the current CDA for rescoring."""
        self._clear_widgets()

        if self.current_index >= len(self.cda_records):
            self._save_and_quit()
            return

        record = self.cda_records[self.current_index]
        self._load_and_scale_image(record["image_path"])

        self.allow_scorekeypress = True

        # Right frame — canvas with image (bounding box already drawn on image)
        self.canvas = tk.Canvas(
            self.right_frame,
            width=self.resized_img_tk.width(),
            height=self.resized_img_tk.height(),
            highlightthickness=0, bg="white",
        )
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.resized_img_tk)
        self.canvas.pack(side=tk.TOP)

        # Show scoring key
        self.scoring_label.config(image=self.resized_key_tk)

        # Left frame
        self.root.update()
        self.left_frame.config(height=self.right_frame.winfo_height())

        font = ("Arial", _scale_val(30, self.scale))
        font_large = ("Arial", _scale_val(40, self.scale))

        self.progress_label = tk.Label(
            self.left_frame, font=font,
            text=f"CDA {self.current_index + 1} / {len(self.cda_records)}",
        )
        self.progress_label.place(relx=0.5, rely=0.02, anchor=tk.N)

        self.info_label = tk.Label(
            self.left_frame, font=font,
            text=(
                f"\nImage: {record['basename']}"
                f"\nRow: {record['row']}"
                f"\nCol: {record['col']}"
                f"\nPos: {record['pos']}"
                f"\n\nThe bounding box is"
                f"\nhighlighted in red."
                f"\n\nEnter a score (0-6):\n"
            ),
        )
        self.info_label.place(relx=0.5, rely=0.08, anchor=tk.N, relwidth=1.0)

        self.scoring_info_label = tk.Label(
            self.left_frame, font=font,
            justify=tk.CENTER,
            text="\nScore:\n",
        )
        self.scoring_info_label.place(relx=0.5, rely=0.52, anchor=tk.S, relwidth=1.0)

        # Score buttons
        score_positions = [
            (0, 0.5, 0.57),
            (1, 0.35, 0.67), (2, 0.65, 0.67),
            (3, 0.35, 0.77), (4, 0.65, 0.77),
            (5, 0.35, 0.87), (6, 0.65, 0.87),
        ]
        for score_val, rx, ry in score_positions:
            btn = tk.Button(
                self.left_frame, text=str(score_val), font=font_large,
                command=lambda s=score_val: self._enter_score(s),
            )
            btn.place(relx=rx, rely=ry, anchor=tk.S)
            setattr(self, f"button_{score_val}", btn)

        # Skip button
        self.button_skip = tk.Button(
            self.left_frame, text="Skip",
            command=self._skip, font=font,
        )
        self.button_skip.place(relx=0, rely=1, anchor=tk.SW)

        # Save and exit button
        self.button_exit = tk.Button(
            self.left_frame, text="Save and Exit",
            command=self._save_and_quit, font=font,
        )
        self.button_exit.place(relx=0, rely=0, anchor=tk.NW)

    # ──────────────────────────────────────────────
    # Score entry and navigation
    # ──────────────────────────────────────────────

    def _enter_score(self, score: int):
        """Record the new score and advance to the next CDA."""
        if not self.allow_scorekeypress:
            return

        record = self.cda_records[self.current_index]
        self.results.append({
            "scorer": record["scorer"],
            "basename": record["basename"],
            "row": record["row"],
            "col": record["col"],
            "pos": record["pos"],
            "x1": record["x1"],
            "x2": record["x2"],
            "y1": record["y1"],
            "y2": record["y2"],
            "old_score": record["old_score"],
            "median_score": record["median_score"],
            "new_score": score,
        })

        self.current_index += 1
        self._show_current_cda()

    def _skip(self):
        """Skip the current CDA without recording a score."""
        self.current_index += 1
        self._show_current_cda()

    def _save_and_quit(self):
        """Destroy the window. Results are available in self.results."""
        self.allow_scorekeypress = False
        self.root.destroy()