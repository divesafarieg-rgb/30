import logging
import json
from datetime import datetime


class JsonAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Экранируем сообщение с помощью json.dumps
        # Это заменит кавычки, переносы строк и другие спецсимволы на экранированные версии
        safe_msg = json.dumps(msg, ensure_ascii=False)
        return safe_msg, kwargs


# Настройка логгера
def setup_logger():
    # Создаем логгер
    logger = logging.getLogger('json_logger')
    logger.setLevel(logging.DEBUG)

    # Обработчик для файла
    file_handler = logging.FileHandler('skillbox_json_messages.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Кастомный форматтер для JSON
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": record.levelname,
                "message": record.getMessage()  # message уже экранирован адаптером
            }
            return json.dumps(log_entry, ensure_ascii=False)

    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    # Возвращаем адаптированный логгер
    return JsonAdapter(logger, extra=None)


# Создаем глобальный логгер
json_logger = setup_logger()