"""
Python script to gather weather data and analyse danger for specific locations, extracted from LiDAr file.
weather data from API: api.openweathermap.org

1. Read a las file (function defined in: get_points())
2. Extract coordinates of las file and convert them from utm into lat,lon (defined in: get_coordinates())
3. Call Weather API at coordinates and check for heat, storm, drought (defined in: get_weather(), check_storm(), check_heat())
4. If there is an alert, check if there is a tree in the area, and set rgb values for the points in tree
    write the points into another las file and return it. 

"""
from urllib import response
import requests
import json
import coord_f
import laspy
import numpy
import colorful_alerts
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

# take lidar points as numpy array and extract location, call API for that location and check for weather alerts
def get_weather(las):
    # get up-left coordinates in las-file:
    danger = 0
    las_points = get_points(las)
    coordinates = get_coordinates(las_points)
    lat = coordinates[0]
    lon = coordinates[1]
    # Call API for requested location
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
    # if there is storm or heat, check if there is high vegetation in lidar file:
    if storm or heat: 
        # las_points is a numpy array, and we want to check for each entry, if the point is classified as high vegetation (classification number 5)
        for point in las_points:
            if point.classification == 5 and danger == 1:
                # request species or family of given tree and calculate risk --> wo ist die denn gespeichert?
                if point.tree_class in check_tree.very_well_adapted_dryness:
                    # yellow
                    point.red = 255
                    point.green = 255
                    point.blue = 102
                elif point.tree_class in check_tree.well_adapted_dryness:
                    # orange
                    point.red = 255
                    point.green = 204
                    point.blue = 153
                elif point.tree_class in check_tree.moderately_well_adapted_dryness:
                    # dark orange
                    point.red = 255
                    point.green = 128
                    point.blue = 0
                elif point.tree_class in check_tree.not_adapted_dryness:
                    # red
                    point.red = 255
                    point.green = 0
                    point.blue = 0
            elif point.classification == 5 and danger == 1:
                # request species or family of given tree and calculate risk --> wo ist die denn gespeichert?
                if point.tree_class in check_tree.very_well_adapted_dryness:
                    # orange
                    point.red = 255
                    point.green = 204
                    point.blue = 153
                elif point.tree_class in check_tree.well_adapted_dryness:
                    # dark orange
                    point.red = 255
                    point.green = 128
                    point.blue = 0

                elif point.tree_class in check_tree.moderately_well_adapted_dryness:
                    # red
                    point.red = 255
                    point.green = 0
                    point.blue = 0    
                elif point.tree_class in check_tree.not_adapted_dryness:
                    # violet
                    point.red = 153
                    point.green = 0
                    point.blue = 153
    return las_points[0].red   
    #return storm, heat


def main():
    lidar_file = "/home/masch/Dokumente/Uni/datachallenges/git/lidar-vegetation-data/lidar-files/wesel_buildings/3dm_32_326_5728_1_nw.las"
    print(get_weather(lidar_file))
    #colorful_alerts.colorize_alert(lidar_file, 5, 100,100,100)

if __name__ == '__main__':
    main()  
