---
permalink: /tutorial/
title: "CDAScorer Tutorial"
---

Welcome to the cdataml package. This package is designed to support in the creation and recording of cell death area (CDA) data in a standardised format for use in the training of machine learning models. This tutorial will guide you through installing and using it.

### Installing the cdataml package:

Install into a conda environment from PyPI.

```sh
$ conda activate <my-env>
(my-env) $ pip3 install cdataml
```

Or install it from GitHub.

```sh
$ conda activate <my-env>
(my-env) $ pip3 install git+https://github.com/joshuandwilliams/cdataml
```

### Quickstart:

Run the package with your own data, where any TIFF images to be used are in a single folder (source folder).

```sh
(my-env) $ cdataml-run -s <SOURCE-FOLDER> -f <DATA-FILE> -n <CDA_Per_Leaf>
```

Or, run the package on an example image included in the package files.

```sh
(my-env) $ cdataml-run -t True
```

Load the help information:

```sh
(my-env) $ cdataml-run -h
```

### Detailed information:

#### Image format:

1. Each image should contain leaves in a grid pattern.
2. Each leaf should contain cell death areas in positions 1 to n, where 1 is upper left of the central vein, and consequent positions count anticlockwise from that position.

![CDA_Format](./images/CDA_Format.png)

In the image above, the table shows an example row of data which will be recorded for each CDA.
1. The maxrow, maxcol, row, and col variables are found by dividing the image into a grid.
2. The pos variable refers to cell death areas in positions 1 to n, where 1 is upper left of the central vein, and consequent positions count anticlockwise from that position (shown in blue numbering).
3. The score variable is recorded in the program.
4. The coordinate variables x1, x2, y1, and y2 are recorded in the program also, and represent the horizontal and vertical positions shown in the blue box on the right.

#### Options:

There are four options:
1. ```-s```: The source folder containing the TIFF images. Defaults to "."
2. ```-f```: The CSV file to contain the recorded data. If it does not exist, it will be created. Defaults to "cdata.csv"
3. ```-n```: The number of CDAs per leaf. Defaults to 8.
4. ```-t```: Defaults to False, but if ```-t True``` supplied, will run the package on an example image.

#### Recording coordinates and scores with the OpenCV interface:

The command line will guide you through using the program, so please watch the output there.

Upon running the program, the first image will be displayed, with a request for the user to input the number of rows and columns. The user should input first the number of rows by pressing a key between 1 and 9, and then the same for the columns.

![Input_Row_Col](./images/Input_Row_Col.png)

The program will then append the scoring key to the bottom of that image, as well as the metadata corresponding to the first CDA at the top.

![Record_Coords_Score](./images/Record_Coords_Score.png)

Using the metadata, identify the corresponding CDA, drag a box around it, and hit enter. This will record the coordinates of that CDA.

Next, input a score between 0 and 6 corresponding to that CDA.

The metadata at the top of the image will update, and the process of recording coordinates and scores can be repeated for the next CDA.

#### What if there are missing CDAs or leaves?

Sometimes leaves will be damaged, resulting in regions being unintelligible, or just being removed from the image altogether.

If the metadata at the top of the OpenCV window doesn't match anything on the screen, non-existent CDAs and leaves can be skipped.

During the coordinate collecting stage, instead of dragging a box, instead press "ESC" to exit the OpenCV selectROI tool.

Then, to skip to the next CDA, press "s", or to skip to position 1 of the next leaf, press "l".

#### Exiting the program.

At any stage of the program, the user can press "ESC" to exit. If the user is in the OpenCV selectROI tool, they will have to press "ESC" twice: once to exit selectROI, and once to exit the program.
