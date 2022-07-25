import laspy
from pathlib import Path
import os
import numpy as np
import colors
import colorize
import visualize
import classifier
import map_rails

lasttols_path = "C:/Users/janja/Desktop/LAStools/bin"

def prepare_demo():
    for f in Path(os.path.join(os.getcwd(), 'Demo')).glob('*.la*'):
        f = str(f)
        las =laspy.read(f)
        
        l, l_num = np.unique(las.points['classification'], return_counts=True)
        print("point distribution", dict(zip(l, l_num)))
        
        
        #las.points['classification'] = list(map(lambda x: x if (x <= 17) else (1 if x ==20 else (17 if x == 21 else (17 if x == 24 else (17 if x== 26 else 2)))), las.points['classification']))
        l, l_num = np.unique(las.points['classification'], return_counts=True)
        print("point distribution", dict(zip(l, l_num)))

        #visualize.plot_las_3d(las, color ="classification")
        las.write(f)
        polys = classifier.read_buildings_nrw(f)
        #save_to1 = str(f.split('.')[0].split('/')[-1].split('\\')[-1]  + 'building.laz')

        classifier.map_points(f,polys,f)
        save_to = str(f.split('.')[0]  + '_classified.laz')

        command = '"'+ str(lasttols_path) + '/lasheight -i "' + f + '" -ignore_class 2 -ignore_class 6 -ignore_class 7 -ignore_class 8 -ignore_class 9 -ignore_class 10 -ignore_class 11 -ignore_class 12 -ignore_class 13 -ignore_class 14 -ignore_class 15 -ignore_class 16 -ignore_class 17 -classify_between 0.0 0.5 3 -classify_between 0.5 2 4 -classify_between 2 70.0 5 -classify_above 70.0 5 -o "' +save_to+ '"'
        os.system(command)    
        
def col():
   for f in Path(os.path.join(os.getcwd(), 'Demo')).glob('*Cloud.la*'):
        colorize.colorize(f, "C:/Users/janja/Desktop/GitHub/lidar-vegetation-data/Demo")
def get_rails():
    for f in Path(os.path.join(os.getcwd(), 'Demo')).glob('*.la*'): 
        print("get_rails ", f)
        map_rails.rails(f)

#get_rails()
#col()
#prepare_demo()
"""
name = "demo/3dm_32_335_5728_1_nw original.laz"
name2 = "demo/clean_3dm_32_335_5728_1_nw.laz"
name3 = "buildings_3dm_32_335_5728_1_nw.laz"
#map_rails.rails(name)
las =laspy.read(name)
        
l, l_num = np.unique(las.points['classification'], return_counts=True)
print("point distribution", dict(zip(l, l_num)))


las.points['classification'] = list(map(lambda x: x if (x <= 17) else (1 if x ==20 else (17 if x == 21 else (17 if x == 24 else (17 if x== 26 else 2)))), las.points['classification']))
l, l_num = np.unique(las.points['classification'], return_counts=True)
print("point distribution", dict(zip(l, l_num)))

#visualize.plot_las_3d(las, color ="classification")
las.write(name2)
polys = classifier.read_buildings_nrw("3dm_32_335_5728_1_nw.laz")
#save_to1 = str(f.split('.')[0].split('/')[-1].split('\\')[-1]  + 'building.laz')

classifier.map_points(name2,polys,name3)"""
f = "C:/Users/janja/Desktop/GitHub\lidar-vegetation-data/Demo/buildings_3dm_32_335_5728_1_nw.laz"
f2 = "C:/Users/janja/Desktop/GitHub\lidar-vegetation-data/Demo/vegetation_3dm_32_335_5728_1_nw.laz"
#-command = '"'+ str(lasttols_path) + '/lasheight -i "' + f + '" -ignore_class 2 -ignore_class 6 -ignore_class 7 -ignore_class 8 -ignore_class 9 -ignore_class 10 -ignore_class 11 -ignore_class 12 -ignore_class 13 -ignore_class 14 -ignore_class 15 -ignore_class 16 -ignore_class 17 -classify_between 0.0 0.5 3 -classify_between 0.5 2 4 -classify_between 2 70.0 5 -classify_above 70.0 5 -o "' +f2+ '"'
#os.system(command)    
colorize.colorize(f2, "C:/Users/janja/Desktop/GitHub/lidar-vegetation-data/Demo/color")