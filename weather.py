import json
import os

import requests

from config import DEFAULT_TIMEOUT, OK, URL, WEATHER_FACT_KEYS, YANDEX_HEADER


class ForeignApiError(Exception):
    def __init__(self, api_name: str, status: int) -> None:
        super().__init__(f'API {api_name} request failed with {status}')


def get_weather(latitude: float, longtitude: float) -> dict:
    headers = {YANDEX_HEADER: os.environ.get('YANDEX_KEY')}
    coordinates = {'lat': latitude, 'lon': longtitude}
    response = requests.get(URL, params=coordinates, headers=headers, timeout=DEFAULT_TIMEOUT)
    if response.status_code != OK:
        raise ForeignApiError('Yandex.Weather', response.status_code)
    fact = json.loads(response.content)['fact']
    return {key: fact[key] for key in WEATHER_FACT_KEYS}
