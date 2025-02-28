import json
import requests
import folium
import os
import random
from dotenv import load_dotenv
from geopy import distance


def get_user_distance(cafe_coordinates):
    return cafe_coordinates['distance']


def random_color():
    color = [
        'gray',
        'orange',
        'darkred',
        'cadetblue',
        'lightblue',
    ]
    return random.choice(color)


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()

    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def main():
    load_dotenv('token.env')
    api_key = os.environ['api_key']
    with open("coffee.json", "r", encoding='CP1251') as my_file:
        file_contents = my_file.read()

    coffee_shops = json.loads(file_contents)

    user_location = input('Где вы находитесь? ')
    user_coordinates = fetch_coordinates(api_key, user_location)

    cafe_coordinates = []
    for coffee_shop in coffee_shops:
        cafe_coordinate = dict()
        cafe_coordinate['Name'] = coffee_shop['Name']
        distance_between_coord = distance.distance(
            (user_coordinates[1], user_coordinates[0]),
            (coffee_shop['geoData']['coordinates'][1],
             coffee_shop['geoData']['coordinates'][0])).km

        cafe_coordinate['distance'] = distance_between_coord
        cafe_coordinate['latitude'] = coffee_shop['geoData']['coordinates'][1]
        cafe_coordinate['longitude'] = coffee_shop['geoData']['coordinates'][0]

        cafe_coordinates.append(cafe_coordinate)
    nearest_cafes = sorted(cafe_coordinates, key=get_user_distance)[:5]

    map = folium.Map([user_coordinates[1], user_coordinates[0]], zoom_start=12)
    for cafe in nearest_cafes:
        folium.Marker(
            location=[cafe['latitude'], cafe['longitude']],
            popup=cafe['Name'],
            icon=folium.Icon(color=random_color()),
        ).add_to(map)
    map.save('index.html')


if __name__ == '__main__':
    main()
