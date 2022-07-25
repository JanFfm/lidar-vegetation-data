from scipy import ndimage as ndi
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage import median_filter
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage import img_as_float
from PIL import Image
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.affinity import scale

import laspy
from sklearn.cluster import DBSCAN
import numpy
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import coord_f
import folium
import visualize
import db_settings
import geopandas
import pandas
from datetime import datetime
from pathlib import Path
import warnings
import random

def save(id,tree_id, gattung_id, save_path_id, algo_id):   
    req = """ ("""+str(id) + """, """+str(tree_id)+""", """+str(gattung_id)+""", """+str(save_path_id)+""", """+str(algo_id)+"""),"""
    #x, y, z = numpy.array(points).transpose()
    #las = create_new_las.build_las(las_scale_factor, x,y,z, header=header)     
    return req #, las
def cluster(file, save_path_id, save_doubles_id,city_code, classes_to_cluster = [5], limit=7000000):
    warnings.filterwarnings("ignore")
    print("starting with ", file)
    start_time = datetime.now()
    print("time: ", start_time)
    #prepare saving:
    print("connecting to database:")
    db =db_settings.db(autocommit=False)
    print("requseting database")

    db_file_name = str(file).split('/')[-1].split('\\')[-1].split('.')[0]
    print(db_file_name)
    req = """SELECT ID, NUMBER_OF_TREES FROM lidar_proj.LIDAR_FILES WHERE FILE_NAME = \'"""+db_file_name+"""\'"""
    print(req)
    lidar_file_number = db.export_to_pandas(req)
    print("lidar file id:", lidar_file_number['ID'][0], " NUMBER_OF_TREES: ", lidar_file_number['NUMBER_OF_TREES'][0])
    req ="""SELECT * FROM lidar_proj.trees WHERE city_ID=""" + str(city_code) +""" and LIDAR_FILE_ID="""+str(lidar_file_number['ID'].values[0])+""" ORDER BY id"""
    print(req)
    trees =db.export_to_pandas(req)
    print (trees)
    if (len(trees) == 0):
        print("#######################################")
        print("NO TREES FOUND")
        print("#######################################")
    else:

        print("complete")

        print("prepare saving:")

        max_id = db.export_to_pandas("""SELECT max(id) FROM lidar_proj.cluster""")['MAX(CLUSTER.ID)'][0]
        if numpy.isnan(max_id):
            max_id = 0
        else:
            max_id=int(max_id)
        print("starting with id=", max_id)
        
        save_to = db.export_to_pandas("""SELECT save_path FROM lidar_proj.cluster_path where id="""+ str(save_path_id))['SAVE_PATH'][0]
        
        save_to = os.path.join(os.getcwd(), "clusters", save_to)
        print("savepath: ", save_to)
        save_doubles_to = db.export_to_pandas("""SELECT save_path FROM lidar_proj.cluster_path where id="""+ str(save_doubles_id))['SAVE_PATH'][0]
        print(save_to)
        save_doubles_to = os.path.join(os.getcwd(),"clusters", save_doubles_to)
        print("savepath doubles: ", save_doubles_to)
        if not os.path.exists(save_doubles_to):
            Path.mkdir(Path(save_doubles_to),parents=True, exist_ok=True)
        if not os.path.exists(save_to):
            Path.mkdir(Path(save_to), parents=True, exist_ok=True)
        csv_save_path = str(save_to)+'/' + str(file).split('.')[0].split('/')[-1].split('\\')[-1] +'_clusters.csv'
        csv_save_path_doubles = str(save_doubles_to)+'/' + str(file).split('.')[0].split('/')[-1].split('\\')[-1]  +'_clusters_doubles.csv'
        print("csv saved to: ", csv_save_path, " ", csv_save_path_doubles)
        if not os.path.exists(csv_save_path):
            

            print("read las file...")

            algo_id = 1 #references dbsvan
            print("read las: ", file)
            las = laspy.read(file)
            #las_points_x = numpy.array(las.points['x']) 
            #las_points_y = numpy.array(las.points['y'])
            #x_max, x_min, y_max, y_min = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()
            #x_range = x_max - x_min
            #y_range = y_max - y_min
            
            #ength = len(las.points['x'])    
            
            print("selecting points to cluster by classification")
            p_t_c= numpy.array([las.points['x'], las.points['y'], las.points['z']]).transpose()
            points_to_cluster = p_t_c[las.points['classification'] == 5]
            #colors =  numpy.array([las.points['red'], las.points['green'], las.points['blue'], las.points['nir']]).transpose()
            #colors = colors[las.points['classification'] == 5]
            print("selecting idices of this poibts")
            if len(points_to_cluster) < limit: 
                #indices_of_cluster_points = numpy.array([i for i in tqdm(range(length)) if (las.points['classification'][i] in classes_to_cluster)]) 
                points_to_cluster2d = points_to_cluster[:,:2]
                print("clustering")
                cluster = DBSCAN(eps=0.6, min_samples=5).fit(points_to_cluster2d)  # parameters according to https://www.degruyter.com/document/doi/10.1515/geo-2020-0266/html?lang=de
                labels = cluster.labels_
                print("building dictionary:")
                cluster_dict = {}
                #color_dict = {}
                for i in tqdm(numpy.unique(labels)):
                    if i >= 0:
                        cluster_dict[i] = points_to_cluster[labels == int(i)]
                        #color_dict[i] = colors[labels == int(i)]
             
                #x/y-convex hull
                hull_dict = {}
                print("calculating convex hulls:")
                for key in tqdm(cluster_dict.keys()):
                    tree = numpy.array(cluster_dict[key]).transpose((1, 0))
                    x = tree[0]
                    y = tree[1]    
                    points_2d = numpy.array([x,y]).transpose()
                    if len(points_2d) > 50:
                        hull = ConvexHull(points_2d)
                        poly = Polygon(points_2d[hull.vertices])
                        poly = scale(poly, xfact=1.1,yfact=1.1)
                        hull_dict[key] = poly
                #db lockup baumkataster

                print("trees in area:")
                print(trees)


                
                # x und y zusammenfassen!
                #dann:
                print("building geopandas dataframes:")
                trees['coords'] = numpy.array(zip(trees['X'],trees['Y']))
                trees['coords'] = trees['coords'].apply(Point)
                trees_df = geopandas.GeoDataFrame(trees, geometry='coords', crs="EPSG:25832")
                print(trees)
                
                hulls_df = pandas.DataFrame({'HULL_DICT_KEY': hull_dict.keys(), 'coords': hull_dict.values()})
                hulls_df = geopandas.GeoDataFrame(hulls_df, geometry='coords', crs="EPSG:25832")
                print("calculating joins")
                intersections = geopandas.tools.sjoin(trees_df,hulls_df, op="intersects", how='inner') #intersects
                print(len(intersections), " intersections found")
                
                
                dropped= 0
                intersections2 = intersections.copy()
                visited = []    
                print("search for doubl matches:")
                c_id = [] 
                t_id = []
                g_id = [] 
                a_id = []
                xs = []
                ys = []
                zs = []
                
                #rs = [] 
                #gs = []
                #bs = []
                #nirs = []

                for i, row in intersections.iterrows():
                        cluster_key= row.HULL_DICT_KEY # index right war das vorher!
                        doubles = intersections.loc[intersections.index_right==cluster_key,:] 
                        if (len(doubles) > 1):
                            genus = []
                            for i, row in doubles.iterrows():            
                                genus.append(row.ID_GATTUNG)
                            #Prüfe: gibt es mehr als eine Gattungs-Zuordnung für diesen Cluster?
                            #print(genus)
                            genus = set(genus)
                            #print(genus)
                            if (len(genus) > 1):                
                                if (row['index_right'] not in visited):
                                    dropped += len(doubles)
                                    visited.append(row['index_right'])
                                    #####save for k-means
                                    if (len(doubles) > 10):  
                                        tree_id =(int(row.ID))
                                        gattung_id =(int(row.ID_GATTUNG))

                                        req = """INSERT INTO LIDAR_PROJ.CLUSTER (ID, TREE_ID, ID_GATTUNG, PATH_ID, ALGO_ID) VALUES """ + str(save(max_id, tree_id, gattung_id, save_doubles_id, algo_id))
                                        req= req[:-1]
                                        print(req)
                                        #print("len cluster_dict:", len(cluster_dict[cluster_key]), "len points", len(c_las.x) )
                                        print("db execute at forest")

                                        #db.execute(req) 
                                        #db.commit()
                                        save_path = os.path.join(save_doubles_to, str(max_id) + ".las")
                                        print("saving large cluster to ", save_path)
                                        #c_las.write(save_path)
                                        for n_point in numpy.array(cluster_dict[cluster_key]):
                                                c_id.append(max_id)
                                                t_id.append(tree_id)
                                                g_id.append(gattung_id)
                                                a_id.append(algo_id)
                                                xs.append(n_point[0])
                                                ys.append(n_point[1])
                                                zs.append(n_point[2])
                                        #for c in  color_dict[cluster_key]:    
                                        #        rs.append(c[0])
                                        #        gs.append(c[1])
                                        #        bs.append(c[2])
                                        #        nirs.append(c[3])
                    
                                        max_id += 1                            
                
                                intersections2 = intersections2.drop(intersections2[intersections2.index_right   == cluster_key].index)
                            elif(row['index_right'] not in visited): 
                                intersections2 = intersections2.drop(intersections2[((intersections2.index_right == cluster_key) & (intersections2.ID != row['ID'])) ].index)
                                visited.append(row['index_right'])
                                dropped += len(doubles) - 1
                if (len(c_id) > 0):
                    csv_frame = pandas.DataFrame({"Cluster_ID":c_id, "Tree_ID": t_id, "GATTUNGS_ID": g_id, "ALGO_ID": a_id, "x": xs, "y": ys, "z": zs})                  #, "red": rs, "green":gs, "blue": bs, "nir": nirs
                    csv_frame.to_csv(csv_save_path_doubles,mode='w')               
                print(len(intersections2), " unambiguously clusters found")
                                
                print(dropped, " clusters dropped beacause of multiple matches")
                #scale 0:1
                normalized_trees = {}
                print("normalizing clusters")
                for i, row in tqdm(intersections2.iterrows()):
                    points = numpy.array(cluster_dict[row.HULL_DICT_KEY])
                    x , y, z = points.transpose()
                    x = numpy.array(x)
                    x = x - numpy.min(x)
                    y = numpy.array(y)
                    y = y - numpy.min(y)
                    z = numpy.array(z)
                    z = z - numpy.min(z)
                    points = numpy.array([x,y,z]).transpose()
                    points = points/ numpy.max(points)   
                    normalized_trees[row.HULL_DICT_KEY] = points
                counter = 0
                c_id = [] 
                t_id = []
                g_id = [] 
                a_id = []
                xs = []
                ys = []
                zs = []
                
                #rs = [] 
                #gs = []
                #bs = []
                #nirs = []
                print("saving")
                req  = """INSERT INTO LIDAR_PROJ.CLUSTER (ID, TREE_ID, ID_GATTUNG, PATH_ID, ALGO_ID) VALUES """
                for k in tqdm(normalized_trees.keys()):
                    counter +=1
                    max_id += 1        
                    normalized_points = normalized_trees[k]
                    
                    #colorized_points = color_dict[k]    
                     
                    row_df = intersections2.loc[intersections2['HULL_DICT_KEY'] == k]
                    try:
                        row = row_df.iloc[0]
                    except:
                        row= row_df  
                        print("except:", row)

                    tree_id =row['ID']
                    gattung_id =row['ID_GATTUNG']

                    req = req + str(save(max_id, tree_id, gattung_id, save_path_id, algo_id))       

                    save_path = os.path.join(save_to,str(max_id) + ".las")
                    #c_las.write(save_path)
                    for n_point in numpy.array(normalized_points):
                        c_id.append(max_id)
                        t_id.append(tree_id)
                        g_id.append(gattung_id)
                        a_id.append(algo_id)
                        xs.append(n_point[0])
                        ys.append(n_point[1])
                        zs.append(n_point[2])
                    #for c in colorized_points:
                    #    rs.append(c[0])
                    #    gs.append(c[1])
                    #    bs.append(c[2])
                    #    nirs.append(c[3])
                    


                    
                    if counter % 100 == 0:
                        print("db execute at % 100")

                        req= req[:-1]
                        print(req)
                        #db.execute(req)
                        
                        print("commit")
                        #db.commit()
                        req  = """INSERT INTO LIDAR_PROJ.CLUSTER (ID, TREE_ID, ID_GATTUNG, PATH_ID, ALGO_ID) VALUES """
                if (len(req) > 90):
                    print("last commit")
                    #req= req[:-1]
                    #db.execute(req)
                    #db.commit()
                    
                csv_frame = pandas.DataFrame({"Cluster_ID":c_id, "Tree_ID": t_id, "GATTUNGS_ID": g_id, "ALGO_ID": a_id, "x": xs, "y": ys, "z": zs}) #, "red": rs, "green":gs, "blue": bs, "nir": nirs

                print("save to ", csv_save_path)

                csv_frame.to_csv(csv_save_path,mode='w')

                print("finish!")
                print("time needed: ", datetime.now() - start_time)
            else:
                print("") 

                print("high vegetation points over limit ",limit)
                with open('skipped.txt', 'a+') as f:
                    f.write(str(file))   
            print("") 
            print("") 


                
        else:
            print("")
            print("allready exisists. skipping")
            print(csv_save_path, str(file) ,"...")    
            print("") 
         
