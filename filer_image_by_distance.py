import numpy as np
import cv2 as cv
import laspy
from shapely.geometry import Point
from tqdm import tqdm
from pathlib import Path
import os
import visualize
"""
def cut_image(img_file):
    img =cv.imread(img_file)
    new_img = cv.imread(img_file)
    print(img)
    
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
             = y-10
            
            print(img[y][x])
    
    
    
    #cv.imshow('ing',img)
    #cv.waitKey(0) 
    
    
cut_image('rails.jpg')
"""



def cut_las(las_file):
    las = laspy.read(las_file)
    distance = 1
    indices = [i for i in range(len(las.points['x']))]
    near_points = []
    
    for x,y,c in tqdm(zip(las.points['x'], las.points['y'], las.points['classification'])):
        if c==str(10):
            for x2,y2,c2, index in zip(las.points['x'], las.points['y'], las.points['classification'],indices):
                  if c2 != str(10):
                    if Point(x,y).distance(Point(x2,y2)) < distance:
                        near_points.append(index)
    near_points = np.unique(np.array(near_points))
    print(near_points)
    for ind in near_points:
            las.points['classification'][ind] = 18
            las.points['red'][ind] = 255
            las.points['green'][ind] = 255
            las.points['blue'][ind] = 255
    visualize.plot_las_3d(las, color='classification')
    
for f in Path(os.path.join(os.getcwd(), 'Demo')).glob('*.las'):
    cut_las(f)  
                
            
        