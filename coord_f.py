import utm

def utm_to_lat_long(x, y, section=32):
    """converts utm coordinatess to lat long
   """
    latlong = utm.to_latlon(x,y,section, northern=True)
    return latlong


def lat_long_to_utm(lat, long):
    """converts lat long to utm coordinaes """ 
    u = utm.from_latlon(lat,long)
    return u
    
