import numpy as np
import laspy   #needs also laszip to be installed
from pathlib import Path
import pyexasol
import pandas as pd


import tqdm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

path="./gelsenkirchen"

#read all .laz from current working dir
las_file_path = []
for file in Path(path).glob('*.laz'):
    #print(file.name)
    las_file_path.append(file)
    
las = laspy.read(las_file_path[0])
print(las.header)  
#<LasHeader(1.2, <PointFormat(1, 0 bytes of extra dims)>)>
labels = list(las.point_format.dimension_names)
point_number = len(las.points)
print("number of points: ", point_number)
print(labels)


points = las.points.copy()

# getting scaling and offset parameters
las_scaleX = las.header.scale[0]
las_offsetX = las.header.offset[0]
las_scaleY = las.header.scale[1]
las_offsetY = las.header.offset[1]
las_scaleZ = las.header.scale[2]
las_offsetZ = las.header.offset[2]

# calculating coordinates
p_X = np.array((points['X'] * las_scaleX) + las_offsetX)
p_Y = np.array((points['Y'] * las_scaleY) + las_offsetY)
p_Z = np.array((points['Z'] * las_scaleZ) + las_offsetZ)

# plotting points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(p_X, p_Y, p_Z, c='r', marker='o')
plt.show()