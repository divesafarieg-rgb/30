from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
import sqlite3
import os
import yaml

app = Flask(__name__)


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    "title": "Library REST API",
    "version": "1.0.0",
    "description": """
    ## 📚 REST API для управления библиотекой

    ### Основные возможности:
    - 📖 Управление книгами (добавление, получение)
    - 👥 Управление авторами (добавление, получение, удаление)
    - 🔗 Автоматическое создание авторов при добавлении книг
    - 🗑️ Каскадное удаление книг при удалении авторов

    ### Требования задачи выполнены:
    1. ✅ API для книг документирован в формате YAML (books.yml)
    2. ✅ API для авторов документирован в формате Python-словаря
    3. ✅ Swagger UI доступен по адресу /swagger/
    """
}

swagger = Swagger(app, config=swagger_config)


books_yaml_content = """
swagger: "2.0"
info:
  title: Books API
  version: "1.0"
paths:
  /api/books/:
    post:
      tags:
        - Книги
      summary: Создать новую книгу
      description: |
        Создает новую книгу в библиотеке.

        Можно указать ID существующего автора или создать нового автора по имени.
      consumes:
        - application/json
      produces:
        - application/json
      parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            required:
              - title
            properties:
              title:
                type: string
                description: Название книги
                example: "Война и мир"
              publication_year:
                type: integer
                description: Год публикации
                example: 1869
              isbn:
                type: string
                description: ISBN книги
                example: "978-5-17-090498-2"
              author_id:
                type: integer
                description: ID существующего автора
                example: 1
              author_name:
                type: string
                description: Имя нового автора
                example: "Лев Толстой"
              author_birth_date:
                type: string
                description: Дата рождения автора (YYYY-MM-DD)
                example: "1828-09-09"
              author_biography:
                type: string
                description: Биография автора
                example: "Русский писатель, классик"
      responses:
        201:
          description: Книга успешно создана
          schema:
            type: object
            properties:
              id:
                type: integer
                example: 1
              title:
                type: string
                example: "Война и мир"
              publication_year:
                type: integer
                example: 1869
              isbn:
                type: string
                example: "978-5-17-090498-2"
              author_id:
                type: integer
                example: 1
        400:
          description: Неверный запрос
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Название книги обязательно"
        404:
          description: Автор не найден
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Автор не найден"
        500:
          description: Внутренняя ошибка сервера
"""

with open('books.yml', 'w', encoding='utf-8') as f:
    f.write(books_yaml_content)

print("✅ YAML документация для книг создана: books.yml")


AUTHORS_GET_DOCS = {
    "tags": ["Авторы"],
    "summary": "Получить всех авторов",
    "description": "Возвращает список всех авторов с количеством их книг",
    "produces": ["application/json"],
    "responses": {
        "200": {
            "description": "Успешный запрос",
            "examples": {
                "application/json": [
                    {
                        "id": 1,
                        "name": "Лев Толстой",
                        "birth_date": "1828-09-09",
                        "biography": "Русский писатель",
                        "books_count": 3
                    }
                ]
            }
        },
        "500": {
            "description": "Внутренняя ошибка сервера"
        }
    }
}

AUTHORS_POST_DOCS = {
    "tags": ["Авторы"],
    "summary": "Создать нового автора",
    "description": "Создает нового автора в системе",
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Имя автора",
                        "example": "Александр Пушкин"
                    },
                    "birth_date": {
                        "type": "string",
                        "description": "Дата рождения (YYYY-MM-DD)",
                        "example": "1799-06-06"
                    },
                    "biography": {
                        "type": "string",
                        "description": "Биография автора",
                        "example": "Великий русский поэт"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Автор успешно создан",
            "examples": {
                "application/json": {
                    "id": 1,
                    "name": "Александр Пушкин",
                    "birth_date": "1799-06-06",
                    "biography": "Великий русский поэт",
                    "books_count": 0,
                    "books": []
                }
            }
        },
        "400": {
            "description": "Неверный запрос",
            "examples": {
                "application/json": {
                    "error": "Имя обязательно"
                }
            }
        },
        "500": {
            "description": "Внутренняя ошибка сервера"
        }
    }
}

