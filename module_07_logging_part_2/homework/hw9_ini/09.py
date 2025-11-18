import logging.config

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': 'app.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        'my_module': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_handler'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger('my_module')
logger.info('Тестируем логирование!')
