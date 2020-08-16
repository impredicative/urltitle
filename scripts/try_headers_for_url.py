"""Read the title of a URL after incrementally adding a header at each read."""
import logging
import time
from typing import Dict

from urltitle import URLTitleError, URLTitleReader, config

TEST_URL = "https://www.osapublishing.org/prj/fulltext.cfm?uri=prj-7-8-823&id=415059"

config.MAX_REQUEST_ATTEMPTS = 1
config.REQUEST_TIMEOUT = 2

config.LOGGING["loggers"] = {
    config.PACKAGE_NAME: {"level": "CRITICAL", "handlers": ["console"], "propagate": False},
    "chardet.charsetprober": {"level": "WARNING", "handlers": ["console"], "propagate": False},
    "": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
}

config.configure_logging()
log = logging.getLogger(__name__)

EXTRA_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip",
    "Referer": "https://google.com/",
    "DNT": 1,
    "Connection": "keep-alive",
    "Cookie": "",
    "Upgrade-Insecure-Requests": 1,
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}
NETLOC = URLTitleReader().netloc(TEST_URL)
log.info("Netloc for %s is %s.", TEST_URL, NETLOC)

titles: Dict[str, str] = {}
config.NETLOC_OVERRIDES[NETLOC] = {"extra_headers": {}}
EXTRA_CONFIG_HEADERS = config.NETLOC_OVERRIDES[NETLOC]["extra_headers"]
for h_key, h_val in EXTRA_HEADERS.items():
    log.debug("Adding header: %s=%s", h_key, h_val)
    EXTRA_CONFIG_HEADERS[h_key] = h_val
    reader = URLTitleReader()  # Fresh instance avoids cache.
    try:
        title = reader.title(TEST_URL)
    except URLTitleError as exc:
        log.error("Ignoring exception after adding header %s=%s: %s", h_key, h_val, exc)
        continue
    if title not in titles.values():
        titles[h_key] = title
        log.info("Found title after adding header %s=%s: %s", h_key, h_val, title)
        # if len(titles) == 3:
        #     log.info('Aborting title search because two unique titles have been found: %s', titles)
        #     break
    time.sleep(1)
log.info("Found %s unique titles: %s", len(titles), titles)