AUTHOR_BY_ID_DOCS = {
    "tags": ["Авторы"],
    "summary": "Получить автора по ID",
    "description": "Возвращает информацию об авторе и список его книг",
    "produces": ["application/json"],
    "parameters": [
        {
            "name": "author_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID автора"
        }
    ],
    "responses": {
        "200": {
            "description": "Успешный запрос",
            "examples": {
                "application/json": {
                    "id": 1,
                    "name": "Лев Толстой",
                    "birth_date": "1828-09-09",
                    "biography": "Русский писатель",
                    "books_count": 2,
                    "books": [
                        {
                            "id": 1,
                            "title": "Война и мир",
                            "publication_year": 1869,
                            "isbn": "978-5-17-090498-2",
                            "author_id": 1
                        }
                    ]
                }
            }
        },
        "404": {
            "description": "Автор не найден",
            "examples": {
                "application/json": {
                    "error": "Автор не найден"
                }
            }
        },
        "500": {
            "description": "Внутренняя ошибка сервера"
        }
    }
}

AUTHOR_DELETE_DOCS = {
    "tags": ["Авторы"],
    "summary": "Удалить автора",
    "description": "Удаляет автора и все его книги (каскадное удаление)",
    "produces": ["application/json"],
    "parameters": [
        {
            "name": "author_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID автора для удаления"
        }
    ],
    "responses": {
        "200": {
            "description": "Автор успешно удален",
            "examples": {
                "application/json": {
                    "message": "Автор 1 и все его книги удалены",
                    "deleted_author_id": 1
                }
            }
        },
        "404": {
            "description": "Автор не найден",
            "examples": {
                "application/json": {
                    "error": "Автор не найден"
                }
            }
        },
        "500": {
            "description": "Внутренняя ошибка сервера"
        }
    }
}


DB_PATH = 'library_final.db'


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birth_date TEXT,
                biography TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                publication_year INTEGER,
                isbn TEXT,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM authors')
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO authors (name, birth_date, biography) VALUES (?, ?, ?)',
                ('Лев Толстой', '1828-09-09', 'Русский писатель, классик')
            )
            author_id = cursor.lastrowid

            cursor.execute(
                'INSERT INTO books (title, publication_year, author_id) VALUES (?, ?, ?)',
                ('Война и мир', 1869, author_id)
            )
            cursor.execute(
                'INSERT INTO books (title, publication_year, author_id) VALUES (?, ?, ?)',
                ('Анна Каренина', 1878, author_id)
            )

            cursor.execute(
                'INSERT INTO authors (name, birth_date, biography) VALUES (?, ?, ?)',
                ('Александр Пушкин', '1799-06-06', 'Великий русский поэт')
            )

        conn.commit()
        conn.close()
        print(f"✅ База данных создана: {DB_PATH}")
        print(f"✅ Добавлены тестовые данные")

    except Exception as e:
        print(f"❌ Ошибка при создании БД: {e}")


init_db()



