import las_cleaner
import classifier
#import cluster_dbscan
import os
from pathlib import Path
import laspy
from tqdm import tqdm
import numpy as np
from os.path import exists
from tqdm import tqdm
import db_settings
import pandas
import geopandas
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#import matplotlib.pyplot as plt
import cluster_dbscan
db =db_settings.db(autocommit=False)
lasttols_path = "C:/Users/janja/Desktop/LAStools/bin"


cwd = os.getcwd()
lidar_wesel = os.path.join(cwd, "lidar-files", "1original", "Wesel")
lidar_köln = os.path.join(cwd, "lidar-files", "1original", "Köln")
lidar_gelsenkirchen = os.path.join(cwd, "lidar-files", "1original", "Gelsenkirchen")

clean_wesel = os.path.join(cwd, "lidar-files", "2cleaned", "Wesel")
clean_köln = os.path.join(cwd, "lidar-files", "2cleaned", "Köln")
clean_gelsenkirchen = os.path.join(cwd, "lidar-files", "2cleaned", "Gelsenkirchen")

cat_wesel = os.path.join(cwd, "lidar-files", "4categorized", "Wesel")
cat_köln = os.path.join(cwd, "lidar-files", "4categorized", "Köln")
cat_gelsenkirchen = os.path.join(cwd, "lidar-files", "4categorized", "Gelsenkirchen")

buildings_wesel = os.path.join(cwd, "lidar-files", "3buildings", "Wesel")
buildings_köln = os.path.join(cwd, "lidar-files", "3buildings", "Köln")
buildings_gelsenkirchen = os.path.join(cwd, "lidar-files", "3buildings", "Gelsenkirchen")

color_köln =  os.path.join(cwd, "lidar-files", "5color", "Köln")
color_wesel =  os.path.join(cwd, "lidar-files", "5color", "Wesel")
color_geslenkirchen =  os.path.join(cwd, "lidar-files", "5color", "Gelsenkirchen")



folders_wesel = [lidar_wesel, clean_wesel, buildings_wesel, cat_wesel, color_wesel]
folders_gelsenkirchen = [lidar_gelsenkirchen,clean_gelsenkirchen, buildings_gelsenkirchen, color_geslenkirchen ]
folders_köln = [lidar_köln, clean_köln, buildings_köln, cat_köln, color_köln]
all_folders = [folders_köln, folders_gelsenkirchen, folders_wesel]
crs_position = "EPSG:25832"

def find(city_code, folder):
    print(folder)
    """
    save lidar edges with city code to db
    to match will tree entrys later
    """
    db = db_settings.db()
    extension = '*.laz' 

    w_request = """INSERT INTO lidar_proj.lidar_files (x_min, x_max, y_min,y_max, file_name, CITY_ID) VALUES"""

    for file in Path(folder).glob(extension):
            las = laspy.read(file)
            x = np.array(las.points['x'])
            y = np.array(las.points['y'])
            x_min = x.min()
            y_min = y.min()
            x_max = x.max()
            y_max = y.max()
            print (x_max, x_min, y_max, y_min)
            filename =str(file).split("/")[-1]
            filename =str(filename).split("\\")[-1].split('.')[0]
            w_request = w_request + " ("+str(x_min) +", "+str(x_max)+ ", " + str(y_min) +", " + str(y_max )+ ",'" + filename+ "', " + str(city_code) +"),"
            print(filename)
    w_request = w_request[:-1]
    print (w_request)
    db.execute(w_request)
    db.commit()
        
