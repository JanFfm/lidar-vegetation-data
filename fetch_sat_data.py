from owslib.wms import WebMapService
from PIL import Image
import numpy as np


def fetch (x1, y1, x2, y2, size=5000):
    """Get DOP-Satelite color map in x1,y1 / x2,y2 coordinates from nrw-geo-prtal
    returns numpy arrays rgb-image nir-image and cir-image
    
    
    """   
    wms_nrw = "https://www.wms.nrw.de/geobasis/wms_nw_dop"
    wms= WebMapService(wms_nrw, version='1.1.1',username="")
    wms_content = list(wms.contents)
    print(wms_content)
    
    color_map = wms_content[2]
    cir_map = wms_content[3]
    nir_map = wms_content[4]
    
    box=(y1,x1,y2, x2)

    #box = (5.59334, 50.0578, 9.74158, 52.7998)
    img = wms.getmap(layers=[color_map],srs='EPSG:4326', bbox=box, format='image/jpeg',transparent=False, size=[size,size] )
    out = open('sat_data.jpg', 'wb')
    out.write(img.read())
    out.close()
    img = Image.open('sat_data.jpg')
    img = np.array(img)
    
    nir_img = wms.getmap(layers=[nir_map],srs='EPSG:4326', bbox=box, format='image/jpeg',transparent=False, size=[size,size] )
    out = open('nir_sat_data.jpg', 'wb')
    out.write(nir_img.read())
    out.close()    
    nir_img = Image.open('nir_sat_data.jpg')
    nir_img = np.array(nir_img)
    
    cir_img = wms.getmap(layers=[cir_map],srs='EPSG:4326', bbox=box, format='image/jpeg',transparent=False, size=[size,size] )
    out = open('cir_sat_data.jpg', 'wb')
    out.write(cir_img.read())
    out.close()    
    cir_img = Image.open('cir_sat_data.jpg')
    cir_img = np.array(cir_img)
    
    print(nir_img.shape)
    print(cir_img.shape)
    
    return img, nir_img, cir_img


    