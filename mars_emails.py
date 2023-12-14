from random import choice
import os

import requests


rover_url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


def get_mars_photo(sol, api_key='DEMO_KEY'):
    params = {'sol': sol, 'api_key': api_key}
    response = requests.get(rover_url, params).json()
    photos = response['photos']

    return choice(photos)['img_src']

get_mars_photo("1000")