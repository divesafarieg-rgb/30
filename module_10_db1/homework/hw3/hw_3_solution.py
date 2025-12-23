import sqlite3

with sqlite3.connect("hw_3_database.db") as conn:
    cursor = conn.cursor()

    # 1. Сколько записей (строк) хранится в каждой таблице?
    for i in range(1, 4):
        cursor.execute(f"SELECT COUNT(*) FROM table_{i}")
        print(f"table_{i}: {cursor.fetchone()[0]} записей")

    # 2. Сколько в таблице table_1 уникальных записей?
    cursor.execute("SELECT COUNT(DISTINCT value) FROM table_1")
    print(f"Уникальных записей в table_1: {cursor.fetchone()[0]}")

    # 3. Как много записей из таблицы table_1 встречается в table_2?
    cursor.execute("""
        SELECT COUNT(DISTINCT t1.value)
        FROM table_1 t1
        JOIN table_2 t2 ON t1.value = t2.value
    """)
    print(f"Записей из table_1 в table_2: {cursor.fetchone()[0]}")

    # 4. Как много записей из таблицы table_1 встречается и в table_2, и в table_3?
    cursor.execute("""
        SELECT COUNT(DISTINCT t1.value)
        FROM table_1 t1
        JOIN table_2 t2 ON t1.value = t2.value
        JOIN table_3 t3 ON t1.value = t3.value
    """)
    print(f"Записей из table_1 в table_2 и table_3: {cursor.fetchone()[0]}")