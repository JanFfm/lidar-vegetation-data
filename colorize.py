import coord_f 
import fetch_sat_data
from tqdm import tqdm
import numpy as np
import pandas as pd
import laspy
import visualize
from datetime import datetime
from pathlib import Path
import os

def colorize(las_file, save_path="D://colorized_las"):
        las = laspy.read(las_file)
        las = laspy.convert(point_format_id=8, source_las=las)
        img, nir_img, cir_img = get_color_map(las)
        las = map_pixels(las, img, nir_img, cir_img )
        file_name = str(las_file).split('/')[-1]
        file_name = str(file_name).split('\\')[-1]
        file_name = str(file_name).split('.')[-2]
        file_name = file_name + ".las"
        save_path = os.path.join(os.getcwd(), save_path)
        
        if not os.path.exists(save_path):
                os.mkdir(save_path)
        save_path = os.path.join(save_path,file_name)
        print("save to ", save_path)
        las.write(save_path)
        


def get_color_map(las):
        las_points_x = np.array(las.points['x']) 
        las_points_y = np.array(las.points['y'])
        x_max, x_min, y_max, y_min = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()
        max_coords =  coord_f.utm_to_lat_long(x_max, y_max)
        min_coords = coord_f.utm_to_lat_long(x_min, y_min)   
   
        return fetch_sat_data.fetch(min_coords[0], min_coords[1], max_coords[0], max_coords[1])

def map_pixels(las, img, nir_img, cir_img):
        start_time = datetime.now()

        las_points_x = np.array(las.points['x']) 
        las_points_y = np.array(las.points['y'])
        x_max, x_min, y_max, y_min = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()
    
        x_factor = ((x_max - x_min)* 10) / (img.shape[1]- 1) 
        #print(x_max, x_min)
        #print(img.shape)
        y_factor = ((y_max - y_min)* 10) / (img.shape[0] -1) 
        #print (x_factor, y_factor)
        #print(((y_max - y_min)* 10) /y_factor)
        
        #print(list(las.point_format))
        print("calculating offset:")
        x_modi = list(map(lambda x :  (x- x_min)*10, las.points['x']))
        y_modi = list(map(lambda y :  (y_max - y)*10, las.points['y']))
        print("calculating coordiantes:")

        img_x = list(map(lambda x: int(round((x /x_factor),0)), x_modi))   #int() 
        img_y = list(map(lambda y: int(round((y /y_factor),0)), y_modi)) 
        print("calculating channel red:")

        las.points['red'] =list(map(lambda x, y: img[y][x][0] , img_x, img_y))
        print("calculating channel green:")
        las.points['green'] =list(map(lambda x, y: img[y][x][1] , img_x, img_y))
        print("calculating channel blue:")
        las.points['blue'] =list(map(lambda x, y: img[y][x][2] , img_x, img_y))
        print("calculating channel nir:")
        las.points['nir'] =list(map(lambda x,y: nir_img[y][x][0] , img_x, img_y))
        print("")
        print("finish!")
        print("time needed: ", datetime.now() - start_time)
        return las
"""       
extension = '*.las' 
folder ='lidar-files/4categorized/Wesel'
print("Colorizing ", folder)
for file in tqdm(Path(folder).glob(extension)):
    colorize(file,save_path="D://colorized_las/Wesel")
    
folder ='lidar-files/4categorized/Köln'
print("Colorizing ", folder)

for file in tqdm(Path(folder).glob(extension)):
    colorize(file,save_path="D://colorized_las/Köln")

"""

