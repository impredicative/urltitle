import logging

from urltitle import config, URLTitleReader

config.configure_logging()

log = logging.getLogger(config.PACKAGE_NAME + '.' + __name__)

TEST_URL = 'https://www.google.com/'

reader = URLTitleReader()
reader.title(TEST_URL)
reader.title(TEST_URL)  # Should use cache.
