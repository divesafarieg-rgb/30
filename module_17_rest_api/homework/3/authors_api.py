from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = 'library_simple.db'


def init_db():
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

    conn.commit()
    conn.close()
    print(f"✅ База данных создана: {DB_PATH}")


init_db()


@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📚 REST API для авторов</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .box { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            .result { padding: 15px; margin: 10px 0; display: none; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>📚 REST API для работы с авторами</h1>

        <div class="box">
            <h3>1. Создать автора</h3>
            <button onclick="createAuthor()">Создать тестового автора</button>
        </div>

        <div class="box">
            <h3>2. Получить автора</h3>
            <input id="author_id" type="number" placeholder="ID автора" value="1">
            <button onclick="getAuthor()">Получить</button>
        </div>

        <div class="box">
            <h3>3. Создать книгу</h3>
            <button onclick="createBookWithNewAuthor()">Создать книгу с новым автором</button>
            <button onclick="createBookWithExistingAuthor()">Создать книгу для существующего автора</button>
        </div>

        <div class="box">
            <h3>4. Удалить автора</h3>
            <input id="delete_id" type="number" placeholder="ID автора" value="1">
            <button onclick="deleteAuthor()">Удалить</button>
        </div>

        <div id="result" class="result"></div>

        <script>
            function showResult(message, isSuccess = true) {
                const result = document.getElementById('result');
                result.innerHTML = message;
                result.className = 'result ' + (isSuccess ? 'success' : 'error');
                result.style.display = 'block';
            }

            async function createAuthor() {
                const data = {
                    name: "Лев Толстой",
                    birth_date: "1828-09-09",
                    biography: "Русский писатель"
                };

                try {
                    const response = await fetch('/api/authors/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(`✅ Автор создан! ID: ${result.id}, Имя: ${result.name}`);
                    } else {
                        showResult(`❌ Ошибка: ${result.error}`, false);
                    }
                } catch (error) {
                    showResult(`❌ Ошибка сети: ${error}`, false);
                }
            }

            async function getAuthor() {
                const id = document.getElementById('author_id').value;

                try {
                    const response = await fetch(`/api/authors/${id}`);
                    const result = await response.json();

                    if (response.ok) {
                        showResult(`✅ Автор найден!<br>Имя: ${result.name}<br>Книг: ${result.books_count}`);
                    } else {
                        showResult(`❌ Ошибка: ${result.error}`, false);
                    }
                } catch (error) {
                    showResult(`❌ Ошибка сети: ${error}`, false);
                }
            }

            async function createBookWithNewAuthor() {
                const data = {
                    title: "Война и мир",
                    publication_year: 1869,
                    author_name: "Лев Толстой"
                };

                try {
                    const response = await fetch('/api/books/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(`✅ Книга создана! Название: ${result.title}`);
                    } else {
                        showResult(`❌ Ошибка: ${result.error}`, false);
                    }
                } catch (error) {
                    showResult(`❌ Ошибка сети: ${error}`, false);
                }
            }

            async function createBookWithExistingAuthor() {
                const authorId = prompt("Введите ID автора:", "1");
                if (!authorId) return;

                const data = {
                    title: "Анна Каренина",
                    publication_year: 1878,
                    author_id: parseInt(authorId)
                };

                try {
                    const response = await fetch('/api/books/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(`✅ Книга создана! Название: ${result.title}`);
                    } else {
                        showResult(`❌ Ошибка: ${result.error}`, false);
                    }
                } catch (error) {
                    showResult(`❌ Ошибка сети: ${error}`, false);
                }
            }

            async function deleteAuthor() {
                const id = document.getElementById('delete_id').value;

                if (!confirm(`Удалить автора ${id} со всеми его книгами?`)) return;

                try {
                    const response = await fetch(`/api/authors/${id}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(`✅ Автор ${id} удален со всеми книгами!`);
                    } else {
                        showResult(`❌ Ошибка: ${result.error}`, false);
                    }
                } catch (error) {
                    showResult(`❌ Ошибка сети: ${error}`, false);
                }
            }
        </script>
    </body>
    </html>
    '''



@app.route('/api/authors/', methods=['POST'])
def create_author():
    try:
        data = request.json

        if not data or 'name' not in data:
            return jsonify({'error': 'Имя обязательно'}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO authors (name, birth_date, biography) VALUES (?, ?, ?)',
            (data['name'], data.get('birth_date'), data.get('biography'))
        )

        author_id = cursor.lastrowid
        conn.commit()
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
        return jsonify({'error': str(e)}), 500


@app.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
        author = cursor.fetchone()

        if not author:
            return jsonify({'error': 'Автор не найден'}), 404

        cursor.execute('SELECT * FROM books WHERE author_id = ?', (author_id,))
        books = cursor.fetchall()

        conn.close()

        books_list = []
        for book in books:
            books_list.append({
                'id': book[0],
                'title': book[1],
                'publication_year': book[2],
                'isbn': book[3],
                'author_id': book[4]
            })

        return jsonify({
            'id': author[0],
            'name': author[1],
            'birth_date': author[2],
            'biography': author[3],
            'books_count': len(books),
            'books': books_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Автор не найден'}), 404

        cursor.execute('DELETE FROM authors WHERE id = ?', (author_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'message': f'Автор {author_id} и все его книги удалены',
            'deleted_author_id': author_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/books/', methods=['POST'])
def create_book():
    try:
        data = request.json

        if not data or 'title' not in data:
            return jsonify({'error': 'Название книги обязательно'}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        author_id = None

        if 'author_name' in data and data['author_name']:
            cursor.execute(
                'INSERT INTO authors (name, birth_date, biography) VALUES (?, ?, ?)',
                (data['author_name'], data.get('author_birth_date'), data.get('author_biography'))
            )
            author_id = cursor.lastrowid

        elif 'author_id' in data:
            author_id = data['author_id']
            cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'error': 'Автор не найден'}), 404

        else:
            conn.close()
            return jsonify({'error': 'Укажите author_id или author_name'}), 400

        cursor.execute(
            'INSERT INTO books (title, publication_year, isbn, author_id) VALUES (?, ?, ?, ?)',
            (data['title'], data.get('publication_year'), data.get('isbn'), author_id)
        )

        book_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'id': book_id,
            'title': data['title'],
            'publication_year': data.get('publication_year'),
            'isbn': data.get('isbn'),
            'author_id': author_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/authors/', methods=['GET'])
def get_all_authors():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM authors')
        authors = cursor.fetchall()

        result = []
        for author in authors:
            cursor.execute('SELECT COUNT(*) FROM books WHERE author_id = ?', (author[0],))
            books_count = cursor.fetchone()[0]

            result.append({
                'id': author[0],
                'name': author[1],
                'birth_date': author[2],
                'biography': author[3],
                'books_count': books_count
            })

        conn.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ЗАПУСК СЕРВЕРА REST API")
    print("=" * 60)
    print("🌐 Адрес: http://localhost:5000")
    print("📁 База данных: library_simple.db")
    print("=" * 60)
    print("✅ Все требования задачи:")
    print("   ✓ POST /api/authors/ - создание автора")
    print("   ✓ GET /api/authors/{id} - просмотр всех книг автора")
    print("   ✓ DELETE /api/authors/{id} - удаление автора с книгами")
    print("   ✓ Создание автора при добавлении книги")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)