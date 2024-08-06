import math
import time
import json
from pypresence import Presence
import requests
from geopy.distance import geodesic

#insert your client id from your application on discord
DISCORD_CLIENT_ID = '1269982804469354526'

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

        # we are getting data from the ets2 telemetry server for the job
        job = data.get('job', {})
        source_city = job.get('sourceCity', {})
        destination_city = job.get('destinationCity', {})

        # we are checking if source city and destination city makes true or not
        job_valid = source_city and destination_city

        # we are getting kilometers data
        kmLeft = data.get('navigation', {}).get('estimatedDistance', {})
        # we are converting from meters to kilometers
        distance_km = kmLeft / 1000
        # we format the distance to display only the 3 first digits
        formatted_distance = f"{distance_km:.1f}"  if job else "N/A"


        # we have to round the speed that we are going on because it's 90.98435 for example, and this is bad.
        # we will fix it with:
        speed = data.get('truck', {}).get('speed', {})
        speed = round(speed)

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

        # if the job is valid, display this data
        if job_valid:
            state = f"Driving from {source_city} to {destination_city} - {formatted_distance} KM left"
            details = f"Currently near {nearest_city} with {speed} KM/H"
        else: #if we don't have a job, display freeroaming
            state = "Freeroaming"
            details = f"Currently in {nearest_city} with {speed} KM/H"


        # showing the final information on discord
        rpc.update(
            state = state,
            details= details,
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
    time.sleep(5)  # set the time to update whatever you want

#TODO: i miss to do
# to display if the game is paused or not
# to display the truck we are driving in the big image on the presence
# to display the speed limit that we have in the small image on the presence