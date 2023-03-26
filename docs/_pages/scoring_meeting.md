---
permalink: /scoring_meeting/
title: "Instructions for Banfield Scoring Meeting 27/03/2023"
classes: wide
---

### Locating your scoring datasets

Now you've got the CDAScorer up and running, you can start using it to score some actual data!

I've divided the existing data up amongst those who are available, and the details can be found in my folder in Mark's shared folder.
- Windows: Z:\Research-Groups\Mark-Banfield\Josh_Williams\CDA_Image_Info.xlsx
- Mac: /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/CDA_Image_Info.xlsx

Navigate to the second sheet called "Scoring_Assignments" and identify your rows in the Assigned_Scorer column.

### Constructing your command (Mac):

You should have a cmd window open, and have navigated to the folder you want your recorded data to be stored.

Your command will consist of 4 elements:

- Running the CDAScorer program.

This will be ```cdascorer```.

- Telling CDAScorer which images you're going to score.

This will be ```--source_folder /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/FOLDER```.

FOLDER comes from the Folder column of the CDA_Image_Info Excel file - you can copy and paste it into the Terminal window.

- Telling CDAScorer the name of your output file.

This will be ```--file cdadata_YOURNAME_FOLDERID.csv``` e.g. cdadata_Josh_2.csv.

YOURNAME is your name.

FOLDERID comes from the FolderID column of the CDA_Image_Info Excel file.

- Telling CDAScorer how many CDAs are on each leaf.

This will be ```-n LEAFPERIMG```

LEAFPERIMG comes from the LeafPerImg column of the CDA_Image_Info Excel file.

##### Bringing this all together you will have a command that looks something like this:

```cdascorer --source_folder /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/FOLDER --file cdatdata_YOURNAME_FOLDERID.csv -n LEAFPERIMG```

And as an example for FolderID 1:

```cdascorer --source_folder /Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Fig2_leaf_images/A/HMAswap/MP/1/ --file cdadata_Raf_1.csv -n 6```

### Constructing your command (Windows):

You should have a Terminal window open, and have nagivated to the folder you want your recorded data to be stored.

Your command will consist of 4 elements:

- Running the CDAScorer program.

This will be ```cdascorer-windows.py```.

- Telling CDAScorer which images you're going to score.

This will be ```--source_folder Z:\Research-Groups\Mark-Banfield\Josh_Williams\FOLDER```.

FOLDER comes from the Folder column of the CDA_Image_Info Excel file - you can copy and paste it into the Terminal window.

- Telling CDAScorer the name of your output file.

This will be ```--file cdadata_YOURNAME_FOLDERID.csv``` e.g. cdadata_Josh_2.csv.

YOURNAME is your name.

FOLDERID comes from the FolderID column of the CDA_Image_Info Excel file.

- Telling CDAScorer how many CDAs are on each leaf.

This will be ```-n LEAFPERIMG```

LEAFPERIMG comes from the LeafPerImg column of the CDA_Image_Info Excel file.

##### Bringing this all together you will have a command that looks something like this:

```cdascorer-windows.py --source_folder Z:\Research-Groups\Mark-Banfield\Josh_Williams\FOLDER --file cdadata_YOURNAME_FOLDERID.csv -n LEAFPERIMG```

And as an example for FolderID 1:

```cdascorer-windows.py --source_folder Z:\Research-Groups\Mark-Banfield\Josh_Williams\Fig2_leaf_images\A\HMAswap\MP\1\ --file cdadata_Raf_1.csv -n 6```

