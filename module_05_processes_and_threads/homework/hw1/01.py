import os
import subprocess
import socket
from time import sleep


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_by_port_windows(port):
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            shell=True
        )

        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                pid = parts[-1]
                print(f"Найден процесс с PID {pid}, занимающий порт {port}")

                subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
                print(f"Процесс {pid} завершен")
                sleep(2)
                return True

        print(f"Не найден процесс, занимающий порт {port}")
        return False

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при завершении процесса: {e}")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def start_flask_server(port):
    try:
        from flask import Flask
        app = Flask(__name__)

        @app.route('/')
        def hello():
            return f'Сервер запущен на порту {port}!'

        print(f"Запускаем Flask сервер на http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        return True

    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")
        return False


def start_server_on_port(port):
    if is_port_in_use(port):
        print(f"Порт {port} занят, пытаемся освободить...")
        kill_process_by_port_windows(port)

    if is_port_in_use(port):
        print(f"Не удалось освободить порт {port}")
        return False

    print(f"Порт {port} свободен, запускаем сервер")
    return start_flask_server(port)


if __name__ == "__main__":
    port = 5000
    start_server_on_port(port)
