import os
import http.server
import socketserver
import socket
import webbrowser


def deploy_site():
    site_folder = "new_year_application"

    if not os.path.exists(site_folder):
        print(f"❌ Папка '{site_folder}' не найдена!")
        print("Убедитесь, что:")
        print(f"1. Файл находится в той же папке, где лежит '{site_folder}'")
        print(f"2. Папка '{site_folder}' содержит файлы сайта")
        return

    os.chdir(site_folder)

    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("🎄" * 50)
        print("НОВОГОДНИЙ САЙТ ЗАПУЩЕН! 🎅")
        print("=" * 50)
        print(f"📁 Папка сайта: {site_folder}")
        print(f"🌐 Порт: {PORT}")
        print("=" * 50)
        print("📍 ДОСТУПНЫЕ АДРЕСА:")
        print(f"• Локально: http://localhost:{PORT}")
        print(f"• Из сети: http://{local_ip}:{PORT}")
        print("=" * 50)
        print("📋 ИНСТРУКЦИЯ ДЛЯ ДРУЗЕЙ:")
        print(f"1. Убедитесь, что вы в одной сети (Wi-Fi)")
        print(f"2. Откройте браузер")
        print(f"3. Введите: http://{local_ip}:{PORT}")
        print("=" * 50)
        print("🛑 Для остановки: Ctrl+C")
        print("🎄" * 50)

        webbrowser.open(f"http://localhost:{PORT}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Сервер остановлен")
            os.chdir("..")


if __name__ == "__main__":
    deploy_site()
