import math
import time
import json
from pypresence import Presence
import requests
from geopy.distance import geodesic

#insert your client id from your application on discord
DISCORD_CLIENT_ID = ''

#connecting to the discord rpc
rpc = Presence(DISCORD_CLIENT_ID)
rpc.connect()

# get the cities.json file here
with open('cities.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    cities_list = data.get('citiesList', [])

# create dictionary for the city names
city_coordinates = {}
for city in cities_list:
    city_name = city.get('realName')
    # we are going to use 3D mapping, so it displays more preciously for the presence
    city_coords = (float(city.get('x')),
                   float(city.get('y')),
                   float(city.get('z')))
    city_coordinates[city_name] = city_coords

# function to get the nearest city by coordinates
def get_nearest_city(x, y, z):
    min_distance = float('inf')
    nearest_city = "Unknown"
    for city, coords in city_coordinates.items():
        distance = math.sqrt((x - coords[0])**2 + (y - coords[1])**2 + (z - coords[2])**2)
        if distance < min_distance:
            min_distance = distance
            nearest_city = city
    return nearest_city


# function to get data from ets2 telemetry server
# make sure that you have installed and launched the ets2 telemetry server
def get_ets2_data():
    response = requests.get('http://localhost:25555/api/ets2/telemetry')
    return response.json()

# function to update the discord rich presence
def update_presence(data):
    try:
        print(data)  # we will print the data to see the logs in the console, so we will know what is going on :)

        # info that will show in the rich presence
        source_city = data.get('job', {}).get('sourceCity', {})
        destination_city = data.get('job', {}).get('destinationCity', {})
        speed = data.get('truck', {}).get('speed', {})
        kmLeft = data.get('navigation', {}).get('estimatedDistance', {})

        # we have to round the speed that we are going on because it's 90.98435 for example, and this is bad.
        # we will fix it with:
        speed = round(speed)

        # converting from meters to kilometers.
        distance_km = kmLeft / 1000

        # we will format the distance_km only to display the first 3 digits for the kilometers.
        formatted_distance = f"{distance_km:.1f}"  # One decimal place

        # we are getting coordinates in real time from the game
        coordinates = data.get('truck', {}).get('placement', {})
        x = coordinates.get('x', None)
        y = coordinates.get('y', None)
        z = coordinates.get('z', None)

        # finding the nearest city to display in the rich presence
        if x is not None and y is not None and z is not None:
            nearest_city = get_nearest_city(float(x), float(y), float(z))
        else:
            nearest_city = "Unknown"

        # showing the final information on discord
        rpc.update(
            state = f"Driving from {source_city} to {destination_city} - {formatted_distance} KM left",
            details=f"Currently near {nearest_city} with {speed} KM/H",
            large_image="large_icon_key",  # to add big image on the presence
            small_image="small_icon_key",  # to add small image on the presence
            start=time.time()
        )
        # exceptions to show if something goes wrong
    except KeyError as e:
        print(f"KeyError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# loop that always works to update and show the data.
while True:
    ets2_data = get_ets2_data()
    update_presence(ets2_data)
    time.sleep(10)  # set the time to update whatever you want

#TODO: i miss to do
# when we are not in a job, to display freeroam
# to display the truck we are driving in the big image on the presence
# to display the speed limit that we have in the small image on the presence