from wsgiref.simple_server import make_server
from wsgi_app import app

if __name__ == '__main__':
    server = make_server('localhost', 8000, app)

    print("=" * 60)
    print("ЗАПУСК WSGI-СЕРВЕРА")
    print("=" * 60)
    print(f"Сервер запущен: http://localhost:8000")
    print("-" * 60)
    print("Проверьте маршруты:")
    print("  http://localhost:8000/hello")
    print("  http://localhost:8000/hello/ВашеИмя")
    print("  http://localhost:8000/info")
    print("-" * 60)
    print("Для остановки: Ctrl+C")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nСервер остановлен")