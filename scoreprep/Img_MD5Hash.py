import hashlib
import pandas as pd
import glob
from pathlib import Path

# Get list of TIF or tif filepaths in Joshua_Williams folder
source_folder = Path("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/")
image_files = [str(file.resolve()) for file in Path(source_folder).rglob("*") if
                   file.is_file() and not file.name.startswith(".") and
                   (file.name.endswith(".tif") or file.name.endswith(".TIF"))]

# Loop through list, and append to csv.
def file_as_bytes(file):
    with file:
        return file.read()

tif_hashes = []
Count = 0
for file in image_files:
    hash = hashlib.md5(file_as_bytes(open(file, 'rb'))).hexdigest()
    tif_hashes.append([file, hash])
    Count += 1
    print(Count)

# Save csv
df = pd.DataFrame(tif_hashes)
df.to_csv("tif_hashes.csv", index=False)

# Checking equal images with different paths have same hash
"""
Path1 = "/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/M1RGA5_M1APB_APia_scoring/211106-images/_DSC0023.tif"
Hash1 = hashlib.md5(file_as_bytes(open(Path1, 'rb'))).hexdigest()
print(Hash1)
Path2 = "/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Data_link_test/211106-images/_DSC0023.tif"
Hash2 = hashlib.md5(file_as_bytes(open(Path2, 'rb'))).hexdigest()
print(Hash2)
"""
# They do!