"""
viewer.py

A tool for viewing existing CDAScorer annotations overlaid on their source image.

Usage:
    cdascorer-view --data scores.csv --image path/to/image.tif
"""

import os
import sys
import argparse

import pandas as pd
import tkinter as tk
from PIL import ImageTk, Image


def _find_image_path(data: pd.DataFrame, image_name: str) -> str:
    """
    Find the full image path from the data file by matching the basename.
    Returns the full path as stored in the CSV, or None if not found.
    """
    for img_path in data["img"].astype(str).unique():
        if os.path.basename(img_path) == os.path.basename(image_name):
            return img_path
    return None


def _view(data: pd.DataFrame, image_path: str) -> None:
    """
    Open a Tkinter window showing the image with scored bounding boxes overlaid.
    """
    root = tk.Tk()
    root.title("CDAScorer View")

    img = Image.open(image_path)
    img_width, img_height = img.size

    # Scale image to fit comfortably on screen (65% of screen width or height)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    cover = 0.65

    width_ratio = img_width / screen_width
    height_ratio = img_height / screen_height
    if width_ratio > height_ratio:
        scale = (screen_width / img_width) * cover
    else:
        scale = (screen_height / img_height) * cover

    resized_width = round(img_width * scale)
    resized_height = round(img_height * scale)
    img = img.resize((resized_width, resized_height))
    img_tk = ImageTk.PhotoImage(img)

    frame = tk.Frame(root, width=resized_width, height=resized_height)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, width=resized_width, height=resized_height)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Draw bounding boxes and scores for all CDAs belonging to this image
    image_basename = os.path.basename(image_path)
    for _, row in data.iterrows():
        if os.path.basename(str(row["img"])) == image_basename:
            x1 = row["x1"] * scale
            y1 = row["y1"] * scale
            x2 = row["x2"] * scale
            y2 = row["y2"] * scale
            canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
            canvas.create_text(
                x1 + 5, y1 + 7,
                text=str(int(row["score"])),
                fill="red",
                anchor=tk.NW,
                font=("Arial", 12),
            )

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="View CDAScorer annotations overlaid on an image.",
    )
    parser.add_argument(
        "-d", "--data",
        help="CDAScorer CSV file containing scores.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-i", "--image",
        help="Path or filename of the image to view.",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    if not os.path.exists(args.data):
        sys.exit(f"ERROR: data file {args.data} does not exist")

    data = pd.read_csv(args.data)

    # Try the image path directly first, then look it up by basename in the CSV
    if os.path.exists(args.image):
        image_path = args.image
    else:
        image_path = _find_image_path(data, args.image)
        if image_path is None:
            sys.exit(
                f"ERROR: image '{args.image}' was not found on disk "
                f"or in the data file {args.data}"
            )
        if not os.path.exists(image_path):
            sys.exit(
                f"ERROR: image '{image_path}' was found in the data file "
                f"but the file does not exist on disk"
            )

    _view(data, image_path)


if __name__ == "__main__":
    main()