import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler('stderr.txt', encoding='utf-8')
    ],
    force=True
)

logger = logging.getLogger()

logger.info("Это информационное сообщение")
logger.warning("Это предупреждение")
logger.error("Это ошибка")

