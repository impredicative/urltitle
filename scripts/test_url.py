import logging

from urltitle import config, CachedURLTitle

config.configure_logging()

log = logging.getLogger(config.PACKAGE_NAME + '.' + __name__)

TEST_URL = 'https://www.cnn.com/2019/02/11/health/insect-decline-study-intl/index.html'

log.debug(0)
cached_url_title = CachedURLTitle()
cached_url_title.title(TEST_URL)
log.debug(1)
cached_url_title.title(TEST_URL)
log.debug(2)
