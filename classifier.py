

import laspy
import os
import requests
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.affinity import scale
from tqdm import tqdm
import xml.dom.pulldom as pulldom
import numpy
import pandas
import geopandas as gpd
from datetime import datetime

def read_buildings_nrw(file="3dm_32_334_5727_1_nw.laz", shapefile_folder="shapes"):
    """reads comparing shape file of buildings for lidar-file
    transfers buildings to  shapely.geometry.polygon.Polygon()

    Args:
        file (str, optional): name of las/laz-file. Defaults to "3dm_32_334_5727_1_nw.laz".
        shapefile_folder (str, optional): save path for shape files. Defaults to "shapes".

    Returns:
        list: buildings  as shapely.geometry.polygon.Polygon()
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
                    poly = scale(poly, xfact=1.1,yfact=1.1)
                    polygons.append(poly)
    print(len(polygons)," buildings found")
    print("finish")
    return polygons

       


def map_points(file, p, save_path):
    """classifies lidar files
    uses intersection wirth building-polygons to classify points as lidar class 6

    Args:
        file (str): path of lidar file
        p (list): list of building polygons
        save_path (str, optional): save path for classified lidar file..
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

        buildings = gpd.GeoDataFrame({'geometry': p}, crs="EPSG:25832")
        
        #########draw image:
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
        for i in building_points['i']:
                las.points['classification'][i] = 6
    else:
        print("no buildings in this area!")

    
    file_name = str(file).split('/')[-1]
    file_name = str(file_name).split('\\')[-1]
    save_path = os.path.join(os.getcwd(), save_path)

    print("save to ", save_path)
    las.write(save_path)
                     
        
def read_csv():
    las = laspy.read("3dm_32_334_5727_1_nw.laz")
    data_frame = pandas.read_csv("geopandas.csv")
    print(data_frame['i'])
    for i in data_frame['i']:
        las.points['classification'][i] = 6          


def get_polygon(points):
    """transfer edge points of building to polygon

    Args:
        points (list): (x,y,z) - 3d points of building

    Returns:
        Polygon: 2d Polygon
    """
    x = list(map(float, points[::3]))
    y = list(map(float, points[1::3]))
    # get list of tupels in
    point_list = list(zip(x,y))
    if (len(point_list) < 3):
        return None
    return Polygon(point_list)
