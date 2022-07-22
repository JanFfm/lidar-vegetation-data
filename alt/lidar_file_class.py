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
        file_name = str(file_name).split('\\')[-1]  # hier hab ich das self raus genomen von self.file_name
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
