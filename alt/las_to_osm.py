from distutils.log import debug
#import overpass  #OSM api
import laspy
import overpy # https://betterprogramming.pub/how-to-get-open-street-and-map-data-using-python-2b777bf5af14
import overpy.helper as helper
import OSMPythonTools
#import osmnx
import folium
#https://jingwen-z.github.io/how-to-install-python-module-fiona-on-windows-os/
#https://levelup.gitconnected.com/working-with-openstreetmap-in-python-c49396d98ad4
import smopy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
from  coord_f import utm_to_lat_long
from plot_las import plot2d, plot3d

import overpass
import requests
import json



def load_osm_tile(lat_1, long_1, lat_2, long_2, server="http://tiles.openrailwaymap.org/", style="standard"):

    if server is not None:
        server = server +style +"/{z}/{x}/{y}.png"
        print(server)

        map = smopy.Map(lat_1 +0.0055, long_1 +.0055,z =15, tileserver=server)  #Add half of OSM coord-with at zoom level 15 to coords: 0.011/2 =0.0055
    #use osm-server as default:
    else: 
        #map = smopy.Map((lat_1, long_1, lat_2, long_2))
        map = smopy.Map(lat_1 +0.0055, long_1+ 0.0055, z =15)
        
    #to plot:
    map = map.to_numpy()
    plt.imshow(map)    
    plt.show()
    return map


def las_to_osm(filename):
    las = laspy.read(filename)
    
    lat_1, long_1 = utm_to_lat_long(las.header.x_min, las.header.y_min)
    lat_2, long_2 =  lat_1 +0.011 , long_1 +0.011
    
    
    map = load_osm_tile(lat_1,long_1, lat_2, long_2,server=None) #load osm
    rail_map = load_osm_tile(lat_1,long_1, lat_2, long_2) #load open railway
    rail_map = cv2.cvtColor(rail_map, cv2.COLOR_RGB2RGBA)
    print(rail_map)
    plot3d(filename, color="Z")

#load_osm_tile()
#las_to_osm("./gelsenkirchen/3dm_32_293_5650_1_nw.laz")


rail_section = ["gelsenkirchen/3dm_32_300_5651_1_nw.laz", "gelsenkirchen/3dm_32_297_5647_1_nw.laz",
 "gelsenkirchen/3dm_32_298_5648_1_nw.laz",
 "gelsenkirchen/3dm_32_298_5649_1_nw.laz",
 "gelsenkirchen/3dm_32_298_5649_1_nw.laz",
 "gelsenkirchen/3dm_32_300_5651_1_nw.laz",
 "gelsenkirchen/3dm_32_298_5649_1_nw.laz",
 "gelsenkirchen/3dm_32_300_5651_1_nw.laz",
"gelsenkirchen/3dm_32_300_5651_1_nw.laz",
"gelsenkirchen/3dm_32_294_5651_1_nw.laz",
"gelsenkirchen/3dm_32_294_5651_1_nw.laz",
"gelsenkirchen/3dm_32_295_5651_1_nw.laz",
"gelsenkirchen/3dm_32_297_5648_1_nw.laz"]

## "gelsenkirchen/3dm_32_300_5651_1_nw.laz" viel schiene, aber kein osm

for file in rail_section:
    las_to_osm(file)
