import imp
import laspy
import open3d as o3d
import numpy as np
from pathlib import Path
import random
from tqdm import tqdm
from colors import get_classification_color


"""
    las_file_path = []
    path = "./gelsenkirchen"
    for file in Path(path).glob('*.laz'):
        #print(file.name)
        las_file_path.append(file)
        
Based on https://medium.com/spatial-data-science/an-easy-way-to-work-and-visualize-lidar-data-in-python-eed0e028996c

color elem of: ['X', 'Y', 'Z', 'intensity', 'return_number', 'number_of_returns', 'scan_direction_flag',  'edge_of_flight_line', 'classification', 'synthetic', 'key_point', 'withheld', 'scan_angle_rank', 'user_data', 'point_source_id', 'gps_time'] 
"""
def plot_las_3d(las, color=None):
    """
    """        
    #las = laspy.read(file)
    #color_map = np.array(las[color])
    #color_map = color_map / color_map.max() # scale to [0 ,.., 1]
    #color_map = np.array([color_map, color_map, color_map]).transpose((1, 0))
    if color == None or color == 'rgb':
        color_map = np.array([las.points['red'] /255, las.points['green'] /255, las.points['blue'] /255]).transpose((1, 0))
        
    elif color =="classification":
        color_map = np.array(las[color])
        alt_map = np.ones([1, len(color)]) /2
        print("colr_ap", color_map)
        print("alt_ap", alt_map)
        color_map = color_map / color_map.max() # scale to [0 ,.., 1]
        color_map = np.array([color_map, color_map, color_map]).transpose((1, 0))
    
        
    print(color_map)

    
    
    point_data = np.stack([las.X, las.Y,las.Z], axis=0).transpose((1, 0))

    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)
    geom.colors = o3d.utility.Vector3dVector(color_map)
    o3d.visualization.draw_geometries([geom])
 
"""
can set 'category' or other las-index as Z dimension, which is also default color map
much faster than plot 3d 
color elem of: ['X', 'Y', 'Z', 'intensity', 'return_number', 'number_of_returns', 'scan_direction_flag',  'edge_of_flight_line', 'classification', 'synthetic', 'key_point', 'withheld', 'scan_angle_rank', 'user_data', 'point_source_id', 'gps_time'] 
"""    
def plot_las_2d(las, color='classification'):
    """_summary_

    Args:
        las (_type_): _description_
        color (str, optional): _description_. Defaults to 'classification'.
    """
    point_data = np.stack([las.X, las.Y,las[color]], axis=0).transpose((1, 0))
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)
    o3d.visualization.draw_geometries([geom])
    
#las= laspy.read("gelsenkrichen classified/test1color.laz")
#plot3d(las)

def label_to_color_map(labels):
     labels = np.array(labels)
     label_number = labels.max() +1 
     label_colors =  np.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(label_number))]) / 255
     print("label_colors", label_colors.shape)
     return  np.array([[label_colors[labels[i]][0], label_colors[labels[i]][1],label_colors[labels[i]][2]] for i in tqdm(range(len(labels)))])


def draw_point_cloud(points, colors):
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(points)
    geom.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([geom])


def merge_class_with_labels(points, labels, inices, classifications):
    points, labels, indices= zip(*((p, l, i) for p, l,i in zip(points, labels, inices) if l > -1))
    points = np.array(points)
    labels = np.array(labels)
    indices = np.array(indices)
    if -1 in labels:
            factor = 1
    else:
        factor= 0
    label_number = (labels.max() + 1 + factor)
    point_number = points.shape[0]

    label_colors = np.array([[random.randint(1, 255) /255, random.randint(1, 255) /255, random.randint(1, 255) /255] for i in tqdm(range(label_number))]) 
    color_map = np.array([[label_colors[labels[i] + factor ][0], label_colors[labels[i]+ factor][1],label_colors[labels[i]+ factor][2]] for i in tqdm(range(point_number))])


    print("colorize points by classification-number:")
    colors = np.array([get_classification_color(classifications[i])for i in tqdm(range(len(classifications)))])
    print("painting clusters:")
    for j in tqdm(range(len(indices))):
        colors[indices[j]] = color_map[j]    
    return color_map  
    


def merge_colors_with_labels(points, labels, inices, rgb):
    points, labels, indices= zip(*((p, l, i) for p, l,i in zip(points, labels, inices) if l > -1))
    points = np.array(points)
    labels = np.array(labels)
    indices = np.array(indices)
    print("filtered: points, labels, indices", points.shape, labels.shape, indices.shape)

    point_number = points.shape[0]
    #factor is needed for handling label -1 in indices:
    if -1 in labels:
        factor = 1
    else:
        factor= 0

    print("facator:", factor)
    label_number = (labels.max() + 1 + factor)
    print("shape labels", labels.shape)
    print("label number ",  label_number)
    label_colors = np.array([[random.randint(1, 255) /255, random.randint(1, 255) /255, random.randint(1, 255) /255] for i in tqdm(range(label_number))]) 
    #label_colors[0] = [1,1,1]
    print("label_colors", label_colors.shape)
    color_map = np.array([[label_colors[labels[i] + factor ][0], label_colors[labels[i]+ factor][1],label_colors[labels[i]+ factor][2]] for i in tqdm(range(point_number))])
    print("color_map shape, indices", color_map.shape)   

 
    r,g,b = rgb
    print("painting clusters:")
    for j in tqdm(range(len(indices))):
            r[indices[j]] = color_map[j][0]
            g[indices[j]] = color_map[j][1]
            b[indices[j]] = color_map[j][2]
    colors = np.array([r, g, b]).transpose((1, 0))
    for j in tqdm(range(len(indices))):
            colors[indices[j]] = color_map[j]    
    return color_map  
    
    

