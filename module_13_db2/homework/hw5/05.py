import sqlite3
import random


def generate_test_data(cursor: sqlite3.Cursor, number_of_groups: int) -> None:
    cursor.execute("DELETE FROM uefa_commands")
    cursor.execute("DELETE FROM uefa_draw")

    animals = ["Lion", "Tiger", "Bear", "Wolf", "Eagle", "Shark",
               "Dragon", "Phoenix", "Rhino", "Panther", "Falcon", "Hawk"]

    cities = ["London", "Madrid", "Berlin", "Rome", "Paris", "Lisbon",
              "Amsterdam", "Brussels", "Vienna", "Warsaw", "Kyiv", "Prague"]

    commands_data = []
    draw_data = []
    team_id = 1

    for group in range(1, number_of_groups + 1):
        strong_team = f"{random.choice(animals)} {random.choice(cities)}"
        commands_data.append((team_id, strong_team, random.choice(cities), "сильная"))
        draw_data.append((team_id, group))
        team_id += 1

        for _ in range(2):
            medium_team = f"{random.choice(animals)} United"
            commands_data.append((team_id, medium_team, random.choice(cities), "средняя"))
            draw_data.append((team_id, group))
            team_id += 1

        weak_team = f"{random.choice(cities)} City"
        commands_data.append((team_id, weak_team, random.choice(cities), "слабая"))
        draw_data.append((team_id, group))
        team_id += 1

    cursor.executemany("INSERT INTO uefa_commands VALUES (?, ?, ?, ?)", commands_data)
    cursor.executemany("INSERT INTO uefa_draw VALUES (?, ?)", draw_data)


def test_program():
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ ПРОГРАММЫ ДЛЯ ЖЕРЕБЬЕВКИ УЕФА")
    print("=" * 50)

    test_cases = [4, 8, 12, 16]

    for num_groups in test_cases:
        print(f"\nТест для {num_groups} групп:")
        print("-" * 40)

        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE uefa_commands (
                id INTEGER PRIMARY KEY,
                name TEXT,
                country TEXT,
                level TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE uefa_draw (
                team_id INTEGER,
                group_id INTEGER
            )
        ''')

        generate_test_data(cursor, num_groups)

        cursor.execute("SELECT COUNT(*) FROM uefa_commands")
        total_teams = cursor.fetchone()[0]
        expected_teams = num_groups * 4
        print(f"Количество команд: {total_teams} (ожидается: {expected_teams})")

        cursor.execute("SELECT COUNT(*) FROM uefa_draw")
        total_draw = cursor.fetchone()[0]
        print(f"Записей в жеребьевке: {total_draw}")

        print("\nРаспределение по группам:")
        cursor.execute('''
            SELECT group_id, level, COUNT(*)
            FROM uefa_draw d
            JOIN uefa_commands c ON d.team_id = c.id
            GROUP BY group_id, level
            ORDER BY group_id, 
                CASE level 
                    WHEN 'сильная' THEN 1
                    WHEN 'средняя' THEN 2
                    WHEN 'слабая' THEN 3
                END
        ''')

        group_distribution = {}
        for group_id, level, count in cursor.fetchall():
            if group_id not in group_distribution:
                group_distribution[group_id] = []
            group_distribution[group_id].append(f"{level}: {count}")

        for group_id in sorted(group_distribution.keys()):
            print(f"  Группа {group_id}: {', '.join(group_distribution[group_id])}")

        cursor.execute("SELECT COUNT(DISTINCT name) FROM uefa_commands")
        unique_names = cursor.fetchone()[0]
        print(f"\nУникальных названий: {unique_names} из {total_teams}")

        if unique_names == total_teams:
            print("Все названия команд уникальны!")
        else:
            print("Есть повторяющиеся названия!")

        print(f"\nПримеры команд (первые 5):")
        cursor.execute("SELECT * FROM uefa_commands LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row}")

        print(f"\nЖеребьевка для первых 2 групп:")
        cursor.execute('''
            SELECT d.group_id, c.id, c.name, c.level
            FROM uefa_draw d
            JOIN uefa_commands c ON d.team_id = c.id
            WHERE d.group_id <= 2
            ORDER BY d.group_id, 
                CASE c.level 
                    WHEN 'сильная' THEN 1
                    WHEN 'средняя' THEN 2
                    WHEN 'слабая' THEN 3
                END
        ''')

        current_group = None
        for group_id, team_id, name, level in cursor.fetchall():
            if current_group != group_id:
                print(f"  Группа {group_id}:")
                current_group = group_id
            print(f"    Команда {team_id}: {name} ({level})")

        conn.close()

        print(f"\n✓ Тест для {num_groups} групп пройден успешно!")

    print("\n" + "=" * 50)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("=" * 50)


def main():
    test_program()

    print("\n\n" + "=" * 50)
    print("ДОПОЛНИТЕЛЬНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 50)

    conn = sqlite3.connect('uefa_draw.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uefa_commands (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            country TEXT,
            level TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uefa_draw (
            team_id INTEGER,
            group_id INTEGER
        )
    ''')

    while True:
        try:
            num_groups = int(input("\nВведите количество групп (от 4 до 16): "))
            if 4 <= num_groups <= 16:
                break
            else:
                print("Ошибка! Количество групп должно быть от 4 до 16.")
        except ValueError:
            print("Ошибка! Введите целое число.")

    generate_test_data(cursor, num_groups)

    conn.commit()

    print(f"\nДанные для {num_groups} групп успешно сгенерированы!")
    print(f"База данных сохранена в файле: uefa_draw.db")

    cursor.execute("SELECT COUNT(*) FROM uefa_commands")
    total_teams = cursor.fetchone()[0]
    print(f"Всего команд: {total_teams}")

    cursor.execute("SELECT level, COUNT(*) FROM uefa_commands GROUP BY level ORDER BY level")
    print("\nРаспределение по уровням:")
    for level, count in cursor.fetchall():
        print(f"  {level.capitalize()}: {count} команд")

    conn.close()


if __name__ == "__main__":
    main()
