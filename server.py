from http.server import BaseHTTPRequestHandler, HTTPServer

import db

HOST, PORT = ('127.0.0.1', 8000)
OK = 200


def database_connection(class_: type) -> type:
    conn_name, cursor_name = 'db_connection', 'db_cursor'
    connection, cursor = db.connect()
    setattr(class_, conn_name, connection)
    setattr(class_, cursor_name, cursor)
    return class_


@database_connection
class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(OK)
        self.send_header('Content-Type', 'text')
        self.end_headers()
        cities = '\n'.join(str(city) for city in db.get_cities(self.db_cursor))
        self.wfile.write(cities.encode())


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), CustomHandler)
    print(f'Server is running on http://{HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Closed by user')
    finally:
        server.server_close()
