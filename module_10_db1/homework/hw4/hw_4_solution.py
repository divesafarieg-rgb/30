import sqlite3


def analyze_incomes_sql_only():
    conn = sqlite3.connect('hw_4_database.db')
    cursor = conn.cursor()

    # 1. Сколько человек с острова N находятся за чертой бедности, то есть получает меньше 5000 гульденов в год
    cursor.execute("SELECT COUNT(*) FROM salaries WHERE salary < 5000")
    poor_count = cursor.fetchone()[0]
    print(f"1. Людей за чертой бедности: {poor_count}")

    # 2. Средняя зарплата по острову N
    cursor.execute("SELECT AVG(salary) FROM salaries")
    avg_salary = cursor.fetchone()[0]
    print(f"2. Средняя зарплата: {avg_salary:.2f} гульденов")

    # 3. Медианная зарплата по острову N
    cursor.execute("""
        SELECT AVG(salary) FROM (
            SELECT salary FROM salaries 
            ORDER BY salary 
            LIMIT 2 - (SELECT COUNT(*) FROM salaries) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM salaries)
        )
    """)
    median_salary = cursor.fetchone()[0]
    print(f"3. Медианная зарплата: {median_salary:.2f} гульденов")

    # 4. Число социального неравенства F по острову N
    cursor.execute("""
        SELECT 
            ROUND(100.0 * top10.total / bottom90.total, 2) as F_coefficient
        FROM 
            (SELECT SUM(salary) as total FROM (
                SELECT salary FROM salaries 
                ORDER BY salary DESC 
                LIMIT (SELECT COUNT(*) * 0.1 FROM salaries)
            )) as top10,
            (SELECT SUM(salary) as total FROM (
                SELECT salary FROM salaries 
                ORDER BY salary ASC 
                LIMIT (SELECT COUNT(*) * 0.9 FROM salaries)
            )) as bottom90
    """)
    f_coefficient = cursor.fetchone()[0]
    print(f"4. Число социального неравенства F: {f_coefficient}%")

    conn.close()


analyze_incomes_sql_only()