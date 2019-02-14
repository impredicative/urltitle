import logging

from urltitle import config, CachedURLTitle

config.configure_logging()

log = logging.getLogger(config.PACKAGE_NAME + '.' + __name__)

TEST_URL = 'https://www.google.com/'

cached_url_title = CachedURLTitle()
cached_url_title.title(TEST_URL)
# cached_url_title.title(TEST_URL)
