from owslib.wms import WebMapService
from PIL import Image
import numpy as np

"""Get DOP-Satelite color map in x1,y1 / x2,y2 coordinates from nrw-geo-prtal"""
def fetch (x1, y1, x2, y2, size=5000):
    """_summary_
    https://pypi.org/project/OWSLib/
    
    wms nasa: http://wms.jpl.nasa.gov/wms.cgi
    wms nrw: https://www.wms.nrw.de/geobasis/wms_nw_dop
    """
    wms_nasa = "http://wms.jpl.nasa.gov/wms.cgi"
    wms_nrw = "https://www.wms.nrw.de/geobasis/wms_nw_dop"
    nasa_map_key = "eb85268ac9785f26c2bd58bfe182fbe"
    wms= WebMapService(wms_nrw, version='1.1.1',username=nasa_map_key)
    print(wms.identification.abstract)
    wms_content = list(wms.contents)
    
    color_map = wms_content[2]
    print(color_map)
    print(wms.identification.version)
    print('bounding box: ', wms[color_map].boundingBoxWGS84)
    print(wms[color_map].crsOptions)
    box=(y1,x1,y2, x2)

    print('box', box)
    #box = (5.59334, 50.0578, 9.74158, 52.7998)
    img = wms.getmap(layers=[color_map],srs='EPSG:4326', bbox=box, format='image/jpeg',transparent=False, size=[size,size] )
    out = open('sat_data.jpg', 'wb')
    out.write(img.read())
    out.close()
    img = Image.open('sat_data.jpg')
    img = np.array(img)
    return img

#fetch(5.72499, 50.1506, 9.53154, 52.602)
    