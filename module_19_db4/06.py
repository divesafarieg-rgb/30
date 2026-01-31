import sqlite3
import pandas as pd


def analyze_read_study_assignments(db_file='homework.db'):

    print("=" * 70)
    print("ЗАДАНИЕ 6: Средняя оценка за задания 'прочитать' и 'выучить'")
    print("=" * 70)
    print("Анализ заданий, содержащих ключевые слова:")
    print("1. 'прочитать' - задания на чтение материалов")
    print("2. 'выучить' - задания на заучивание информации")
    print()
    print("Используемые операторы:")
    print("- LIKE '%прочитать%' - ищет слово 'прочитать' в любом месте текста")
    print("- OR - логическое ИЛИ для объединения условий")
    print("- IN() - проверка вхождения в список из подзапроса")
    print()

    query = """
    /* Основной запрос: считаем среднюю оценку */
    SELECT 
        ROUND(AVG(ag.grade), 2) as средняя_оценка,
        COUNT(*) as количество_оценок,
        COUNT(DISTINCT ag.student_id) as уникальных_учеников,
        COUNT(DISTINCT ag.assignment_id) as уникальных_заданий  

    FROM assignments_grades ag

    /* WHERE с подзапросом: фильтруем только нужные задания */
    WHERE ag.assignment_id IN (  
        /* Подзапрос: находим ID заданий с нужными ключевыми словами */
        SELECT a.assignment_id  
        FROM assignments a
        WHERE a.assignment_text LIKE '%прочитать%'
           OR a.assignment_text LIKE '%выучить%'
    );
    """

    try:
        conn = sqlite3.connect(db_file)

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            result = df.iloc[0]
            print("📊 ОБЩАЯ СТАТИСТИКА:")
            print("-" * 50)
            print(f"  Средняя оценка: {result['средняя_оценка']}")
            print(f"  Всего оценок: {result['количество_оценок']}")
            print(f"  Уникальных учеников: {result['уникальных_учеников']}")
            print(f"  Уникальных заданий: {result['уникальных_заданий']}")

        print("\n" + "=" * 60)
        print("📝 ПОДРОБНЫЙ АНАЛИЗ ПО ТИПАМ ЗАДАНИЙ:")
        print("=" * 60)

        query_detailed = """
        /* Анализируем отдельно задания с 'прочитать' и 'выучить' */
        SELECT 
            CASE 
                WHEN a.assignment_text LIKE '%прочитать%' AND a.assignment_text LIKE '%выучить%' 
                    THEN 'И прочитать, и выучить'
                WHEN a.assignment_text LIKE '%прочитать%' 
                    THEN 'Только прочитать'
                WHEN a.assignment_text LIKE '%выучить%' 
                    THEN 'Только выучить'
            END as тип_задания,

            COUNT(DISTINCT a.assignment_id) as количество_заданий,  
            ROUND(AVG(ag.grade), 2) as средняя_оценка,
            MIN(ag.grade) as минимальная_оценка,
            MAX(ag.grade) as максимальная_оценка,
            COUNT(*) as всего_оценок

        FROM assignments a
        JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  

        WHERE a.assignment_text LIKE '%прочитать%'
           OR a.assignment_text LIKE '%выучить%'

        GROUP BY тип_задания
        ORDER BY средняя_оценка DESC;
        """

        df_detailed = pd.read_sql_query(query_detailed, conn)
        if not df_detailed.empty:
            print(df_detailed.to_string(index=False))

        print("\n" + "=" * 60)
        print("📋 ПРИМЕРЫ ЗАДАНИЙ:")
        print("=" * 60)

        query_examples = """
        /* Показываем конкретные задания и их средние оценки */
        SELECT 
            a.assignment_text as текст_задания,
            ROUND(AVG(ag.grade), 2) as средняя_оценка,
            COUNT(ag.grade_id) as количество_оценок,
            ROUND(MIN(ag.grade), 1) as минимум,
            ROUND(MAX(ag.grade), 1) as максимум  

        FROM assignments a
        JOIN assignments_grades ag ON a.assignment_id = ag.assignment_id  

        WHERE a.assignment_text LIKE '%прочитать%'
           OR a.assignment_text LIKE '%выучить%'

        GROUP BY a.assignment_id, a.assignment_text

        ORDER BY средняя_оценка DESC
        LIMIT 10;
        """

        df_examples = pd.read_sql_query(query_examples, conn)
        if not df_examples.empty:
            print("Топ-10 заданий 'прочитать/выучить' по средней оценке:")
            print("-" * 100)
            for i, (_, row) in enumerate(df_examples.iterrows(), 1):
                text = row['текст_задания'][:60] + "..." if len(row['текст_задания']) > 60 else row['текст_задания']
                print(f"{i:2}. {text}")
                print(f"    Оценка: {row['средняя_оценка']} (от {row['минимум']} до {row['максимум']}), "
                      f"всего оценок: {row['количество_оценок']}")
                print()

        print("\n" + "=" * 60)
        print("🔄 СРАВНЕНИЕ С ОБЩЕЙ СТАТИСТИКОЙ:")
        print("=" * 60)

        query_comparison = """
        SELECT 
            'Все задания' as категория,
            ROUND(AVG(grade), 2) as средняя_оценка,
            COUNT(*) as количество_оценок
        FROM assignments_grades

        UNION ALL

        SELECT 
            'Задания "прочитать/выучить"' as категория,
            ROUND(AVG(grade), 2) as средняя_оценка,
            COUNT(*) as количество_оценок
        FROM assignments_grades
        WHERE assignment_id IN (  
            SELECT assignment_id  
            FROM assignments
            WHERE assignment_text LIKE '%прочитать%'
               OR assignment_text LIKE '%выучить%'
        );
        """

        df_comparison = pd.read_sql_query(query_comparison, conn)
        print(df_comparison.to_string(index=False))

        if len(df_comparison) == 2:
            all_avg = df_comparison.iloc[0]['средняя_оценка']
            read_learn_avg = df_comparison.iloc[1]['средняя_оценка']
            difference = read_learn_avg - all_avg

            print(f"\n📊 АНАЛИЗ РАЗНИЦЫ:")
            if difference > 0.5:
                print(f"✅ Задания 'прочитать/выучить' имеют среднюю оценку НА {difference:.2f} балла ВЫШЕ среднего")
                print("   Вывод: такие задания выполняются лучше среднего")
            elif difference > 0:
                print(f"📈 Задания 'прочитать/выучить' имеют среднюю оценку НА {difference:.2f} балла выше среднего")
                print("   Вывод: такие задания выполняются немного лучше")
            elif difference < -0.5:
                print(
                    f"⚠️  Задания 'прочитать/выучить' имеют среднюю оценку НА {abs(difference):.2f} балла НИЖЕ среднего")
                print("   Вывод: такие задания вызывают больше сложностей")
            elif difference < 0:
                print(
                    f"📉 Задания 'прочитать/выучить' имеют среднюю оценку НА {abs(difference):.2f} балла ниже среднего")
                print("   Вывод: такие задания выполняются немного хуже")
            else:
                print(f"📊 Средние оценки одинаковые")
                print("   Вывод: тип задания не влияет на результат")

        conn.close()
        return df

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    analyze_read_study_assignments()