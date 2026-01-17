import sqlite3
import os
from dataclasses import dataclass
from typing import Optional, List, Dict

DATABASE_NAME = 'table_books.db'
BOOKS_TABLE_NAME = 'books'
AUTHORS_TABLE_NAME = 'authors'


@dataclass
class Author:
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    id: Optional[int] = None

    def full_name(self) -> str:
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)

    def short_name(self) -> str:
        result = self.last_name
        if self.first_name:
            result += f" {self.first_name[0]}."
        if self.middle_name:
            result += f"{self.middle_name[0]}."
        return result


@dataclass
class Book:
    title: str
    author_id: int
    id: Optional[int] = None


def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {AUTHORS_TABLE_NAME}(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                middle_name TEXT
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {BOOKS_TABLE_NAME}(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) 
                REFERENCES {AUTHORS_TABLE_NAME}(id) 
                ON DELETE CASCADE
            )
        ''')

        cursor.execute(f'SELECT COUNT(*) FROM {AUTHORS_TABLE_NAME}')
        if cursor.fetchone()[0] == 0:
            test_authors = [
                ('Swaroop', 'C.', 'H.'),
                ('Herman', 'Melville', None),
                ('Leo', 'Tolstoy', None),
            ]
            cursor.executemany(
                f'INSERT INTO {AUTHORS_TABLE_NAME} (first_name, last_name, middle_name) VALUES (?, ?, ?)',
                test_authors
            )

            cursor.execute('SELECT id FROM authors ORDER BY id')
            author_ids = [row[0] for row in cursor.fetchall()]

            test_books = [
                ('A Byte of Python', author_ids[0]),
                ('Moby-Dick; or, The Whale', author_ids[1]),
                ('War and Peace', author_ids[2]),
            ]
            cursor.executemany(
                f'INSERT INTO {BOOKS_TABLE_NAME} (title, author_id) VALUES (?, ?)',
                test_books
            )

        conn.commit()


def get_all_books():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT b.id, b.title, b.author_id, 
                   a.first_name, a.last_name, a.middle_name 
            FROM {BOOKS_TABLE_NAME} b
            JOIN {AUTHORS_TABLE_NAME} a ON b.author_id = a.id
            ORDER BY b.title
        ''')
        books = []
        for row in cursor.fetchall():
            book_id, title, author_id, first_name, last_name, middle_name = row
            author_obj = Author(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                id=author_id
            )
            books.append({
                'id': book_id,
                'title': title,
                'author_id': author_id,
                'author': author_obj.full_name(),
                'author_short': author_obj.short_name()
            })
        return books


def get_all_authors():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {AUTHORS_TABLE_NAME} ORDER BY last_name, first_name')
        authors = []
        for row in cursor.fetchall():
            authors.append(Author(id=row[0], first_name=row[1], last_name=row[2], middle_name=row[3]))
        return authors


def get_author_by_id(author_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {AUTHORS_TABLE_NAME} WHERE id = ?', (author_id,))
        row = cursor.fetchone()
        if row:
            return Author(id=row[0], first_name=row[1], last_name=row[2], middle_name=row[3])
        return None


def add_book(title, author_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(
            f'INSERT INTO {BOOKS_TABLE_NAME} (title, author_id) VALUES (?, ?)',
            (title, author_id)
        )
        return cursor.lastrowid


def add_author(first_name, last_name, middle_name=None):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'INSERT INTO {AUTHORS_TABLE_NAME} (first_name, last_name, middle_name) VALUES (?, ?, ?)',
            (first_name, last_name, middle_name)
        )
        return cursor.lastrowid


def delete_author(author_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(
            f'SELECT * FROM {AUTHORS_TABLE_NAME} WHERE id = ?',
            (author_id,)
        )
        if not cursor.fetchone():
            return False
        cursor.execute(f'DELETE FROM {AUTHORS_TABLE_NAME} WHERE id = ?', (author_id,))
        conn.commit()
        return True


def check_cascade():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('PRAGMA foreign_key_list(books)')
        for fk in cursor.fetchall():
            if fk[5] == 'CASCADE':
                return True
        return False


def reset_db():
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    init_db()