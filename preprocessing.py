import las_cleaner
import classifier
import os
from pathlib import Path
import laspy
from tqdm import tqdm

cwd = os.getcwd()
lidar_wesel = os.path.join(cwd, "lidar-files", "1original", "Wesel")
lidar_koeln = os.path.join(cwd, "lidar-files", "1original", "Koeln")
lidar_gelsenkirchen = os.path.join(cwd, "lidar-files", "1original", "Gelsenkirchen")

clean_wesel = os.path.join(cwd, "lidar-files", "2cleaned", "Wesel")
clean_koeln = os.path.join(cwd, "lidar-files", "2cleaned", "Koeln")
clean_gelsenkirchen = os.path.join(cwd, "lidar-files", "2cleaned", "Gelsenkirchen")

cat_wesel = os.path.join(cwd, "lidar-files", "3.1categorized", "Wesel")
cat_koeln = os.path.join(cwd, "lidar-files", "3.1categorized", "Koeln")
cat_gelsenkirchen = os.path.join(cwd, "lidar-files", "3.1categorized", "Gelsenkirchen")

buildings_wesel = os.path.join(cwd, "lidar-files", "3.2buildings", "Wesel")
buildings_koeln = os.path.join(cwd, "lidar-files", "3.2buildings", "Koeln")
buildings_gelsenkirchen = os.path.join(cwd, "lidar-files", "3.2buildings", "Gelsenkirchen")

merged_wesel = os.path.join(cwd, "lidar-files", "4merged", "Wesel")

folders_wesel = [lidar_wesel, clean_wesel, cat_wesel, buildings_wesel, merged_wesel]

extension = '*.laz' 

def step1(folders):
    print("cleaning files from ", folders[0])
    #for file in Path(folders[0]).glob(extension):
    #    las_cleaner.clean_las(file,folders[1])
    #print("categorizing buildings")
    for file in Path(folders[1]).glob(extension):
        polygons = classifier.read_buildings_nrw(file)
        classifier.map_points(file, polygons,folders[3])
    
#step1(folders_wesel)


def step2_merge(folders):
    buildings = []
    cats = {}
    
    
    for file in Path(folders[3]).glob(extension):
        buildings.append(file)
    for file in Path(folders[2]).glob(extension):
        
        cat_file = file
        print(file)
        index = str(file).split(".")[-2].split("_")[-1].removeprefix("nw")
        print(index)
        #while (len(index) <3):
        #    index = '0'+index
        cats[int(index)] = cat_file
        
    save_path = folders[4]             
    if not os.path.exists(save_path):
                os.mkdir(save_path) 
                
                
    for i in range(len(buildings)):
        merge_from = laspy.read(buildings[i])
        merge_in = laspy.read(cats[i+1])
        
        for j in tqdm(range(len(merge_from.points['x']))):
            if merge_from.points['classification'][j] == 6:
                 merge_in.points['classification'][j] = 6
        file_name = str(buildings[i]).split("\\")[-1]
        file_name = str(file_name).split("/")[-1]

        print("save to ", os.path.join(save_path, file_name))
        merge_in.write(os.path.join(save_path, file_name))
    
step2_merge(folders_wesel)
        
        
