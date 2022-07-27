from sklearn.cluster import  KMeans
import numpy as np
from tqdm import tqdm
import random
from colors import get_classification_color
import visualize
  

        
    
#raus!!??    
def k_means_with_given_centroids( labels, points_to_cluster):
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


def k_means( centroids, points_to_cluster, iterations, plot=False):        
    print("starting k-means:")
    centroids = np.array(centroids)
    kmeans = KMeans(n_clusters=len(centroids) , max_iter=iterations,init=centroids, n_init=1, tol=0.01).fit(points_to_cluster)
    print("finish!")
    if plot:
        kmeans_labels = kmeans.labels_
       
        kmeans_color_map =visualize.label_to_color_map(points_to_cluster, kmeans_labels)

        visualize.plot_cluster(points_to_cluster, kmeans_color_map)
    return kmeans




