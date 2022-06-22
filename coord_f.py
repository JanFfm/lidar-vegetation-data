import utm
import geopy

def utm_to_lat_long(x, y, section=32):
    """_summary_

    Args:
        x (_type_): _description_
        y (_type_): _description_
        section (int, optional): _description_. Defaults to 32.

    Returns:
        _type_: _description_
    """
    print(x, " ", y)
    latlong = utm.to_latlon(x,y,section, northern=True)
    print(latlong)
    return latlong

def lat_long_to_gps(lat, long):
    point = geopy.Point(lat, long)
    pass
