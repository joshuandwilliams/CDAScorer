import pandas as pd
import subprocess
import os

data = pd.read_csv("randomised_info.csv")

for index, row in data.iterrows():
    print(f"progress: {index}")
    in_dest = data.loc[index, '0']
    out_dest_1 = os.path.join("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May", data.loc[index,'scorer1'])
    out_dest_2 = os.path.join("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May", data.loc[index,'scorer2'])
    out_dest_3 = os.path.join("/Volumes/shared/Research-Groups/Mark-Banfield/Josh_Williams/Scoring_5May", data.loc[index,'scorer3'])
    
    print(in_dest)
    subprocess.run(["cp", in_dest, out_dest_1])
    print(out_dest_1)
    subprocess.run(["cp", in_dest, out_dest_2])
    print(out_dest_2)
    subprocess.run(["cp", in_dest, out_dest_3])
    print(out_dest_3)
