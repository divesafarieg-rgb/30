import sqlite3
import os
import sys
import time


def print_query_results(filename, cursor, query_text):
    try:
        cursor.execute(query_text)
        results = cursor.fetchall()

        print(f"\n{'=' * 60}")
        print(f"РЕЗУЛЬТАТЫ: {filename}")
        print(f"{'=' * 60}")

        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            print(" | ".join(columns))
            print("-" * 80)

        max_rows = 10
        for i, row in enumerate(results[:max_rows]):
            print(" | ".join(str(item) for item in row))

        if len(results) > max_rows:
            print(f"... и ещё {len(results) - max_rows} строк")

        print(f"Всего записей: {len(results)}")
        return True

    except Exception as e:
        print(f"Ошибка при выполнении {filename}: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("SQL-ЗАПРОСЫ К БАЗЕ ДАННЫХ")
    print("=" * 60)

    print("\n1. Проверка и закрытие соединений с базой данных...")

    if os.path.exists("hw.db"):
        print("Файл базы данных существует. Пытаемся удалить...")
        for attempt in range(5):
            try:
                os.remove("hw.db")
                print("Старая база данных удалена!")
                break
            except PermissionError:
                print(f"Попытка {attempt + 1}: Файл занят. Ждем 1 секунду...")
                time.sleep(1)
        else:
            print("Не удалось удалить файл. Закройте все программы, использующие hw.db")
            print("Можно попробовать удалить файл вручную или перезапустить компьютер.")
            sys.exit(1)

    if not os.path.exists("generate_hw_database.py"):
        print("Ошибка: файл generate_hw_database.py не найден!")
        print("Убедитесь, что он находится в текущей директории.")
        sys.exit(1)

    print("\n2. Создание новой базы данных...")
    try:
        import generate_hw_database

        generate_hw_database.prepare_tables()
        print("Новая база данных создана!")
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        sys.exit(1)

    print("\n3. Подключение к базе данных...")
    try:
        conn = sqlite3.connect('hw.db')
        cursor = conn.cursor()
        print("Подключение успешно!")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        sys.exit(1)

    queries = {
        '2_1.sql': """SELECT 
    c.full_name AS customer_name,
    m.full_name AS manager_name,
    o.purchase_amount,
    o.date
FROM "order" o
LEFT JOIN customer c ON o.customer_id = c.customer_id
LEFT JOIN manager m ON o.manager_id = m.manager_id;""",

        '2_2.sql': """SELECT 
    c.full_name
FROM customer c
LEFT JOIN "order" o ON c.customer_id = o.customer_id
WHERE o.order_no IS NULL;""",

        '2_3.sql': """SELECT 
    o.order_no,
    m.full_name AS manager_name,
    c.full_name AS customer_name
FROM "order" o
JOIN customer c ON o.customer_id = c.customer_id
JOIN manager m ON o.manager_id = m.manager_id
WHERE c.city != m.city;""",

        '2_4.sql': """SELECT 
    c.full_name AS customer_name,
    o.order_no
FROM "order" o
JOIN customer c ON o.customer_id = c.customer_id
WHERE o.manager_id IS NULL;""",

        '2_5.sql': """SELECT DISTINCT
    c1.full_name AS customer1,
    c2.full_name AS customer2
FROM customer c1
JOIN customer c2 ON c1.customer_id < c2.customer_id
WHERE c1.city = c2.city 
    AND c1.manager_id = c2.manager_id
    AND c1.manager_id IS NOT NULL;"""
    }

    print("\n4. Подготовка SQL-файлов...")
    for filename, query in queries.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(query)
        print(f"  - {filename} готов")

    print("\n5. Выполнение запросов...")
    queries_files = ['2_1.sql', '2_2.sql', '2_3.sql', '2_4.sql']

    all_success = True
    for sql_file in queries_files:
        if os.path.exists(sql_file):
            print(f"\n{'=' * 60}")
            print(f"Выполнение {sql_file}:")
            print(f"{'=' * 60}")

            with open(sql_file, 'r', encoding='utf-8') as f:
                query_text = f.read()

            print("Запрос:")
            print(query_text[:200] + "..." if len(query_text) > 200 else query_text)

            success = print_query_results(sql_file, cursor, query_text)
            if not success:
                all_success = False

    conn.close()

    print(f"\n{'=' * 60}")
    if all_success:
        print("ВСЕ ЗАПРОСЫ ВЫПОЛНЕНЫ УСПЕШНО!")
    else:
        print("НЕКОТОРЫЕ ЗАПРОСЫ ЗАВЕРШИЛИСЬ С ОШИБКАМИ")
    print(f"{'=' * 60}")