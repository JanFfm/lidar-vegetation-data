import imp
import laspy
import open3d as o3d
import numpy as np
from pathlib import Path

"""
Based on https://medium.com/spatial-data-science/an-easy-way-to-work-and-visualize-lidar-data-in-python-eed0e028996c


"""


las_file_path = []
path = "./gelsenkirchen"
for file in Path(path).glob('*.laz'):
    #print(file.name)
    las_file_path.append(file)
    
las = laspy.read(las_file_path[0])
color_map = np.array(las['classification'])
color_map = color_map / color_map.max() # scale to [0 ,.., 1]
color_map = np.array([color_map, color_map, color_map]).transpose((1, 0))
print(color_map)

print(list(las.point_format.dimension_names))
point_data = np.stack([las.X, las.Y,las.Z], axis=0).transpose((1, 0))
print(point_data)



geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(point_data)

geom.colors = o3d.utility.Vector3dVector(color_map)
o3d.visualization.draw_geometries([geom])


"""

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

print(las.xyz[0])
print(las.header.global_encoding)
print(las.header.x_max)
print(las.header.x_min)
print(las.header.y_max)
print(las.header.y_min)
print(las.header.file_source_id)
print(las.header.DEFAULT_POINT_FORMAT)
print(las.X)
print(las.Y)
print(las.header.extra_header_bytes)
"""
"""

points = las.points.copy()

#scale [0.01 0.01 0.01]
#offet[     -0. 5000000.      -0.]

geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(points)
o3d.visualization.draw_geometries([geom])
"""
"""
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
"""