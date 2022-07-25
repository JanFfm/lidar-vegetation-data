import pandas as pd
import numpy as np
from tqdm import tqdm
import csv
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import os

def make_featue_set(df_list, savepath='feature_list_color.csv', extract_colors=False):
    individuals = []
    features_list = []
    print("extracting trees:")    
    for df in tqdm(df_list):     
            cluster_ids = np.unique(np.array(df['Cluster_ID']).astype(int))
            for id in cluster_ids:
                    df_split =df[df['Cluster_ID'] == id]
                    individuals.append(df_split)
    
    print("extracting features:")
    for individuum in tqdm(individuals):
        features = [np.unique(np.array(df['GATTUNGS_ID']).astype(int))[0]]
        for df in [individuum,individuum[individuum.x > np.percentile(individuum.x ,75)] ,individuum[individuum.x < np.percentile(individuum.x ,25)], individuum[(np.percentile(individuum.x ,25) < individuum.x) & (individuum.x < np.percentile(individuum.x ,75))], individuum[individuum.y > np.percentile(individuum.y ,75)],individuum[individuum.y < np.percentile(individuum.y ,25)], individuum[(np.percentile(individuum.y ,25) < individuum.y) & (individuum.y < np.percentile(individuum.y ,75))], individuum[individuum.z > np.percentile(individuum.z ,75)],individuum[individuum.z < np.percentile(individuum.z ,25)], individuum[(np.percentile(individuum.z ,25) < individuum.z) & (individuum.z < np.percentile(individuum.z ,75))]]:
                
                xs = df['x']
                ys = df['y']
                zs = df['z']
                features +=[len(xs)]
                if extract_colors:
                        r  = df['red']
                        g  = df['green']
                        b  = df['blue']
                        nir  = df['nir']
                        all = list(zip(xs,ys,zs,r,g,b,nir))
                        features += extract([xs,ys,zs,r,g,b,nir])
                else:
                        all = list(zip(xs,ys,zs))
                        features += extract([xs,ys,zs])
                all=np.array(all)

        keys = ['feature_' + str(i) for i in range(len(features))]
        keys[0] = 'ID_GATTUNG'
        dic = dict(zip(keys, features))
        

        features_list.append(dic)
        
        
    
                
        
    with open(savepath, 'w', newline='') as csvfile:        
        writer = csv.DictWriter(csvfile, keys, extrasaction='ignore')
        writer.writeheader()                
        writer.writerows(features_list)


def extract(values):
        features = []
        for ax in values:
                features += [np.mean(ax), np.median(ax), np.min(ax), np.max(ax),np.std(ax)]
        return features
        










def make_images(list_of_points, gattung, save_path, counter):
        list_of_points = np.array(list_of_points)
        
        xz = np.zeros([256,256])        
        yz = np.zeros([256,256])
        xy = np.zeros([256,256])
        list_of_points = (list_of_points * 255).astype(int)
        for x,y ,z in list_of_points:
                xz[255 -z][x] += y
                yz[255- z][y] +=x
                xy[255 - y][x] += z
       
        img = np.array([xz, yz, xy]).transpose()
        m = np.max(img)
        img = (img/m) * 255 
        
        path = Path(os.path.join(save_path,str(gattung)))
        path.mkdir(parents=True, exist_ok=True)
        save_path = os.path.join(path, str(counter)+".png")      

        img = Image.fromarray(np.uint8(img)).rotate(270)
        img.save(save_path)


               
        
        
#make_images([[1,0,1],[0,1,0], [0.001, 0.33, 0.75]])

        

csv_folder ='clusters/dbscan'
extension = '*.csv' 

"""    

features_list = []
print("readinf files")

for file in tqdm(Path(csv_folder).glob(extension)):        
        df = pd.read_csv(file)
        features_list.append(df)     
   
make_featue_set(features_list)
"""
img_counter = 0
for file in tqdm(Path(csv_folder).glob(extension)):  
        individuals = []
        df = pd.read_csv(file)
        cluster_ids = np.unique(np.array(df['Cluster_ID']).astype(int))
        for id in cluster_ids:
                df_split =df[df['Cluster_ID'] == id]
                individuals.append(df_split)
        for ind in individuals:
                gattung = np.array(ind['GATTUNGS_ID'])[0]
                xs = ind['x']
                ys =ind['y']
                zs = ind['z']
                points = np.array([xs,ys,zs]).transpose()
                make_images(points, gattung, 'D://train_data_images_z_intensity_gelsenkirchen', img_counter)
                img_counter +=1


            
        