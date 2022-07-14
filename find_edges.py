import laspy
import db_settings
from pathlib import Path
import numpy as np
"""
Saves the name of each laz with corner-coordinates to db

"""

def find(city_code, folder):
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
                filename =str(filename).split("\\")[-1]
                w_request = w_request + " ("+str(x_min) +", "+str(x_max)+ ", " + str(y_min) +", " + str(y_max )+ ",'" + filename+ "', " + str(city_code) +"),"
                print(filename)
        w_request = w_request[:-1]
        print (w_request)
        db.execute(w_request)
        db.commit()