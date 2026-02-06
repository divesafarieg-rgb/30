from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    count = Column(Integer, default=1)
    release_date = Column(Date, nullable=False)
    author_id = Column(Integer, nullable=False)


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    average_score = Column(Float, nullable=False)
    scholarship = Column(Boolean, nullable=False)

    @classmethod
    def get_scholarship_students(cls, session):
        return session.query(cls).filter(cls.scholarship == True).all()

    @classmethod
    def get_students_by_score(cls, session, min_score):
        return session.query(cls).filter(cls.average_score > min_score).all()


class ReceivingBook(Base):
    __tablename__ = 'receiving_books'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    date_of_issue = Column(DateTime, nullable=False, default=datetime.now)
    date_of_return = Column(DateTime)

    @hybrid_property
    def count_date_with_book(self):
        if self.date_of_return:
            end_date = self.date_of_return
        else:
            end_date = datetime.now()

        days_difference = (end_date - self.date_of_issue).days
        return max(days_difference, 0)


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
            Author(name="Антон", surname="Чехов")
        ]
        session.add_all(authors)

        books = [
            Book(name="Война и мир", count=3, release_date=date(1869, 1, 1), author_id=1),
            Book(name="Анна Каренина", count=2, release_date=date(1877, 1, 1), author_id=1),
            Book(name="Преступление и наказание", count=4, release_date=date(1866, 1, 1), author_id=2),
            Book(name="Евгений Онегин", count=5, release_date=date(1833, 1, 1), author_id=3),
            Book(name="Капитанская дочка", count=3, release_date=date(1836, 1, 1), author_id=3),
            Book(name="Вишнёвый сад", count=2, release_date=date(1904, 1, 1), author_id=4)
        ]
        session.add_all(books)

        students = [
            Student(name="Иван", surname="Иванов", phone="+79111234567",
                    email="ivan@example.com", average_score=4.5, scholarship=True),
            Student(name="Петр", surname="Петров", phone="+79117654321",
                    email="petr@example.com", average_score=3.8, scholarship=False),
            Student(name="Мария", surname="Сидорова", phone="+79119876543",
                    email="maria@example.com", average_score=4.9, scholarship=True),
            Student(name="Анна", surname="Смирнова", phone="+79115557788",
                    email="anna@example.com", average_score=3.2, scholarship=False)
        ]
        session.add_all(students)

        receiving_books = [
            ReceivingBook(book_id=1, student_id=1,
                          date_of_issue=datetime(2024, 1, 10),
                          date_of_return=datetime(2024, 1, 20)),
            ReceivingBook(book_id=2, student_id=2,
                          date_of_issue=datetime(2024, 2, 1)),
            ReceivingBook(book_id=3, student_id=3,
                          date_of_issue=datetime(2024, 1, 15)),
            ReceivingBook(book_id=4, student_id=4,
                          date_of_issue=datetime(2024, 2, 5)),
            ReceivingBook(book_id=5, student_id=1,
                          date_of_issue=datetime(2024, 1, 25))
        ]
        session.add_all(receiving_books)

        session.commit()
        print("База данных успешно создана и заполнена тестовыми данными!")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        session.close()

    return engine


def get_db_engine():
    return create_engine('sqlite:///library.db', echo=False)


if __name__ == "__main__":
    init_db()