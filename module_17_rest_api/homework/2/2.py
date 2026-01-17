from flask import Flask
from flask_restx import Api, Resource, fields, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app, version='1.0', title='Books API', description='A simple Books API')


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'genre': self.genre
        }


book_model = api.model('Book', {
    'title': fields.String(required=True, description='Название книги'),
    'author': fields.String(required=True, description='Автор книги'),
    'year': fields.Integer(description='Год издания'),
    'genre': fields.String(description='Жанр книги')
})


@api.route('/api/books/<int:book_id>')
@api.doc(params={'book_id': 'ID книги'})
class BookResource(Resource):
    @api.doc(description='Получить информацию о книге')
    @api.response(200, 'Успешно', book_model)
    @api.response(404, 'Книга не найдена')
    def get(self, book_id):
        session: Session = db.session
        book = session.get(Book, book_id)
        if not book:
            abort(404, message=f'Книга с ID {book_id} не найдена')
        return book.to_dict(), 200

    @api.doc(description='Изменить книгу (полное обновление)')
    @api.expect(book_model)
    @api.response(200, 'Книга обновлена', book_model)
    @api.response(404, 'Книга не найдена')
    @api.response(400, 'Неверные данные')
    def put(self, book_id):
        session: Session = db.session
        book = session.get(Book, book_id)
        if not book:
            abort(404, message=f'Книга с ID {book_id} не найдена')

        data = api.payload

        if 'author' in data:
            if not isinstance(data['author'], str) or len(data['author'].strip()) == 0:
                abort(400, message='Имя автора обязательно и должно быть строкой')

        if 'title' not in data or 'author' not in data:
            abort(400, message='Для PUT запроса обязательные поля: title и author')

        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.year = data.get('year', book.year)
        book.genre = data.get('genre', book.genre)

        session.commit()
        return book.to_dict(), 200

    @api.doc(description='Частичное изменение книги')
    @api.expect(book_model)
    @api.response(200, 'Книга обновлена', book_model)
    @api.response(404, 'Книга не найдена')
    @api.response(400, 'Неверные данные')
    def patch(self, book_id):
        session: Session = db.session
        book = session.get(Book, book_id)
        if not book:
            abort(404, message=f'Книга с ID {book_id} не найдена')

        data = api.payload

        if 'author' in data:
            if not isinstance(data['author'], str) or len(data['author'].strip()) == 0:
                abort(400, message='Имя автора обязательно и должно быть строкой')
            book.author = data['author']

        if 'title' in data:
            book.title = data['title']
        if 'year' in data:
            book.year = data['year']
        if 'genre' in data:
            book.genre = data['genre']

        session.commit()
        return book.to_dict(), 200

    @api.doc(description='Удалить книгу')
    @api.response(200, 'Книга удалена')
    @api.response(404, 'Книга не найдена')
    def delete(self, book_id):
        session: Session = db.session
        book = session.get(Book, book_id)
        if not book:
            abort(404, message=f'Книга с ID {book_id} не найдена')

        session.delete(book)
        session.commit()
        return {'message': f'Книга с ID {book_id} удалена'}, 200


with app.app_context():
    db.create_all()
    session: Session = db.session
    if session.query(Book).count() == 0:
        books = [
            Book(title='Война и мир', author='Лев Толстой', year=1869, genre='Роман'),
            Book(title='Преступление и наказание', author='Фёдор Достоевский', year=1866, genre='Роман'),
            Book(title='Мастер и Маргарита', author='Михаил Булгаков', year=1967, genre='Фантастика'),
            Book(title='1984', author='Джордж Оруэлл', year=1949, genre='Антиутопия'),
            Book(title='Гарри Поттер и философский камень', author='Джоан Роулинг', year=1997, genre='Фэнтези')
        ]
        session.add_all(books)
        session.commit()
        print("База данных инициализирована с тестовыми данными")

if __name__ == '__main__':
    print("Сервер запущен. Доступные эндпоинты:")
    print("GET    /api/books/{id}     - Получить книгу")
    print("PUT    /api/books/{id}     - Полное обновление книги")
    print("PATCH  /api/books/{id}     - Частичное обновление книги")
    print("DELETE /api/books/{id}     - Удалить книгу")
    print("\nSwagger документация доступна по адресу: http://127.0.0.1:5000/")
    print("Пример тестирования через curl:")
    print("  curl http://127.0.0.1:5000/api/books/1")
    print(
        "  curl -X PUT http://127.0.0.1:5000/api/books/1 -H \"Content-Type: application/json\" -d '{\"title\":\"Новое название\",\"author\":\"Новый автор\",\"year\":2024}'")
    app.run(debug=True)