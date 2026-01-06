import sqlite3
import csv
import os


def fix_double_encoding(text: str) -> str:
    try:
        if 'пї' in text or 'їЅ' in text:
            fixed = text.encode('cp1251', errors='ignore').decode('utf-8', errors='ignore')
            return fixed
    except:
        pass
    return text


def delete_wrong_fees(cursor: sqlite3.Cursor, wrong_fees_file: str) -> None:
    try:
        with open(wrong_fees_file, 'r', encoding='utf-8') as file:
            content = file.read()

            if 'пї' in content or '�' in content:
                print("Обнаружено двойное кодирование, пытаемся исправить...")
                lines = content.splitlines()
                fixed_lines = []

                for line in lines:
                    fixed_line = fix_double_encoding(line)
                    fixed_lines.append(fixed_line)

                reader = csv.reader(fixed_lines)
                header = next(reader, None)

                if header:
                    print(f"Заголовок после исправления: {header}")

                deleted_count = 0
                for row in reader:
                    if len(row) >= 2:
                        car_number = row[0].strip()
                        timestamp = row[1].strip()

                        cursor.execute(
                            "DELETE FROM table_fees WHERE timestamp = ? AND car_number = ?",
                            (timestamp, car_number)
                        )

                        if cursor.rowcount > 0:
                            deleted_count += cursor.rowcount

                print(f"Удалено записей (после исправления кодировки): {deleted_count}")
                return
            else:
                file.seek(0)
                reader = csv.reader(file)
                next(reader)

                deleted_count = 0
                for row in reader:
                    if len(row) >= 2:
                        car_number = row[0].strip()
                        timestamp = row[1].strip()

                        cursor.execute(
                            "DELETE FROM table_fees WHERE timestamp = ? AND car_number = ?",
                            (timestamp, car_number)
                        )

                        if cursor.rowcount > 0:
                            deleted_count += cursor.rowcount

                print(f"Удалено записей: {deleted_count}")
                return

    except UnicodeDecodeError:
        pass

    try:
        with open(wrong_fees_file, 'r', encoding='cp1251') as file:
            reader = csv.reader(file)
            next(reader)

            deleted_count = 0
            for row in reader:
                if len(row) >= 2:
                    car_number = row[0].strip()
                    timestamp = row[1].strip()

                    cursor.execute(
                        "DELETE FROM table_fees WHERE timestamp = ? AND car_number = ?",
                        (timestamp, car_number)
                    )

                    if cursor.rowcount > 0:
                        deleted_count += cursor.rowcount

            print(f"Удалено записей (cp1251): {deleted_count}")
            return

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")


def delete_wrong_fees_simple(cursor: sqlite3.Cursor, wrong_fees_file: str) -> None:
    try:
        with open(wrong_fees_file, 'rb') as f:
            raw_data = f.read()

        try:
            content = raw_data.decode('utf-8')
        except UnicodeDecodeError:
            content = raw_data.decode('cp1251')

        lines = content.splitlines()

        if any('пї' in line or '�' in line for line in lines):
            print("Исправляем двойное кодирование...")
            fixed_lines = []
            for line in lines:
                try:
                    fixed = line.encode('cp1251').decode('utf-8')
                    fixed_lines.append(fixed)
                except:
                    fixed_lines.append(line)
            lines = fixed_lines

        reader = csv.reader(lines)
        next(reader)

        for row in reader:
            if len(row) >= 2:
                car_number = row[0].strip()
                timestamp = row[1].strip()

                cursor.execute(
                    "DELETE FROM table_fees WHERE timestamp = ? AND car_number = ?",
                    (timestamp, car_number)
                )

    except Exception as e:
        print(f"Ошибка: {e}")


def delete_wrong_fees_for_your_file(cursor: sqlite3.Cursor, wrong_fees_file: str) -> None:
    with open(wrong_fees_file, 'rb') as f:
        raw_data = f.read()


    try:
        content_cp1251 = raw_data.decode('cp1251')

        bytes_cp1251 = content_cp1251.encode('cp1251')

        content_utf8 = bytes_cp1251.decode('utf-8', errors='ignore')

        print("Первые 200 символов после исправления кодировки:")
        print(content_utf8[:200])

        lines = content_utf8.splitlines()
        reader = csv.reader(lines)
        header = next(reader, None)

        if header:
            print(f"Заголовок: {header}")

        deleted_count = 0
        for row in reader:
            if len(row) >= 2:
                car_number = row[0].strip()
                timestamp = row[1].strip()

                print(f"Обработка: {car_number}, {timestamp}")

                cursor.execute(
                    "DELETE FROM table_fees WHERE timestamp = ? AND car_number = ?",
                    (timestamp, car_number)
                )

                if cursor.rowcount > 0:
                    deleted_count += cursor.rowcount
                    print(f"✓ Удалена запись: {car_number}")

        print(f"\nВсего удалено записей: {deleted_count}")

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

        with open(wrong_fees_file, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 2:
                    car_number = row[0].strip()
                    timestamp = row[1].strip()

                    cursor.execute(
                        "DELETE FROM table_fees WHERE timestamp = ? AND car_number = ?",
                        (timestamp, car_number)
                    )


def test_fix():
    test_string = "пїЅ095пїЅпїЅ778"
    print(f"Исходная строка: {test_string}")

    try:
        fixed = test_string.encode('cp1251').decode('utf-8')
        print(f"Исправленная строка: {fixed}")
    except Exception as e:
        print(f"Ошибка: {e}")

    print(f"\nБайты исходной строки (hex): {test_string.encode('utf-8').hex()}")

    for char in test_string:
        print(f"'{char}' - код: {ord(char):04x}")


if __name__ == "__main__":
    test_fix()

    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE table_fees (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            car_number TEXT,
            amount INTEGER
        )
    ''')

    cursor.execute(
        "INSERT INTO table_fees (timestamp, car_number, amount) VALUES (?, ?, ?)",
        ('2021-12-23T11:18:41', 'х049хм11', 400)
    )
    conn.commit()

    print("\n" + "=" * 60)
    print("Тестирование функции удаления...")
    print("=" * 60)

    if os.path.exists('wrong_fees.csv'):
        delete_wrong_fees_for_your_file(cursor, 'wrong_fees.csv')
        conn.commit()
    else:
        print("Файл wrong_fees.csv не найден!")

    cursor.execute("SELECT * FROM table_fees")
    rows = cursor.fetchall()
    print(f"\nОсталось записей: {len(rows)}")

    conn.close()