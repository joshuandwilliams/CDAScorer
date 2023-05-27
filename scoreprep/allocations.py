import pandas as pd
import numpy as np
import os

hashdata, imginfo = pd.read_csv("tif_hashes.csv"), pd.read_csv("image_info.csv")

imagepaths = hashdata.sample(frac=1).reset_index()

cda_count = 0
cda_cutoff = sum(imginfo['CDA_Count_Image']/8)

def retrieve_count(path):
    match_index = imginfo['Image'][imginfo['Image'] == os.path.basename(path)].index[0]
    return imginfo.loc[match_index, 'CDA_Count_Image']

for index, row in imagepaths.iterrows():
    imagepaths.loc[index, 'count'] = retrieve_count(imagepaths.loc[index,'0'])
    imagepaths.loc[index, 'basename'] = os.path.basename(imagepaths.loc[index,'0'])

    

imagepaths = imagepaths.drop_duplicates(subset=['basename'], keep='first')

for index, row in imagepaths.iterrows():
    cda_count += imagepaths.loc[index, 'count']
    if cda_count > cda_cutoff:
        print(cda_count)
        cda_count = 0
print(cda_count)
print(sum(imagepaths['count']))

imagepaths.to_csv("randomised_info.csv")