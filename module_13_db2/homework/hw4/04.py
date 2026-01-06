import sqlite3

IVAN_SOVIN_SALARY = 100000


def ivan_sovin_the_most_effective(
        cursor: sqlite3.Cursor,
        name: str,
) -> None:
    cursor.execute(
        """
        SELECT id, name, salary 
        FROM table_effective_manager 
        WHERE name LIKE ? AND name != 'Иван Совин'
        """,
        (f'%{name}%',)
    )

    employees = cursor.fetchall()

    if not employees:
        print(f"Сотрудники с именем, содержащим '{name}', не найдены.")
        return

    print(f"Найдено {len(employees)} сотрудников с именем, содержащим '{name}':")

    employees_to_delete = []
    employees_to_update = []

    for emp_id, emp_name, current_salary in employees:
        new_salary = current_salary * 1.10

        if new_salary > IVAN_SOVIN_SALARY:
            employees_to_delete.append(emp_id)
            print(f"  ❌ {emp_name}: {current_salary} → {new_salary:.2f} > {IVAN_SOVIN_SALARY} (будет уволен)")
        else:
            employees_to_update.append((new_salary, emp_id, emp_name, current_salary))
            print(f"  ✅ {emp_name}: {current_salary} → {new_salary:.2f} <= {IVAN_SOVIN_SALARY} (получит повышение)")

    if employees_to_delete:
        placeholders = ','.join('?' for _ in employees_to_delete)
        cursor.execute(
            f"DELETE FROM table_effective_manager WHERE id IN ({placeholders})",
            employees_to_delete
        )
        print(f"\nУволено {len(employees_to_delete)} сотрудников.")

    if employees_to_update:
        for new_salary, emp_id, emp_name, old_salary in employees_to_update:
            cursor.execute(
                "UPDATE table_effective_manager SET salary = ? WHERE id = ?",
                (new_salary, emp_id)
            )
        print(f"Повышена зарплата {len(employees_to_update)} сотрудникам.")


