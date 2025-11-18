import logging
import logging.handlers
import time


def setup_logger_timed():
    logger = logging.getLogger('utils')
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    handler = logging.handlers.TimedRotatingFileHandler(
        filename='utils.log',
        when='H',
        interval=10,
        backupCount=1,
        encoding='utf-8'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger_timed()

    logger.debug("Это DEBUG сообщение - не должно появиться")
    logger.info("Это INFO сообщение")
    logger.warning("Это WARNING сообщение")
    logger.error("Это ERROR сообщение")

    print("Логи записаны в utils.log")
