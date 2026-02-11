from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, func, event, \
    Table
from sqlalchemy.orm import declarative_base, relationship, Session, joinedload, subqueryload, selectinload
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import sessionmaker
import os
import re

Base = declarative_base()

student_book_association = Table('student_book_association', Base.metadata,
                                 Column('student_id', Integer, ForeignKey('students.id')),
                                 Column('book_id', Integer, ForeignKey('books.id'))
                                 )


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")

    @hybrid_property
    def full_name(self):
        return f"{self.name} {self.surname}"


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    count = Column(Integer, default=1)
    release_date = Column(Date, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id', ondelete="CASCADE"))

    author = relationship("Author", back_populates="books")
    receiving_records = relationship("ReceivingBook", back_populates="book", cascade="all, delete-orphan")

    students = association_proxy('receiving_records', 'student')


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    average_score = Column(Float, nullable=False)
    scholarship = Column(Boolean, nullable=False)

    receiving_records = relationship("ReceivingBook", back_populates="student", cascade="all, delete-orphan")

    books = association_proxy('receiving_records', 'book')

    @classmethod
    def get_scholarship_students(cls, session):
        return session.query(cls).filter(cls.scholarship == True).all()

    @classmethod
    def get_students_by_score(cls, session, min_score):
        return session.query(cls).filter(cls.average_score > min_score).all()


class ReceivingBook(Base):
    __tablename__ = 'receiving_books'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey('students.id', ondelete="CASCADE"))
    date_of_issue = Column(DateTime, nullable=False, default=datetime.now)
    date_of_return = Column(DateTime)

    book = relationship("Book", back_populates="receiving_records")
    student = relationship("Student", back_populates="receiving_records")

    @hybrid_property
    def count_date_with_book(self):
        if self.date_of_return:
            end_date = self.date_of_return
        else:
            end_date = datetime.now()

        days_difference = (end_date - self.date_of_issue).days
        return max(days_difference, 0)


@event.listens_for(Student, 'before_insert')
def validate_phone_format(mapper, connection, target):
    phone_pattern = r'^\+7\(9\d{2}\)-\d{3}-\d{2}-\d{2}$'
    if not re.match(phone_pattern, target.phone):
        raise ValueError(f"Неверный формат телефона: {target.phone}. Ожидается формат: +7(9**)-***-**-**")


def init_db():
    engine = create_engine('sqlite:///library.db', echo=False)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        authors = [
            Author(name="Лев", surname="Толстой"),
            Author(name="Фёдор", surname="Достоевский"),
            Author(name="Александр", surname="Пушкин"),
            Author(name="Антон", surname="Чехов"),
            Author(name="Михаил", surname="Булгаков")
        ]
        session.add_all(authors)

        books = [
            Book(name="Война и мир", count=3, release_date=date(1869, 1, 1), author_id=1),
            Book(name="Анна Каренина", count=2, release_date=date(1877, 1, 1), author_id=1),
            Book(name="Воскресение", count=1, release_date=date(1899, 1, 1), author_id=1),
            Book(name="Преступление и наказание", count=4, release_date=date(1866, 1, 1), author_id=2),
            Book(name="Братья Карамазовы", count=3, release_date=date(1880, 1, 1), author_id=2),
            Book(name="Идиот", count=2, release_date=date(1869, 1, 1), author_id=2),
            Book(name="Евгений Онегин", count=5, release_date=date(1833, 1, 1), author_id=3),
            Book(name="Капитанская дочка", count=3, release_date=date(1836, 1, 1), author_id=3),
            Book(name="Руслан и Людмила", count=2, release_date=date(1820, 1, 1), author_id=3),
            Book(name="Вишнёвый сад", count=2, release_date=date(1904, 1, 1), author_id=4),
            Book(name="Три сестры", count=1, release_date=date(1901, 1, 1), author_id=4),
            Book(name="Мастер и Маргарита", count=3, release_date=date(1967, 1, 1), author_id=5)
        ]
        session.add_all(books)

        students = [
            Student(name="Иван", surname="Иванов", phone="+7(912)-345-67-89",
                    email="ivan@example.com", average_score=4.5, scholarship=True),
            Student(name="Петр", surname="Петров", phone="+7(917)-654-32-10",
                    email="petr@example.com", average_score=3.8, scholarship=False),
            Student(name="Мария", surname="Сидорова", phone="+7(919)-876-54-32",
                    email="maria@example.com", average_score=4.9, scholarship=True),
            Student(name="Анна", surname="Смирнова", phone="+7(915)-557-78-90",
                    email="anna@example.com", average_score=3.2, scholarship=False),
            Student(name="Алексей", surname="Кузнецов", phone="+7(911)-123-45-67",
                    email="alex@example.com", average_score=4.2, scholarship=True)
        ]
        session.add_all(students)

        current_year = datetime.now().year
        current_month = datetime.now().month

        receiving_books = [
            ReceivingBook(book_id=1, student_id=1,
                          date_of_issue=datetime(current_year, 1, 10),
                          date_of_return=datetime(current_year, 1, 20)),
            ReceivingBook(book_id=4, student_id=2,
                          date_of_issue=datetime(current_year, 2, 15)),
            ReceivingBook(book_id=5, student_id=2,
                          date_of_issue=datetime(current_year, 1, 20),
                          date_of_return=datetime(current_year, 2, 1)),
            ReceivingBook(book_id=7, student_id=3,
                          date_of_issue=datetime(current_year, 2, 5)),
            ReceivingBook(book_id=8, student_id=3,
                          date_of_issue=datetime(current_year, 1, 25),
                          date_of_return=datetime(current_year, 2, 10)),
            ReceivingBook(book_id=12, student_id=5,
                          date_of_issue=datetime(current_year, 2, 10))
        ]
        session.add_all(receiving_books)

        for book in books:
            borrowed_count = session.query(ReceivingBook).filter(
                ReceivingBook.book_id == book.id,
                ReceivingBook.date_of_return == None
            ).count()
            book.count = max(book.count - borrowed_count, 0)

        session.commit()
        print("База данных успешно создана и заполнена тестовыми данными!")
        print(f"Все записи созданы с датами {current_year} года")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании базы данных: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

    return engine


def get_db_engine():
    return create_engine('sqlite:///library.db', echo=False)


if __name__ == "__main__":
    init_db()