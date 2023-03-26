---
permalink: /mac_install/
title: "Getting CDAScorer Running: Mac"
classes: wide
toc: true
---

## Step 1: Make sure you are connected to Eduroam

## Step 2: Map the Banfield shared drive to your Finder

Right click on finder and select "Connect to Server".

In the top bar it should say "smb://nbi-ufiles". Click "Connect".

Then click on "Shared" and click "Ok".

## Step 3: Make sure Python is installed

Open up a Terminal window and type "python3 -V". If Python 3.11.2 (replace with your version number) appears, Python is installed.

If an error occurs or if your version is older than 3.9, head to [the Python download page](https://python.org/downloads/) and click on the yellow button "Download Python 3.11.2". Then click on your download and work through the installer.

Once complete, "python3 -V" should work.

## Step 4: Make sure Anaconda is installed

In the Terminal window, type "conda env list". If you get a list of filepaths headed by "conda environments:", Anaconda is installed.

If an error occurs, head to [the Anaconda download page](https://www.anaconda.com/products/distribution) and click on the green button "Download". Then click on your download and work through the installer (warning - this can take a while so you'll need to be patient).

Once complete, "conda env list" should work.

## Step 5: Navigate to where you want to store your scoring data outputs.

Use the cd (change directory) command in the cmd window to navigate to an empty folder location you'd like to store your files. For example, if you have a folder called CDAScorer_Data in your Documents folder, you could navigate there by typing "cd /Documents/CDAScorer_Data/".

## Step 6: Creating a conda environment

We installed Anaconda so we can run packages inside what is effectively a sealed box on your computer. So that if the packages make any changes to local or global settings, they are contained and don't make permanent changes to your computer. This box is called a conda environment.

To create a conda environment for scoring, type ```conda create --name CDAScorer```. This creates an environment called CDAScorer.

Then activate this environment (stepping inside the sealed box), and this can be done by typing ```conda activate CDAScorer```. You should now see that at the start of your line it says (CDAScorer). Every time you open the Terminal window, if your environment is (base) you should activate a conda environment.

## Step 7: Downloading the CDAScorer package

To download my CDAScorer package, we use pip, which comes with Python. Do this using the code ```pip install cdascorer```.

This will install my package as well as any other Python packages it depends on to run.

## Step 8: Running the CDAScorer package with test data

Now you are all set to run the program. Run a the test program to verify that it works with the following command ```cdascorer-test```

When you enter that command, a user interface should appear. You can press the exit button in the top left to quit.

If you enter "ls" into the Terminal window, you should see two new files, one called "test_cdata.csv" and one called "backup_X_test_data.csv", where X is replaced with the day, month, year, hour, minute.

This is great! It means the package is running successfully on your laptop.
