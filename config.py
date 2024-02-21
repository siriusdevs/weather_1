HOST, PORT = ('127.0.0.1', 8000)
OK = 200
SERVER_ERROR = 500
BAD_REQUEST = 400
CREATED = 201
NO_CONTENT = 204
NOT_ALLOWED = 405

CITY_KEYS = 'name', 'lat', 'lon'
WEATHER_FACT_KEYS = 'temp', 'feels_like', 'wind_speed'

YANDEX_HEADER = 'X-Yandex-API-KEY'
URL = 'https://api.weather.yandex.ru/v2/informers'

TEMPLATE_FOLDER = 'templates'
TEMPLATE_MAIN = f'{TEMPLATE_FOLDER}/index.html'
TEMPLATE_WEATHER = f'{TEMPLATE_FOLDER}/weather.html'
TEMPLATE_WEATHER_DUMMY = f'{TEMPLATE_FOLDER}/weather_dummy.html'
TEMPLATE_CITIES = f'{TEMPLATE_FOLDER}/cities.html'

DEFAULT_TIMEOUT = 8
