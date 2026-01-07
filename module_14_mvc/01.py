from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from typing import List

from models import init_db, get_all_books, DATA

app: Flask = Flask(__name__)


def _get_html_table_for_books(books: List[dict]) -> str:
    table = """
<table>
    <thead>
    <tr>
        <th>ID</td>
        <th>Title</td>
        <th>Author</td>
    </tr>
    </thead>
    <tbody>
        {books_rows}
    </tbody>
</table>
"""
    rows: str = ''
    for book in books:
        rows += '<tr><td>{id}</tb><td>{title}</tb><td>{author}</tb></tr>'.format(
            id=book['id'], title=book['title'], author=book['author'],
        )
    return table.format(books_rows=rows)


@app.route('/books')
def all_books() -> str:
    return render_template(
        'index.html',
        books=get_all_books(),
    )


@app.route('/books/form', methods=['GET', 'POST'])
def get_books_form() -> str:
    if request.method == 'POST':
        title = request.form.get('book_title', '').strip()
        author = request.form.get('author_name', '').strip()

        if not title or not author:
            return "Ошибка: Название книги и автор обязательны для заполнения!", 400

        with sqlite3.connect('table_books.db') as conn:
            cursor: sqlite3.Cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO `table_books` (title, author) 
                VALUES (?, ?)
                """,
                (title, author)
            )
            conn.commit()

        return redirect('/books')

    return render_template('add_book.html')


if __name__ == '__main__':
    init_db(DATA)
    app.run(debug=True)
