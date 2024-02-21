import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Optional

import config
import db
import views
import weather


def database_connection(class_: type) -> type:
    conn_name, cursor_name = 'db_connection', 'db_cursor'
    connection, cursor = db.connect()
    setattr(class_, conn_name, connection)
    setattr(class_, cursor_name, cursor)
    return class_


@database_connection
class CustomHandler(BaseHTTPRequestHandler):
    def get_query(self) -> dict:
        qm_index = self.path.find('?')
        if qm_index == -1 or qm_index == len(self.path) - 1:
            return {}
        pairs = self.path[qm_index+1:].split('&')
        query = {}
        for pair in pairs:
            key, value = pair.split('=')
            if value.isdigit():
                query[key] = int(value)
                continue
            try:
                float(value)
            except ValueError:
                query[key] = views.plusses_to_spaces(value)
            else:
                query[key] = float(value)
        return query

    def respond(
        self, status: int, 
        body: Optional[str] = None,
        headers: Optional[dict] = None,
        message: Optional[str] = None,
    ) -> None:
        self.send_response(status, message)
        self.send_header('Content-Type', 'text')
        if headers:
            for header, h_value in headers.items():
                self.send_header(header, h_value)
        self.end_headers()
        if body:
            self.wfile.write(body.encode())

    def cities_page(self) -> None:
        try:
            cities = db.get_cities(self.db_cursor)
        except Exception as error:
            status, body = config.SERVER_ERROR, f'Database error: {error}'
        else:
            status, body = config.OK, views.cities(cities)
        self.respond(status, body)

    def weather_page(self) -> None:
        CITY_KEY = 'city'
        query = self.get_query()
        if CITY_KEY not in query.keys():
            cities = [city for city, _, _ in db.get_cities(self.db_cursor)]
            self.respond(config.OK, views.weather_dummy(cities))
            return
        city_name = query[CITY_KEY]
        db_response = db.coordinates_by_city(self.db_cursor, city_name)
        if not db_response:
            self.respond(config.OK, f'No city named {city_name} in database')
            return
        weather_params = weather.get_weather(*db_response)
        weather_params[CITY_KEY] = city_name
        self.respond(config.OK, views.weather(weather_params))

    def do_GET(self) -> None:
        if self.path.startswith('/cities'):
            self.cities_page()
        elif self.path.startswith('/weather'):
            self.weather_page()
        else:
            self.respond(config.OK, views.main())

    def respond_not_allowed(self):
        self.respond(config.NOT_ALLOWED, '', headers=config.ALLOW_GET_HEAD)

    def do_POST(self) -> None:
        if not self.path.startswith('/cities'):
            self.respond_not_allowed()
            return
        try:
            body_len = int(self.headers.get('Content-Length'))
        except ValueError:
            self.respond(config.BAD_REQUEST, 'Content-Length header error')
            return
        body = self.rfile.read(body_len)
        try:
            city = json.loads(body)
        except json.JSONDecodeError:
            self.respond(config.BAD_REQUEST, 'Invalid JSON')
            return
        keys_absent = any(key not in city.keys() for key in config.CITY_KEYS)
        redundant_keys = len(city) != len(config.CITY_KEYS)
        if keys_absent or redundant_keys:
            msg = f'City json data is invalid, required keys: {config.CITY_KEYS}'
            self.respond(config.BAD_REQUEST, msg)
            return
        insert_args = (self.db_cursor, self.db_connection, [city[key] for key in config.CITY_KEYS])
        self.change_db(db.add_city, insert_args, 'created', config.CREATED, body.decode())

    def do_DELETE(self) -> None:
        if not self.path.startswith('/cities'):
            self.respond_not_allowed()
            return
        query = self.get_query()
        if 'city' not in query.keys():
            self.respond(config.BAD_REQUEST, 'City is not specified')
            return
        delete_args = (self.db_cursor, self.db_connection, query['city'])
        self.change_db(db.delete_city, delete_args, 'deleted', config.NO_CONTENT)

    def change_db(self, method: Callable, args: tuple, action: str, success_code: int, body: Optional[str] = None) -> None:
        try:
            deleted = method(*args)
        except Exception as error:
            self.respond(config.SERVER_ERROR, f'Database error: {error}')
            self.db_connection.rollback()  # Roll back the transaction if it failed
            return
        if deleted:
            self.respond(success_code, body if config.CREATED else None)
        else:
            self.respond(config.SERVER_ERROR, f'Record was not {action}: {args[-1]}')


if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), CustomHandler)
    print(f'Server is running on http://{config.HOST}:{config.PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Closed by user')
    finally:
        server.server_close()
