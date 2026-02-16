import json
import urllib.parse
from wsgiref.simple_server import make_server


class WSGIApplication:
    def __init__(self):
        self.routes = {}
        self.error_handlers = {}

    def route(self, pattern):
        def decorator(handler):
            self.routes[pattern] = handler
            return handler

        return decorator

    def error_handler(self, code):
        def decorator(handler):
            self.error_handlers[code] = handler
            return handler

        return decorator

    def __call__(self, environ, start_response):
        path = urllib.parse.unquote(environ.get('PATH_INFO', '/'))

        print(f"Запрос: {environ.get('REQUEST_METHOD')} {path}")

        response_data = None
        status = '404 Not Found'

        if path in self.routes:
            handler = self.routes[path]
            response_data = handler(environ)
            status = '200 OK'

        elif path.startswith('/hello/'):
            name = path.replace('/hello/', '')
            if name and '/hello/<name>' in self.routes:
                handler = self.routes['/hello/<name>']
                response_data = handler(environ, name=name)
                status = '200 OK'

        if response_data is None:
            if 404 in self.error_handlers:
                response_data = self.error_handlers[404](environ, path)
            else:
                response_data = {"error": "Not Found", "path": path}

        response_body = json.dumps(
            response_data,
            ensure_ascii=False,
            indent=2
        ).encode('utf-8')

        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(response_body)))
        ]

        start_response(status, headers)
        return [response_body]


app = WSGIApplication()


@app.route("/hello")
def hello_handler(environ):
    return {"response": "Hello, world!"}


@app.route("/hello/<name>")
def hello_name_handler(environ, name):
    return {"response": f"Hello, {name}!"}


@app.route("/info")
def info_handler(environ):
    return {
        "server": "Custom WSGI Server",
        "path": environ.get('PATH_INFO'),
        "method": environ.get('REQUEST_METHOD'),
        "query": environ.get('QUERY_STRING', ''),
        "user_agent": environ.get('HTTP_USER_AGENT', 'unknown')
    }


@app.error_handler(404)
def not_found_handler(environ, path):
    return {
        "error": "Page Not Found",
        "path": path,
        "status": 404
    }


if __name__ == '__main__':
    server = make_server('localhost', 8000, app)
    print("=" * 60)
    print("СОБСТВЕННОЕ WSGI-ПРИЛОЖЕНИЕ")
    print("=" * 60)
    print(f"Сервер запущен: http://localhost:8000")
    print("-" * 60)
    print("ДОСТУПНЫЕ МАРШРУТЫ:")
    print("  ✓ /hello          - приветствие")
    print("  ✓ /hello/<имя>    - персональное приветствие")
    print("  ✓ /info           - информация о запросе")
    print("-" * 60)
    print("ПРИМЕРЫ:")
    print("  http://localhost:8000/hello")
    print("  http://localhost:8000/hello/Иван")
    print("  http://localhost:8000/hello/John")
    print("  http://localhost:8000/info")
    print("-" * 60)
    print("Для остановки: Ctrl+C")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nСервер остановлен")