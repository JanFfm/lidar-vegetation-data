from distutils.log import debug
#import overpass  #OSM api
import laspy
import overpy # https://betterprogramming.pub/how-to-get-open-street-and-map-data-using-python-2b777bf5af14
import overpy.helper as helper
import OSMPythonTools
#import osmnx
import folium
#https://jingwen-z.github.io/how-to-install-python-module-fiona-on-windows-os/
#https://levelup.gitconnected.com/working-with-openstreetmap-in-python-c49396d98ad4

















api = overpy.Overpass()

wuppertal_querry =  api.query("""node["name"="Wuppertal"];out body;""")
print(wuppertal_querry)
print(wuppertal_querry)
print("-------------------------------------------")

#MapQuery = overpass.MapQuery(50.746, 7.154, 50.748, 7.157)
map =  api.query("node(50.745,7.17,50.75,7.18);out;")
print(map)

print("finish")

