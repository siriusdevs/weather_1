CITIES_SELECT = 'SELECT * FROM city'
CITIES_INSERT = 'INSERT INTO city (name, latitude, longtitude) VALUES (%s, %s, %s)'
CITIES_COORD_BY_CITY = 'SELECT latitude, longtitude FROM city WHERE name=%s'
