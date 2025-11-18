import logging
import logging.config

class ASCIIFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        return message.isascii()

logging_config = {
    'version': 1,
    'filters': {
        'ascii_filter': {
            '()': ASCIIFilter
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['ascii_filter'],
            'level': 'DEBUG'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger()

logger.debug("Hello World!")
logger.debug("Привет мир!")
logger.debug("Café au lait")
logger.debug("Simple text")
