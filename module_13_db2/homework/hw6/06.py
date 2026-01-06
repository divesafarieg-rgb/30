import sqlite3
import datetime
from collections import defaultdict


def update_work_schedule(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT id, preferred_sport FROM table_friendship_employees")
    employees = cursor.fetchall()

    sport_by_employee = {}
    for emp_id, sport in employees:
        sport_by_employee[emp_id] = sport

    sport_to_forbidden_day = {
        'футбол': 0,
        'хоккей': 1,
        'шахматы': 2,
        'SUP сёрфинг': 3,
        'SUP-сёрфинг': 3,
        'бокс': 4,
        'Dota2': 5,
        'шах-бокс': 6,
        'шахбокс': 6
    }

    cursor.execute("SELECT DISTINCT shift_date FROM table_friendship_schedule ORDER BY shift_date")
    all_dates = [row[0] for row in cursor.fetchall()]

    employees_by_day = {day: [] for day in range(7)}

    for emp_id, sport in employees:
        forbidden_day = sport_to_forbidden_day.get(sport, -1)
        for day in range(7):
            if day != forbidden_day:
                employees_by_day[day].append(emp_id)

    for day in range(7):
        available_count = len(employees_by_day[day])
        if available_count < 10:
            print(f"ОШИБКА: В день {day} доступно только {available_count} сотрудников")
            print("Расписание невозможно составить!")
            return

    cursor.execute("DELETE FROM table_friendship_schedule")

    work_days_count = defaultdict(int)

    new_schedule = []

    for date_str in all_dates:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        weekday = date_obj.weekday()

        available_employees = employees_by_day[weekday]

        sorted_employees = sorted(
            available_employees,
            key=lambda emp_id: work_days_count[emp_id]
        )

        selected = sorted_employees[:10]

        for emp_id in selected:
            work_days_count[emp_id] += 1

        for emp_id in selected:
            new_schedule.append((emp_id, date_str))

    print("Статистика рабочих дней:")
    print(f"Всего сотрудников: {len(employees)}")
    print(f"Всего дней: {len(all_dates)}")
    print(f"Всего смен: {len(all_dates) * 10}")

    min_days = min(work_days_count.values())
    max_days = max(work_days_count.values())
    avg_days = sum(work_days_count.values()) / len(work_days_count)

    print(f"Минимальное количество рабочих дней: {min_days}")
    print(f"Максимальное количество рабочих дней: {max_days}")
    print(f"Среднее количество рабочих дней: {avg_days:.2f}")

    cursor.executemany(
        "INSERT INTO table_friendship_schedule (employee_id, shift_date) VALUES (?, ?)",
        new_schedule
    )


def test_update_work_schedule():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ update_work_schedule")
    print("=" * 60)

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE table_friendship_employees (
            id INTEGER PRIMARY KEY,
            full_name VARCHAR(100),
            preferred_sport VARCHAR(50)
        )
    """)

    cursor.execute("""
        CREATE TABLE table_friendship_schedule (
            employee_id INTEGER,
            shift_date VARCHAR(10),
            FOREIGN KEY (employee_id) REFERENCES table_friendship_employees(id)
        )
    """)

    test_employees = [
        (1, 'Андреева Ц.Б.', 'Dota2'),
        (2, 'Дмитриев Л.З.', 'Dota2'),
        (3, 'Алексеева Э.И.', 'Dota2'),
        (4, 'Семёнов З.И.', 'бокс'),
        (5, 'Егоров Ф.Б.', 'бокс'),
        (6, 'Соловьёв О.В.', 'SUP сёрфинг'),
        (7, 'Волкова Я.Ц.', 'футбол'),
        (8, 'Кузнецов К.И.', 'футбол'),
        (9, 'Смирнова Ю.Ф.', 'SUP сёрфинг'),
        (10, 'Петрова У.У.', 'бокс'),
        (11, 'Яковлев Ф.Ш.', 'бокс'),
        (12, 'Александрова Я.М.', 'SUP сёрфинг'),
        (13, 'Попов Ж.Р.', 'хоккей'),
        (14, 'Лебедев Н.И.', 'бокс'),
        (15, 'Андреева Д.Г.', 'футбол'),
        (16, 'Фёдорова Е.Ц.', 'шахматы'),
        (17, 'Фёдоров Т.Щ.', 'футбол'),
        (18, 'Егоров Ч.Т.', 'футбол'),
        (19, 'Дмитриев Б.Ц.', 'шах-бокс'),
        (20, 'Смирнов У.Д.', 'бокс'),
        (21, 'Степанов Т.Я.', 'шах-бокс'),
        (22, 'Фёдорова Х.Ц.', 'хоккей'),
        (23, 'Петров А.О.', 'хоккей'),
        (24, 'Григорьев Э.М.', 'хоккей'),
        (25, 'Петров Г.Ф.', 'шах-бокс'),
        (26, 'Степанов Т.Г.', 'SUP сёрфинг'),
        (27, 'Александрова М.Ж.', 'SUP сёрфинг'),
        (28, 'Смирнова Ч.Е.', 'шахматы'),
        (29, 'Лебедев Д.К.', 'шахматы'),
        (30, 'Алексеева Ж.Ж.', 'шахматы'),
        (31, 'Михайлова Б.М.', 'шахматы'),
        (32, 'Соколова Д.М.', 'бокс'),
        (33, 'Михайлов Е.М.', 'хоккей'),
        (34, 'Михайлова М.Ч.', 'Dota2'),
        (35, 'Григорьев М.И.', 'футбол'),
        (36, 'Павлова Р.Ш.', 'хоккей'),
        (37, 'Волкова Т.Х.', 'SUP сёрфинг'),
        (38, 'Андреева Р.Ю.', 'Dota2'),
        (39, 'Фёдорова Б.Ж.', 'футбол'),
        (40, 'Дмитриева Т.Э.', 'хоккей'),
        (41, 'Богданова Ц.Ц.', 'футбол'),
        (42, 'Никитин Э.У.', 'шах-бокс'),
        (43, 'Дмитриев И.Ф.', 'шахматы'),
        (44, 'Михайлова Ж.Я.', 'бокс'),
        (45, 'Кузнецов И.М.', 'SUP сёрфинг'),
        (46, 'Волкова С.Щ.', 'SUP сёрфинг'),
        (47, 'Лебедева Ц.Я.', 'SUP сёрфинг'),
        (48, 'Андреев Т.Р.', 'шах-бокс'),
        (49, 'Смирнова И.Т.', 'футбол'),
        (50, 'Богданов С.Щ.', 'хоккей')
    ]

    cursor.executemany(
        "INSERT INTO table_friendship_employees VALUES (?, ?, ?)",
        test_employees
    )

    print("\n1. Создание тестового расписания...")
    start_date = datetime.date(2020, 1, 1)
    test_schedule = []

    for i in range(366):
        date_str = (start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        for j in range(10):
            emp_id = (i * 10 + j) % 50 + 1
            test_schedule.append((emp_id, date_str))

    cursor.executemany(
        "INSERT INTO table_friendship_schedule VALUES (?, ?)",
        test_schedule
    )

    cursor.execute("SELECT COUNT(*) FROM table_friendship_schedule")
    initial_count = cursor.fetchone()[0]
    print(f"Создано {initial_count} записей в расписании")

    print("\n2. Проверка начального расписания на нарушения...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM table_friendship_schedule s
        JOIN table_friendship_employees e ON s.employee_id = e.id
        WHERE (
            (e.preferred_sport = 'футбол' AND strftime('%w', s.shift_date) = '1') OR
            (e.preferred_sport = 'хоккей' AND strftime('%w', s.shift_date) = '2') OR
            (e.preferred_sport = 'шахматы' AND strftime('%w', s.shift_date) = '3') OR
            (e.preferred_sport LIKE 'SUP%' AND strftime('%w', s.shift_date) = '4') OR
            (e.preferred_sport = 'бокс' AND strftime('%w', s.shift_date) = '5') OR
            (e.preferred_sport = 'Dota2' AND strftime('%w', s.shift_date) = '6') OR
            (e.preferred_sport LIKE 'шах%бокс' AND strftime('%w', s.shift_date) = '0')
        )
    """)

    violations_before = cursor.fetchone()[0]
    print(f"Нарушений в начальном расписании: {violations_before}")

    print("\n3. Вызов функции update_work_schedule()...")
    update_work_schedule(cursor)

    print("\n4. Проверка результатов...")

    cursor.execute("SELECT COUNT(*) FROM table_friendship_schedule")
    final_count = cursor.fetchone()[0]
    print(f"Всего записей в финальном расписании: {final_count}")

    if final_count != 3660:
        print(f"ОШИБКА: Ожидается 3660 записей, получено {final_count}")

    cursor.execute("""
        SELECT shift_date, COUNT(*) as cnt 
        FROM table_friendship_schedule 
        GROUP BY shift_date
        HAVING cnt != 10
    """)

    bad_days = cursor.fetchall()
    if bad_days:
        print(f"ОШИБКА: Найдено {len(bad_days)} дней с неправильным количеством сотрудников")
        for date_str, count in bad_days[:3]:
            print(f"{date_str}: {count} сотрудников")
    else:
        print("В каждый день ровно 10 сотрудников")

    cursor.execute("""
        SELECT COUNT(*) 
        FROM table_friendship_schedule s
        JOIN table_friendship_employees e ON s.employee_id = e.id
        WHERE (
            (e.preferred_sport = 'футбол' AND strftime('%w', s.shift_date) = '1') OR
            (e.preferred_sport = 'хоккей' AND strftime('%w', s.shift_date) = '2') OR
            (e.preferred_sport = 'шахматы' AND strftime('%w', s.shift_date) = '3') OR
            (e.preferred_sport LIKE 'SUP%' AND strftime('%w', s.shift_date) = '4') OR
            (e.preferred_sport = 'бокс' AND strftime('%w', s.shift_date) = '5') OR
            (e.preferred_sport = 'Dota2' AND strftime('%w', s.shift_date) = '6') OR
            (e.preferred_sport LIKE 'шах%бокс' AND strftime('%w', s.shift_date) = '0')
        )
    """)

    violations_after = cursor.fetchone()[0]
    print(f"Нарушений в финальном расписании: {violations_after}")

    if violations_after == 0:
        print("Нарушений не обнаружено!")
    else:
        print("ОШИБКА: Найдены нарушения!")

    print("\n5. Анализ распределения нагрузки...")

    cursor.execute("""
        SELECT employee_id, COUNT(*) as work_days
        FROM table_friendship_schedule
        GROUP BY employee_id
        ORDER BY work_days
    """)

    work_stats = cursor.fetchall()

    if work_stats:
        min_work = work_stats[0][1]
        max_work = work_stats[-1][1]
        avg_work = sum(w[1] for w in work_stats) / len(work_stats)

        print(f"Минимальная нагрузка: {min_work} дней")
        print(f"Максимальная нагрузка: {max_work} дней")
        print(f"Средняя нагрузка: {avg_work:.1f} дней")

        ideal = 3660 / 50
        print(f"Идеальная нагрузка: {ideal:.1f} дней на сотрудника")

        if max_work - min_work <= 2:
            print("Нагрузка распределена равномерно")
        else:
            print(f"Разница в нагрузке: {max_work - min_work} дней")

    print("\n6. Пример расписания (первые 5 дней):")
    cursor.execute("""
        SELECT s.shift_date, s.employee_id, e.full_name, e.preferred_sport
        FROM table_friendship_schedule s
        JOIN table_friendship_employees e ON s.employee_id = e.id
        WHERE s.shift_date IN (
            '2020-01-01', '2020-01-02', '2020-01-03', '2020-01-04', '2020-01-05'
        )
        ORDER BY s.shift_date, s.employee_id
    """)

    schedule_example = cursor.fetchall()
    current_date = None
    for date_str, emp_id, name, sport in schedule_example:
        if date_str != current_date:
            print(f"\n   {date_str} (день недели: {get_weekday_name(date_str)}):")
            current_date = date_str
        print(f"Сотрудник {emp_id}: {name} ({sport})")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


def get_weekday_name(date_str):
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    weekdays = ['понедельник', 'вторник', 'среда', 'четверг',
                'пятница', 'суббота', 'воскресенье']
    return weekdays[date_obj.weekday()]


if __name__ == "__main__":
    test_update_work_schedule()

    print("\n\nПример использования с существующей базой данных:")
    print("""
conn = sqlite3.connect('ваша_база_данных.db')
cursor = conn.cursor()

update_work_schedule(cursor)

conn.commit()
conn.close()
    """)
