import logging
import unittest

from urltitle import config, CachedURLTitle

config.configure_logging()

log = logging.getLogger(config.PACKAGE_NAME + '.' + __name__)


TEST_CASES = {
    'https://www.cnn.com/2019/02/13/media/jeff-bezos-national-enquirer-leaker/index.html':
        "As questions linger around Jeff Bezos' explosive suggestions, identity of tabloid leaker is confirmed - CNN",
    'https://docs.python.org/2/library/unittest.html':
        '25.3. unittest — Unit testing framework — Python 2.7.15 documentation',
    'https://www.kdnuggets.com/2019/02/ai-help-solve-humanity-challenges.html':
        'How AI can help solve some of humanity’s greatest challenges – and why we might fail',
    'https://www.nbcnews.com/politics/donald-trump/trump-installs-state-art-golf-simulator-white-house-n971176':
        'Trump installs state-of-the-art golf simulator in the White House',
    'https://www.swansonvitamins.com/swanson-premium-vitamin-c-rose-hips-1000-mg-250-caps':
        'Vitamin C with Rose Hips - 1,000 mg - Swanson Health Products',
    'https://towardsdatascience.com/introducing-ubers-ludwig-5bd275a73eda':
        'Introducing Uber’s Ludwig – Towards Data Science',
}

url_title = CachedURLTitle()


class TestURLs(unittest.TestCase):
    def test_url_titles(self):
        for url, expected_title in TEST_CASES.items():
            with self.subTest(url=url):
                self.assertEqual(expected_title, url_title.title(url))
