import http.server
import base64
import json
from urllib.parse import urlparse, parse_qs


class CustomServerHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="demo_realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        # Проверка на отсутствие заголовка об аутентификации
        if self.headers.get('Authorization') is None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        # Если схема указана Basic, то начинается процесс сверки данных
        elif self.headers.get('Authorization') == 'Basic ' + self.get_auth_key():
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            getvars = self._parse_GET()

            response = {
                'path': self.path,
                'get_vars': str(getvars)
            }

            base_path = urlparse(self.path).path
            if base_path == '/path1':
                # Do some work
                pass
            elif base_path == '/path2':
                # Do some work
                pass

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        # В иных случаях будет отправлен ответ с ошибочным статусом
        else:

            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def _parse_GET(self):
        getvars = parse_qs(urlparse(self.path).query)
        return getvars


class CustomHTTPServer(http.server.HTTPServer):
    key = ''

    def __init__(self, address, handlerClass=CustomServerHandler):
        super().__init__(address, handlerClass)

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key


if __name__ == '__main__':
    server = CustomHTTPServer(('localhost', 8080))
    server.set_auth('login', 'pass')
    server.serve_forever()
