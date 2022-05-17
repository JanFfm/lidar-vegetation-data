import numpy as np
import laspy
import matplotlib.pyplot as plt


class LidarFileData():
    map_image = None
    railway_map = None
    lidar_data = None
    def __init__(self, lidar_file):
        self.lidar_data = laspy.read(lidar_file)
    
    
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
     



class LidarExasolData(LidarFileData):
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name


las = LidarFileData("gelsenkirchen/3dm_32_300_5651_1_nw.laz")
las.plot_image(reduction=10, colormode="Z")