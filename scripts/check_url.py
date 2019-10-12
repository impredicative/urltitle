import logging

from urltitle import config, URLTitleReader

config.configure_logging()
log = logging.getLogger(f'{config.PACKAGE_NAME}.{__name__}')

TEST_URL = 'https://google.com'

reader = URLTitleReader()
reader.title(TEST_URL)
log.info('Testing cache.')
reader.title(TEST_URL)  # Should use cache.
