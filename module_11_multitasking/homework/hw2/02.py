import requests
import sqlite3
import time
import threading
from concurrent.futures import ThreadPoolExecutor


def create_database():
    conn = sqlite3.connect('star_wars.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age TEXT,
            gender TEXT,
            url TEXT
        )
    ''')

    conn.commit()
    conn.close()


def get_character_data(character_id):
    url = f"https://swapi.dev/api/people/{character_id}/"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()

            name = data.get('name', 'Unknown')
            birth_year = data.get('birth_year', 'Unknown')
            gender = data.get('gender', 'Unknown')

            return {
                'name': name,
                'age': birth_year,
                'gender': gender,
                'url': url
            }
        else:
            print(f"Ошибка при получении персонажа {character_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при запросе персонажа {character_id}: {e}")
        return None


def save_to_database(character_data):
    if character_data is None:
        return

    conn = sqlite3.connect('star_wars.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR IGNORE INTO characters (name, age, gender, url)
        VALUES (?, ?, ?, ?)
    ''', (character_data['name'], character_data['age'],
          character_data['gender'], character_data['url']))

    conn.commit()
    conn.close()


def sequential_download():
    print("Запуск последовательной версии...")
    start_time = time.time()

    create_database()

    successful_downloads = 0
    for i in range(1, 21):
        character_data = get_character_data(i)
        if character_data:
            save_to_database(character_data)
            print(f"Обработан персонаж {i}: {character_data['name']}")
            successful_downloads += 1
        else:
            print(f"Не удалось обработать персонажа {i}")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Последовательная версия выполнена за {execution_time:.2f} секунд")
    print(f"Успешно загружено: {successful_downloads} персонажей")
    return execution_time


def threaded_download():
    print("Запуск версии с потоками...")
    start_time = time.time()

    create_database()

    def process_character(character_id):
        character_data = get_character_data(character_id)
        if character_data:
            save_to_database(character_data)
            print(f"Обработан персонаж {character_id}: {character_data['name']}")
            return True
        else:
            print(f"Не удалось обработать персонажа {character_id}")
            return False

    successful_downloads = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_character, range(1, 21)))
        successful_downloads = sum(results)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Версия с потоками выполнена за {execution_time:.2f} секунд")
    print(f"Успешно загружено: {successful_downloads} персонажей")
    return execution_time


def show_database_content(limit=10):
    conn = sqlite3.connect('star_wars.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM characters')
    total_count = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM characters LIMIT ?', (limit,))
    characters = cursor.fetchall()

    print(f"\nСодержимое базы данных (всего записей: {total_count}):")
    print("-" * 70)
    for char in characters:
        print(f"ID: {char[0]:2} | Имя: {char[1]:15} | Возраст: {char[2]:10} | Пол: {char[3]:10}")

    conn.close()


def clear_database():
    create_database()

    conn = sqlite3.connect('star_wars.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM characters')

    conn.commit()
    conn.close()
    print("База данных очищена")


def compare_performance():
    print("=" * 60)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ЗАГРУЗКИ ПЕРСОНАЖЕЙ STAR WARS")
    print("=" * 60)

    clear_database()

    print("\n1. ПОСЛЕДОВАТЕЛЬНАЯ ЗАГРУЗКА:")
    sequential_time = sequential_download()

    print("\n" + "-" * 60)

    clear_database()

    print("\n2. ПАРАЛЛЕЛЬНАЯ ЗАГРУЗКА С ПОТОКАМИ:")
    threaded_time = threaded_download()

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ:")
    print("=" * 60)
    print(f"Последовательная версия: {sequential_time:.2f} секунд")
    print(f"Версия с потоками: {threaded_time:.2f} секунд")

    if threaded_time < sequential_time:
        improvement = ((sequential_time - threaded_time) / sequential_time) * 100
        print(f"Ускорение: {improvement:.1f}%")
    else:
        slowdown = ((threaded_time - sequential_time) / sequential_time) * 100
        print(f"Замедление: {slowdown:.1f}%")

    print("\n" + "=" * 60)
    show_database_content()


def simple_test():
    print("ПРОСТОЙ ТЕСТ РАБОТОСПОСОБНОСТИ")
    print("=" * 50)

    print("Тестируем загрузку 5 персонажей...")
    start_time = time.time()

    create_database()

    for i in range(1, 6):
        data = get_character_data(i)
        if data:
            save_to_database(data)
            print(f"✓ {data['name']} - {data['age']} - {data['gender']}")
        else:
            print(f"✗ Персонаж {i} не загружен")

    end_time = time.time()
    print(f"\nВремя выполнения: {end_time - start_time:.2f} секунд")

    show_database_content()


def main():
    try:
        print("Проверка подключения к API Star Wars...")
        test_response = requests.get("https://swapi.dev/api/people/1/", timeout=5)
        if test_response.status_code == 200:
            print("✓ Подключение успешно!\n")

            print("Выберите вариант запуска:")
            print("1 - Полное сравнение производительности")
            print("2 - Простой тест работоспособности")

            choice = input("Введите 1 или 2: ").strip()

            if choice == "1":
                compare_performance()
            else:
                simple_test()
        else:
            print("✗ Ошибка подключения к API")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        print("Проверьте интернет-соединение и попробуйте снова")


if __name__ == "__main__":
    main()
