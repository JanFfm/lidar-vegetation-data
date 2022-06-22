import laspy
from tqdm import tqdm
import os
import numpy



def clean_las(file, save_path="cleaned"):
    """ converts las file ti min 8 (for rgb channel) and removes all categiorizations > 18 (the largest standart classification value)
    """
    
    las = laspy.read(file)
    x = las.point_format
    if int(las.point_format.id ) < 8:    
           las = laspy.convert(las, point_format_id=8)
    print(las.point_format)
    classifications = numpy.array(las.points['classification'])
    for i in tqdm(range(len(classifications))):
        las_class = classifications[i]
        if las_class > 18:
             las.points['classification'][i] = 1
    classifications = numpy.array(las.points['classification'])
    print("max class ",classifications.max())

    
    file_name = str(file).split('/')[-1]
    file_name = str(file_name).split('\\')[-1]
    save_path = os.path.join(os.getcwd(), save_path)
    
    if not os.path.exists(save_path):
            os.mkdir(save_path)
    save_path = os.path.join(save_path,file_name)
    print("save to ", save_path)
    las.write(save_path)
    
