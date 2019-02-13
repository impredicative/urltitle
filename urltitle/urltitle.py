import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cachetools.func import ttl_cache

from . import config
from .util.humanize import humanize_bytes, humanize_len

log = logging.getLogger(__name__)


class URLTitleError(Exception):
    def __init__(self, msg: str):
        log.error(msg)
        super().__init__(msg)


class CachedURLTitle:
    def __init__(self,
                 cache_max_size: int = config.DEFAULT_CACHE_MAX_SIZE, cache_ttl: float = config.DEFAULT_CACHE_TTL):
        log.debug('Max cache size is %s and cache TTL is %s seconds.', cache_max_size, cache_ttl)
        self.title = ttl_cache(maxsize=cache_max_size, ttl=cache_ttl)(self.title)   # type: ignore  # Instance level cache

    @staticmethod
    def _title_from_partial_content(content: bytes) -> str:
        return 'random page title'

    def title(self, url: str) -> str:
        # Can raise: URLTitleError
        max_attempts = config.MAX_REQUEST_ATTEMPTS
        request_desc = f'request for title of URL {url}'
        log.debug('Received %s with up to %s attempts.', request_desc, max_attempts)
        for num_attempt in range(1, max_attempts + 1):
            # Request
            log.debug('Starting attempt %s processing %s', num_attempt, request_desc)
            try:
                start_time = time.monotonic()
                request = Request(url, headers={'User-Agent': config.USER_AGENT})
                response = urlopen(request, timeout=config.REQUEST_TIMEOUT)
                time_used = time.monotonic() - start_time
            except (ValueError, HTTPError, URLError) as exc:
                exception_desc = f'The prior exception is: {exc.__class__.__qualname__}: {exc}'
                log.warning('Error in attempt %s processing %s. %s', num_attempt, request_desc, exception_desc)
                if isinstance(exc, ValueError) or (isinstance(exc, HTTPError) and (exc.code in (400, 401, 404))):
                    msg = f'Unrecoverable error processing {request_desc}. The request will not be reattempted. ' \
                        f'{exception_desc}'
                    raise URLTitleError(msg)
                if num_attempt == max_attempts:
                    raise URLTitleError(f'Exhausted all {max_attempts} attempts for {request_desc}')
                continue
            else:
                break

        content_type = response.headers['Content-Type']
        content_len = humanize_bytes(response.headers.get('Content-Length'))
        log.debug('Started receiving response in attempt %s with declared content type "%s" and '
                  'content length %s in %.1fs.', num_attempt, content_type, content_len, time_used)
        if not content_type.startswith('text/html'):
            content_type = content_type.replace('; charset=utf-8', '')
            title = f'{content_type} ({content_len})'
            log.info('Returning title "%s" for URL %s', title, url)
            return title

        # Iterate over content
        content = b''
        amt = config.DEFAULT_REQUEST_SIZE
        read = True
        while read:
            log.debug(f'Reading %s in this iteration with a total of %s read so far.',
                      humanize_bytes(amt), humanize_len(content))
            content_new = response.read(amt) or b''
            read &= bool(content_new)
            content += content_new
            read &= (len(content) <= config.REQUEST_SIZE_MAX)
            log.debug('Read %s in this iteration with a total of %s read so far.',
                      humanize_len(content_new), humanize_len(content))
            title = self._title_from_partial_content(content)
            if not title:
                amt += amt
                continue
            log.info('Returning title "%s" for URL %s after reading %s.', title, url, humanize_len(content))
            return title  # TODO: Determine if a partial title has a risk of being returned.
        raise URLTitleError(f'Unable to find title in HTML content of length {humanize_len(content)}.')
