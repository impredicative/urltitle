import logging
import time

import requests

from cachetools.func import ttl_cache

from . import config
from .util.humanize import humanize_bytes

log = logging.getLogger(__name__)


class CachedURLTitle:
    def __init__(self,
                 cache_max_size: int = config.DEFAULT_CACHE_MAX_SIZE, cache_ttl: float = config.DEFAULT_CACHE_TTL):
        log.debug('Max cache size is %s and cache TTL is %s seconds.', cache_max_size, cache_ttl)
        self.title = ttl_cache(maxsize=cache_max_size, ttl=cache_ttl)(self.title)   # type: ignore  # Instance level cache

    def title(self, url: str):
        # Can raise: requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout
        max_attempts = config.MAX_REQUEST_ATTEMPTS
        request_desc = f'request for title of URL {url}'
        log.debug('Received %s', request_desc)
        for num_attempt in range(1, max_attempts + 1):
            try:
                start_time = time.monotonic()
                with requests.get(url, stream=True, timeout=config.REQUEST_TIMEOUT,
                                  headers={'User-Agent': config.USER_AGENT}) as request:
                    time_used = time.monotonic() - start_time
                    content_type = request.headers.get('Content-Type')
                    content_len = humanize_bytes(request.headers.get('Content-Length'))
                    log.debug('Started receiving streaming response with declared content type "%s" and content '
                              'length %s in %.2fs.', content_type, content_len, time_used)
                    request.raise_for_status()
            except (requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout) as exception:
                exception_desc = f'The exception is: {exception.__class__.__qualname__}: {exception}'
                log.warning('Error in attempt %s getting %s. %s', num_attempt, request_desc, exception_desc)
                if isinstance(exception, requests.HTTPError) and (request.status_code == 400):
                    log.error('Unrecoverable error 400 getting %s. The request will not be reattempted. %s',
                              request_desc, exception_desc)
                    raise
                if num_attempt == max_attempts:
                    log.error('Exhausted all %s attempts for %s', max_attempts, request_desc)
                    raise
            break
        return url
