import open3d as o3d
import numpy as np
import random
from tqdm import tqdm
from colors import get_classification_color

def plot_las_3d(las, color=None):
    """
    build 3D Visualisation of lidar Data. Creates color channel from rgb or classification values
    """

    if color == None or color == 'rgb':
        color_map = np.array([las.points['red'] /255, las.points['green'] /255, las.points['blue'] /255]).transpose((1, 0))
    elif color=='nir':
        color_map = np.array([las.points['nir'] /255, las.points['red'] /255, las.points['blue'] /255]).transpose((1, 0))
        
    elif color =="classification":
        color_map = np.array(list(map(get_classification_color, las.points[color])))

    
        
    print(color_map)

    
    
    point_data = np.stack([las.X, las.Y,las.Z], axis=0).transpose((1, 0))

    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)
    geom.colors = o3d.utility.Vector3dVector(color_map)
    o3d.visualization.draw_geometries([geom])
 

def plot_las_2d(las, color='classification'):
    """2d visualisation of lidar data (faster then 3d)

    Args:
        las (laspy.las): las_ffiel
        color (str, optional): lidar-value groupt to colorize data. Defaults to 'classification'.
    """
    point_data = np.stack([las.X, las.Y,las[color]], axis=0).transpose((1, 0))
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)
    o3d.visualization.draw_geometries([geom])


def label_to_color_map(labels):
    """creates a color map for a list of labels

    Args:
        labels (lsit): list of labels

    Returns:
        list: coor map with color for each label
    """
    labels = np.array(labels)
    label_number = labels.max() +1 
    label_colors =  np.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(label_number))]) / 255
    print("label_colors", label_colors.shape)
    return  np.array([[label_colors[labels[i]][0], label_colors[labels[i]][1],label_colors[labels[i]][2]] for i in tqdm(range(len(labels)))])


def draw_point_cloud(points, colors):
    """makes the visualisation i open§D

    Args:
        points (list): point cloud
        colors (list): color values for each point
    """
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(points)
    geom.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([geom])


def merge_class_with_labels(points, labels, inices, classifications):
    """paints each point according to their classification
    afterwards, paint each cluster in a certain color

    Args:
        points (list): list of 3d points
        labels (list): list of labeling for each point
        inices (list): inidices of points i riginal lidar data
        classifications (list): classification values

    Returns:
        list: color map for each point
    """
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
    return colors  
    


def merge_colors_with_labels(points, labels, inices, rgb):
    """paints each point according to their r g b values
    afterwards, paint each cluster in a certain color

    Args:
        points (list): list of 3d points
        labels (list): list of labeling for each point
        inices (list): inidices of points i riginal lidar data
        rgb (list): rgb values for each point

    Returns:
        list: color map for each point
    """
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
    return colors  
    
    

