
#from  whitebox.whitebox_tools import WhiteboxTools

import laspy
import plot_las
import os
#import shapefile   #das wär eher für OsM
import requests
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#import networkx as nx
from tqdm import tqdm
import xml.dom.pulldom as pulldom
import numpy
import pandas
import geopandas as gpd
from datetime import datetime

def read_buildings_nrw(file="3dm_32_334_5727_1_nw.laz", shapefile_folder="shapes"):
    """_summary_

    Args:
        file (str, optional): _description_. Defaults to "3dm_32_334_5727_1_nw.laz".
        shapefile_folder (str, optional): _description_. Defaults to "shapes".

    Returns:
        _type_: _description_
    """
    shapefile_folder = os.path.join(os.getcwd(), shapefile_folder)
    try:
        os.mkdir(shapefile_folder)
    except:
        pass
    file_name = str(file).split("\\")[-1]
    file_name = str(file_name).split("/")[-1]

    file_name = file_name.split(".")[-0]
    file_name = file_name[3:-2]
    file_name  ='LoD2'+ file_name+ 'NW.gml'
    ## download shapefile:
    print(file_name)
    gml_file = os.path.join(shapefile_folder, file_name)

    if not os.path.exists(gml_file):
            url = 'https://www.opengeodata.nrw.de/produkte/geobasis/3dg/lod2_gml/lod2_gml/' +file_name
            print("downloading from", url)
            gml = requests.get(url, allow_redirects=True)
            open(gml_file, 'wb').write(gml.content)
    ### finish downloading
    ####read gml/xml:    
    document = pulldom.parse(gml_file)
    polygons=[]
    print("reading gml file:")
    for event, node in tqdm(document):
        if event == pulldom.START_ELEMENT:
            if node.tagName == "gml:posList":
                document.expandNode(node)
            
                data= node.toxml()
                data = data.split('<')[1]
                tag = data.split('>')[0]
                values = data.split('>')[1] 
                values = values.split(' ')
                #print(dimension, values)
                
                poly = get_polygon(values)
                if poly is not None:
                    polygons.append(poly)
    print("finish")
    return polygons

       


def map_points(file, p, save_path):
    """_summary_

    Args:
        file (_type_): _description_
        p (_type_): _description_
        save_path (str, optional): _description_. Defaults to "self_classi".
    """
    
    global glob_polygons
    glob_polygons = p
    
    las= laspy.read(file)
    if (len(p) > 0):
        x = numpy.array( las.points['x'])
        y = numpy.array( las.points['y'])
        classifications = numpy.array(las.points['classification'])
        print(datetime.now())
        print("insgesamt ", len(classifications), " Punkte")
        indices = numpy.array([i for i in range(len(classifications))])
        print("#############################")
        #with Pool() as pool:
        #las.points['classification']= list(map(map_fkt,l))
        buildings = gpd.GeoDataFrame({'geometry': p}, crs="EPSG:25832")
        
        #########draw image:
        #buildings.plot(figsize=(6, 6))
        #plt.show()
        #plot_las.plot2d(las) 
        print(buildings)
        df = pandas.DataFrame({'i':indices, 'x': x, 'y':y,'classification': classifications })
        print("punkte ungefiltert:")
        print(df)
        df = df[(df['classification'] == 1) | (df['classification'] > 17)]
        df['coords'] = numpy.array(zip(df['x'],df['y']))
        df['coords'] = df['coords'].apply(Point)
        print("punkte gefiltert:")

        print(df)
        print("erstelle geopnadas.dataframe", datetime.now())
        points = gpd.GeoDataFrame(df, geometry='coords', crs="EPSG:25832")
        print(points)
        print("Scuhe Schnittpunkte", datetime.now())
        building_points = gpd.tools.sjoin(points, buildings, op="intersects", how='inner')
        print(building_points)
        print(datetime.now())
        save_path_csv = os.path.join(os.getcwd(), "geopandasgeopandas_inner_intersection.csv")
        building_points.drop('coords',axis=1).to_csv(save_path_csv)
        ###muss das vielleicht anders rum?
        #print(building_points[0]['i'], building_points[0]['x'], building_points[0]['y'], building_points[0]['classification'])
        for i in building_points['i']:
                las.points['classification'][i] = 6
    else:
        print("no buildings in this area!")

    #plot_las.plot2d(las) 
    
    file_name = str(file).split('/')[-1]
    file_name = str(file_name).split('\\')[-1]
    #save_path = os.path.join(os.getcwd(), save_path)
    
    if not os.path.exists(save_path):
            os.mkdir(save_path)
    save_path = os.path.join(save_path,file_name)
    print("save to ", save_path)
    las.write(save_path)
                     
        
def read_csv():
    las = laspy.read("3dm_32_334_5727_1_nw.laz")
    data_frame = pandas.read_csv("geopandas.csv")
    print(data_frame['i'])
    for i in data_frame['i']:
        las.points['classification'][i] = 6
    #plot_las.plot2d(las)
          


  
"""
def wb_tools():
    
    wbt = WhiteboxTools()
    wbt.set_whitebox_dir('C:/QGIS2/WBT')
    wbt.set_verbose_mode(True)

    file = os.path.join(os.getcwd(), "cleaned",  "3dm_32_334_5727_1_nw.laz" )


    #gfs geht vielleicht
    buildings = os.path.join(os.getcwd(),"building shape","OSM_buildings_wesel.shp")
    #las = laspy.read(file)
    save = os.path.join(os.getcwd(), "buildings_py.las")


    ## linearity_threshold= 0.7, verringern wenn vegetation missclaiifiziert wird
    ## planarity_threshold=0.85,  auch verringern
    new_las = wbt.classify_buildings_in_lidar(i =file, output=save, buildings= buildings)

    #plot_las.plot2d(save)
"""  
def get_polygon(points):
    """_summary_

    Args:
        points (_type_): _description_

    Returns:
        _type_: _description_
    """
    x = list(map(float, points[::3]))
    y = list(map(float, points[1::3]))
    # get list of tupels in
    point_list = list(zip(x,y))
    if (len(point_list) < 3):
        return None
    return Polygon(point_list)

#polygons = read_buildings_nrw("3dm_32_334_5727_1_nw.laz")

#map_points("cleaned/3dm_32_334_5727_1_nw.laz", polygons)
