import sqlite3
import pandas as pd


def find_top_students(db_file='homework.db'):

    print("=" * 70)
    print("ЗАДАНИЕ 2: 10 лучших учеников для награждения")
    print("=" * 70)
    print("Критерии отбора:")
    print("1. Высокий средний балл за все задания")
    print("2. Выполнено не менее 3 заданий (для объективности)")
    print("3. Только 10 лучших из-за ограничения картриджа")
    print()

    query = """
    SELECT 
        s.student_id as id_ученика,
        s.full_name as имя_ученика,
        s.group_id as группа,
        ROUND(AVG(ag.grade), 2) as средний_балл,  
        COUNT(ag.grade_id) as выполнено_заданий,
        ROUND(MIN(ag.grade), 1) as худшая_оценка,
        ROUND(MAX(ag.grade), 1) as лучшая_оценка  
    FROM students s
    JOIN assignments_grades ag ON s.student_id = ag.student_id
    GROUP BY s.student_id, s.full_name, s.group_id
    HAVING выполнено_заданий >= 3  
    ORDER BY средний_балл DESC  
    LIMIT 10;  
    """

    try:
        conn = sqlite3.connect(db_file)

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            print("🏆 ТОП-10 ЛУЧШИХ УЧЕНИКОВ:")
            print("-" * 100)
            print(f"{'Место':^6} | {'ID':^5} | {'Имя ученика':^25} | {'Группа':^7} | "
                  f"{'Средний балл':^12} | {'Заданий':^8} | {'Лучшая':^7} | {'Худшая':^7}")
            print("-" * 100)

            for i, (_, row) in enumerate(df.iterrows(), 1):
                print(f"{i:^6} | {row['id_ученика']:^5} | {row['имя_ученика']:^25} | "
                      f"{row['группа']:^7} | {row['средний_балл']:^12} | "
                      f"{row['выполнено_заданий']:^8} | {row['лучшая_оценка']:^7} | "
                      f"{row['худшая_оценка']:^7}")

            print("\n" + "=" * 50)
            print("📊 СТАТИСТИКА:")
            print("=" * 50)
            print(f"Средний балл топ-10: {df['средний_балл'].mean():.2f}")
            print(f"Минимальный средний балл в топе: {df['средний_балл'].min():.2f}")
            print(f"Максимальный средний балл в топе: {df['средний_балл'].max():.2f}")
        else:
            print("⚠️  Данные не найдены!")

        print("\n" + "=" * 50)
        print("📝 Альтернативный вариант (без ограничения по количеству заданий):")
        print("=" * 50)

        query_alt = """
        SELECT 
            s.full_name as ученик,
            ROUND(AVG(ag.grade), 2) as средний_балл,
            COUNT(*) as заданий
        FROM students s
        JOIN assignments_grades ag ON s.student_id = ag.student_id
        GROUP BY s.student_id
        ORDER BY средний_балл DESC
        LIMIT 10;
        """

        df_alt = pd.read_sql_query(query_alt, conn)
        print(df_alt.to_string(index=False))

        conn.close()
        return df

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    find_top_students()