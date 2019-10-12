import logging

from urltitle import config, URLTitleReader

config.configure_logging()
log = logging.getLogger(f'{config.PACKAGE_NAME}.{__name__}')

TEST_URL = 'https://m.slashdot.org/story/361844'

reader = URLTitleReader()
reader.title(TEST_URL)
log.info('Testing cache.')
reader.title(TEST_URL)  # Should use cache.
