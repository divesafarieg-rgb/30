import os


def get_summary_rss(file_path):
    total_bytes = 0
    process_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()[1:]

            for line in lines:
                columns = line.strip().split('","')
                if len(columns) >= 5:
                    mem_str = columns[4].replace('"', '').replace(' K', '').replace(',', '')
                    if mem_str.isdigit():
                        total_bytes += int(mem_str) * 1024
                        process_count += 1

        print(f"Обработано процессов: {process_count}")

    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
        print(f"Текущая директория: {os.getcwd()}")
        print("Создаю тестовый файл...")
        create_test_file()
        return get_summary_rss(file_path)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return "0 Б"

    return convert_bytes(total_bytes)


def convert_bytes(bytes_count):

    units = [
        ('Гб', 1024 ** 3),
        ('Мб', 1024 ** 2),
        ('Кб', 1024),
        ('Б', 1)
    ]

    for unit_name, unit_size in units:
        if bytes_count >= unit_size:
            value = bytes_count / unit_size
            if value == int(value):
                return f"{int(value)} {unit_name}"
            else:
                return f"{value:.1f} {unit_name}"

    return f"{bytes_count} Б"


def create_test_file():
    test_data = '''"Image Name","PID","Session Name","Session#","Mem Usage"
"System","4","Services","0","12,345 K"
"Registry","128","Services","0","45,678 K"
"smss.exe","456","Console","1","1,234 K"
"csrss.exe","784","Console","1","5,678 K"
"winlogon.exe","892","Console","1","8,901 K"
"explorer.exe","1234","Console","1","67,890 K"
"python.exe","5678","Console","1","15,432 K"'''

    with open("output_file.txt", "w", encoding="utf-8") as f:
        f.write(test_data)

    print("Тестовый файл создан!")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "output_file.txt")

    print("Анализ использования памяти процессами...")
    print(f"Ищем файл: {file_path}")

    result = get_summary_rss(file_path)
    print(f"Суммарный объем памяти: {result}")