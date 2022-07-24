"""
Python script to gather weather data and analyse danger for specific locations, extracted from LiDAr file.
weather data from API: api.openweathermap.org

1. Read a las file (function defined in: get_points())
2. Extract coordinates of las file and convert them from utm into lat,lon (defined in: get_coordinates())
3. Call Weather API at coordinates and check for heat, storm, drought (defined in: get_weather(), check_storm(), check_heat())
4. return danger score for coordinate (defined in get_danger())

"""
from urllib import response
from matplotlib.pyplot import get
import requests
import json
import coord_f
import laspy
import numpy
import check_tree

# read a las file and return all points in numpy array
def get_points(las_file):
    las = laspy.read(las_file)
    las = laspy.convert(point_format_id=8, source_las=las)  
    return las

# takes first point in las array and calculates lat, lon from utm. returns two points as tuples (lat, lon)
def get_coordinates(las):
    #coords = numpy.vstack((las.x, las.y)).transpose()
    x = min(las.points.x)
    y = max(las.points.y)
    coord = coord_f.utm_to_lat_long(x, y)
    # return tuple (lat,lon)
    return coord

# pretty print json object
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# gather api response
def call_api(url):
    response = requests.get(url)
    return response.json()

# needs dictionary object as api_response, returns True if there is a storm, False if there is no storm (definition for 'storm' from openweather.com)
def check_storm(api_response):
    storm = False
    wind = api_response.get('wind')
    if wind['speed'] >= 27.8: # meter/second
        storm = True 
    return storm

# needs dictionary object as api_response definition for drought: more than 4 months less rain than usual
def drought(api_response):
    rain = api_response.json()['regen']
    # call API to get historic rain data (or alerts for dryness?)
    pass

# needs dictionary object as api_response, returns True when heat: more than 30° Celsius = 303 Kelvin
def check_heat(api_response):
    heat = False
    weather = api_response.get('main')
    temperature = weather['temp']
    if temperature >= 203: 
        heat = True
    return heat

# needs dictionary object as api_response, returns True if there is an alert for the location
def call_weather_alerts(api_response):
    alert = False
    request = requests.get("https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/")
    warning = api_response.get('warnings_nowcast')
    return warning

# return danger score for a coordinate Score range: 0 to 6
def get_danger(lon, lat, class_of_tree):
    danger = 0
    base_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang=de&appid=d1eb6e68d2df1de466fdf3a936b966dd"
    api_response = call_api(base_url)
    # check if it is stormy and increment danger score
    storm = check_storm((api_response))
    if storm: 
        danger += 1
    # check if it is hot and increment danger score
    heat = check_heat((api_response))
    if heat: 
        danger += 1
    if class_of_tree in check_tree.very_well_adapted_dryness:
        danger += 1
    if class_of_tree in check_tree.well_adapted_dryness:
        danger += 2
    if class_of_tree in check_tree.moderately_well_adapted_dryness:
        danger += 3
    if class_of_tree in check_tree.not_adapted_dryness:
        danger += 4
    # return danger score 
    return danger

def main():
    lidar_file = "/home/masch/Dokumente/Uni/datachallenges/git/lidar-vegetation-data/lidar-files/wesel_buildings/3dm_32_326_5728_1_nw.las"
    las_points = get_points(lidar_file)
    coordinates = get_coordinates(las_points)
    print(get_danger(coordinates[0], coordinates[1], "Fichte"))

if __name__ == '__main__':
    main()  
