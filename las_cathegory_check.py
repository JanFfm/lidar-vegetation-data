from unicodedata import category
import numpy as np
import laspy   #needs also laszip to be installed
from pathlib import Path
import pyexasol
import pandas as pd
import open3d as o3d

import tqdm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



"""_summary_
check if a lidar-cetegory number (eg 10 for railway) is tagged in a  directory
prints all files with this category
"""
def check_dir(dir="./gelsenkirchen", cat=10, type="laz"):
    print("start")
    #read all .laz from current working dir
    las_file_path = []
    extension = '*.' +type
    for file in Path(dir).glob(extension):
        #print(file.name)
        las = laspy.read(file)
        print(file)
        category_list = las['classification']
        if cat in category_list:
            las_file_path.append(file)
            print("categrory ", cat, " in ", file)

check_dir()