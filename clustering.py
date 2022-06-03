from array import array
from operator import length_hint
from tabnanny import verbose
from sklearn.cluster import DBSCAN, KMeans

import open3d as o3d

import laspy
import numpy as np
from tqdm import tqdm

import random

import plot_las
exclude = [2]
e_2 = [ i for i in range(6, 19)]
exclude = exclude + e_2
def check_classification(x_1,y_2,z_2, classification):
    if classification not in exclude:
        return True
    else:
        return False


def dbscan():

    print(exclude)
    las = laspy.read("colored_files_gelsenkirchen/3dm_32_293_5647_1_nw.laz")
    length = len(las.points['x'])
    print(length)
    x = las.points['x']
    y = las.points['y']
    z = las.points['z']
    classification = las.points['classification']
    number_of_returns = las.points['number_of_returns']
    print(number_of_returns)
    
    #plot_las.plot3d(las)
    r = las.points['red'] /255
    g = las.points['green'] /255
    b = las.points['blue'] /255
    # number_of_returns[i] > 1 and 
    
    print("selectiong points for clustering")
    #### das exclude ist halt sehr lidar-nrw-spezifisch!!!!
    #### bei number of returns > 2 bleiben die lsiten leer!
    large_cluster_points = np.array([[x[i], y[i], z[i]] for i in tqdm(range(length)) if (classification[i] not in exclude )]) 
    small_cluster_points = np.array([[x[i], y[i], z[i]] for i in tqdm(range(length)) if (number_of_returns[i] > 1 and classification[i] not in exclude )]) 
    #x, y, z, _ = zip(*filter(check_classification(), zip(x,y,z, classification)))
    #all_cluster_points = np.array([x, y, z]).transpose((1, 0))
    #print(all_cluster_points)
    print("selecting indices:")
    large_indices = np.array([i for i in tqdm(range(length)) if (classification[i] not in exclude)]) 
    small_indices = np.array([i for i in tqdm(range(length)) if (number_of_returns[i] > 1 and classification[i] not in exclude)])
    
    print("clustering")
    large_cluster = DBSCAN(eps=1, min_samples=1).fit(large_cluster_points)  # parameters according to https://www.degruyter.com/document/doi/10.1515/geo-2020-0266/html?lang=de
     
    large_labels = large_cluster.labels_
    
    small_cluster  = DBSCAN(eps=1, min_samples=1).fit(small_cluster_points) 
    small_labels = small_cluster.labels_
    
    print("plotting:")
    plot_labels_with_sat(large_cluster_points, large_labels, large_indices, x, y, z, r, g, b)
    plot_labels_with_sat(small_cluster_points, small_labels, small_indices, x, y, z, r, g, b)
    """
    centroids = np.array([])
    visited_labels =np.array([])
    




    for point, label in tqdm(zip(small_cluster_points, small_labels)):
        if label not in visited_labels:
            if point in large_cluster_points:                
                centroids = np.append(centroids, point)
                visited_labels=np.append(visited_labels, label)
    # jetzt ist aus jedem label ein punkt in centroids
    print("found ", len(centroids) , "small clusters")
                
    final_labels = np.empty(0)
    final_points = np.empty(0)
    final_indices = np.empty(0)

    i = 0
    #hier muss auch noch ne visited_sache für die punkte im große set rein
    for i in tqdm(range(len(centroids))):
        point = centroids[i]
        #final_points.append(point)
        #final_labels.append(i)
        
        index= np.where(large_cluster == point)   #das == stimmt nicht..
        label = large_labels[index]
        for i in range(len(large_labels)):
            if large_labels[i] == label:
                    final_points= np.append(final_points, large_cluster[i])
                    final_labels= np.append(final_labels, i)
                    final_indices= np.append(final_indices, large_indices[i])
                
        
        
        
    #points_2d = points[][:1]
    #print("2d shape", points_2d.shape)
   # print("all points, idicies:", all_cluster_points.shape, indices.shape)
    #all_points_number = all_cluster_points.shape[0]
    #print("number of points", all_points_number)
    # ep 0.5 ist zu kein  #ok: 0.75|1
    
    

    #filter unlabeld points:
    print("unfiltered: points, labels", final_points.shape, final_labels.shape)

"""
def plot_labels_with_sat(final_points, final_labels, final_indices, x, y, z, r, g, b):
    points, labels, indices= zip(*((p, l, i) for p, l,i in zip(final_points, final_labels, final_indices) if l > -1))
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
    
    
    
    for j in tqdm(range(len(indices))):
        r[indices[j]] = color_map[j][0]
        g[indices[j]] = color_map[j][1]
        b[indices[j]] = color_map[j][2]
    colors = np.array([r, g, b]).transpose((1, 0))
    point_cloud = np.array([x, y, z]).transpose((1, 0))
    #print("colors, points, labels, ",len(colors), all_points_number, labels.max() +1)
    
    plot_cluster(point_cloud, colors)
    
    #k_means(labels.max()-1 ,all_cluster_points)
    
    
def k_means(cluster_number, points_to_cluster):
    kmeans = KMeans(n_clusters=cluster_number, max_iter=3, n_init=1, tol=0.01, verbose=100).fit(points_to_cluster)
    kmeans_labels = kmeans.labels_
    kmeans_label_number = kmeans_labels.max() +1 
    kmeans_label_color =  np.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(kmeans_label_number))]) / 255
    print("label_colors", kmeans_label_color.shape)
    kmeans_color_map = np.array([[kmeans_label_color[kmeans_labels[i]][0], kmeans_label_color[kmeans_labels[i]][1],kmeans_label_color[kmeans_labels[i]][2]] for i in tqdm(range(point_number))])

    plot_cluster(points_to_cluster, kmeans_color_map)

def plot_cluster(points, colors):
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(points)
    geom.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([geom])

dbscan()