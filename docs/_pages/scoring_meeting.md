---
permalink: /scoring_meeting/
title: "Instructions for Banfield Scoring Meeting 27/03/2023"
classes: wide
toc: True
---

### Locating your scoring datasets

Now you've got the CDAScorer up and running, you can start using it to score some actual data!

In File Explorer or Finder please navigate to my folder in Mark's area on the shared drive.

I've divided the existing data up amongst those who are available, and the details can be in CDA_Image_Info.xlsx.

Navigate to the second sheet called "Scoring_Assignments" and make sure you can see your rows in the Assigned_Scorer column.

Please use CDAScorer package as explained below and work through as many of your assigned folders as you can during this time.

At the end of the time, please copy any completed datasets to the Scored_Data_Complete folder.

## Quickstart (If you've done this before - otherwise skip):

Mac:

```cdascorer --source_folder <SOURCE FOLDER> --file <OUTPUT FILE> -n <CDAs PER LEAF>```

Windows:

```cdascorer-windows.py --source_folder <SOURCE FOLDER> --file <OUTPUT FILE> -n <CDAs PER LEAF>```

## Constructing your command (Mac):

You should have a cmd window open, and have navigated to the folder you want your recorded data to be stored.

Your command will consist of 4 elements:

- **Running the CDAScorer program**.

This will be ```cdascorer```.

- **Telling CDAScorer which images you're going to score**.

This will be ```--source_folder /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/FOLDER```.

FOLDER comes from the Folder column of the CDA_Image_Info Excel file - you can copy and paste it into the Terminal window.

- **Telling CDAScorer the name of your output file**.

This will be ```--file cdadata_YOURNAME_FOLDERID.csv``` e.g. cdadata_Josh_2.csv.

YOURNAME is your name.

FOLDERID comes from the FolderID column of the CDA_Image_Info Excel file.

- **Telling CDAScorer how many CDAs are on each leaf**.

This will be ```-n LEAFPERIMG```

LEAFPERIMG comes from the LeafPerImg column of the CDA_Image_Info Excel file.

### Bringing this all together you will have a command that looks something like this:

```cdascorer --source_folder /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/FOLDER --file cdatdata_YOURNAME_FOLDERID.csv -n LEAFPERIMG```

And as an example for FolderID 1:

```cdascorer --source_folder /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Fig2_leaf_images/A/HMAswap/MP/1/ --file cdadata_Raf_1.csv -n 6```

## Constructing your command (Windows):

You should have a Terminal window open, and have nagivated to the folder you want your recorded data to be stored.

Your command will consist of 4 elements:

- **Running the CDAScorer program**.

This will be ```cdascorer-windows.py```.

- **Telling CDAScorer which images you're going to score**.

This will be ```--source_folder Z:\Research-Groups\Mark-Banfield\Josh_Williams\FOLDER```.

FOLDER comes from the Folder column of the CDA_Image_Info Excel file - you can copy and paste it into the Terminal window.

- **Telling CDAScorer the name of your output file**.

This will be ```--file cdadata_YOURNAME_FOLDERID.csv``` e.g. cdadata_Josh_2.csv.

YOURNAME is your name.

FOLDERID comes from the FolderID column of the CDA_Image_Info Excel file.

- **Telling CDAScorer how many CDAs are on each leaf**.

This will be ```-n LEAFPERIMG```

LEAFPERIMG comes from the LeafPerImg column of the CDA_Image_Info Excel file.

### Bringing this all together you will have a command that looks something like this:

```cdascorer-windows.py --source_folder Z:\Research-Groups\Mark-Banfield\Josh_Williams\FOLDER --file cdadata_YOURNAME_FOLDERID.csv -n LEAFPERIMG```

And as an example for FolderID 1:

```cdascorer-windows.py --source_folder Z:\Research-Groups\Mark-Banfield\Josh_Williams\Fig2_leaf_images\A\HMAswap\MP\1\ --file cdadata_Raf_1.csv -n 6```
