import logging

from cachetools.func import ttl_cache
import requests

from . import config

log = logging.getLogger(__name__)


class CachedURLTitle:
    def __init__(self,
                 max_cache_size: int = config.DEFAULT_MAX_CACHE_SIZE,cache_ttl: float = config.DEFAULT_CACHE_TTL):
        log.debug('Max cache size is %s and cache TTL is %s seconds.', max_cache_size, cache_ttl)
        self.title = ttl_cache(maxsize=max_cache_size, ttl=cache_ttl)(self.title)   # type: ignore  # Instance level cache

    def title(self, url: str):
        log.debug('Reading URL %s', url)
        return url

