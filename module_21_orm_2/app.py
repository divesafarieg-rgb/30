from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker, joinedload
import csv
from io import StringIO

from models import Base, Book, Student, ReceivingBook, Author, get_db_engine

app = Flask(__name__)

engine = get_db_engine()
Base.metadata.create_all(engine)


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


@app.route('/books', methods=['GET'])
def get_all_books():
    session = get_db_session()
    try:
        books = session.query(Book).options(joinedload(Book.author)).all()
        result = []
        for book in books:
            result.append({
                'id': book.id,
                'name': book.name,
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
                'author_id': book.author_id,
                'author_name': f"{book.author.name} {book.author.surname}" if book.author else None
            })
        return jsonify(result)
    finally:
        session.close()


@app.route('/debtors', methods=['GET'])
def get_debtors_route():
    session = get_db_session()
    try:
        fourteen_days_ago = datetime.now() - timedelta(days=14)

        debtors_records = session.query(ReceivingBook).options(
            joinedload(ReceivingBook.student),
            joinedload(ReceivingBook.book)
        ).filter(
            ReceivingBook.date_of_return == None,
            ReceivingBook.date_of_issue < fourteen_days_ago
        ).all()

        debtors = []
        for record in debtors_records:
            debtors.append({
                'student_id': record.student.id,
                'student_name': f"{record.student.name} {record.student.surname}",
                'student_email': record.student.email,
                'student_phone': record.student.phone,
                'book_id': record.book.id,
                'book_name': record.book.name,
                'date_of_issue': record.date_of_issue.isoformat(),
                'days_with_book': record.count_date_with_book
            })

        return jsonify(debtors)
    finally:
        session.close()


