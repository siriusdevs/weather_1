CITIES_SELECT = 'SELECT * FROM city'
CITIES_INSERT = 'INSERT INTO city (name, latitude, longtitude) VALUES (%s, %s, %s)'
CITIES_COORD_BY_CITY = 'SELECT latitude, longtitude FROM city WHERE name=%s'
CITIES_DELETE_BY_NAME = 'DELETE FROM city WHERE name=%s'

HOST, PORT = ('127.0.0.1', 8000)
OK = 200
SERVER_ERROR = 500
BAD_REQUEST = 400
CREATED = 201
NO_CONTENT = 204
NOT_ALLOWED = 405

CITY_KEYS = 'name', 'lat', 'lon'

YANDEX_KEY_HEADER = 'X-Yandex-API-KEY'
URL = 'https://api.weather.yandex.ru/v2/informers'
