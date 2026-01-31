import sqlite3
import pandas as pd


def find_students_of_easiest_teacher(db_file='homework.db'):

    print("=" * 70)
    print("ЗАДАНИЕ 3: Ученики преподавателя с самыми простыми заданиями")
    print("=" * 70)
    print("Алгоритм решения (вложенные запросы):")
    print("1. Находим преподавателя с самыми ВЫСОКИМИ средними оценками")
    print("2. Находим все его задания")
    print("3. Находим всех учеников, которые выполняли эти задания")
    print()

    query = """
    SELECT DISTINCT
        s.student_id as id_ученика,
        s.full_name as имя_ученика,
        s.group_id as группа

    FROM students s

    WHERE s.student_id IN (
        SELECT ag.student_id
        FROM assignments_grades ag
        WHERE ag.assignment_id IN (  
            SELECT a.assignment_id  
            FROM assignments a
            WHERE a.teacher_id = (
                SELECT t.teacher_id
                FROM teachers t
                JOIN assignments a ON t.teacher_id = a.teacher_id
                JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
                GROUP BY t.teacher_id
                ORDER BY AVG(ag.grade) DESC
                LIMIT 1
            )
        )
    )

    ORDER BY s.student_id;  
    """

    try:
        conn = sqlite3.connect(db_file)

        print("🔍 Нахожу преподавателя с самыми простыми заданиями...")

        query_teacher = """
        SELECT 
            t.teacher_id,
            t.full_name,
            ROUND(AVG(ag.grade), 2) as avg_grade
        FROM teachers t
        JOIN assignments a ON t.teacher_id = a.teacher_id
        JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
        GROUP BY t.teacher_id
        ORDER BY avg_grade DESC
        LIMIT 1;
        """

        df_teacher = pd.read_sql_query(query_teacher, conn)

        if df_teacher.empty:
            print("⚠️  Преподаватель не найден!")
            conn.close()
            return None

        teacher = df_teacher.iloc[0]
        print(f"\n🎯 Преподаватель с самыми простыми заданиями:")
        print(f"   Имя: {teacher['full_name']}")
        print(f"   ID: {teacher['teacher_id']}")
        print(f"   Средняя оценка за его задания: {teacher['avg_grade']}")

        print("\n👨‍🎓 Ищу учеников этого преподавателя...")

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            print(f"\n✅ Найдено учеников: {len(df)}")
            print("\n📋 Список учеников (первые 20):")
            print("-" * 60)

            df_display = df.head(20)
            for i, (_, row) in enumerate(df_display.iterrows(), 1):
                print(f"{i:3}. {row['имя_ученика']} (Группа: {row['группа']}, ID: {row['id_ученика']})")

            if len(df) > 20:
                print(f"... и еще {len(df) - 20} учеников")

            print("\n" + "=" * 50)
            print("📊 Распределение по группам:")
            print("=" * 50)

            group_stats = df['группа'].value_counts().sort_index()
            for group, count in group_stats.items():
                print(f"Группа {group}: {count} учеников")

        else:
            print("⚠️  Ученики не найдены!")

        conn.close()
        return df

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    find_students_of_easiest_teacher()