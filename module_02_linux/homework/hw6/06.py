from flask import Flask
import os

app = Flask(__name__)


@app.route('/head_file/<int:size>/<path:relative_path>')
def head_file(size, relative_path):
    try:
        abs_path = os.path.abspath(relative_path)

        if not os.path.exists(relative_path):
            return f"Файл не найден: {relative_path}", 404

        with open(relative_path, 'r', encoding='utf-8') as file:
            content = file.read(size)

        result_size = len(content)

        return f"<b>{abs_path}</b> {result_size}<br>{content}"

    except Exception as e:
        return f"Ошибка: {str(e)}", 500


def create_test_files():
    os.makedirs('docs', exist_ok=True)
    with open('docs/simple.txt', 'w', encoding='utf-8') as f:
        f.write('hello world!')
    print("Тестовые файлы созданы")


if __name__ == '__main__':
    create_test_files()
    app.run(debug=True)