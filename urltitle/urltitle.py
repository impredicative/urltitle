import logging
import time

import requests

from cachetools.func import ttl_cache

from . import config

log = logging.getLogger(__name__)


class CachedURLTitle:
    def __init__(self,
                 cache_max_size: int = config.DEFAULT_CACHE_MAX_SIZE, cache_ttl: float = config.DEFAULT_CACHE_TTL):
        log.debug('Max cache size is %s and cache TTL is %s seconds.', cache_max_size, cache_ttl)
        self.title = ttl_cache(maxsize=cache_max_size, ttl=cache_ttl)(self.title)   # type: ignore  # Instance level cache

    def title(self, url: str):
        log.debug('Received request for title for URL %s', url)
        for attempt in range(config.MAX_REQUEST_ATTEMPTS):
            try:
                start_time = time.monotonic()
                response = requests.get(url, stream=True, timeout=config.REQUEST_TIMEOUT,
                                        headers={'User-Agent': config.USER_AGENT})
                time_used = time.monotonic() - start_time
                log.debug('Started receiving streaming response in %.2fs.', time_used)
                response.raise_for_status()
            except (requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout) as exception:
                pass
            break
        return url
