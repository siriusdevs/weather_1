from http.server import BaseHTTPRequestHandler, HTTPServer

import db
import json
from typing import Optional

from config import *


def database_connection(class_: type) -> type:
    conn_name, cursor_name = 'db_connection', 'db_cursor'
    connection, cursor = db.connect()
    setattr(class_, conn_name, connection)
    setattr(class_, cursor_name, cursor)
    return class_


@database_connection
class CustomHandler(BaseHTTPRequestHandler):
    def respond(self, status: int, body: str, message: Optional[str] = None) -> None:
        self.send_response(status, message)
        self.send_header('Content-Type', 'text')
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self) -> None:
        try:
            cities = db.get_cities(self.db_cursor)
        except Exception as error:
            status, body = SERVER_ERROR, f'Database error: {error}'
        else:
            status, body = OK, '\n'.join(str(city) for city in cities)
        self.respond(status, body)

    def do_POST(self) -> None:
        try:
            body_len = int(self.headers.get('Content-Length'))
        except ValueError:
            self.respond(BAD_REQUEST, 'Content-Length header error')
            return
        try:
            city = json.loads(self.rfile.read(body_len))
        except json.JSONDecodeError:
            self.respond(BAD_REQUEST, 'Invalid JSON')
            return
        if any(key not in city.keys() for key in CITY_KEYS) or len(city) != len(CITY_KEYS):
            self.respond(BAD_REQUEST, f'City json data is invalid, required keys: {CITY_KEYS}')
            return
        try:
            created = db.add_city(self.db_cursor, self.db_connection, [city[key] for key in CITY_KEYS])
        except Exception as error:
            self.respond(SERVER_ERROR, f'Database error: {error}')
            return
        if created:
            self.respond(CREATED, f'Record with {city} was created')
        else:
            self.respond(SERVER_ERROR, f'City was not created: {city["name"]}')


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), CustomHandler)
    print(f'Server is running on http://{HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Closed by user')
    finally:
        server.server_close()
