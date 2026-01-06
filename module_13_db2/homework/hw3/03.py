import sqlite3
from datetime import datetime


def log_bird(
        cursor: sqlite3.Cursor,
        bird_name: str,
        date_time: str,
) -> None:
    cursor.execute("""
        INSERT INTO table_birds (bird_name, time_seen)
        VALUES (?, ?)
    """, (bird_name, date_time))


def check_if_such_bird_already_seen(
        cursor: sqlite3.Cursor,
        bird_name: str
) -> bool:
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 
            FROM table_birds 
            WHERE bird_name = ?
        )
    """, (bird_name,))

    result = cursor.fetchone()
    return result[0] == 1  # 1 = True, 0 = False


def main():
    connection = sqlite3.connect('birds.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table_birds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bird_name TEXT NOT NULL,
            time_seen TEXT NOT NULL
        )
    ''')

    print("=== Журнал птиц ЮНат v0.1 ===")

    while True:
        print("\nВыберите действие:")
        print("1. Добавить новую птицу")
        print("2. Проверить, видели ли птицу")
        print("3. Выйти")

        choice = input("Ваш выбор: ")

        if choice == "1":
            bird_name = input("Введите название птицы: ")
            time_seen = input("Введите время наблюдения (или нажмите Enter для текущего времени): ")

            if not time_seen:
                time_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_bird(cursor, bird_name, time_seen)
            connection.commit()
            print(f"Птица '{bird_name}' добавлена в журнал!")

        elif choice == "2":
            bird_name = input("Введите название птицы для проверки: ")
            if check_if_such_bird_already_seen(cursor, bird_name):
                print(f"✓ Птицу '{bird_name}' уже видели ранее!")
            else:
                print(f"✗ Птицу '{bird_name}' еще не видели")

        elif choice == "3":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

    connection.close()


if __name__ == "__main__":
    main()