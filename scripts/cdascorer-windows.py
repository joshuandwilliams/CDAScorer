#!/usr/bin/env python
'''
cdascorer-run

A utility for running the cdascorer GUI on a folder of images.

See the help:

    cdascorer-run --help

Usage examples:

    Basic use:
        cdascorer-run --source_folder ~/Desktop/image_folder/ --file ~/Desktop/data_file.csv

    Test case:
        cdascorer-test
        or
        cdascorer-run --file --test True

    On a smaller screen where part of the image is being cut off:
        cdascorer-run --source_folder ~/Desktop/image_folder/ --file ~/Desktop/data_file.csv --window_width 500


'''

import cdascorer
import os
import sys
import pandas as pd
import argparse
from pathlib import Path
import numpy as np
from datetime import datetime
import tkinter as tk

parser = argparse.ArgumentParser(add_help=True, formatter_class=argparse.RawDescriptionHelpFormatter, description = "test-script")
parser.add_argument("-s", "--source_folder", help="folder containing images to analyse", type=str, default=".")
parser.add_argument("-f", "--file", help="cdata csv file to update. created if does not exist.", type=str, default="cdata.csv")
parser.add_argument("-n", "--num_spots", help="the number of spots per leaf. must be consistent across all leaves", type=int, default=8)
parser.add_argument("-t", "--test", help="use an existing image to test the program. true or false", type=bool, default=False)
parser.add_argument("-w", "--window_width", help="change the size of the window to fit your screen.", type=int, default=1000)
args = parser.parse_args()

if not os.path.exists(args.source_folder):
    if not args.test == True:
        sys.exit(f"ERROR: source folder {args.source_folder} does not exist")

if not os.path.exists(args.file):
    print(f"Input file {args.file} does not exist. creating ...")
    cdata = pd.DataFrame(columns=["img", "maxrow", "maxcol", "row", "col", "pos", "score", "x1", "x2", "y1", "y2"])
    cdata.to_csv(args.file, index=False)
else:
    if not args.file.endswith('.csv'):
        sys.exit(f"ERROR: input file {args.file} is not a CSV file")
    cdata = pd.read_csv(args.file)
    if not list(cdata.columns.values) == ["img", "maxrow", "maxcol", "row", "col", "pos", "score", "x1", "x2", "y1", "y2"]:
        sys.exit(f"ERROR: input file {args.file} contains incorrect column names")

if args.num_spots <= 0:
    sys.exit("ERROR: number of spots per leaf cannot be less than or equal to zero")

def _save_and_quit(df, file_path):
    '''
    _save_and_quit()

    Moves the starting file to a dated backup.
    Then, updates the working file with the current metadata dataframe

    '''
    print(f"Saving and Quitting. Your data went to the file: {args.file}")
    # Move Previous Version to Backup and Save Existing Version
    now = datetime.now()
    os.rename(file_path, os.path.join(os.path.dirname(file_path) + "backup_" + now.strftime("%d_%m_%Y_%H_%M_") + os.path.basename(file_path)))
    df.to_csv(file_path, index = False)
    sys.exit()


def _record_cdata(source_folder, df, num_spots):
    '''
    record_cdata()

    Wrapper function for running the CDAScorer Tkinter object (class MainWindow)

    1. Find the filepaths to all TIFF images in the source folder.
    2. Initialise metadata object.
    3. Run the MainWindow Tkinter GUI using these inputs.
    4. Save the updated metadata dataframe and exit the program.

    '''
    # Find TIF Files in Source Folder of load test img
    if args.test == True:
        image_files = ["test_cda_img.jpg"]
    else:
        image_files = [str(file.resolve()) for file in Path(source_folder).iterdir() if
                   file.is_file() and not file.name.startswith(".") and
                   file.name.endswith(".tif")]

    # Initialise CDAMetadata Object
    current_metadata = cdascorer.cdametadata.CDAMetadata(image_files, df)

    if current_metadata.row == current_metadata.maxrow:
        if current_metadata.col == current_metadata.maxcol:
            if current_metadata.pos == args.num_spots:
                if current_metadata.img == image_files[-1]:
                    print("Dataset already completed")
                    sys.exit()

    if not current_metadata.score == None:
        current_metadata = current_metadata._update(args.num_spots)

    # Loop through image files, starting at current_metadata.image
    root = tk.Tk()
    root.title("CDAScorer")
    main_window = cdascorer.cdascorer_gui_windows.MainWindow(root, cdata, current_metadata, args.window_width, args.num_spots)
    root.protocol("WM_DELETE_WINDOW", main_window._save_and_quit)
    root.mainloop()

    #print(main_window.dataframe)
    _save_and_quit(main_window.dataframe, args.file)


if __name__ == '__main__':
    if args.test == True:
        _record_cdata(None, cdata, args.num_spots)
    else:
        _record_cdata(args.source_folder, cdata, args.num_spots)
