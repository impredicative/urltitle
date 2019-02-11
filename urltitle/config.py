import datetime
import logging.config
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


CACHE_TTL = datetime.timedelta(minutes=58).total_seconds()
DEFAULT_USER_AGENT = 'Mozilla/5.0'
MAX_CACHE_SIZE = 2048
PACKAGE_NAME = Path(__file__).parent.stem
REQUEST_TIMEOUT = 60

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(thread)x-%(threadName)s:%(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        PACKAGE_NAME: {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
