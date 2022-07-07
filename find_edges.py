import laspy
import db_settings
from pathlib import Path
import numpy as np
"""
Saves the name of each laz with corner-coordinates to db

"""


db = db_settings.db()

folders= ["lidar-files/1original/Wesel","lidar-files/1original/Köln", "lidar-files/1original/Gelsenkirchen"]

extension = '*.laz' 

w_request = """INSERT INTO lidar.lidar_files (x_min, x_max, y_min,y_max, file_name, STADT) VALUES"""

for file in Path(folders[0]).glob(extension):
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
        w_request = w_request + " ("+str(x_min) +", "+str(x_max)+ ", " + str(y_min) +", " + str(y_max )+ ",'" + filename+ "', " + str(3) +"),"
        print(filename)
w_request = w_request[:-1]
print (w_request)
db.execute(w_request)
db.commit()