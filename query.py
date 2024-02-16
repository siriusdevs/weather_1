SELECT_CITY = 'SELECT * FROM city'
INSERT_CITY = 'INSERT INTO city (name, latitude, longtitude) VALUES (%s, %s, %s)'
COORD_BY_CITY = 'SELECT latitude, longtitude FROM city WHERE name=%s'
DELETE_BY_NAME = 'DELETE FROM city WHERE name=%s'
