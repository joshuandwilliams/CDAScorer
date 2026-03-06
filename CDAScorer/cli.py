"""
cli.py

Command-line entry point for the CDAScorer GUI.

Usage examples:

    Basic use:
        cdascorer --source_folder ~/Desktop/image_folder/ --file ~/Desktop/data_file.csv

    Test case:
        cdascorer --test

"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
import tkinter as tk

from cdascorer.cdametadata import CDAMetadata
from cdascorer.cdascorer_gui import MainWindow

COLUMNS = ["img", "maxrow", "maxcol", "row", "col", "pos", "score", "x1", "x2", "y1", "y2"]


def _save_and_quit(df: pd.DataFrame, file: str) -> None:
    """
    Move the existing file to a dated backup, then save the current dataframe.
    """
    print(f"Saving and Quitting. Your data went to the file: {file}")
    if os.path.exists(file):
        now = datetime.now()
        backup_name = f"backup_{now.strftime('%d_%m_%Y_%H_%M_')}{os.path.basename(file)}"
        backup_path = os.path.join(os.path.dirname(file), backup_name)
        os.rename(file, backup_path)
    df.to_csv(file, index=False)
    sys.exit()


def _cdascorer(source_folder: str, df: pd.DataFrame, test: bool, file: str) -> None:
    """
    Wrapper function for running the CDAScorer Tkinter GUI.
    """
    if test:
        image_files = ["test_cda_img.jpg"]
    else:
        image_files = [
            str(f.resolve())
            for f in Path(source_folder).iterdir()
            if f.is_file()
            and not f.name.startswith(".")
            and f.suffix.lower() in (".tif", ".tiff", ".jpg", ".jpeg", ".png")
        ]

    if not image_files:
        sys.exit(f"ERROR: no image files found in {source_folder}")

    current_metadata = CDAMetadata(image_files, df)

    root = tk.Tk()
    root.title("CDAScorer")

    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()

    main_window = MainWindow(root, df, current_metadata, window_width, window_height)
    root.protocol("WM_DELETE_WINDOW", main_window._save_and_quit)
    root.mainloop()

    _save_and_quit(main_window.dataframe, file)


def main() -> None:
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Run the CDAScorer GUI.",
    )
    parser.add_argument(
        "-s", "--source_folder",
        help="Folder containing images to analyse.",
        type=str,
        default=".",
    )
    parser.add_argument(
        "-f", "--file",
        help="CSV file to update. Created if it does not exist.",
        type=str,
        default="cdata.csv",
    )
    parser.add_argument(
        "-t", "--test",
        help="Use a built-in test image.",
        action="store_true",
    )
    args = parser.parse_args()

    if not os.path.exists(args.source_folder) and not args.test:
        sys.exit(f"ERROR: source folder {args.source_folder} does not exist")

    if not os.path.exists(args.file):
        print(f"Input file {args.file} does not exist. Creating ...")
        cdata = pd.DataFrame(columns=COLUMNS)
        cdata.to_csv(args.file, index=False)
    else:
        if not args.file.endswith(".csv"):
            sys.exit(f"ERROR: input file {args.file} is not a CSV file")
        cdata = pd.read_csv(args.file)
        if list(cdata.columns) != COLUMNS:
            sys.exit(f"ERROR: input file {args.file} contains incorrect column names")

    _cdascorer(args.source_folder, cdata, args.test, args.file)


if __name__ == "__main__":
    main()