from flask import Flask, render_template
import os

app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "Мастер и Маргарита", "author": "Михаил Булгаков", "year": 1967, "genre": "Роман"},
    {"id": 2, "title": "Собачье сердце", "author": "Михаил Булгаков", "year": 1925, "genre": "Повесть"},
    {"id": 3, "title": "Преступление и наказание", "author": "Фёдор Достоевский", "year": 1866, "genre": "Роман"},
    {"id": 4, "title": "Идиот", "author": "Фёдор Достоевский", "year": 1869, "genre": "Роман"},
    {"id": 5, "title": "Война и мир", "author": "Лев Толстой", "year": 1869, "genre": "Роман"},
    {"id": 6, "title": "Анна Каренина", "author": "Лев Толстой", "year": 1877, "genre": "Роман"},
]


def get_books_by_author(author_name):
    return [book for book in BOOKS if book["author"].lower() == author_name.lower()]


@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Главная - Библиотека</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            h1 { color: #333; }
            .menu { margin: 20px 0; }
            .menu a { 
                display: inline-block; 
                margin: 5px; 
                padding: 10px 20px; 
                background: #0066cc; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h1>Добро пожаловать в библиотеку!</h1>
        <p>Здесь вы можете найти книги по авторам.</p>

        <div class="menu">
            <a href="/search">🔍 Поиск книг</a>
            <a href="/author/Михаил Булгаков">Михаил Булгаков</a>
            <a href="/author/Фёдор Достоевский">Фёдор Достоевский</a>
            <a href="/author/Лев Толстой">Лев Толстой</a>
        </div>
    </body>
    </html>
    '''


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/author/<author_name>')
def author_books(author_name):
    books = get_books_by_author(author_name)

    return render_template(
        'author_books.html',
        author=author_name,
        books=books,
        count=len(books)
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)