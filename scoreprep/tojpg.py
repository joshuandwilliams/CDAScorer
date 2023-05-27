import pandas as pd
import os
from PIL import Image

data = pd.read_csv("randomised_info.csv")

rotation_vals = pd.read_csv("rotation_vals.csv")

for index, row in data.iterrows():
    print(f"Progress: {index} / 88")
    in_dest = data.loc[index, '0']
    out_dest = os.path.join(f"{os.path.splitext(os.path.basename(in_dest))[0]}.jpg")
    print(in_dest)
    print(out_dest)

    orientation = rotation_vals['Orientation'][rotation_vals['Image'] == os.path.basename(in_dest)].values

    print(f"Rotating by {orientation * 90} degrees clockwise.")
    img = Image.open(in_dest)
    img = img.convert('RGB')
    img = img.rotate(-(orientation * 90), expand=1)
    img.save(out_dest, "JPEG", optimize=True, quality=10)