from urltitle import config, URLTitleReader

config.configure_logging()

TEST_URL = 'https://www.google.com/'

reader = URLTitleReader()
reader.title(TEST_URL)
reader.title(TEST_URL)  # Should use cache.
