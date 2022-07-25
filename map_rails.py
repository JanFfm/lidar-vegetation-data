
import laspy
from owslib.wms import WebMapService
import numpy as np
import coord_f
from PIL import Image
import visualize
import os

def rails(las_file="demo/3dm_32_335_5728_1_nw.laz", size=5000):
    las = laspy.read(las_file)
    wms_nrw = "https://www.wms.nrw.de/geobasis/wms_nw_inspire-verkehrsnetze_alkis"
    wms = WebMapService(wms_nrw, version='1.3.0',username="")
    wms_content = list(wms.contents)
    print(wms_content)
    color_map = wms_content[5]
    las_points_x = np.array(las.points['x']) 
    las_points_y = np.array(las.points['y'])
    x_max, x_min, y_max, y_min = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()
    x_max, y_max =  coord_f.utm_to_lat_long(x_max, y_max)
    x_min, y_min=  coord_f.utm_to_lat_long(x_min, y_min)   
    box=(y_min,x_min,y_max, x_max)

    #box = (5.59334, 50.0578, 9.74158, 52.7998)
    img = wms.getmap(layers=[color_map],srs='EPSG:4326', bbox=box, format='image/jpeg',transparent=False, size=[size,size] )
    out = open('rails.jpg', 'wb')
    out.write(img.read())
    out.close()
    img = np.array(Image.open('rails.jpg'))    
    
    #to get um coordinates again:
    x_max, x_min, y_max, y_min = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()

    x_factor = ((x_max - x_min)) / (img.shape[1]- 1) 
    y_factor = ((y_max - y_min) / (img.shape[0] -1) )
    print("calculating offset:")
    x_modi = list(map(lambda x :  (x- x_min), las.points['x']))
    y_modi = list(map(lambda y :  (y_max - y), las.points['y'])) # das stimt vielleicht nicht?
    print("calculating coordiantes:")

    img_x = list(map(lambda x: int(round((x /x_factor),0)), x_modi))   #int() 
    img_y = list(map(lambda y: int(round((y /y_factor),0)), y_modi)) 
    print("mapping rails")
    rail =list(map(lambda x, y: 10 if not np.array_equal(img[y][x],np.array([255,255,255])) else 100 , img_x, img_y))
    
    l, l_num = np.unique(rail, return_counts=True)
    print(dict(zip(l, l_num)))
    las.points['classification'] = np.array(list(map(lambda c, r: r if r==10 and c==2 else c,  las.points['classification'] , rail)))  
    visualize.plot_las_3d(las, color='classification')
    print("saving", las_file)
    #las_file = str(os.path.join(os.getcwd(), las_file))

    #las.write(las_file)
