import logging
import unittest

from urltitle import config, CachedURLTitle

config.configure_logging()

log = logging.getLogger(config.PACKAGE_NAME + '.' + __name__)


TEST_CASES = {
    'https://www.swansonvitamins.com/swanson-premium-vitamin-c-rose-hips-1000-mg-250-caps':
        'Vitamin C with Rose Hips - 1,000 mg - Swanson Health Products',
    'https://docs.python.org/3/library/unittest.html':
        'unittest — Unit testing framework — Python 3.7.2 documentation',
}

url_title = CachedURLTitle()


class TestURLs(unittest.TestCase):
    def test_url_titles(self):
        for url, expected_title in TEST_CASES.items():
            with self.subTest(url=url):
                self.assertEqual(expected_title, url_title.title(url))
