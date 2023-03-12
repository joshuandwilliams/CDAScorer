---
title: "Generating Blank Metadata Tables"
permalink: /docs/generate-metadata/
author_profile: false
sidebar:
  - title: "Tutorials"
    nav: docs
---

### Introduction:

Before collecting coordinate data for individual cell death areas, there needs to be a way to accurately reference each in a metadata table by following a standardised infiltration format.

<details markdown=1><summary markdown="span">Infiltration format - click to expand</summary>

Each cell death area will be identified though a number of factors.

1. The Img-ID variable references to a specific image filename.
2. The Plant-Per-Img-ID variable references a pair of technical replicates from the same plant.
3. The Leaf-ID variable references a particular leaf from the pair (1 or 2).
4. The Offset variable references the position from which to start counting anti-clockwise to identify the individual cell death area. An Offset of 1 indicates the user should start at the position to the upper left of the central vein, and an Offset of 2 indicates that the user should start from one position anticlockwise of position 1.
5. The Spot-ID variable references how far to count anticlockwise from the Offset. A Spot-ID of 1 means that the cell death area in question is the same as the Offset, and a Spot-ID of 2 means that the user should count one position anticlockwise from the Offset.

![CDA_Format_1](./images/CDA_Format_1.png)

In the image above, the red numbered boxes represent the technical replicates (Plant-IDs). Each of the two white numbered leaves (Leaf-IDs) in each replicate have been treated with the same infiltration pattern. Two technical replicates are missing a leaf. This is ok, as long as not both of the technical replicates are missing, since then the correct Offset value cannot be known.

![CDA_Format_2](./images/CDA_Format_2.png)

In the above image, the red numbers in A) represent the Offset positions, starting from the top left of the central vein, and counting anticlockwise. These leaves each have 8 cell death areas - a different number can be used, but must be consistent across all leaves. In B) An example is given to show the cell death area assigned to Offset 3, Spot-ID 6. Beginning at the Offset 3 (in red), the user counts anti-clockwise, until position 6, highlighted in a blue box.

</details>


### Running cdataml_metadata:

The ```cdataml_metadata``` module can be used to automatically generate metadata tables in this format, which can become inputs for the next steps.

The module can be run from the command line.

```sh
(my-env) $ python3 -m cdataml_generate -i <folder-containing-tif-images> -o <output-location>
```

### Options:

There are two options taken by ```cdataml_generate```:
1. ```-i```: Path to a folder containing the raw images in .tif format.
2. ```-o```: Path to contain the three output files.

### Outputs:

There are three output files from ```cdataml_generate```:

1) ```images.csv```: File containing the locations of each .tif file in the input folder.

| Img-ID | Path |
| - | - |
| 1 | path/to/image_1.tif |
| 2 | path/to/image_2.tif |
| n | path/to/image_n.tif |

2) ```treatments.csv```: File to contain infiltration treatment information. This isn't used in any other function and is for the user to fill out manually if wished.

| Treat-ID | Treatname | Effector | NLR1 | NLR2 |
| - | - | - | - | - |
| 1 | | | | | 
| 2 | | | | |
| n | | | | |

3) ```cdata.csv```: File to contain the data pointing to a particular cell death area, with blank columns for score, biological replicate, and coordinates to be filled in the next steps.

| Unique_Spot_ID | Img-ID | Plant-ID | Plant-Per-Img-ID | Leaf-ID | Spot-ID | Offset | Treat-ID | Replicate | Score | y1 | y2 | x1 | x2 |
| - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| S1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | | | | | | |
| S2 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | | | | | | |
| Sn | x | x | x | x | x | x | x | | | | | | |

### Troubleshooting:

- If your Img-ID file has no rows, check that the ```i``` option exists and contains .tif files.
