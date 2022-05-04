import numpy as np
import cv2
import laspy   #needs also laszip to be installed
from pathlib import Path
import pyexasol
import pandas as pd


import tqdm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def convert(filename="gelsenkirchen/3dm_32_290_5647_1_nw.laz", color="Z"):
    las = laspy.read(filename)
    X =np.array(las.X)
    Y =np.array(las.Y)

    
    x_max = X.max()
    x_min = X.min()
    y_max = Y.max()
    y_min = Y.min()
    
    del X
    del Y
    
    
    x_dist = x_max - x_min
    y_dist = y_max - y_min

    
    point_data = np.stack([las.X, las.Y, las[color]], axis=0).transpose((1, 0))
    print(point_data)
    #img = cv2.resize( point_data,[512,512] )
    #cv2.imshow(img)
    #cv2.waitKey(0)   
    #closing all open windows 
    #cv2.destroyAllWindows() 
    
    #dimension_x = las.header.x_max - las.header.x_min
    
    #print(dimension_x)  
    
    print(las.header.scales)
    print(las.header.offsets)  
    #print(las.x)
    #
    # 
    # print(las.X)






convert()