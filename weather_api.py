"""
Python script to gather weather data of one location, 
location extracted from a LiDAR-file.
API: api.openweathermap.org
"""
from urllib import response
import requests
import json
import coord_f
import laspy
import numpy

# take up-left, down-right points in one las file and extract lat,lon coordinates. returns two points as tuples (lat, lon)
def get_coordinates(las_file):
    las = laspy.read(las_file)
    las_points_x = numpy.array(las.points['x']) 
    las_points_y = numpy.array(las.points['y'])
    x2, x1, y2, y1 = las_points_x.max(),  las_points_x.min(), las_points_y.max(),  las_points_y.min()
    top_left = coord_f.utm_to_lat_long(x1, y2)
    down_right = coord_f.utm_to_lat_long(x2, y1)
    return top_left, down_right

# pretty print json object
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# gather api response
def call_api(url):
    response = requests.get(url)
    return response.json()

# needs dictionary object as api_response, returns True if there is a storm, False if there is no storm (definition for 'storm' from openweather.com)
def call_storm(api_response):
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
def call_heat(api_response):
    heat = False
    weather = api_response.get('main')
    temperature = weather['temp']
    if temperature >= 303: 
        heat = True
    return heat

# needs dictionary object as api_response, returns True if there is an alert for the location
def call_weather_alerts(api_response):
    alert = False
    request = requests.get("https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/")
    warning = api_response.get('warnings_nowcast')
    return warning

# take las-file and extract location, call API for that location and check for weather alerts
def get_weather(las_file):
    # get up-left, down-right coordinates in las-file:
    coordinates = get_coordinates(las_file)
    lat = [y[0] for y in coordinates]
    lon = [y[1] for y in coordinates]
    # Call API for requested location
    for x in range(2):
        base_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat[x]}&lon={lon[x]}&lang=de&appid=d1eb6e68d2df1de466fdf3a936b966dd"
        api_response = call_api(base_url)
        storm = call_storm((api_response))
        heat = call_heat((api_response))
    return storm, heat

# check for weather alerts in one LiDAR-File:
def set_alert(lidar_file):
    alert = get_weather(lidar_file)
    if alert[0] == True:
        print("Storm", alert)
    elif alert[1] == True:
        print("Heat", alert)
    else: 
        print("No alert", alert)

def main():
    lidar_file = "/home/3dm_32_326_5728_1_nw.las"
    set_alert(lidar_file)



if __name__ == '__main__':
    main()  
