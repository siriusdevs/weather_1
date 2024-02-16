import requests
import os
import json
from config import YANDEX_KEY_HEADER, URL, OK

class ForeignApiError(Exception):
    def __init__(self, api_name: str, status: int) -> None:
        super().__init__(f'API {api_name} request failed with {status}')

def get_weather(latitude: float, longtitude: float) -> dict:
    headers = {YANDEX_KEY_HEADER: os.environ.get('YANDEX_KEY')}
    coordinates = {'lat': latitude, 'lon': longtitude}
    response = requests.get(URL, params=coordinates, headers=headers)
    if response.status_code != OK:
        raise ForeignApiError('Yandex.Weather', response.status_code)
    
    return json.loads(response.content)