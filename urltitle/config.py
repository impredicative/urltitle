import datetime
import logging.config
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


KiB = 1024
MiB = KiB ** 2

DEFAULT_CACHE_TTL = datetime.timedelta(weeks=1).total_seconds()
DEFAULT_CACHE_MAX_SIZE = 4 * KiB
DEFAULT_REQUEST_SIZE = 4 * KiB
MAX_REQUEST_ATTEMPTS = 3
PACKAGE_NAME = Path(__file__).parent.stem
REQUEST_SIZE_MAX = MiB  # Amazon product links, for example, have the title between 512K and 1M.
REQUEST_TIMEOUT = 30
USER_AGENT = 'Mozilla/5.0'

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