def cluster_las(las):
    warnings.filterwarnings("ignore")
    start_time = datetime.now()
    print("time: ", start_time)    
   
    #x_max, x_min, y_max, y_min = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()

    print("selecting points to cluster by classification")
    p_t_c= numpy.array([las.points['x'], las.points['y'], las.points['z']]).transpose()
    points_to_cluster = p_t_c[las.points['classification'] == 5]

    indices = numpy.array([i for i in range(len(las.points['x']))])
    indices = indices[las.points['classification'] ==5]

    #colors =  numpy.array([las.points['red'], las.points['green'], las.points['blue'], las.points['nir']]).transpose()
    #colors = colors[las.points['classification'] == 5]

        #indices_of_cluster_points = numpy.array([i for i in tqdm(range(length)) if (las.points['classification'][i] in classes_to_cluster)]) 
    points_to_cluster2d = points_to_cluster[:,:2]
    print("clustering")
    cluster = DBSCAN(eps=0.6, min_samples=5).fit(points_to_cluster2d)  # parameters according to https://www.degruyter.com/document/doi/10.1515/geo-2020-0266/html?lang=de
    labels = cluster.labels_
    label_colors =  numpy.array([[random.randint(0,255), random.randint(0,255), random.randint(0,255)] for i in tqdm(range(len(labels)))])

    print("building dictionary:")
    cluster_dict = {}
    color_dict = {}
    indices_dict = {
        
    }
    for i in tqdm(numpy.unique(labels)):
        if i >= 0:
            cluster_dict[i] = points_to_cluster[labels == int(i)]
            color_dict[i] = label_colors[int(i)]  
            indices_dict[i] =indices[labels == int(i)]  

    return cluster_dict, color_dict, indices_dict

    #normalized_trees = {}
    
    """
    print("normalizing clusters")
    for i, row in tqdm(intersections2.iterrows()):
        points = numpy.array(cluster_dict[row.HULL_DICT_KEY])
        x , y, z = points.transpose()
        x = numpy.array(x)
        x = x - numpy.min(x)
        y = numpy.array(y)
        y = y - numpy.min(y)
        z = numpy.array(z)
        z = z - numpy.min(z)
        points = numpy.array([x,y,z]).transpose()
        points = points/ numpy.max(points)   
        normalized_trees[row.HULL_DICT_KEY] = points
    """
  
   

        

        


"""
f ="lidar-files/4categorized/Wesel/3dm_32_335_5725_1_nw.las"
extension = '*.las' 

for file in Path("D:/colorized_las/Köln").glob(extension):    
        cluster(file, 3,4, 1)
        #print("############## failure")

for file in Path("D:/colorized_las/Wesel").glob(extension):    
        cluster(file, 3,4, 3)
        #print("############## failure")
"""