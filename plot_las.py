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
    
las = laspy.read(las_file_path[1])
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

