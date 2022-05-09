import utm


def utm_to_lat_long(x, y, section=32):
    print(x, " ", y)
    latlong = utm.to_latlon(x,y,section, northern=True)
    print(latlong)
    return latlong