import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Optional

import config
import db
import views
import weather
import psycopg


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

    def cities_getter(self, method: Callable, args: tuple) -> None:
        try:
            cities = method(*args)
        except Exception as error:
            return config.SERVER_ERROR, f'Database error: {error}'
        else:
            return config.OK, views.cities(cities)

    def cities_page(self) -> None:
        query = self.get_query()
        if not query or any(key not in config.CITY_KEYS for key in query.keys()):
            method = db.get_all_cities
            args = (self.db_cursor,)
        else:
            print('?????????????')
            method = db.get_cities
            attrs, attr_vals = [], []
            for attr, attr_val in query.items():
                attrs.append(attr)
                attr_vals.append(attr_val)
            args = (self.db_cursor, attrs, attr_vals)
        status, body = self.cities_getter(method, args)
        self.respond(status, body)

    def weather_page(self) -> None:
        CITY_KEY = 'city'
        query = self.get_query()
        if CITY_KEY not in query.keys():
            cities = [city for city, _, _ in db.get_all_cities(self.db_cursor)]
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

    def respond_not_allowed(self) -> None:
        self.respond(config.NOT_ALLOWED, '', headers=config.ALLOW_GET_HEAD)

    def check_auth(self) -> bool:
        if config.AUTH_HEADER not in self.headers.keys():
            return False
        return db.check_token(self.db_cursor, self.headers[config.AUTH_HEADER])

    def allowed_and_auth(self) -> bool:
        if not self.path.startswith('/cities'):
            self.respond_not_allowed()
            return False
        if not self.check_auth():
            self.respond(config.FORBIDDEN)
            return False
        return True

    def read_json_body(self) -> dict | None:
        try:
            body_len = int(self.headers.get('Content-Length'))
        except ValueError:
            self.respond(config.BAD_REQUEST, 'Content-Length header error')
            return
        body = self.rfile.read(body_len)
        try:
            content = json.loads(body)
        except json.JSONDecodeError as error:
            self.respond(config.BAD_REQUEST, f'Invalid JSON: {error}')
            return
        return content

    def do_POST(self) -> None:
        if not self.allowed_and_auth():
            return
        city = self.read_json_body()
        if not city:
            return
        keys_absent = any(key not in city.keys() for key in config.CITY_KEYS)
        redundant_keys = len(city) != len(config.CITY_KEYS)
        if keys_absent or redundant_keys:
            msg = f'City json data is invalid, required keys: {config.CITY_KEYS}'
            self.respond(config.BAD_REQUEST, msg)
            return
        insert_args = (self.db_cursor, self.db_connection, [city[key] for key in config.CITY_KEYS])
        if self.change_db(db.add_city, insert_args, 'created', config.CREATED, json.dumps(city)):
            location = {config.LOCATION_HEADER: f'{config.HOST}:{config.PORT}/cities?name={city["name"]}'}
            self.respond(config.CREATED, headers=location)

    def check_query_key(self, query: dict, key: str) -> None:
        city_key = 'name'
        if city_key not in query.keys():
            self.respond(config.BAD_REQUEST, f'City key {city_key} is not specified')
            return False
        return True

    def do_DELETE(self) -> None:
        if not self.allowed_and_auth():
            return
        city_key = 'name'
        query = self.get_query()
        if not self.check_query_key(query, city_key):
            return
        delete_args = (self.db_cursor, self.db_connection, query[city_key])
        if self.change_db(db.delete_city, delete_args, 'deleted', ):
            self.respond(config.NO_CONTENT)

    def do_PUT(self) -> None:
        if not self.allowed_and_auth():
            return
        city_key = 'name'
        query = self.get_query()
        if city_key not in query.keys():
            self.do_POST()
            return
        city = query[city_key]
        if not db.coordinates_by_city(self.db_cursor, city):
            self.do_POST()
            return
        content = self.read_json_body()
        if not content:
            return
        for key in content.keys():
            if key not in config.CITY_KEYS:
                self.respond(config.BAD_REQUEST, f'key {key} is not defined for this instance')
                return
        if db.update_city(self.db_cursor, self.db_connection, city, content):
            self.respond(config.OK, f'instance was updated')
        else:
            self.respond(config.SERVER_ERROR, f'failed updating instance')
        
    def do_HEAD(self) -> None:
        self.respond(config.OK)

    def change_db(
        self,
        method: Callable, 
        args: tuple,
    ) -> bool:
        try:
            changed = method(*args)
        except psycopg.errors.UniqueViolation:
            self.respond(config.OK, f'already exists: {args[-1]}')
            self.db_connection.rollback()  # Roll back the transaction if it failed
            return False
        except Exception as error:
            self.respond(config.SERVER_ERROR, f'Database error: {error}')
            self.db_connection.rollback()  # Roll back the transaction if it failed
            return False
        if not changed:
            self.respond(config.SERVER_ERROR, f'operation failed on behalf of database')
        return changed


if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), CustomHandler)
    print(f'Server is running on http://{config.HOST}:{config.PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Closed by user')
    finally:
        server.server_close()
