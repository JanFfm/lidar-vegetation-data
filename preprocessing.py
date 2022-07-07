from urllib import request
import las_cleaner
import classifier
import os
from pathlib import Path
import laspy
from tqdm import tqdm

from tqdm import tqdm
import db_settings
import pandas
import geopandas
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt

db =db_settings.db(autocommit=False)

cwd = os.getcwd()
lidar_wesel = os.path.join(cwd, "lidar-files", "1original", "Wesel")
lidar_koeln = os.path.join(cwd, "lidar-files", "1original", "Koeln")
lidar_gelsenkirchen = os.path.join(cwd, "lidar-files", "1original", "Gelsenkirchen")

clean_wesel = os.path.join(cwd, "lidar-files", "2cleaned", "Wesel")
clean_koeln = os.path.join(cwd, "lidar-files", "2cleaned", "Koeln")
clean_gelsenkirchen = os.path.join(cwd, "lidar-files", "2cleaned", "Gelsenkirchen")

cat_wesel = os.path.join(cwd, "lidar-files", "3.1categorized", "Wesel")
cat_koeln = os.path.join(cwd, "lidar-files", "3.1categorized", "Koeln")
cat_gelsenkirchen = os.path.join(cwd, "lidar-files", "3.1categorized", "Gelsenkirchen")

buildings_wesel = os.path.join(cwd, "lidar-files", "3.2buildings", "Wesel")
buildings_koeln = os.path.join(cwd, "lidar-files", "3.2buildings", "Koeln")
buildings_gelsenkirchen = os.path.join(cwd, "lidar-files", "3.2buildings", "Gelsenkirchen")

merged_wesel = os.path.join(cwd, "lidar-files", "4merged", "Wesel")

folders_wesel = [lidar_wesel, clean_wesel, cat_wesel, buildings_wesel, merged_wesel]

crs_position = "EPSG:25832"
def step1(folders, city_code):
    print("db-requests ---")
    lidar_entrys =db.export_to_pandas("""SELECT * FROM LIDAR.LIDAR_FILES WHERE STADT=""" + str(city_code) +"""ORDER BY id""")
    trees =db.export_to_pandas("""SELECT * FROM BAEUME.BAEUME WHERE STADT=""" + str(city_code)+"""ORDER BY id""")
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
    lidar_polys = geopandas.GeoDataFrame(pandas.DataFrame({'polygon': lidar_polygons, 'id':lidar_entrys.index}), geometry='polygon', crs=crs_position)

    print() 
    intersections = geopandas.tools.sjoin(tree_points, lidar_polys, op="intersects", how='inner')
    
    #for i, r in tqdm(zip(intersections['id_left'], intersections['index_right'])):                 
    #    req ="""UPDATE BAEUME.BAEUME set LIDAR_FILE="""+str(r)+ """ WHERE stadt="""+str(city_code)+""" and id= """+ str(i)
    #    db.execute(req)    
    #db.commit()
    df=db.export_to_pandas("""SELECT s.*, l.file_name, l.id FROM (SELECT COUNT(b.*), LIDAR_FILE  FROM BAEUME.BAEUME b WHERE Stadt=3 GROUP BY LIDAR_FILE) s, lidar.LIDAR_FILES  l WHERE l.id = s.lidar_file ORDER BY s.lidar_file""")
    print(df)
    #for _, row in df.iterrows():
    #    c = row['Count(())']
    #    id = row['ID']
    #    req ="""UPDATE LIDAR.LIDAR_FILES set NUMBER_OF_TREES="""+str(c)+ """ WHERE stadt="""+str(city_code)+""" and id= """+ str(id)
    #    db.execute(req)
    #db.commit()
    files_with_trees = list(df['FILE_NAME'])
    print(files_with_trees)    
        
    
    print("cleaning files from ", folders[0])
    extension = '*.laz' 

    for file in Path(folders[0]).glob(extension): 
        break
        if str(file).split("/")[-1].split("\\")[-1] in files_with_trees:         
            las_cleaner.clean_las(file,folders[1])
            
    print("categorizing buildings")
    extension = '*.las' 
    for file in Path(folders[1]).glob(extension):
        polygons = classifier.read_buildings_nrw(file)
        classifier.map_points(file, polygons,folders[3])
        
    
step1(folders_wesel, 3)


def step2_merge(folders):
    extension = '*.las' 

    buildings = []
    cats = {}
    
    
    for file in Path(folders[3]).glob(extension):
        buildings.append(file)
    for file in Path(folders[2]).glob(extension):
        
        cat_file = file
        print(file)
        index = str(file).split(".")[-2].split("_")[-1].removeprefix("nw")
        print(index)
        #while (len(index) <3):
        #    index = '0'+index
        cats[int(index)] = cat_file
        
    save_path = folders[4]             
    if not os.path.exists(save_path):
                os.mkdir(save_path) 
                
                
    for i in range(len(buildings)):
        merge_from = laspy.read(buildings[i])
        merge_in = laspy.read(cats[i+1])
        
        for j in tqdm(range(len(merge_from.points['x']))):
            if merge_from.points['classification'][j] == 6:
                 merge_in.points['classification'][j] = 6
        file_name = str(buildings[i]).split("\\")[-1]
        file_name = str(file_name).split("/")[-1]

        print("save to ", os.path.join(save_path, file_name))
        merge_in.write(os.path.join(save_path, file_name))
    
#step2_merge(folders_wesel)
        
        
