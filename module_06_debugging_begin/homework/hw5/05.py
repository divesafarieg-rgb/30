import logging
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def measure_me():
    logger.info("Enter measure_me")
    time.sleep(0.1)
    logger.info("Leave measure_me")

for i in range(5):
    measure_me()