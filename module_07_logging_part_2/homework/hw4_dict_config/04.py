import logging.config
from config import dict_config


def setup_logging():
    logging.config.dictConfig(dict_config)


def process_data():
    processor_logger = logging.getLogger('data_processor')
    processor_logger.info('Начало обработки данных')

    try:
        data = [1, 2, 3, 4, 5]
        result = sum(data) / len(data)
        processor_logger.debug(f'Результат обработки: {result}')
        processor_logger.info('Обработка данных завершена успешно')
        return result
    except Exception as e:
        processor_logger.error(f'Ошибка при обработке данных: {e}')
        return None


def main():
    setup_logging()

    logger = logging.getLogger('my_app')
    logger.info('Приложение запущено')

    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
    logger.warning('Предупреждение')

    result = process_data()
    if result:
        logger.info(f'Получен результат: {result}')
    else:
        logger.error('Не удалось получить результат обработки')

    try:
        x = 1 / 0
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}', exc_info=True)

    logger.info('Приложение завершает работу')


if __name__ == '__main__':
    main()
