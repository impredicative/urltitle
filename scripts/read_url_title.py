"""Read and log the title of a URL."""
import logging

from urltitle import URLTitleReader, config

config.configure_logging()
log = logging.getLogger(f"{config.PACKAGE_NAME}.{__name__}")

URL = "https://google.com"

reader = URLTitleReader()  # pylint: disable=invalid-name
reader.title(URL)
log.info("Testing cache.")
reader.title(URL)  # Should use cache.
