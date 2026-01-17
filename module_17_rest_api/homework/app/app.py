from flask import Flask, request, jsonify, render_template_string
from models import (
    init_db,
    get_all_books,
    get_all_authors,
    get_author_by_id,
    add_book,
    add_author,
    delete_author,
    Author
)

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Библиотека - Нормализация БД</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .container { display: flex; gap: 30px; margin-top: 20px; }
        .column { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        ul { list-style: none; padding: 0; }
        li { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 4px; }
        .success { color: green; }
        .demo { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>📚 Библиотека - Нормализация Базы Данных</h1>

    <div class="demo">
        <h3>✅ Нормализация базы данных выполнена</h3>
        <ul>
            <li>✅ Авторы вынесены в отдельную таблицу</li>
            <li>✅ Книги ссылаются на авторов через внешний ключ</li>
            <li>✅ Реализовано каскадное удаление</li>
        </ul>
    </div>

    <div class="container">
        <div class="column">
            <h2>📖 Книги</h2>
            <ul>
                {% for book in books %}
                <li><strong>"{{ book.title }}"</strong><br>Автор: {{ book.author }}</li>
                {% endfor %}
            </ul>
            <p><a href="/api/books">API: GET /api/books</a></p>
        </div>

        <div class="column">
            <h2>👥 Авторы</h2>
            <ul>
                {% for author in authors %}
                <li><strong>{{ author.full_name() }}</strong><br>ID: {{ author.id }}</li>
                {% endfor %}
            </ul>
            <p><a href="/api/authors">API: GET /api/authors</a></p>
        </div>
    </div>

    <div class="demo">
        <h3>API Эндпоинты:</h3>
        <p><strong>GET</strong> <a href="/api/books">/api/books</a> - все книги</p>
        <p><strong>POST</strong> /api/books - добавить книгу (JSON: {"title": "...", "author_id": ...})</p>
        <p><strong>GET</strong> <a href="/api/authors">/api/authors</a> - все авторы</p>
        <p><strong>POST</strong> /api/authors - добавить автора (JSON: {"first_name": "...", "last_name": "..."})</p>
        <p><strong>DELETE</strong> /api/authors/&lt;id&gt; - удалить автора (каскадное удаление книг)</p>
    </div>
</body>
</html>
'''


@app.route('/')
def index():
    books = get_all_books()
    authors = get_all_authors()
    return render_template_string(HTML_TEMPLATE, books=books, authors=authors)


@app.route('/api/books', methods=['GET'])
def get_books():
    books = get_all_books()
    return jsonify({'books': books})


@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or 'title' not in data or 'author_id' not in data:
        return jsonify({'error': 'Требуются поля: title и author_id'}), 400

    try:
        book_id = add_book(data['title'], int(data['author_id']))
        author = get_author_by_id(int(data['author_id']))
        return jsonify({
            'id': book_id,
            'title': data['title'],
            'author_id': data['author_id'],
            'author': author.full_name() if author else 'Неизвестен'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/authors', methods=['GET'])
def get_authors():
    authors = get_all_authors()
    result = []
    for author in authors:
        result.append({
            'id': author.id,
            'full_name': author.full_name(),
            'first_name': author.first_name,
            'last_name': author.last_name,
            'middle_name': author.middle_name
        })
    return jsonify({'authors': result})


@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.json
    if not data or 'first_name' not in data or 'last_name' not in data:
        return jsonify({'error': 'Требуются поля: first_name и last_name'}), 400

    author_id = add_author(data['first_name'], data['last_name'], data.get('middle_name'))
    author = Author(data['first_name'], data['last_name'], data.get('middle_name'), author_id)

    return jsonify({
        'id': author_id,
        'full_name': author.full_name(),
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'middle_name': data.get('middle_name')
    }), 201


@app.route('/api/authors/<int:author_id>', methods=['DELETE'])
def delete_author_route(author_id):
    author = get_author_by_id(author_id)
    if not author:
        return jsonify({'error': 'Автор не найден'}), 404

    success = delete_author(author_id)
    if success:
        return jsonify({
            'message': f'Автор {author.full_name()} удален',
            'cascade': 'Все книги автора удалены автоматически'
        }), 200
    else:
        return jsonify({'error': 'Не удалось удалить автора'}), 400


if __name__ == '__main__':
    print("=" * 60)
    print("НОРМАЛИЗАЦИЯ БАЗЫ ДАННЫХ - БИБЛИОТЕКА")
    print("=" * 60)

    init_db()

    books = get_all_books()
    authors = get_all_authors()

    print(f"\n📚 Книг: {len(books)}")
    print(f"👥 Авторов: {len(authors)}")

    print("\n🌐 Сервер: http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, port=5000)