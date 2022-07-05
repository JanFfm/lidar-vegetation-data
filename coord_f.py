import utm
#import geopy

def utm_to_lat_long(x, y, section=32):
    """_summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
        section (int, optional): _description_. Defaults to 32.

    Returns:
        _type_: _description_
    """
    latlong = utm.to_latlon(x,y,section, northern=True)
    return latlong


def lat_long_to_utm(lat, long):
    """_summary_

    Args:
        lat (_type_): y
        long (_type_): x
    Returns:
        _type_: _description_
    """
    u = utm.from_latlon(lat,long)
    return u
    
