---
permalink: /scoring_meeting/
title: "Instructions for Banfield Scoring Meeting 27/03/2023"
classes: wide
toc: True
---

## For the scoring meeting 5/5/23

## Step 1: Make sure you're connected to Eduroam and the shared drive.

If you need a reminder of how to do this please see the 2nd step of the Window or Mac Installation Tutorials in the top bar.

## Step 2: Navigate to today's directory

In the command line type:

```cd /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May/```

Then, type ```ls```. You should see your name. Type ```cd YOURNAME``` where YOURNAME is the name of the folder with your name on it.

If you type ```ls``` again, you will see there are images in your folder. These are the images you will need to score.

## Step 3: Activate the conda environment you made last time.

In the command line type:

```conda activate CDAScorer```

## Step 4: Update the CDAScorer package

In the command line type:

```pip3 install --upgrade cdascorer```

## Step 5: Run the package

Mac:

```cdascorer -s .```

Windows:

```cdascorer-windows.py -s .```

