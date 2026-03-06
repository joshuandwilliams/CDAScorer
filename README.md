# CDAScorer

A Python/Tkinter tool for annotating cell death areas (CDAs) from agroinfiltration leaf images. Designed for plant science researchers who need to systematically score lesion severity across large image datasets.

## What it does

CDAScorer provides a GUI workflow for recording bounding box coordinates and severity scores (0–6) for individual CDAs on photographed leaves arranged in a grid pattern. It also includes a viewer for reviewing previously scored annotations.

## Installation

```bash
pip install cdascorer
```

Or install from source:

```bash
git clone https://github.com/joshuandwilliams/CDAScorer.git
cd CDAScorer
pip install .
```

Requires Python 3.9 or later.

## Quick start

### Scoring new images

```bash
cdascorer --source_folder /path/to/images/ --file output.csv
```

This opens a GUI that walks you through each image:

1. **Grid entry** — specify the number of leaf rows and columns in the image, and the number of CDAs per leaf.
2. **Scoring** — for each CDA, draw a bounding box around it and assign a severity score (0–6).

Scores are saved to the CSV file as you go, with automatic backups on exit.

To try it out with a built-in test image:

```bash
cdascorer --test
```

### Viewing existing annotations

```bash
cdascorer-view --data output.csv --image /path/to/image.tif
```

Opens a read-only view of the image with all scored bounding boxes overlaid in red.

## Output format

The output CSV contains one row per CDA:

| Column | Description |
|--------|-------------|
| `img` | Image filepath |
| `maxrow` | Total rows in the leaf grid |
| `maxcol` | Total columns in the leaf grid |
| `row` | Grid row of this leaf |
| `col` | Grid column of this leaf |
| `pos` | CDA position on the leaf (numbered from top-left of central vein, anti-clockwise) |
| `score` | Severity score (0–6) |
| `x1`, `x2` | Left and right pixel bounds of the bounding box |
| `y1`, `y2` | Upper and lower pixel bounds of the bounding box |

## Keyboard shortcuts

During scoring, keys `0`–`6` enter the corresponding score directly (same as clicking the score buttons).

## Supported image formats

TIFF (.tif/.tiff), JPEG (.jpg/.jpeg), and PNG (.png).

## Tutorial

For a detailed walkthrough with screenshots, see the [tutorial page](https://joshuandwilliams.github.io/CDAScorer/tutorial/).

## License

See [LICENSE.txt](LICENSE.txt).