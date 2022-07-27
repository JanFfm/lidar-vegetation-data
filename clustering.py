from sklearn.cluster import DBSCAN, KMeans

import open3d as o3d

import laspy
import numpy as np
from tqdm import tqdm

import random

from colors import get_classification_color
import os
import visualize



def dbscan_1(include_med_veg = False):

    las = laspy.read(os.path.join(os.getcwd(),"lidar-files/4merged/Wesel/3dm_32_341_5726_1_nw.laz")) 
    
    length = len(las.points['x'])
    print(length)
    x = las.points['x']
    y = las.points['y']
    z = las.points['z']
    classification = las.points['classification']
    number_of_returns = las.points['number_of_returns']
    print(number_of_returns)

    
    print("selectiong points for clustering")
    #### das exclude ist halt sehr lidar-nrw-spezifisch!!!!
    #### bei number of returns > 2 bleiben die lsiten leer!
    if include_med_veg:
        points_to_cluster = np.array([[x[i], y[i], z[i]] for i in tqdm(range(length)) if (classification[i] == 4 or classification[i] == 5)]) 
        print("selecting indices:")

        indices_of_cluster_points = np.array([i for i in tqdm(range(length)) if (classification[i] == 4 or classification[i] == 5)]) 
    else:
        points_to_cluster = np.array([[x[i], y[i], z[i]] for i in tqdm(range(length)) if (classification[i] == 5)]) 
        print("selecting indices:")
        indices_of_cluster_points = np.array([i for i in tqdm(range(length)) if (classification[i] == 5)]) 
    #x, y, z, _ = zip(*filter(check_classification(), zip(x,y,z, classification)))
    #all_cluster_points = np.array([x, y, z]).transpose((1, 0))
    #print(all_cluster_points)
    return points_to_cluster, indices_of_cluster_points, x, y, z, classification
  
def dbscan_2(points_to_cluster, indices_of_cluster_points, x, y, z, classification, eps=1,min_samples=1):   
    print("clustering")
    cluster = DBSCAN(eps=eps, min_samples=min_samples).fit(points_to_cluster)  # parameters according to https://www.degruyter.com/document/doi/10.1515/geo-2020-0266/html?lang=de
     
    large_labels = cluster.labels_
    


    
    print("plotting:")
    plot_labels_with_sat(points_to_cluster, large_labels, indices_of_cluster_points, x, y, z, None, classification,show_no_clusters=True)
    plot_labels_with_sat(points_to_cluster, large_labels, indices_of_cluster_points, x, y, z, None, classification)

    print("start k means")
    k_means(large_labels, points_to_cluster)

    

        
    
#raus!!??    
def k_means( labels, points_to_cluster):
    used_labels = []
    centroids= []
    print("number of labels: ", labels.max())
    for i in tqdm(range(len(labels))):
        if(labels[i] not in used_labels and labels[i] != -1):
            used_labels.append(labels[i])
            centroids.append(points_to_cluster[i])    
    print("number of centroids: ", len(centroids), len(used_labels))        
        
    print("starting k-means:")
    centroids = np.array(centroids)
    kmeans = KMeans(n_clusters=len(centroids) , max_iter=30,init=centroids, n_init=1, tol=0.01).fit(points_to_cluster)
    print("finish!")
    kmeans_labels = kmeans.labels_
    kmeans_label_number = kmeans_labels.max() +1 
    kmeans_label_color =  np.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(kmeans_label_number))]) / 255
    print("label_colors", kmeans_label_color.shape)
    kmeans_color_map = np.array([[kmeans_label_color[kmeans_labels[i]][0], kmeans_label_color[kmeans_labels[i]][1],kmeans_label_color[kmeans_labels[i]][2]] for i in tqdm(range(len(points_to_cluster)))])

    visualize.plot_cluster(points_to_cluster, kmeans_color_map)


"""Die kann eigentlich raus:"""
def k_means_no_dbscan( centroids, points_to_cluster, iterations, plot=False):        
    print("starting k-means:")
    centroids = np.array(centroids)
    kmeans = KMeans(n_clusters=len(centroids) , max_iter=iterations,init=centroids, n_init=1, tol=0.01).fit(points_to_cluster)
    print("finish!")
    if plot:
        kmeans_labels = kmeans.labels_
       
        kmeans_color_map =visualize.label_to_color_map(points_to_cluster, kmeans_labels)

        visualize.plot_cluster(points_to_cluster, kmeans_color_map)
    return kmeans





#points_to_cluster, indices_of_cluster_points, x, y, z, classification = dbscan_1()
#eps = [2] #0.9]
#mins = [14]#  6]
#for e in eps:
#    for m in mins:
#        print("eps: ", e, " min_points: ", m)
#        dbscan_2(points_to_cluster, indices_of_cluster_points, x, y, z, classification,e,m)