@app.route('/issue-book', methods=['POST'])
def issue_book():
    data = request.json
    book_id = data.get('book_id')
    student_id = data.get('student_id')

    if not book_id or not student_id:
        return jsonify({'error': 'Необходимо указать book_id и student_id'}), 400

    session = get_db_session()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        student = session.query(Student).filter(Student.id == student_id).first()

        if not book:
            return jsonify({'error': 'Книга не найдена'}), 404
        if not student:
            return jsonify({'error': 'Студент не найден'}), 404

        if book.count <= 0:
            return jsonify({'error': 'Этой книги нет в наличии'}), 400

        existing_issue = session.query(ReceivingBook).filter(
            ReceivingBook.book_id == book_id,
            ReceivingBook.student_id == student_id,
            ReceivingBook.date_of_return == None
        ).first()

        if existing_issue:
            return jsonify({'error': 'Эта книга уже выдана данному студенту'}), 400

        new_issue = ReceivingBook(
            book_id=book_id,
            student_id=student_id,
            date_of_issue=datetime.now()
        )

        session.add(new_issue)
        book.count -= 1
        session.commit()

        return jsonify({
            'message': 'Книга успешно выдана',
            'issue_id': new_issue.id,
            'date_of_issue': new_issue.date_of_issue.isoformat(),
            'book_name': book.name,
            'student_name': f"{student.name} {student.surname}"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/return-book', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    student_id = data.get('student_id')

    if not book_id or not student_id:
        return jsonify({'error': 'Необходимо указать book_id и student_id'}), 400

    session = get_db_session()
    try:
        issue_record = session.query(ReceivingBook).filter(
            ReceivingBook.book_id == book_id,
            ReceivingBook.student_id == student_id,
            ReceivingBook.date_of_return == None
        ).first()

        if not issue_record:
            return jsonify({'error': 'Не найдена активная запись о выдаче этой книги данному студенту'}), 404

        issue_record.date_of_return = datetime.now()

        book = session.query(Book).filter(Book.id == book_id).first()
        if book:
            book.count += 1

        session.commit()

        return jsonify({
            'message': 'Книга успешно возвращена',
            'days_with_book': issue_record.count_date_with_book,
            'book_name': book.name if book else 'Неизвестно',
            'student_name': f"{issue_record.student.name} {issue_record.student.surname}"
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/search-books', methods=['GET'])
def search_books():
    search_string = request.args.get('q', '')

    if not search_string:
        return jsonify({'error': 'Необходимо указать поисковый запрос (параметр q)'}), 400

    session = get_db_session()
    try:
        books = session.query(Book).options(joinedload(Book.author)).filter(
            Book.name.ilike(f"%{search_string}%")
        ).all()

        result = []
        for book in books:
            result.append({
                'id': book.id,
                'name': book.name,
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
                'author_id': book.author_id,
                'author_name': f"{book.author.name} {book.author.surname}" if book.author else None
            })

        return jsonify(result)
    finally:
        session.close()


@app.route('/students/scholarship', methods=['GET'])
def get_scholarship_students():
    session = get_db_session()
    try:
        students = Student.get_scholarship_students(session)
        result = []
        for student in students:
            result.append({
                'id': student.id,
                'name': student.name,
                'surname': student.surname,
                'email': student.email,
                'phone': student.phone,
                'average_score': student.average_score,
                'scholarship': student.scholarship
            })
        return jsonify(result)
    finally:
        session.close()


@app.route('/students/score/<float:min_score>', methods=['GET'])
def get_students_by_score(min_score):
    session = get_db_session()
    try:
        students = Student.get_students_by_score(session, min_score)
        result = []
        for student in students:
            result.append({
                'id': student.id,
                'name': student.name,
                'surname': student.surname,
                'email': student.email,
                'phone': student.phone,
                'average_score': student.average_score,
                'scholarship': student.scholarship
            })
        return jsonify(result)
    finally:
        session.close()



@app.route('/books/remaining/<int:author_id>', methods=['GET'])
def get_remaining_books_by_author(author_id):
    session = get_db_session()
    try:
        total_count = session.query(func.sum(Book.count)).filter(
            Book.author_id == author_id
        ).scalar()

        return jsonify({
            'author_id': author_id,
            'remaining_books': total_count if total_count else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/students/<int:student_id>/recommended-books', methods=['GET'])
def get_recommended_books(student_id):
    session = get_db_session()
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({'error': 'Студент не найден'}), 404

        authors_read = select(Book.author_id).join(
            ReceivingBook, Book.id == ReceivingBook.book_id
        ).where(
            ReceivingBook.student_id == student_id
        ).distinct()

        books_read = select(ReceivingBook.book_id).where(
            ReceivingBook.student_id == student_id
        ).distinct()

        recommended_books = session.query(Book).join(
            Author, Book.author_id == Author.id
        ).filter(
            Book.author_id.in_(authors_read),
            Book.id.notin_(books_read),
            Book.count > 0
        ).all()

        result = []
        for book in recommended_books:
            result.append({
                'id': book.id,
                'name': book.name,
                'author': f"{book.author.name} {book.author.surname}",
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/stats/avg-books-this-month', methods=['GET'])
def get_avg_books_this_month():
    session = get_db_session()
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year

        books_per_student = session.query(
            ReceivingBook.student_id,
            func.count(ReceivingBook.id).label('book_count')
        ).filter(
            func.strftime('%Y', ReceivingBook.date_of_issue) == str(current_year),
            func.strftime('%m', ReceivingBook.date_of_issue) == f"{current_month:02d}"
        ).group_by(ReceivingBook.student_id).subquery()

        avg_books = session.query(
            func.avg(books_per_student.c.book_count)
        ).scalar()

        return jsonify({
            'month': current_month,
            'year': current_year,
            'average_books_per_student': round(float(avg_books or 0), 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/stats/popular-book-high-score', methods=['GET'])
def get_popular_book_high_score():
    session = get_db_session()
    try:
        high_score_students = select(Student.id).where(
            Student.average_score > 4.0
        ).subquery()

        popular_book = session.query(
            Book.id,
            Book.name,
            func.count(ReceivingBook.id).label('borrow_count')
        ).join(ReceivingBook).join(Author).filter(
            ReceivingBook.student_id.in_(select(high_score_students.c.id))
        ).group_by(Book.id).order_by(
            func.count(ReceivingBook.id).desc()
        ).first()

        if popular_book:
            return jsonify({
                'book_id': popular_book.id,
                'book_name': popular_book.name,
                'borrow_count': popular_book.borrow_count
            })
        else:
            return jsonify({'message': 'Нет данных'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/stats/top-readers-this-year', methods=['GET'])
def get_top_readers_this_year():
    session = get_db_session()
    try:
        current_year = datetime.now().year

        top_readers = session.query(
            Student.id,
            Student.name,
            Student.surname,
            func.count(ReceivingBook.id).label('books_read')
        ).join(ReceivingBook, Student.id == ReceivingBook.student_id).filter(
            func.strftime('%Y', ReceivingBook.date_of_issue) == str(current_year)
        ).group_by(Student.id).order_by(
            func.count(ReceivingBook.id).desc()
        ).limit(10).all()

        result = []
        for reader in top_readers:
            result.append({
                'student_id': reader.id,
                'name': f"{reader.name} {reader.surname}",
                'books_read': reader.books_read
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/students/upload-csv', methods=['POST'])
def upload_students_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Файл должен быть в формает CSV'}), 400

    session = get_db_session()
    try:
        csv_data = StringIO(file.read().decode('utf-8'))
        csv_reader = csv.DictReader(csv_data, delimiter=';')

        students_data = []
        for row in csv_reader:
            students_data.append({
                'name': row.get('name'),
                'surname': row.get('surname'),
                'phone': row.get('phone'),
                'email': row.get('email'),
                'average_score': float(row.get('average_score', 0)),
                'scholarship': row.get('scholarship', '').lower() == 'true'
            })

        session.bulk_insert_mappings(Student, students_data)
        session.commit()

        return jsonify({
            'message': f'Успешно добавлено {len(students_data)} студентов',
            'count': len(students_data)
        }), 201

    except ValueError as e:
        session.rollback()
        return jsonify({'error': f'Ошибка валидации: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/test-associations', methods=['GET'])
def test_associations():
    session = get_db_session()
    try:
        result = {}

        books_with_authors = session.query(Book).options(
            joinedload(Book.author)
        ).limit(3).all()

        result['joinedload_example'] = [
            {
                'book': book.name,
                'author': f"{book.author.name} {book.author.surname}"
            }
            for book in books_with_authors
        ]

        student = session.query(Student).filter(Student.id == 1).first()
        if student:
            result['association_proxy_student_books'] = [
                book.name for book in student.books[:3]
            ]

            result['student_info'] = {
                'name': f"{student.name} {student.surname}",
                'total_books_borrowed': len(student.books)
            }

        result['cascade_info'] = "При удалении автора удаляются все его книги каскадно"

        return jsonify(result)
    finally:
        session.close()


if __name__ == '__main__':
    print("Запуск Flask приложения...")
    print("\nДоступные роуты:")
    print("  GET  /books - получить все книги")
    print("  GET  /debtors - получить список должников")
    print("  POST /issue-book - выдать книгу студенту")
    print("  POST /return-book - сдать книгу")
    print("  GET  /search-books?q=<строка> - поиск книг по названию")
    print("  GET  /students/scholarship - студенты со стипендией")
    print("  GET  /students/score/<балл> - студенты с баллом выше указанного")
    print("\nНовые роуты:")
    print("  GET  /books/remaining/<author_id> - количество оставшихся книг по автору")
    print("  GET  /students/<student_id>/recommended-books - рекомендованные книги")
    print("  GET  /stats/avg-books-this-month - среднее количество книг в этом месяце")
    print("  GET  /stats/popular-book-high-score - популярная книга у хороших студентов")
    print("  GET  /stats/top-readers-this-year - ТОП-10 читающих студентов")
    print("  POST /students/upload-csv - загрузка студентов из CSV")
    print("  GET  /test-associations - тест связей и association proxy")

    app.run(debug=True, port=5000)