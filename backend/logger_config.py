import logging

from config import Config

debug_level = logging.DEBUG if Config.DEBUG else logging.INFO

LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            # 'filename': 'app_2.log',
            'filename': Config.LOG_FILE_PATH,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': debug_level,
            'stream': 'ext://sys.stdout',
        }
    },
    'formatters': {
        'standard': {
            'style': '{',
            'format': '{asctime} [{levelname:^8}] {name}: {message}',
            # 'format': '{asctime}.{msecs:03.0f} [{levelname:^8}] {module} {name}: {message}',
            # 'datefmt': '%Y-%m-%d %H:%M:%S',
            # 'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['file', 'console'],
            'level': debug_level,
        },
    }
}
