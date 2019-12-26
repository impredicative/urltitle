"""Read the title of a URL using a variety of user agent strings."""
import logging
import time
from typing import Dict

from urltitle import URLTitleError, URLTitleReader, config

TEST_URL = "https://pubs.acs.org/doi/abs/10.1021/acs.jafc.7b03118"

config.MAX_REQUEST_ATTEMPTS = 1
config.REQUEST_TIMEOUT = 15

config.LOGGING["loggers"] = {
    config.PACKAGE_NAME: {"level": "CRITICAL", "handlers": ["console"], "propagate": False},
    "chardet.charsetprober": {"level": "WARNING", "handlers": ["console"], "propagate": False},
    "": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
}

config.configure_logging()
log = logging.getLogger(__name__)

# pylint: disable=line-too-long
USER_AGENTS = [
    # Basic
    config.USER_AGENT,
    "Mozilla/5.0",
    config.PACKAGE_NAME,
    # Promising
    "Googlebot-News",
    "FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)",
    # https://support.google.com/webmasters/answer/1061943?hl=en
    "APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)",
    "Mediapartners-Google",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G920A) AppleWebKit (KHTML, like Gecko) Chrome Mobile Safari (compatible; AdsBot-Google-Mobile; +http://www.google.com/mobile/adsbot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1 (compatible; AdsBot-Google-Mobile; +http://www.google.com/mobile/adsbot.html)",
    "AdsBot-Google (+http://www.google.com/adsbot.html)",
    "Googlebot-Image/1.0",
    "Googlebot-News",
    "Googlebot-Video/1.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "compatible; Mediapartners-Google/2.1; +http://www.google.com/bot.html",
    "AdsBot-Google-Mobile-Apps",
    "FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)",
    # https://www.bing.com/webmaster/help/which-crawlers-does-bing-use-8c184ec0
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (Windows Phone 8.1; ARM; Trident/7.0; Touch; rv:11.0; IEMobile/11.0; NOKIA; Lumia 530) like Gecko (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "msnbot/2.0b (+http://search.msn.com/msnbot.htm)",
    "msnbot-media/1.1 (+http://search.msn.com/msnbot.htm)",
    "Mozilla/5.0 (compatible; adidxbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; adidxbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (Windows Phone 8.1; ARM; Trident/7.0; Touch; rv:11.0; IEMobile/11.0; NOKIA; Lumia 530) like Gecko (compatible; adidxbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534+ (KHTML, like Gecko) BingPreview/1.0b",
    "Mozilla/5.0 (Windows Phone 8.1; ARM; Trident/7.0; Touch; rv:11.0; IEMobile/11.0; NOKIA; Lumia 530) like Gecko BingPreview/1.0b",
]
# pylint: enable=line-too-long

USER_AGENTS = list(dict.fromkeys(USER_AGENTS))
NETLOC = URLTitleReader().netloc(TEST_URL)
log.info("Netloc for %s is %s.", TEST_URL, NETLOC)

titles: Dict[str, str] = {}
for user_agent in USER_AGENTS:
    log.debug("Trying user agent: %s", user_agent)
    config.NETLOC_OVERRIDES[NETLOC] = {"user_agent": user_agent}
    reader = URLTitleReader()  # Fresh instance avoids cache.
    try:
        title = reader.title(TEST_URL)
    except URLTitleError as exc:
        log.error("Ignoring exception with user agent %s: %s", repr(user_agent), exc)
        continue
    if title not in titles.values():
        titles[user_agent] = title
        log.info("Found title with user agent %s: %s", repr(user_agent), title)
        if len(titles) == 2:
            log.info("Aborting title search because two unique titles have been found: %s", titles)
            break
    time.sleep(1)
else:
    log.info("Found %s unique titles: %s", len(titles), titles)