def preprocess(city_code, update_db=False, classify=True):
    
    folders = all_folders[city_code - 1]
    if update_db:
        find(city_code=city_code, folder=folders[0])
        
        print("db-requests ---")
        #check files listetd to baumkataster:
        lidar_entrys =db.export_to_pandas("""SELECT * FROM lidar_proj.LIDAR_FILES WHERE CITY_ID=""" + str(city_code) +""" ORDER BY id""")
        trees =db.export_to_pandas("""SELECT * FROM lidar_proj.TREES WHERE CITY_ID=""" + str(city_code)+"""ORDER BY id""")
        #fetching lidar:
        lidar_polygons=[]
        for _, row in lidar_entrys.iterrows():
            p = Polygon([(row['X_MIN'],row['Y_MIN']),(row['X_MIN'],row['Y_MAX']),(row['X_MAX'],row['Y_MAX']),(row['X_MAX'],row['Y_MIN'])])
            lidar_polygons.append(p)
            
        #fetching trees:
        tree_points=[]
        for _, row in trees.iterrows():
            p = Point((row['X'],row['Y']))
            tree_points.append(p)      
        print("checking, which lidar files is aprt of tree-collection...")

        tree_points = geopandas.GeoDataFrame(pandas.DataFrame({'points': tree_points, 'index':trees.index, 'id':trees['ID']}), geometry='points', crs=crs_position)
        lidar_polys = geopandas.GeoDataFrame(pandas.DataFrame({'polygon': lidar_polygons, 'id':lidar_entrys.ID}), geometry='polygon', crs=crs_position)

        intersections = geopandas.tools.sjoin(tree_points, lidar_polys, op="intersects", how='inner')
        print(intersections)    
        for i, r in tqdm(zip(intersections['id_left'], intersections['id_right'])):                 
            req ="""UPDATE lidar_proj.TREES set LIDAR_FILE_ID="""+str(r)+ """ WHERE CITY_ID="""+str(city_code)+""" and id= """+ str(i)
            db.execute(req)
        print("finish")    
        db.commit()
        print("commited")
    
    df=db.export_to_pandas("""SELECT s.*, l.file_name, l.id FROM (SELECT COUNT(t.*), LIDAR_FILE_ID  FROM lidar_proj.TREES t WHERE t.CITY_ID="""+str(city_code) +""" GROUP BY t.LIDAR_FILE_ID) s, lidar_proj.LIDAR_FILES  l WHERE l.id = s.lidar_file_ID ORDER BY s.lidar_file_ID""")
    print(df)
    if update_db:
        print("update tree count")
        for _, row in tqdm(df.iterrows()):
            c = row['Count(())']
            id = row['ID']
            req ="""UPDATE lidar_proj.LIDAR_FILES set NUMBER_OF_TREES="""+str(c)+ """ WHERE CITY_ID="""+str(city_code)+""" and id= """+ str(id)
            db.execute(req)
        db.commit()
        print("commited")
    
    files_with_trees = list(df['FILE_NAME'])
    print(files_with_trees)            
    
    print("cleaning files from ", folders[0])
    extension = '*.laz' 
    counter = len(files_with_trees)
    print(counter, " trees to clean")
    
    for file in Path(folders[0]).glob(extension):         
        if str(file).split("/")[-1].split("\\")[-1].split('.')[0] in files_with_trees:     
            if not exists(folders[1] +"/" +str(file).split("/")[-1].split("\\")[-1].split('.')[0] + ".las"):
                print("cleaning" , file) 
                las_cleaner.clean_las(file,folders[1])
            else:
                print(folders[1] +"/" +str(file).split("/")[-1].split("\\")[-1].split('.')[0] + ".las allready exists")
            counter -= 1
            print(counter, " trees to clean left from ",len(files_with_trees))
        else:
            print("skipping ", file)
    
    print("categorizing buildings")
    extension = '*.las' 
    counter = len(files_with_trees)
    for file in Path(folders[1]).glob(extension):
        if not exists(folders[2] +"/" +str(file).split("/")[-1].split("\\")[-1].split('.')[0] + ".las"):
                print("categorizing" , file) 
                polygons = classifier.read_buildings_nrw(file)
                classifier.map_points(file, polygons,folders[2])      
        else:
            print(folders[2] +"/" +str(file).split("/")[-1].split("\\")[-1].split('.')[0] + ".las allready exists")     
        counter -= 1
        print(counter, " trees to classify left from ",len(files_with_trees))
    
    if classify:
        for file in Path(folders[2]).glob(extension):
            file_name = str(file).split("/")[-1].split("\\")[-1] 
            command = '"'+ str(lasttols_path) + '/lasheight -i "' + str(file) + '" -ignore_class 2 -ignore_class 6 -ignore_class 7 -ignore_class 8 -ignore_class 9 -ignore_class 10 -ignore_class 11 -ignore_class 12 -ignore_class 13 -ignore_class 14 -ignore_class 15 -ignore_class 16 -ignore_class 17 -classify_between 0.0 0.5 3 -classify_between 0.5 2 4 -classify_between 2 70.0 5 -classify_above 70.0 5 -o "' +str(folders[3]) +'/'+ str(file_name) + '"'
            os.system(command)    
    
    extension = '*.las' 
    #for file in Path(folders[3]).glob(extension):  
    #   cluster_dbscan.cluster(file, 1,2, city_code)
    
    
        
     
#extension = '*.las' 
#for file in Path(all_folders[3]).glob(extension):   
#    cluster_dbscan.cluster(file)
preprocess(city_code=2, update_db= False, classify=True)
#preprocess(city_code=1, update_db= False, classify=True)

