from wsgiref.simple_server import make_server
from wsgi_app import app

if __name__ == '__main__':
    server = make_server('127.0.0.1', 8000, app)

    print("=" * 70)
    print("ЗАПУСК WSGI-СЕРВЕРА (для динамических запросов)")
    print("=" * 70)
    print(f"WSGI сервер запущен: http://127.0.0.1:8000")
    print(f"Статика отдается через Nginx: http://localhost/static/")
    print("-" * 70)
    print("ДОСТУПНЫЕ МАРШРУТЫ:")
    print("  WSGI приложение:  http://localhost/hello")
    print("  WSGI приложение:  http://localhost/hello/ВашеИмя")
    print("  WSGI приложение:  http://localhost/info")
    print("  Статические файлы: http://localhost/static/images/image1.jpg")
    print("  Галерея:          http://localhost/static/index.html")
    print("-" * 70)
    print("Для остановки: Ctrl+C")
    print("=" * 70)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nWSGI сервер остановлен")