#from pycrown.pycrown import pycrown

import laspy
from osgeo import gdal
import geopandas as gpd
import pandas as pd

import os

##zip:
import gzip
import shutil
#web-requests:
import requests


input_lidar_foler= "lidar-files/2cleaned/Wesel"
lidar_fila_name = "3dm_32_324_5729_1_nw"


laz = laspy.read(str(os.path.join(os.getcwd(), input_lidar_foler, (lidar_fila_name + ".laz"))))

if not os.path.exists("tmp"):
    os.mkdir("tmp")
#las_path ist argument 1
las_path = str(os.path.join(os.getcwd(), "tmp", (lidar_fila_name + ".las")))
laz.write(las_path,None)

#get dsm:
url = "https://www.opengeodata.nrw.de/produkte/geobasis/hm/dgm1_xyz/dgm1_xyz/"
url = url +"dgm1" + lidar_fila_name[3:] +".xyz.gz"
print(url)
dsm  = requests.get(url, allow_redirects=True)
tempfile_dsm = str(os.path.join(os.getcwd(), "tmp", "dsm.gz"))
open(tempfile_dsm, 'wb').write(dsm.content)
#open(dsm, 'wb').write(dsm.content)

xyz_path = os.path.join(os.getcwd(), "xyz", ("dgm1" + lidar_fila_name[3:] +".xyz"))
with gzip.open(tempfile_dsm, 'rb') as gz:    
    with open(xyz_path,"w") as xyz:
        if not os.path.exists("xyz"):
            os.mkdir("xyz")      
        xyz.write(gz.read().decode("utf-8"))
            #shutil.copyfileobj(f_in, f_out)
            #xyz.write(str(os.path.join(os.getcwd(), "xyz", ("dgm1" + lidar_fila_name[3:] +".xyz"))))
if not os.path.exists("elevations/dgm"):
            os.mkdir("elevations/dgm")
#read xyz line by line:    
with open (xyz_path) as xyz:
    dgm_tiff = os.path.join(os.getcwd(), "elevations", "dgm", ("dgm1" + lidar_fila_name[3:] +".tiff"))
    lines = []
    for line in xyz.readlines():
        if(line != "\n"):
            lines.append(line.split(" \n")[0])
    print(lines[-1])
#parse lines to geoTIFF:

l_x = []
l_y = []
l_z = []
for line in lines:
    x,y,z  =line.split(" ") 
    l_x.append(x)
    l_y.append(y)
    l_z.append(z)
data = {
    'x':l_x,
    'y':l_y,
    'z':l_z
}
xyz_dataframe = gpd.GeoDataFrame(pd.DataFrame(data, columns= ['x', 'y', 'z']))
print(xyz_dataframe)

driver = gdal.GetDriverByName(  "GTiff" )
metadata = driver.GetMetadata()
