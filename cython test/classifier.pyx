
#from  whitebox.whitebox_tools import WhiteboxTools
from multiprocessing import Process
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
import cython
import numpy

from multiprocessing import Pool, freeze_support



def read_buildings_nrw(file="3dm_32_334_5727_1_nw.laz", shapefile_folder="shapes"):
    shapefile_folder = os.path.join(os.getcwd(), shapefile_folder)
    try:
        os.mkdir(shapefile_folder)
    except:
        pass
    gml_file = file.split("/")[-1]
    gml_file = gml_file.split(".")[-0]
    gml_file = gml_file[3:-2]
    gml_file  ='LoD2'+ gml_file+ 'NW.gml'
    ## download shapefile:
    gml_file = os.path.join(shapefile_folder, gml_file)

    if not os.path.exists(gml_file):
            url = 'https://www.opengeodata.nrw.de/produkte/geobasis/3dg/lod2_gml/lod2_gml/' +gml_file
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
                poly = polygon(values)
                polygons.append(poly)
    print("finish")
    return polygons



def map_fkt(l):
    cdef float x
    cdef float y
    cdef int c
    cdef int bar
    x, y, c, bar =l 
    if c == 1: # for unclassified, noise or vlues above:            
        point = Point(x, y)        
        for p in glob_polygons:
            if p.match(point):
                return 6
    return c       


def map_points(file,p):
    
    global glob_polygons
    glob_polygons = p
    
    las= laspy.read(file)
    DEF point_number = 9380632 #len(list(las.points['classification']))
    cdef int[point_number] classifications = numpy.array(las.points['classification'])

    
    cdef float[point_number] x = numpy.array(las.points['x'])
    cdef float[point_number] y = numpy.array(las.points['y'])

    pbar = tqdm(range( point_number))
    l = zip(x,y,classifications, pbar)
    #with Pool() as pool:
    print("mapping")
    las.points['classification']= list(map(map_fkt,l))
        #las.points['classification']= list(map(map_fkt,x,y,classifications, pbar))
    print("finish")
    return las
        
        


  
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
class polygon(): 
    point_list = cython.declare(cython.list, visibility='public')

    #polygon  = cython.declare(Polygon, visibility='public')
    def __init__(self, points): 
        cdef list x = list(map(float, points[::3]))
        cdef list y = list(map(float, points[1::3]))
        # get list of tupels in
        self.point_list = list(zip(x,y))
        if (len(self.point_list) == 2):
            self.point_list.append(self.point_list[0])
        
        self.polygon = Polygon(self.point_list)
    def match(self, point):
        return self.polygon.contains(point)

    
if cython.compiled:
    print("Yep, I'm compiled.")
else:
    print("Just a lowly interpreted script.")   
    
#polygons = read_buildings_nrw("3dm_32_334_5727_1_nw.laz")

#map_points("cleaned/3dm_32_334_5727_1_nw.laz", polygons)

"""if __name__=="__main__":
    freeze_support()
    main()"""