import imp
import laspy
import open3d as o3d
import numpy as np
from pathlib import Path

"""
    las_file_path = []
    path = "./gelsenkirchen"
    for file in Path(path).glob('*.laz'):
        #print(file.name)
        las_file_path.append(file)
        
Based on https://medium.com/spatial-data-science/an-easy-way-to-work-and-visualize-lidar-data-in-python-eed0e028996c


"""
def plot_3d(file, color='classification'):

        
    las = laspy.read(file)
    color_map = np.array(las[color])
    color_map = color_map / color_map.max() # scale to [0 ,.., 1]
    color_map = np.array([color_map, color_map, color_map]).transpose((1, 0))

    point_data = np.stack([las.X, las.Y,las.Z], axis=0).transpose((1, 0))

    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)

    geom.colors = o3d.utility.Vector3dVector(color_map)
    o3d.visualization.draw_geometries([geom])
 
"""
can set 'category' or other las-index as Z dimension, which is also default color map
much faster than plot 3d 

"""    
def plot2d(file="./gelsenkirchen/3dm_32_293_5650_1_nw.laz", color='classification'):
    las = laspy.read(file)
    #color_map = np.array(las[color])
    #color_map = color_map / color_map.max() # scale to [0 ,.., 1]
    #color_map = np.array([color_map, color_map, color_map]).transpose((1, 0))
    #print(color_map)

    point_data = np.stack([las.X, las.Y,las[color]], axis=0).transpose((1, 0))

    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)

    #geom.colors = o3d.utility.Vector3dVector(color_map)
    o3d.visualization.draw_geometries([geom])
    

plot2d()