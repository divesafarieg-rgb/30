from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__)

static_directory = os.path.join(os.path.dirname(__file__), 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def send_static(filename):
    print(f"[LOG] Запрошен статический файл: /static/{filename}")
    return send_from_directory(static_directory, filename)

if __name__ == '__main__':
    print("=" * 50)
    print("Flask сервер ЗАПУЩЕН!")
    print("Откройте в браузере: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
