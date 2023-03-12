---
title: "Fitting Existing Scores to cdata.csv"
permalink: /docs/fitting-scores/
author_profile: false
sidebar:
  - title: "Tutorials"
    nav: docs
---

### Introduction:

If you already have existing scores, you can fit them into your metadata table. This should be done after the coordinates have been recorded, since then the number of scores = the number of coordinates = the number of CDAs.

If the existing score data file also contains values about biological replicate number, this will be fitted too.

### Running cdataml_fitscores:

The module can be run from the command line.

```sh
(my-env) $ python3 -m cdataml_fitscores -i cdata.csv -o cdata.csv_scored -r <path-to-existing-score-data>
```

### Options:

There are three options taken by ```cdataml_fitscores```:
1. ```-i```: Input path.
2. ```-o```: Output path.
3. ```-r```: Path to file containing existing score data. The score data must be in a column named "Score", and must be the same length as the number of CDAs.

### Outputs:

The Score (and optionally Replicate) columns of the metadata file will be filled.

### Troubleshooting:

- The most likely causes of issues here are A) the path given in -r doesn't exist or B) the number of Scores in the -r data file differs from the number of CDAs. 
