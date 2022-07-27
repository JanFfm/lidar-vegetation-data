import numpy as np
from tqdm import tqdm
import csv
from pathlib import Path
from PIL import Image
import os

def make_featue_set(df_list, savepath='feature_list_color.csv', extract_colors=False):
        """_summary_

        Args:
        df_list (list): list of pandas.DataFrame
        savepath (str, optional): _description_. Defaults to 'feature_list_color.csv'.
        extract_colors (bool, optional): _description_. Defaults to False.
        """
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
        """_summary_

        Args:
        values (_type_): _description_

        Returns:
        _type_: _description_
        """
        features = []
        for ax in values:
                features += [np.mean(ax), np.median(ax), np.min(ax), np.max(ax),np.std(ax)]
        return features    




def make_images(list_of_points, gattung, save_path, counter):
        """_summary_

        Args:
            list_of_points (_type_): _description_
            gattung (_type_): _description_
            save_path (_type_): _description_
            counter (_type_): _description_
        """
        
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


               

        