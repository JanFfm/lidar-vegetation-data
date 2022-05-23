from genericpath import exists
import imp
from itertools import count
import numpy as np
import laspy
import matplotlib.pyplot as plt
import fetch_sat_data
import coord_f
import plot_las
from tqdm import tqdm
import las_parser
from pathlib import Path
import os
import db_interface
import db_settings

class LidarFileData():    
    x_min = None
    x_max = None
    y_min = None
    y_max = None
    
    map_image = None
    railway_map = None
    def __init__(self, lidar_file):
        self.file_name = lidar_file

        self.lidar_data = laspy.read(lidar_file)    
        if self.lidar_data.point_format < 8:    
            self.lidar_data = laspy.convert(self.lidar_data, point_format_id=8)
        print(self.lidar_data.point_format)

        self.x_max = np.array(self.lidar_data.points['x']).max()
        self.x_min = np.array(self.lidar_data.points['x']).min()
        self.y_max =  np.array(self.lidar_data.points['y']).max()
        self.y_min =  np.array(self.lidar_data.points['y']).min()
        
    
    def load_and_save_colors(self):
        self.get_color_map()
        self.map_pixels()

    def get_color_map(self):
        max_coords =  coord_f.utm_to_lat_long(self.x_max, self.y_max)
        min_coords = coord_f.utm_to_lat_long(self.x_min, self.y_min)    
   
        self.map_image = fetch_sat_data.fetch(min_coords[0], min_coords[1], max_coords[0], max_coords[1])
    def map_pixels(self):
        x_factor = ((self.x_max - self.x_min)* 10) / (self.map_image.shape[1]- 1) 
        print(self.x_max, self.x_min)
        print(self.map_image.shape)
        y_factor = ((self.y_max - self.y_min)* 10) / (self.map_image.shape[0] -1) 
        print (x_factor, y_factor)
        print(((self.y_max - self.y_min)* 10) /y_factor)
        
        #print(list(self.lidar_data.point_format))

        for i in tqdm(range(len(self.lidar_data.points))):
            x = (self.lidar_data.points['x'][i]  - self.x_min) *10
            y = (self.lidar_data.points['y'][i] - self.y_min) *10
            
            img_x = int(round((x /x_factor),0)) 
            img_y = (self.map_image.shape[0] -1)  - int(round((y /y_factor),0) )
            
            ### map rgb values:
            self.lidar_data.points['red'][i] =self.map_image[img_y][img_x][0]
            self.lidar_data.points['green'][i] = self.map_image[img_y][img_x][1]  
            self.lidar_data.points['blue'][i] =self.map_image[img_y][img_x][2]

    def detect_vegetation(self):
        #detecting vegetation
        count = 0
        for i in tqdm(range(len(self.lidar_data.points))): 
            if self.lidar_data['classification'][i] <= 1  or self.lidar_data['classification'][i] > 18: #0 never classified, 1: unclassified
                if self.lidar_data['number_of_returns'][i] > 1:
                    vari = (self.lidar_data['green'][i]  - self.lidar_data['red'][i] ) / (self.lidar_data['green'][i] + self.lidar_data['red'][i] - self.lidar_data['blue'][i]) 
                    if vari > 0.5:
                        self.lidar_data['classification'][i] = 4 # 4 = medium vegetation 
                        count += 1
        print(count ," points of veg detected!")
            


    def plot_image(self, colormode="combination", reduction=1):
        points = self.lidar_data.points.copy()
        # calculating coordinates
        X = np.array(points['X'][::reduction])
        Y = np.array(points['Y'][::reduction])
        
        if colormode =="combination":
            r = np.array(points['Z'][::reduction])
            r = r /r.max()
            g = np.array(points['classification'][::reduction])
            g = g/g.max()
            b = np.array(points['number_of_returns'][::reduction])
            b = b/b.max()
            
            color = [[r[i], g[i], b[i]] for i in range(len(r))]
        else:
            r = np.array(points[colormode][::reduction])
            color = r /r.max()    
            
        print (color)
        # plotting points
        fig = plt.figure()
        ax = fig.add_subplot() #111, projection='3d')
        ax.scatter(X, Y, c=color, marker=1)
        plt.show()
        
        # get numpy from plot:
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    def plot3d(self, color=None):
        plot_las.plot3d(self.lidar_data, color)
    def save(self,folder="/lidar_saves"):
        file_name = str(self.file_name).split('/')[-1]
        file_name = str(self.file_name).split('\\')[-1]
        print('filename', file_name)
        folder = os.path.join(os.getcwd(), folder)
        if not os.path.exists(folder):
            os.mkdir(folder)
        save_path = os.path.join(folder,file_name)
        print("save to ", save_path)
        self.lidar_data.write(save_path)
        #las_parser.save_to_db(self.lidar_data, name=name, postfix=postfix)
     
def colorize_folder(dir="./gelsenkirchen",extension = '*.laz' ):
    i =1
    for file in Path(dir).glob(extension):
        print(file)
        las= LidarFileData(file)
        las.save("colored_files_gelsenkirchen")
        i+=1
        

#las = LidarFileData("gelsenkirchen/3dm_32_300_5651_1_nw.laz")
#las.plot3d()
#las.detect_vegetation()
#las.plot_image(reduction=10, colormode="Z")
