import laspy
from pathlib import Path
import os
import numpy as np
import colors
import visualize
import classifier
lasttols_path = "C:/Users/janja/Desktop/LAStools/bin"

def prepare_demo():
    for f in Path(os.path.join(os.getcwd(), 'Demo')).glob('*.la*'):
        f = str(f)
        las =laspy.read(f)

        l, l_num = np.unique(las.points['classification'], return_counts=True)
        print("point distribution", dict(zip(l, l_num)))
        
        
        las.points['classification'] = list(map(lambda x: x if (x <= 17) else (1 if x ==20 else (17 if x == 21 else (17 if x == 24 else (17 if x== 26 else 2)))), las.points['classification']))
        l, l_num = np.unique(las.points['classification'], return_counts=True)
        print("point distribution", dict(zip(l, l_num)))

        #visualize.plot_las_3d(las, color ="classification")
        las.write(f)
        polys = classifier.read_buildings_nrw(f)
        classifier.map_points(f,polys,f)
        #save_to =str(os.path.join(os.getcwd(), 'Demo', 'edited', f.split)) 
        save_to = str(f.split('.')[0] + '_classified.laz')
        command = '"'+ str(lasttols_path) + '/lasheight -i "' + f + '" -ignore_class 2 -ignore_class 6 -ignore_class 7 -ignore_class 8 -ignore_class 9 -ignore_class 10 -ignore_class 11 -ignore_class 12 -ignore_class 13 -ignore_class 14 -ignore_class 15 -ignore_class 16 -ignore_class 17 -classify_between 0.0 0.5 3 -classify_between 0.5 2 4 -classify_between 2 70.0 5 -classify_above 70.0 5 -o "' +save_to+ '"'
        os.system(command)    
        
prepare_demo()