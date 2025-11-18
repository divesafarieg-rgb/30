import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s | %(name)-12s | %(asctime)s | %(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.debug("Это сообщение уровня DEBUG")
    logger.info("Это сообщение уровня INFO")
    logger.warning("Это сообщение уровня WARNING")
    logger.error("Это сообщение уровня ERROR")
