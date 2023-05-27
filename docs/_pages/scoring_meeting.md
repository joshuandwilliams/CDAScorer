---
permalink: /scoring_meeting/
title: "Instructions for Banfield Group Scoring"
classes: wide
toc: True
---

There is a video form of this tutorial [at this link](https://youtu.be/mnZx5ndiYMM).


## Step 1: Make sure you're connected to Eduroam and the shared drive.

If you need a reminder of how to do this please see the 2nd step of the Window or Mac Installation Tutorials in the top bar.

## Step 2: Navigate to today's directory

For Mac users, in the command line type:

```cd /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May/```

On Windows you need to first enter the volume that you mapped the shared drive to, e.g. Z ```z:```. Then you can type:

```cd Research-Groups\\Mark-Banfield\\Josh_Williams\\Scoring_5May\\```

Note: I don't have a Windows laptop to test this on so it may not be exactly correct - please use your intuition to modify this command and reach the correct folder.

Then, type ```ls``` (for Windows ```dir```). You should see your name. Type ```cd YOURNAME``` where YOURNAME is the name of the folder with your name on it.

If you type ```ls``` again, you will see there are images in your folder. These are the images you will need to score.

## Step 3: Activate the conda environment you made last time.

In the command line type:

```conda activate CDAScorer```

## Step 4: Update the CDAScorer package to the latest version

In the command line type:

```pip3 install --upgrade cdascorer```

## Step 5: Run the package

Mac:

```cdascorer -s .```

Windows:

```cdascorer-windows.py -s .```

## Scoring Guidance

The row and columns should ALWAYS start from the top left leaf. Proceed as if reading lines on a page, no matter the orientation of the photo.
The first position of the leaf should ALWAYS be the first CDA encountered when counting anticlockwise from the top of the central vein, no matter the orientation of the leaf.

If the image contains 5 leaves in a dice-5 pattern, consider there to be 3 rows and 3 columns. Skip the intermediates.

Skip any orange chimaeric CDAs, but still score the yellow CDAs on the same leaf (you can use the "next" button").

You can view your scores for a particular image by typing ```cdascorer-view -d cdata.csv -i IMAGENAME``` where IMAGENAME is the name of the image you wish to view.
