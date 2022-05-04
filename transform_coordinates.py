




def transform(x,y,z=0, offset=[  -0., 5000000., -0.], scale= [0.01, 0.01, 0.01]):
    x = x * scale[0] + offset[0]
    y = y * scale[1] + offset[1]
    z = z *scale[2] + offset[2]
    gps = (x,y,z)
    print(gps)
    return gps

transform(29000001,64700007,9524)