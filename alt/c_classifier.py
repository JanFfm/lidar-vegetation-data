import pyximport; pyximport.install()
import classifier
import plot_las
import os
import laspy
import cython

save_path = "self_categorizzided"
file = "3dm_32_334_5727_1_nw.laz"
polygons = classifier.read_buildings_nrw("3dm_32_334_5727_1_nw.laz")
print(polygons)
las = classifier.map_points(file, polygons)

plot_las.plot2d(las) 
    
file_name = str(file).split('/')[-1]
file_name = str(file_name).split('\\')[-1]
save_path = os.path.join(os.getcwd(), save_path)

if not os.path.exists(save_path):
        os.mkdir(save_path)
save_path = os.path.join(save_path,file_name)
print("save to ", save_path)
las.write(save_path)
                    