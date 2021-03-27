"""Package configuration."""
import datetime
import logging.config
from pathlib import Path
from typing import Any, Dict

from .overrides import NETLOC_OVERRIDES


def configure_logging() -> None:
    """Configure logging."""
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug("Logging is configured.")


KiB = 1024
MiB = KiB ** 2

DEFAULT_CACHE_TTL = datetime.timedelta(weeks=1).total_seconds()
DEFAULT_CACHE_MAX_SIZE = 4 * KiB
DEFAULT_REQUEST_SIZE = 16 * KiB  # Note: 8 KiB causes more undesirable matches of og:title over head.title.
GOOGLE_WEBCACHE_URL_PREFIX = "https://webcache.googleusercontent.com/search?q=cache:"
CONTENT_TYPE_PREFIXES: Dict[str, Any] = {
    "html": ("text/html", "*/*"),  # Nature.com EPDFs are HTML but use */*
    "ipynb": "text/plain",
    "pdf": "application/pdf",
}  # Values must be lowercase.
MAX_REQUEST_ATTEMPTS = 3
MAX_REQUEST_SIZES: Dict[str, int] = {"html": MiB, "ipynb": 8 * MiB, "pdf": 8 * MiB}  # Title observed toward the bottom.
#   Note: Amazon product links, for example, have the title between 512K and 1M in the HTML content.
PACKAGE_NAME = Path(__file__).parent.parent.stem
REQUEST_TIMEOUT = 15
STRAINERS: Dict[str, Dict[str, Any]] = {
    "title": {"name": "title", "attr": "text"},
    "og:title": {"name": "meta", "kwargs": {"property": "og:title"}},
    "twitter:title": {"name": "meta", "kwargs": {"attrs": {"name": "twitter:title"}}},
}
UNRECOVERABLE_HTTP_CODES = 400, 401, 404
URL_SCHEME_GUESSES = "https", "http"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0"

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    "version": 1,
    "formatters": {"detailed": {"format": "%(asctime)s %(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "detailed", "stream": "ext://sys.stdout"}},
    "loggers": {"": {"level": "WARNING", "handlers": ["console"], "propagate": False}, PACKAGE_NAME: {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
}
