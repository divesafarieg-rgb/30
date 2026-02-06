from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Book, Student, ReceivingBook, get_db_engine

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
        books = session.query(Book).all()
        result = []
        for book in books:
            result.append({
                'id': book.id,
                'name': book.name,
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
                'author_id': book.author_id
            })
        return jsonify(result)
    finally:
        session.close()


@app.route('/debtors', methods=['GET'])
def get_debtors_route():
    session = get_db_session()
    try:
        fourteen_days_ago = datetime.now() - timedelta(days=14)

        debtors_records = session.query(ReceivingBook).filter(
            ReceivingBook.date_of_return == None,
            ReceivingBook.date_of_issue < fourteen_days_ago
        ).all()

        debtors = []
        for record in debtors_records:
            student = session.query(Student).filter(Student.id == record.student_id).first()
            book = session.query(Book).filter(Book.id == record.book_id).first()

            if student and book:
                debtors.append({
                    'student_id': student.id,
                    'student_name': f"{student.name} {student.surname}",
                    'student_email': student.email,
                    'student_phone': student.phone,
                    'book_id': book.id,
                    'book_name': book.name,
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
            'student_name': f"{session.query(Student).filter(Student.id == student_id).first().name} {session.query(Student).filter(Student.id == student_id).first().surname}"
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
        books = session.query(Book).filter(
            Book.name.ilike(f"%{search_string}%")
        ).all()

        result = []
        for book in books:
            result.append({
                'id': book.id,
                'name': book.name,
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
                'author_id': book.author_id
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


if __name__ == '__main__':
    print("Запуск Flask приложения...")
    print("Доступные роуты:")
    print("  GET  /books - получить все книги")
    print("  GET  /debtors - получить список должников")
    print("  POST /issue-book - выдать книгу студенту")
    print("  POST /return-book - сдать книгу")
    print("  GET  /search-books?q=<строка> - поиск книг по названию")
    print("  GET  /students/scholarship - студенты со стипендией")
    print("  GET  /students/score/<балл> - студенты с баллом выше указанного")
    app.run(debug=True, port=5000)