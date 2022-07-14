import laspy
import os
import numpy as np


def build_las(factor, x, y, z, c=None, r=None, g=None, b=None, nir=None, header=None):    
    if header == None:
        header = laspy.LasHeader(point_format=8, version="1.4")
        offsets = np.array([0, 0, 0])
        scales =np.array([factor,factor,factor])
    else:
        offsets = header.offsets 
        scales = header.scales
        
    
    las = laspy.create(point_format=header.point_format, file_version=header.version)
    las.header.point_count = len(x)
    #las = laspy.LasData(header)
    las.header.offsets = offsets
    las.header.scales = scales
    if header != None:
        las.vlrs = header.vlrs
    
    las = laspy.convert(las, point_format_id=8)
    print(las.header)
    las.x = x
    las.y = y
    las.z =z
    if c is not None:
        las.points['classification'] = c
    else:
        #set all to high classification
         las.points['classification'] = np.ones(len(x)) * 5
    if r is not None and g is not None and b is not None:
        las.red = r
        las.green = g
        las.blue = b
    if nir is not None:
        las.nir = nir

    return las
         
    
    
