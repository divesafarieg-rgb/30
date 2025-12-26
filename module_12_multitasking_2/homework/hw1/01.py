import requests
import sqlite3
import time
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool


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
            try:
                list_url = "https://swapi.dev/api/people/"
                list_response = requests.get(list_url, timeout=10)
                if list_response.status_code == 200:
                    all_characters = list_response.json()['results']
                    if character_id <= len(all_characters):
                        char = all_characters[character_id - 1]
                        return {
                            'name': char.get('name', 'Unknown'),
                            'age': char.get('birth_year', 'Unknown'),
                            'gender': char.get('gender', 'Unknown'),
                            'url': char.get('url', url)
                        }
            except:
                pass

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


def process_character(character_id):
    character_data = get_character_data(character_id)
    if character_data:
        save_to_database(character_data)
        print(f"Обработан персонаж {character_id}: {character_data['name']}")
        return True
    else:
        print(f"Не удалось обработать персонажа {character_id}")
        return False


def download_with_process_pool(num_workers=4):
    print(f"\nЗапуск версии с пулом процессов (workers: {num_workers})...")
    start_time = time.time()

    create_database()

    character_ids = list(range(1, 21))

    with Pool(processes=num_workers) as pool:
        results = pool.map(process_character, character_ids)

    successful_downloads = sum(results)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Версия с пулом процессов выполнена за {execution_time:.2f} секунд")
    print(f"Успешно загружено: {successful_downloads} персонажей")

    return execution_time, successful_downloads


def download_with_thread_pool(num_workers=10):
    print(f"\nЗапуск версии с пулом потоков (workers: {num_workers})...")
    start_time = time.time()

    create_database()

    character_ids = list(range(1, 21))

    with ThreadPool(processes=num_workers) as pool:
        results = pool.map(process_character, character_ids)

    successful_downloads = sum(results)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Версия с пулом потоков выполнена за {execution_time:.2f} секунд")
    print(f"Успешно загружено: {successful_downloads} персонажей")

    return execution_time, successful_downloads


def compare_performance():
    print("=" * 60)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ: ПРОЦЕССЫ VS ПОТОКИ")
    print("=" * 60)

    results = {}

    configs = [
        ("Процессы (2 workers)", lambda: download_with_process_pool(2)),
        ("Процессы (4 workers)", lambda: download_with_process_pool(4)),
        ("Процессы (8 workers)", lambda: download_with_process_pool(8)),
        ("Потоки (5 workers)", lambda: download_with_thread_pool(5)),
        ("Потоки (10 workers)", lambda: download_with_thread_pool(10)),
        ("Потоки (20 workers)", lambda: download_with_thread_pool(20)),
    ]

    for name, func in configs:
        conn = sqlite3.connect('star_wars.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM characters')
        conn.commit()
        conn.close()

        print(f"\n{name}:")
        time_taken, success_count = func()
        results[name] = {
            'time': time_taken,
            'success': success_count
        }

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ:")
    print("=" * 60)

    sorted_results = sorted(results.items(), key=lambda x: x[1]['time'])

    for i, (name, data) in enumerate(sorted_results, 1):
        print(f"{i}. {name}: {data['time']:.2f} сек, успешно: {data['success']}")

    best = sorted_results[0]
    worst = sorted_results[-1]

    improvement = ((worst[1]['time'] - best[1]['time']) / worst[1]['time']) * 100
    print(f"\nЛучший результат: {best[0]} ({best[1]['time']:.2f} сек)")
    print(f"Худший результат: {worst[0]} ({worst[1]['time']:.2f} сек)")
    print(f"Ускорение лучшего над худшим: {improvement:.1f}%")


def show_database_content(limit=20):
    conn = sqlite3.connect('star_wars.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM characters')
    total_count = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM characters LIMIT ?', (limit,))
    characters = cursor.fetchall()

    print(f"\nСодержимое базы данных (всего записей: {total_count}):")
    print("-" * 70)
    print(f"{'ID':<4} {'Имя':<20} {'Возраст':<12} {'Пол':<10}")
    print("-" * 70)

    for char in characters:
        print(f"{char[0]:<4} {char[1]:<20} {char[2]:<12} {char[3]:<10}")

    conn.close()


def main():
    print("ЗАГРУЗКА ПЕРСОНАЖЕЙ STAR WARS С ИСПОЛЬЗОВАНИЕМ POOL И THREADPOOL")
    print("=" * 70)

    try:
        print("Проверка подключения к API Star Wars...")
        test_response = requests.get("https://swapi.dev/api/people/1/", timeout=5)

        if test_response.status_code == 200:
            print("✓ Подключение успешно!\n")

            print("Выберите вариант запуска:")
            print("1 - Сравнение производительности (все конфигурации)")
            print("2 - Только пул процессов (4 workers)")
            print("3 - Только пул потоков (10 workers)")
            print("4 - Просмотр содержимого базы данных")

            choice = input("Введите номер варианта (1-4): ").strip()

            if choice == "1":
                compare_performance()
                show_database_content()
            elif choice == "2":
                create_database()
                time_taken, success = download_with_process_pool(4)
                show_database_content()
            elif choice == "3":
                create_database()
                time_taken, success = download_with_thread_pool(10)
                show_database_content()
            elif choice == "4":
                show_database_content()
            else:
                print("Неверный выбор. Запускаю полное сравнение...")
                compare_performance()
                show_database_content()
        else:
            print("✗ Ошибка подключения к API")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        print("Проверьте интернет-соединение и попробуйте снова")


if __name__ == "__main__":
    main()