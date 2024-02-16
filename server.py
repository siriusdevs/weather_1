from http.server import HTTPServer, BaseHTTPRequestHandler

HOST, PORT = ('127.0.0.1', 8000)
OK = 200

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(OK)
        self.send_header('Content-Type', 'text/json')
        self.end_headers()
        self.wfile.write(''.encode())


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), CustomHandler)
    print(f'Server is running on http://{HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Closed by user')
    finally:
        server.server_close()
