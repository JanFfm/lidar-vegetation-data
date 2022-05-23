from operator import length_hint
from sklearn.cluster import DBSCAN, KMeans

import open3d as o3d

import laspy
import numpy as np
from tqdm import tqdm

import random

import plot_las



def dbscan():
    exclude = [2]
    e_2 = [ i for i in range(6, 19)]
    exclude = exclude + e_2
    print(exclude)
    las = laspy.read("colored_files_gelsenkirchen/3dm_32_290_5647_1_nw.laz")
    length = len(las.points['x'])
    print(length)
    x = las.points['x']
    y = las.points['y']
    z = las.points['z']
    classification = las.points['classification']
    print(x)
    
    #plot_las.plot3d(las)
    
    points = np.array([[x[i], y[i], z[i]] for i in tqdm(range(length)) if classification[i] not in exclude])
    print(points.shape)
    point_number = points.shape[0]
    print("number of points", point_number)
    clustering = DBSCAN(eps=1, min_samples=5).fit(points)  # parameters according to https://www.degruyter.com/document/doi/10.1515/geo-2020-0266/html?lang=de
    
    
    labels = clustering.labels_
    print("labels ", labels)
    label_number = (labels.max() + 2)
    print("shape labels", labels.shape)
    print("label number ",  label_number)
    label_colors = np.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(label_number))]) / 255
    label_colors[0] = [0,0,0]
    print("label_colors", label_colors.shape)
    color_map = np.array([[label_colors[labels[i] + 1 ][0], label_colors[labels[i]][1 +1],label_colors[labels[i]][2] +1] for i in tqdm(range(point_number))])
    print("color_map shape", color_map.shape)
    print(color_map)
    
    plot_cluster(points, color_map)
    
    
    kmeans = KMeans(n_clusters=label_number, max_iter=20).fit(points)
    kmeans_labels = kmeans.labels_
    kmeans_label_number = kmeans_labels.max() +1 
    kmeans_label_color =  np.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(kmeans_label_number))]) / 255
    print("label_colors", kmeans_label_color.shape)
    kmeans_color_map = np.array([[kmeans_label_color[kmeans_labels[i]][0], kmeans_label_color[kmeans_labels[i]][1],kmeans_label_color[kmeans_labels[i]][2]] for i in tqdm(range(point_number))])

    plot_cluster(points, kmeans_color_map)

def plot_cluster(points, colors):
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(points)
    geom.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([geom])
    

dbscan()