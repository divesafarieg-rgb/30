from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)


_initialized = False


@app.before_request
def initialize_database():
    global _initialized
    if not _initialized:
        with app.app_context():
            db.create_all()
            if Book.query.count() == 0:
                books = [
                    Book(title="Война и мир", author="Лев Толстой"),
                    Book(title="Преступление и наказание", author="Фёдор Достоевский"),
                    Book(title="Мастер и Маргарита", author="Михаил Булгаков")
                ]
                db.session.add_all(books)
                db.session.commit()
        _initialized = True


@app.route('/books')
def show_books():
    books = Book.query.all()
    result = "<h1>Список книг</h1><ul>"

    for book in books:
        book.views += 1
        result += f'<li><a href="/books/{book.id}">{book.title}</a> - {book.author} (Просмотры: {book.views})</li>'

    db.session.commit()
    result += "</ul>"
    return result


@app.route('/books/<int:book_id>')
def show_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return "Книга не найдена"

    book.views += 1
    db.session.commit()

    return f'''
    <h1>{book.title}</h1>
    <p>Автор: {book.author}</p>
    <p>Просмотры: {book.views}</p>
    <a href="/books">Вернуться к списку</a>
    '''


if __name__ == '__main__':
    app.run(debug=True)