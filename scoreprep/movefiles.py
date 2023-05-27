import pandas as pd
import subprocess
import os
from PIL import Image

data = pd.read_csv("randomised_info.csv")

rotation_vals = pd.read_csv("rotation_vals.csv")

for index, row in data.iterrows():
    print(f"Progress: {index} / 88")
    in_dest = data.loc[index, '0']
    print(in_dest)
    out_dest_1 = os.path.join("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May", data.loc[index,'scorer1'])
    out_dest_2 = os.path.join("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May", data.loc[index,'scorer2'])
    out_dest_3 = os.path.join("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May", data.loc[index,'scorer3'])

    orientation = rotation_vals['Orientation'][rotation_vals['Image'] == os.path.basename(in_dest)].values

    if orientation != 0:
        print(f"Rotating by {orientation * 90} degrees clockwise.")
        img = Image.open(in_dest)
        img = img.rotate(-(orientation * 90), expand=1)
        img.save(os.path.basename(in_dest), "TIFF")
        print(out_dest_1)
        subprocess.run(["cp", os.path.basename(in_dest), out_dest_1])
        print(out_dest_2)
        subprocess.run(["cp", os.path.basename(in_dest), out_dest_2])
        print(out_dest_3)
        subprocess.run(["cp", os.path.basename(in_dest), out_dest_3])
    else:
        print(out_dest_1)
        subprocess.run(["cp", in_dest, out_dest_1])
        print(out_dest_2)
        subprocess.run(["cp", in_dest, out_dest_2])
        print(out_dest_3)
        subprocess.run(["cp", in_dest, out_dest_3])
