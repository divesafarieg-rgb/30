import sqlite3
import pandas as pd


def analyze_groups(db_file='homework.db'):

    print("=" * 70)
    print("ЗАДАНИЕ 5: Анализ всех групп")
    print("=" * 70)
    print("Анализируемые показатели:")
    print("1. 📊 Всего учеников - общее количество учащихся в группе")
    print("2. ⭐ Средняя оценка - успеваемость группы")
    print("3. ❌ Не сдали работы - ученики с оценкой < 3 или без оценок")
    print("4. ⏰ Просрочили дедлайн - ученики с опоздавшими сдачами")
    print("5. 🔄 Повторные попытки - количество пересдач заданий")
    print()

    query = """
    SELECT 
        g.group_id as группа,

        /* 1. Общее количество учеников в группе */
        COUNT(DISTINCT s.student_id) as всего_учеников,

        /* 2. Средняя оценка по группе */
        ROUND(AVG(ag.grade), 2) as средняя_оценка,

        /* 3. Ученики, которые не сдали работы (оценка < 3 или нет оценок) */
        COUNT(DISTINCT CASE 
            WHEN ag.grade IS NULL OR ag.grade < 3 
            THEN s.student_id 
        END) as не_сдали_работы,

        /* Процент не сдавших от общего числа */
        ROUND(
            COUNT(DISTINCT CASE WHEN ag.grade IS NULL OR ag.grade < 3 THEN s.student_id END) * 100.0 /
            NULLIF(COUNT(DISTINCT s.student_id), 0), 
            1
        ) as процент_не_сдавших,

        /* 4. Ученики, которые просрочили дедлайн хотя бы раз */
        COUNT(DISTINCT CASE 
            WHEN ag.date > a.due_date 
            THEN s.student_id 
        END) as просрочили_дедлайн,

        /* Процент просрочивших */
        ROUND(
            COUNT(DISTINCT CASE WHEN ag.date > a.due_date THEN s.student_id END) * 100.0 /
            NULLIF(COUNT(DISTINCT s.student_id), 0), 
            1
        ) as процент_просрочивших,

        /* 5. Количество повторных попыток (пересдач) */
        (
            SELECT COUNT(*)
            FROM (
                SELECT ag2.student_id, ag2.assignment_id, COUNT(*) as cnt  
                FROM assignments_grades ag2
                JOIN students s2 ON ag2.student_id = s2.student_id
                WHERE s2.group_id = g.group_id
                GROUP BY ag2.student_id, ag2.assignment_id
                HAVING COUNT(*) > 1
            )
        ) as повторные_попытки

    FROM students_groups g

    /* Подключаем учеников группы */
    LEFT JOIN students s ON g.group_id = s.group_id

    /* Подключаем оценки (LEFT JOIN чтобы учесть учеников без оценок) */
    LEFT JOIN assignments_grades ag ON s.student_id = ag.student_id  

    /* Подключаем информацию о заданиях для проверки дедлайнов */
    LEFT JOIN assignments a ON ag.assignment_id = a.assignment_id  

    /* Группируем по группам */
    GROUP BY g.group_id

    /* Сортируем по номеру группы */
    ORDER BY g.group_id;
    """

    try:
        conn = sqlite3.connect(db_file)

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА ГРУПП:")
            print("-" * 120)

            pd.set_option('display.float_format', '{:.2f}'.format)
            print(df.to_string(index=False))

            print("\n" + "=" * 60)
            print("📈 АНАЛИЗ РЕЗУЛЬТАТОВ:")
            print("=" * 60)

            if not df.empty:
                best_groups = df.nlargest(3, 'средняя_оценка')
                print("\n🏆 ТОП-3 группы по успеваемости:")
                for i, (_, row) in enumerate(best_groups.iterrows(), 1):
                    print(f"{i}. Группа {row['группа']}: средняя оценка {row['средняя_оценка']}, "
                          f"не сдали {row['не_сдали_работы']} чел. ({row['процент_не_сдавших']}%)")

            problem_groups = df.nlargest(3, 'процент_не_сдавших')
            if not problem_groups.empty:
                print("\n⚠️  Группы с наибольшим процентом не сдавших:")
                for i, (_, row) in enumerate(problem_groups.iterrows(), 1):
                    print(f"{i}. Группа {row['группа']}: {row['процент_не_сдавших']}% не сдали "
                          f"({row['не_сдали_работы']}/{row['всего_учеников']})")

            disciplined_groups = df[df['просрочили_дедлайн'] == 0]
            if not disciplined_groups.empty:
                print("\n✅ Группы без просрочек дедлайнов:")
                groups = ", ".join(str(g) for g in disciplined_groups['группа'].tolist())
                print(f"  Группы: {groups}")

            print("\n" + "=" * 60)
            print("📋 ОБЩАЯ СТАТИСТИКА ПО ВСЕМ ГРУППАМ:")
            print("=" * 60)
            total_students = df['всего_учеников'].sum()
            total_failed = df['не_сдали_работы'].sum()
            total_late = df['просрочили_дедлайн'].sum()
            total_retries = df['повторные_попытки'].sum()

            print(f"Всего групп: {len(df)}")
            print(f"Всего учеников: {total_students}")
            print(f"Не сдали работы: {total_failed} ({total_failed / total_students * 100:.1f}%)")
            print(f"Просрочили дедлайн: {total_late} ({total_late / total_students * 100:.1f}%)")
            print(f"Повторных попыток: {total_retries}")
            print(f"Средняя оценка по всем группам: {df['средняя_оценка'].mean():.2f}")

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
    analyze_groups()