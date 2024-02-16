CITIES_SELECT = 'SELECT * FROM city'
CITIES_INSERT = 'INSERT INTO city (name, latitude, longtitude) VALUES (%s, %s, %s)'
CITIES_COORD_BY_CITY = 'SELECT latitude, longtitude FROM city WHERE name=%s'

HOST, PORT = ('127.0.0.1', 8000)
OK = 200
SERVER_ERROR = 500
BAD_REQUEST = 400
CREATED = 201

CITY_KEYS = 'name', 'lat', 'lon'
