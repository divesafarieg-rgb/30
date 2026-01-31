import sqlite3
import pandas as pd


def find_most_difficult_teacher(db_file='homework.db'):

    print("=" * 70)
    print("ЗАДАНИЕ 1: Преподаватель с самыми сложными заданиями")
    print("=" * 70)
    print("Запрос находит преподавателя, чьи задания получают")
    print("самые низкие средние оценки.")
    print()

    query = """
    SELECT 
        t.teacher_id as id_преподавателя,
        t.full_name as имя_преподавателя,
        ROUND(AVG(ag.grade), 2) as средняя_оценка,
        COUNT(ag.grade_id) as всего_оценок,
        MIN(ag.grade) as минимальная_оценка,
        MAX(ag.grade) as максимальная_оценка
    FROM teachers t
    JOIN assignments a ON t.teacher_id = a.teacher_id
    JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
    GROUP BY t.teacher_id, t.full_name
    ORDER BY средняя_оценка ASC  
    LIMIT 1;  
    """

    try:
        conn = sqlite3.connect(db_file)

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            teacher = df.iloc[0]
            print("📊 РЕЗУЛЬТАТ:")
            print(f"   Преподаватель: {teacher['имя_преподавателя']}")
            print(f"   ID: {teacher['id_преподавателя']}")
            print(f"   Средняя оценка за его задания: {teacher['средняя_оценка']}")
            print(f"   Всего оценок: {teacher['всего_оценок']}")
            print(f"   Диапазон оценок: {teacher['минимальная_оценка']} - {teacher['максимальная_оценка']}")
        else:
            print("⚠️  Данные не найдены!")

        print("\n" + "-" * 60)
        print("📈 ТОП-5 самых сложных преподавателей:")
        print("-" * 60)

        query_top5 = """
        SELECT 
            t.full_name as преподаватель,
            ROUND(AVG(ag.grade), 2) as средняя_оценка,
            COUNT(*) as всего_оценок
        FROM teachers t
        JOIN assignments a ON t.teacher_id = a.teacher_id
        JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
        GROUP BY t.teacher_id
        ORDER BY средняя_оценка
        LIMIT 5;
        """

        df_top5 = pd.read_sql_query(query_top5, conn)
        print(df_top5.to_string(index=False))

        conn.close()
        return df

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    find_most_difficult_teacher()