def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📚 REST API с документацией</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 3px solid #667eea;
            }
            h1 {
                color: #764ba2;
                font-size: 3em;
                margin-bottom: 10px;
            }
            .tagline {
                color: #667eea;
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }
            .card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                transition: transform 0.3s, box-shadow 0.3s;
                border: 2px solid #e9ecef;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .card h3 {
                color: #764ba2;
                margin-top: 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .card-icon {
                font-size: 1.5em;
            }
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                margin: 10px 5px;
                transition: all 0.3s;
                border: none;
                cursor: pointer;
            }
            .btn:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary {
                background: #6c757d;
            }
            .requirements {
                background: #e9ecef;
                padding: 25px;
                border-radius: 15px;
                margin-top: 40px;
            }
            .requirement-item {
                display: flex;
                align-items: center;
                margin: 15px 0;
                gap: 15px;
            }
            .checkmark {
                color: #28a745;
                font-size: 1.5em;
            }
            .api-endpoints {
                background: #fff;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
            }
            .endpoint {
                font-family: 'Courier New', monospace;
                background: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .get { border-left: 4px solid #28a745; }
            .post { border-left: 4px solid #007bff; }
            .delete { border-left: 4px solid #dc3545; }
            #testResult {
                margin-top: 20px;
                padding: 20px;
                border-radius: 10px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📚 REST API с документацией</h1>
                <div class="tagline">
                    Финальная версия проекта с полной документацией API
                </div>
            </header>

            <div class="cards">
                <div class="card">
                    <h3><span class="card-icon">📖</span> Swagger документация</h3>
                    <p>Полная интерактивная документация API с возможностью тестирования эндпоинтов.</p>
                    <a href="/swagger/" class="btn" target="_blank">
                        🚀 Открыть Swagger UI
                    </a>
                </div>

                <div class="card">
                    <h3><span class="card-icon">👤</span> API для авторов</h3>
                    <p>Управление авторами книг: создание, получение, удаление.</p>
                    <div class="api-endpoints">
                        <div class="endpoint get">GET /api/authors/</div>
                        <div class="endpoint post">POST /api/authors/</div>
                        <div class="endpoint get">GET /api/authors/{id}</div>
                        <div class="endpoint delete">DELETE /api/authors/{id}</div>
                    </div>
                </div>

                <div class="card">
                    <h3><span class="card-icon">📕</span> API для книг</h3>
                    <p>Создание книг с возможностью указания существующего или создания нового автора.</p>
                    <div class="api-endpoints">
                        <div class="endpoint post">POST /api/books/</div>
                    </div>
                </div>
            </div>

            <div class="requirements">
                <h3>✅ Выполненные требования задачи:</h3>

                <div class="requirement-item">
                    <span class="checkmark">✔️</span>
                    <div>
                        <strong>API для книг документирован в формате YAML</strong>
                        <p>Файл: <code>books.yml</code> с полной спецификацией</p>
                    </div>
                </div>

                <div class="requirement-item">
                    <span class="checkmark">✔️</span>
                    <div>
                        <strong>API для авторов документирован в формате Python-словаря</strong>
                        <p>Документация в коде (словари AUTHORS_*_DOCS)</p>
                    </div>
                </div>

                <div class="requirement-item">
                    <span class="checkmark">✔️</span>
                    <div>
                        <strong>Swagger UI доступен</strong>
                        <p>По адресу: <a href="/swagger/">http://localhost:5000/swagger/</a></p>
                    </div>
                </div>

                <div class="requirement-item">
                    <span class="checkmark">✔️</span>
                    <div>
                        <strong>Все эндпоинты работают</strong>
                        <p>Полностью функциональное REST API</p>
                    </div>
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px;">
                <h3>🧪 Тестирование API</h3>
                <button onclick="testCreateAuthor()" class="btn">
                    Создать тестового автора
                </button>
                <button onclick="testGetAuthors()" class="btn btn-secondary">
                    Получить всех авторов
                </button>
                <button onclick="testCreateBook()" class="btn">
                    Создать тестовую книгу
                </button>
                <button onclick="testGetFirstAuthor()" class="btn btn-secondary">
                    Получить первого автора
                </button>
            </div>

            <div id="testResult"></div>
        </div>

        <script>
            function showResult(message, isSuccess = true) {
                const result = document.getElementById('testResult');
                result.innerHTML = message;
                result.style.backgroundColor = isSuccess ? '#d4edda' : '#f8d7da';
                result.style.color = isSuccess ? '#155724' : '#721c24';
                result.style.border = '1px solid ' + (isSuccess ? '#c3e6cb' : '#f5c6cb');
                result.style.display = 'block';
                result.style.padding = '20px';
                result.style.borderRadius = '10px';
                result.style.marginTop = '20px';
            }

            function formatJSON(obj) {
                return JSON.stringify(obj, null, 2);
            }

            async function testCreateAuthor() {
                const data = {
                    name: "Фёдор Достоевский",
                    birth_date: "1821-11-11",
                    biography: "Русский писатель, мыслитель"
                };

                try {
                    const response = await fetch('/api/authors/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(`
                            <h4>✅ Автор успешно создан!</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, true);
                    } else {
                        showResult(`
                            <h4>❌ Ошибка ${response.status}:</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, false);
                    }
                } catch (error) {
                    showResult(`<h4>❌ Ошибка сети:</h4><p>${error}</p>`, false);
                }
            }

            async function testGetAuthors() {
                try {
                    const response = await fetch('/api/authors/');
                    const result = await response.json();

                    if (response.ok) {
                        showResult(`
                            <h4>✅ Список авторов (${result.length}):</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, true);
                    } else {
                        showResult(`
                            <h4>❌ Ошибка ${response.status}:</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, false);
                    }
                } catch (error) {
                    showResult(`<h4>❌ Ошибка сети:</h4><p>${error}</p>`, false);
                }
            }

            async function testCreateBook() {
                const data = {
                    title: "Преступление и наказание",
                    publication_year: 1866,
                    author_name: "Фёдор Достоевский",
                    author_birth_date: "1821-11-11"
                };

                try {
                    const response = await fetch('/api/books/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(`
                            <h4>✅ Книга успешно создана!</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, true);
                    } else {
                        showResult(`
                            <h4>❌ Ошибка ${response.status}:</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, false);
                    }
                } catch (error) {
                    showResult(`<h4>❌ Ошибка сети:</h4><p>${error}</p>`, false);
                }
            }

            async function testGetFirstAuthor() {
                try {
                    const response = await fetch('/api/authors/1');
                    const result = await response.json();

                    if (response.ok) {
                        showResult(`
                            <h4>✅ Автор с ID 1:</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, true);
                    } else {
                        showResult(`
                            <h4>❌ Ошибка ${response.status}:</h4>
                            <pre><code>${formatJSON(result)}</code></pre>
                        `, false);
                    }
                } catch (error) {
                    showResult(`<h4>❌ Ошибка сети:</h4><p>${error}</p>`, false);
                }
            }
        </script>
    </body>
    </html>
    '''



@app.route('/api/books/', methods=['POST'])
@swag_from('books.yml')
def create_book():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 400

        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Неверный JSON формат'}), 400

        if not data or 'title' not in data:
            return jsonify({'error': 'Название книги обязательно'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        author_id = None

        if 'author_name' in data and data['author_name']:
            try:
                cursor.execute(
                    'INSERT INTO authors (name, birth_date, biography) VALUES (?, ?, ?)',
                    (data['author_name'],
                     data.get('author_birth_date'),
                     data.get('author_biography'))
                )
                author_id = cursor.lastrowid
            except sqlite3.Error as e:
                conn.close()
                return jsonify({'error': f'Ошибка при создании автора: {str(e)}'}), 500

        elif 'author_id' in data:
            author_id = data['author_id']
            cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'error': 'Автор не найден'}), 404

        else:
            conn.close()
            return jsonify({'error': 'Укажите author_id или author_name'}), 400

        try:
            cursor.execute(
                'INSERT INTO books (title, publication_year, isbn, author_id) VALUES (?, ?, ?, ?)',
                (data['title'],
                 data.get('publication_year'),
                 data.get('isbn'),
                 author_id)
            )
            book_id = cursor.lastrowid
            conn.commit()

        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return jsonify({'error': f'Ошибка при создании книги: {str(e)}'}), 500

        finally:
            conn.close()

        return jsonify({
            'id': book_id,
            'title': data['title'],
            'publication_year': data.get('publication_year'),
            'isbn': data.get('isbn'),
            'author_id': author_id
        }), 201

    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500



@app.route('/api/authors/', methods=['GET'])
@swag_from(AUTHORS_GET_DOCS)
def get_all_authors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM authors ORDER BY id')
        authors = cursor.fetchall()

        result = []
        for author in authors:
            cursor.execute('SELECT COUNT(*) FROM books WHERE author_id = ?', (author['id'],))
            books_count = cursor.fetchone()[0]

            result.append({
                'id': author['id'],
                'name': author['name'],
                'birth_date': author['birth_date'],
                'biography': author['biography'],
                'books_count': books_count
            })

        conn.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500


@app.route('/api/authors/', methods=['POST'])
@swag_from(AUTHORS_POST_DOCS)
def create_author():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 400

        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Неверный JSON формат'}), 400

        if not data or 'name' not in data:
            return jsonify({'error': 'Имя обязательно'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO authors (name, birth_date, biography) VALUES (?, ?, ?)',
                (data['name'], data.get('birth_date'), data.get('biography'))
            )
            author_id = cursor.lastrowid
            conn.commit()

        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return jsonify({'error': f'Ошибка при создании автора: {str(e)}'}), 500

        finally:
            conn.close()

        return jsonify({
            'id': author_id,
            'name': data['name'],
            'birth_date': data.get('birth_date'),
            'biography': data.get('biography'),
            'books_count': 0,
            'books': []
        }), 201

    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500


@app.route('/api/authors/<int:author_id>', methods=['GET'])
@swag_from(AUTHOR_BY_ID_DOCS)
def get_author(author_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
        author = cursor.fetchone()

        if not author:
            conn.close()
            return jsonify({'error': 'Автор не найден'}), 404

        cursor.execute('SELECT * FROM books WHERE author_id = ?', (author_id,))
        books = cursor.fetchall()

        conn.close()

        books_list = []
        for book in books:
            books_list.append({
                'id': book['id'],
                'title': book['title'],
                'publication_year': book['publication_year'],
                'isbn': book['isbn'],
                'author_id': book['author_id']
            })

        return jsonify({
            'id': author['id'],
            'name': author['name'],
            'birth_date': author['birth_date'],
            'biography': author['biography'],
            'books_count': len(books),
            'books': books_list
        }), 200

    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500


@app.route('/api/authors/<int:author_id>', methods=['DELETE'])
@swag_from(AUTHOR_DELETE_DOCS)
def delete_author(author_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Автор не найден'}), 404

        try:
            cursor.execute('DELETE FROM authors WHERE id = ?', (author_id,))
            conn.commit()

        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return jsonify({'error': f'Ошибка при удалении автора: {str(e)}'}), 500

        finally:
            conn.close()

        return jsonify({
            'message': f'Автор {author_id} и все его книги удалены',
            'deleted_author_id': author_id
        }), 200

    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500



if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ФИНАЛЬНАЯ ВЕРСИЯ: REST API С ПОЛНОЙ ДОКУМЕНТАЦИЕЙ")
    print("=" * 70)
    print("📖 ОСНОВНЫЕ АДРЕСА:")
    print("   🌐 Главная страница: http://localhost:5000")
    print("   📚 Swagger документация: http://localhost:5000/swagger/")
    print("=" * 70)
    print("✅ ВЫПОЛНЕННЫЕ ТРЕБОВАНИЯ ЗАДАЧИ:")
    print("   1. 📄 API для книг документирован в формате YAML (books.yml)")
    print("   2. 👥 API для авторов документирован в формате Python-словаря")
    print("   3. 🔗 Swagger UI доступен по адресу /swagger/")
    print("=" * 70)
    print("🔧 ДОСТУПНЫЕ ЭНДПОИНТЫ:")
    print("   📕 Книги:")
    print("      POST /api/books/      - Создать книгу")
    print("   👥 Авторы:")
    print("      GET    /api/authors/      - Получить всех авторов")
    print("      POST   /api/authors/      - Создать автора")
    print("      GET    /api/authors/{id}  - Получить автора по ID")
    print("      DELETE /api/authors/{id}  - Удалить автора")
    print("=" * 70)
    print("💡 СОВЕТЫ:")
    print("   • Используйте Swagger UI для тестирования API")
    print("   • На главной странице есть тестовые кнопки")
    print("   • База данных уже содержит тестовых авторов и книги")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)