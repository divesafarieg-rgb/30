import sqlite3


def create_schema():
    sql_queries = [
        """
        CREATE TABLE IF NOT EXISTS actors (
            act_id INTEGER PRIMARY KEY,
            act_first_name VARCHAR(50) NOT NULL,
            act_last_name VARCHAR(50) NOT NULL,
            act_gender VARCHAR(1) CHECK(act_gender IN ('M', 'F'))
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS movie (
            mov_id INTEGER PRIMARY KEY,
            mov_title VARCHAR(50) NOT NULL
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS director (
            dir_id INTEGER PRIMARY KEY,
            dir_first_name VARCHAR(50) NOT NULL,
            dir_last_name VARCHAR(50) NOT NULL
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS movie_cast (
            act_id INTEGER,
            mov_id INTEGER,
            role VARCHAR(50),
            PRIMARY KEY (act_id, mov_id),
            FOREIGN KEY (act_id) REFERENCES actors(act_id) ON DELETE CASCADE,
            FOREIGN KEY (mov_id) REFERENCES movie(mov_id) ON DELETE CASCADE
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS oscar_awarded (
            award_id INTEGER PRIMARY KEY,
            mov_id INTEGER NOT NULL,
            FOREIGN KEY (mov_id) REFERENCES movie(mov_id) ON DELETE CASCADE
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS movie_direction (
            dir_id INTEGER,
            mov_id INTEGER,
            PRIMARY KEY (dir_id, mov_id),
            FOREIGN KEY (dir_id) REFERENCES director(dir_id) ON DELETE CASCADE,
            FOREIGN KEY (mov_id) REFERENCES movie(mov_id) ON DELETE CASCADE
        )
        """
    ]

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON")

        for query in sql_queries:
            cursor.execute(query)

        conn.commit()
        print("Схема базы данных успешно создана!")


if __name__ == "__main__":
    create_schema()