"""
rescore.py

Command-line entry point for the CDAScorer rescoring workflow.

Randomly selects 100 CDAs previously scored by a given scorer and
launches a simplified GUI for rescoring (score only, no bounding box).

Usage:
    cdascorer-rescore --data combined_data.csv --scorer JoshW --source_folder ./images/
"""

import os
import sys
import argparse
from datetime import datetime

import pandas as pd
import tkinter as tk

from rescore_gui import RescoreWindow

OUTPUT_COLUMNS = [
    "scorer", "basename", "row", "col", "pos",
    "x1", "x2", "y1", "y2",
    "old_score", "median_score", "new_score",
]


def _find_scorer_cdas(data: pd.DataFrame, scorer: str) -> pd.DataFrame:
    """
    Find all CDAs scored by a given scorer across all three scorer positions,
    and return a normalised dataframe with consistent column names.

    For each CDA, uses the Centre_Coords bounding box (not the scorer's own box).
    The 'old_score' is the scorer's own original score.
    """
    rows = []

    for position in [1, 2, 3]:
        scorer_col = f"Scorer{position}"
        score_col = f"Score{position}"

        # Find rows where this scorer was in this position
        mask = data[scorer_col] == scorer
        subset = data[mask]

        for _, row in subset.iterrows():
            # Get the Centre_Coords bounding box
            cc = int(row["Centre_Coords"])
            rows.append({
                "scorer": scorer,
                "basename": row["Basename"],
                "row": int(row["Row"]),
                "col": int(row["Col"]),
                "pos": int(row["Pos"]),
                "x1": row[f"X1_{cc}"],
                "x2": row[f"X2_{cc}"],
                "y1": row[f"Y1_{cc}"],
                "y2": row[f"Y2_{cc}"],
                "old_score": row[score_col],
                "median_score": row["Median_Score"],
            })

    return pd.DataFrame(rows)


def _resolve_image_path(basename: str, source_folder: str) -> str:
    """Find the full path to an image file in the source folder."""
    # Try exact match first
    path = os.path.join(source_folder, basename)
    if os.path.exists(path):
        return path

    # Try case-insensitive match
    for f in os.listdir(source_folder):
        if f.lower() == basename.lower():
            return os.path.join(source_folder, f)

    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Rescore 100 previously scored CDAs for intra-scorer consistency.",
    )
    parser.add_argument(
        "-d", "--data",
        help="Combined CDA data CSV (e.g. combined_CDA_data_median.csv).",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-s", "--scorer",
        help="Name of the scorer (must match a name in the Scorer columns).",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-f", "--source_folder",
        help="Folder containing the source images.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-o", "--output",
        help="Output CSV file for rescore results (default: rescore_<scorer>.csv).",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-n", "--num_samples",
        help="Number of CDAs to rescore (default: 100).",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--seed",
        help="Random seed for reproducible sampling (default: 42).",
        type=int,
        default=42,
    )
    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.data):
        sys.exit(f"ERROR: data file {args.data} does not exist")
    if not os.path.exists(args.source_folder):
        sys.exit(f"ERROR: source folder {args.source_folder} does not exist")

    data = pd.read_csv(args.data)

    # Find all CDAs for this scorer
    scorer_cdas = _find_scorer_cdas(data, args.scorer)
    if len(scorer_cdas) == 0:
        sys.exit(f"ERROR: scorer '{args.scorer}' not found in the data file")

    # Exclude CDAs with median score 0 (near-universal agreement, not meaningful to rescore)
    scorer_cdas = scorer_cdas[scorer_cdas["median_score"] != 0]
    if len(scorer_cdas) == 0:
        sys.exit(f"ERROR: all CDAs for '{args.scorer}' have median score 0")

    if len(scorer_cdas) < args.num_samples:
        print(
            f"WARNING: scorer '{args.scorer}' only has {len(scorer_cdas)} CDAs, "
            f"using all of them instead of {args.num_samples}."
        )
        sample = scorer_cdas
    else:
        sample = scorer_cdas.sample(n=args.num_samples, random_state=args.seed)

    print(f"Selected {len(sample)} CDAs for {args.scorer} to rescore (seed={args.seed}).")

    # Resolve image paths and build record list
    cda_records = []
    missing_images = set()
    for _, row in sample.iterrows():
        image_path = _resolve_image_path(row["basename"], args.source_folder)
        if image_path is None:
            missing_images.add(row["basename"])
            continue
        record = row.to_dict()
        record["image_path"] = image_path
        cda_records.append(record)

    if missing_images:
        print(f"WARNING: {len(missing_images)} images not found, skipping those CDAs:")
        for name in sorted(missing_images):
            print(f"  - {name}")

    if not cda_records:
        sys.exit("ERROR: no CDA images could be found in the source folder")

    print(f"Launching rescore GUI with {len(cda_records)} CDAs...")

    # Launch the GUI
    root = tk.Tk()
    root.title(f"CDAScorer Rescore — {args.scorer}")

    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()

    rescore_window = RescoreWindow(root, cda_records, window_width, window_height)
    root.protocol("WM_DELETE_WINDOW", rescore_window._save_and_quit)
    root.mainloop()

    # Save results
    output_file = args.output or f"rescore_{args.scorer}.csv"
    results_df = pd.DataFrame(rescore_window.results, columns=OUTPUT_COLUMNS)

    if os.path.exists(output_file):
        now = datetime.now()
        backup_name = f"backup_{now.strftime('%d_%m_%Y_%H_%M_')}{os.path.basename(output_file)}"
        backup_path = os.path.join(os.path.dirname(output_file) or ".", backup_name)
        os.rename(output_file, backup_path)
        print(f"Existing file backed up to: {backup_path}")

    results_df.to_csv(output_file, index=False)
    print(f"Saved {len(results_df)} rescored CDAs to: {output_file}")


if __name__ == "__main__":
    main()