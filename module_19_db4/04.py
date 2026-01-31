import sqlite3
import pandas as pd


def analyze_late_assignments(db_file='homework.db'):

    print("=" * 70)
    print("ЗАДАНИЕ 4: Статистика просроченных заданий по группам")
    print("=" * 70)
    print("Что считается просрочкой:")
    print("- Дата сдачи задания (ag.date) позже дедлайна (a.due_date)")
    print("- Формула: ag.date > a.due_date")
    print("\nИспользуются вложенные запросы для каждой агрегатной функции")
    print()

    query = """
    SELECT 
        g.group_id as группа,

        /* Среднее количество просрочек на ученика в группе */
        (
            SELECT COALESCE(AVG(late_count), 0)
            FROM (
                /* Подсчет просрочек для каждого ученика группы */
                SELECT COUNT(*) as late_count
                FROM assignments a
                JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
                JOIN students s ON ag.student_id = s.student_id
                WHERE s.group_id = g.group_id  /* Текущая группа */
                  AND ag.date > a.due_date     /* Просроченные сдачи */
                GROUP BY ag.student_id
            )
        ) as среднее_просрочек,

        /* Максимальное количество просрочек в группе */
        (
            SELECT COALESCE(MAX(late_count), 0)
            FROM (
                SELECT COUNT(*) as late_count
                FROM assignments a
                JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
                JOIN students s ON ag.student_id = s.student_id
                WHERE s.group_id = g.group_id
                  AND ag.date > a.due_date
                GROUP BY ag.student_id
            )
        ) as максимум_просрочек,

        /* Минимальное количество просрочек в группе */
        (
            SELECT COALESCE(MIN(late_count), 0)
            FROM (
                SELECT COUNT(*) as late_count
                FROM assignments a
                JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
                JOIN students s ON ag.student_id = s.student_id
                WHERE s.group_id = g.group_id
                  AND ag.date > a.due_date
                GROUP BY ag.student_id
            )
        ) as минимум_просрочек,

        /* Общее количество просрочек в группе */
        (
            SELECT COUNT(*)
            FROM assignments a
            JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
            JOIN students s ON ag.student_id = s.student_id
            WHERE s.group_id = g.group_id
              AND ag.date > a.due_date
        ) as всего_просрочек,

        /* Количество учеников с просрочками в группе */
        (
            SELECT COUNT(DISTINCT ag.student_id)  
            FROM assignments a
            JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  
            JOIN students s ON ag.student_id = s.student_id
            WHERE s.group_id = g.group_id
              AND ag.date > a.due_date
        ) as учеников_с_просрочками

    FROM students_groups g
    ORDER BY группа;
    """

    try:
        conn = sqlite3.connect(db_file)

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            print("📊 СТАТИСТИКА ПРОСРОЧЕННЫХ ЗАДАНИЙ:")
            print("-" * 120)
            print(df.to_string(index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x, float) else str(x)))

            print("\n" + "=" * 60)
            print("📈 АНАЛИЗ РЕЗУЛЬТАТОВ:")
            print("=" * 60)

            if df['всего_просрочек'].sum() > 0:
                max_group = df.loc[df['всего_просрочек'].idxmax()]
                print(f"👎 Группа с наибольшим количеством просрочек: #{max_group['группа']}")
                print(f"   Всего просрочек: {max_group['всего_просрочек']}")
                print(f"   В среднем на ученика: {max_group['среднее_просрочек']:.2f}")
                print(f"   Максимум у одного ученика: {max_group['максимум_просрочек']}")

                non_zero = df[df['всего_просрочек'] > 0]
                if not non_zero.empty:
                    min_group = non_zero.loc[non_zero['всего_просрочек'].idxmin()]
                    print(f"\n👍 Группа с наименьшим количеством просрочек: #{min_group['группа']}")
                    print(f"   Всего просрочек: {min_group['всего_просрочек']}")
                    print(f"   В среднем на ученика: {min_group['среднее_просрочек']:.2f}")

                zero_groups = df[df['всего_просрочек'] == 0]
                if not zero_groups.empty:
                    print(f"\n✅ Группы без просрочек: {', '.join(map(str, zero_groups['группа'].tolist()))}")

            print("\n" + "=" * 60)
            print("📋 ОБЩАЯ СТАТИСТИКА:")
            print("=" * 60)
            print(f"Всего групп: {len(df)}")
            print(f"Всего просроченных заданий: {df['всего_просрочек'].sum()}")
            print(f"Среднее количество просрочек на группу: {df['всего_просрочек'].mean():.2f}")
            print(f"Групп без просрочек: {len(df[df['всего_просрочек'] == 0])}")

        else:
            print("⚠️  Данные не найдены!")

        conn.close()
        return df

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    analyze_late_assignments()