def create_test_database() -> tuple:
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE table_effective_manager (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            salary INTEGER
        )
    ''')

    employees = [
        (1, 'Иван Совин', 100000),
        (2, 'Алексеева К.М.', 56500),
        (3, 'Александрова Ж.П.', 44000),
        (4, 'Смирнов Е.З.', 29800),
        (5, 'Петров Т.И.', 69900),
        (6, 'Степанова Ц.М.', 59400),
        (7, 'Александров Д.М.', 63800),
        (8, 'Михайлова К.Н.', 39100),
        (9, 'Соловьёв Ф.Н.', 76400),
        (10, 'Андреева Л.П.', 18900),
        (11, 'Фёдоров В.Р.', 67800),
        (12, 'Егорова Н.Ш.', 33800),
        (13, 'Дмитриев Я.Н.', 55900),
        (14, 'Соловьёв Ц.Н.', 42300),
        (15, 'Петрова Ц.Ю.', 42100),
        (16, 'Богданова Л.В.', 49300),
        (17, 'Никитин Р.Ш.', 58500),
        (18, 'Михайлов Б.Е.', 56300),
        (19, 'Дмитриева Ж.К.', 45400),
        (20, 'Фёдоров Н.Г.', 29400),
        (21, 'Кузнецова Р.И.', 52400),
        (22, 'Николаева Н.Ш.', 53700),
        (23, 'Иванов Е.Б.', 58400),
        (24, 'Павлов О.М.', 42900),
        (25, 'Николаев Х.Е.', 66900),
        (26, 'Андреева Б.М.', 36900),
        (27, 'Александрова Я.Я.', 17000),
        (28, 'Кузнецова А.Н.', 42000),
        (29, 'Соловьёва С.И.', 66000),
        (30, 'Фёдорова Ю.Т.', 46200),
        (31, 'Павлова О.С.', 43300),
        (32, 'Михайлов П.С.', 16600),
        (33, 'Богданова Д.И.', 65600),
        (34, 'Попова Ч.Щ.', 63200),
        (35, 'Никитин У.А.', 23200),
        (36, 'Лебедева Г.З.', 34500),
        (37, 'Дмитриев А.Т.', 30100),
        (38, 'Алексеев М.Ц.', 18800),
        (39, 'Иванов Х.Т.', 53400),
        (40, 'Александрова Б.В.', 16400),
        (41, 'Николаева Х.О.', 26700),
        (42, 'Богданов Л.Ч.', 57200),
        (43, 'Александров Г.Е.', 61400),
        (44, 'Волков Г.Ж.', 33100),
        (45, 'Богданов У.Ю.', 68900),
        (46, 'Николаева О.У.', 40000),
        (47, 'Соколов Г.С.', 58300),
        (48, 'Александров Ю.Г.', 76500),
        (49, 'Никитина Р.Х.', 71800),
        (50, 'Павлова Б.Х.', 63400),
    ]

    cursor.executemany(
        'INSERT INTO table_effective_manager VALUES (?, ?, ?)',
        employees
    )

    conn.commit()
    return conn, cursor


def print_all_employees(cursor: sqlite3.Cursor, title: str = "Все сотрудники"):
    print(f"\n{'=' * 60}")
    print(f"{title}:")
    print(f"{'=' * 60}")

    cursor.execute("SELECT id, name, salary FROM table_effective_manager ORDER BY id")

    print(f"{'ID':<4} | {'Имя':<25} | {'Зарплата':<10} | {'После повышения':<15} | Статус")
    print("-" * 80)

    for emp_id, emp_name, salary in cursor.fetchall():
        new_salary = salary * 1.10
        if emp_name == 'Иван Совин':
            status = "Менеджер"
        elif new_salary > IVAN_SOVIN_SALARY:
            status = "Будет уволен"
        else:
            status = "Останется"

        print(f"{emp_id:<4} | {emp_name:<25} | {salary:<10} | {new_salary:<15.2f} | {status}")


def test_specific_names():
    conn, cursor = create_test_database()

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ ivAN_SOVIN_THE_MOST_EFFECTIVE")
    print("=" * 60)

    print_all_employees(cursor, "ИСХОДНЫЕ ДАННЫЕ")

    print("\n" + "=" * 60)
    print("ТЕСТ 1: Обработка всех 'Александров' (частичное совпадение)")
    print("=" * 60)
    ivan_sovin_the_most_effective(cursor, 'Александров')
    conn.commit()

    print("\n" + "=" * 60)
    print("ТЕСТ 2: Обработка всех 'Соловьёв'")
    print("=" * 60)
    ivan_sovin_the_most_effective(cursor, 'Соловьёв')
    conn.commit()

    print("\n" + "=" * 60)
    print("ТЕСТ 3: Попытка обработать 'Иван' (должен пропустить Ивана Совина)")
    print("=" * 60)
    ivan_sovin_the_most_effective(cursor, 'Иван')
    conn.commit()

    print("\n" + "=" * 60)
    print("ТЕСТ 4: Обработка всех 'Петр' (проверим Петрова и Петрову)")
    print("=" * 60)
    ivan_sovin_the_most_effective(cursor, 'Петр')
    conn.commit()

    print_all_employees(cursor, "ФИНАЛЬНОЕ СОСТОЯНИЕ БАЗЫ ДАННЫХ")

    cursor.execute("SELECT COUNT(*) FROM table_effective_manager")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM table_effective_manager WHERE name = 'Иван Совин'")
    ivan = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM table_effective_manager WHERE name != 'Иван Совин'")
    others = cursor.fetchone()[0]

    print(f"\nСтатистика:")
    print(f"Всего записей в БД: {total}")
    print(f"  - Иван Совин: {ivan}")
    print(f"  - Другие сотрудники: {others}")

    conn.close()


def test_who_will_be_fired():
    conn, cursor = create_test_database()

    print("=" * 60)
    print("АНАЛИЗ: КТО БУДЕТ УВОЛЕН ПРИ ПОВЫШЕНИИ НА 10%")
    print("=" * 60)
    print(f"Зарплата Ивана Совина: {IVAN_SOVIN_SALARY}")
    print(f"Максимальная зарплата для сохранения: {IVAN_SOVIN_SALARY / 1.1:.2f}")
    print("=" * 60)

    cursor.execute("""
        SELECT name, salary, salary * 1.10 as new_salary 
        FROM table_effective_manager 
        WHERE name != 'Иван Совин'
        ORDER BY new_salary DESC
    """)

    will_be_fired = []
    will_stay = []

    for name, old_salary, new_salary in cursor.fetchall():
        if new_salary > IVAN_SOVIN_SALARY:
            will_be_fired.append((name, old_salary, new_salary))
        else:
            will_stay.append((name, old_salary, new_salary))

    print(f"\nБУДУТ УВОЛЕНЫ ({len(will_be_fired)} чел.):")
    print("-" * 60)
    for name, old_salary, new_salary in will_be_fired:
        print(f"{name:25} {old_salary:8} → {new_salary:10.2f} > {IVAN_SOVIN_SALARY}")

    print(f"\nОСТАНУТСЯ ({len(will_stay)} чел.):")
    print("-" * 60)
    for name, old_salary, new_salary in will_stay[:10]:  # Покажем только первых 10
        print(f"{name:25} {old_salary:8} → {new_salary:10.2f} <= {IVAN_SOVIN_SALARY}")

    if len(will_stay) > 10:
        print(f"... и еще {len(will_stay) - 10} сотрудников")

    conn.close()


if __name__ == "__main__":
    print("Выберите тест:")
    print("1. Основной тест функции")
    print("2. Анализ: кто будет уволен")
    print("3. Оба теста")

    choice = input("Введите номер (1-3): ").strip()

    if choice == "1":
        test_specific_names()
    elif choice == "2":
        test_who_will_be_fired()
    elif choice == "3":
        test_who_will_be_fired()
        print("\n" + "=" * 60)
        print("СЛЕДУЮЩИЙ ТЕСТ:")
        print("=" * 60)
        test_specific_names()
    else:
        print("Неверный выбор. Запускаю оба теста...")
        test_who_will_be_fired()
        print("\n" + "=" * 60)
        print("СЛЕДУЮЩИЙ ТЕСТ:")
        print("=" * 60)
        test_specific_names()