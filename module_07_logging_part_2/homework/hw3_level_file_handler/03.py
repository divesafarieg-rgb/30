import logging
import os
import glob


def setup_logging():
    logger = logging.getLogger('calculator')
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    current_dir = os.getcwd()
    print(f"Текущая директория: {current_dir}")

    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for level_name in levels:
        filename = f"calc_{level_name.lower()}.log"
        full_path = os.path.join(current_dir, filename)
        print(f"Создаем файл: {full_path}")

        try:
            handler = logging.FileHandler(filename, encoding='utf-8')
            handler.setLevel(getattr(logging, level_name))

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            handler.addFilter(lambda record, lvl=level_name: record.levelname == lvl)

            logger.addHandler(handler)
            print(f"  Обработчик для уровня {level_name} добавлен")

        except Exception as e:
            print(f"  Ошибка при создании обработчика {level_name}: {e}")

    return logger


def check_log_files():
    print("\n--- Проверка файлов логов ---")

    log_patterns = ['calc_*.log', '*.log']

    for pattern in log_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"Найдены файлы по шаблону '{pattern}':")
            for file in files:
                file_size = os.path.getsize(file)
                print(f"  {file} ({file_size} байт)")
        else:
            print(f"Файлы по шаблону '{pattern}' не найдены")

    expected_files = ['calc_debug.log', 'calc_info.log', 'calc_warning.log',
                      'calc_error.log', 'calc_critical.log']

    print("\n--- Проверка ожидаемых файлов ---")
    for file in expected_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} - существует ({size} байт)")
        else:
            print(f"✗ {file} - не существует")


if __name__ == "__main__":
    logger = setup_logging()

    print("\n--- Генерация логов ---")
    test_logs = [
        (logger.debug, "Debug сообщение"),
        (logger.info, "Info сообщение"),
        (logger.warning, "Warning сообщение"),
        (logger.error, "Error сообщение"),
        (logger.critical, "Critical сообщение")
    ]

    for log_func, message in test_logs:
        log_func(message)
        print(f"Записано: {message}")

    for handler in logger.handlers:
        handler.flush()

    check_log_files()
