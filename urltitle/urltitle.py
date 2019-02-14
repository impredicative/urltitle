from functools import lru_cache
import logging
from socket import timeout as RareTimeoutError
from statistics import mean
import time
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, SoupStrainer
from cachetools.func import LFUCache, ttl_cache

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
        log.debug('Max cache size of each of various caches is %s.', cache_max_size)
        log.debug('Cache TTL of title cache is %s seconds.', cache_ttl)
        self._content_amount_guesses = LFUCache(maxsize=cache_max_size)
        self._netloc = lru_cache(maxsize=cache_max_size)(self._netloc)
        self.title = ttl_cache(maxsize=cache_max_size, ttl=cache_ttl)(self.title)  # type: ignore  # Instance level cache

    def _guess_content_amount_for_title(self, url: str) -> int:
        netloc = self._netloc(url)
        guess = self._content_amount_guesses.get(netloc,  config.DEFAULT_REQUEST_SIZE)
        log.debug('Returning content amount guess for %s of %s.', netloc, humanize_bytes(guess))
        return guess

    @staticmethod
    def _netloc(url: str) -> str:
        is_webcache = url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)
        if is_webcache:
            url = url.replace(config.GOOGLE_WEBCACHE_URL_PREFIX, '', 1)
        netloc = urlparse(url).netloc
        if is_webcache:
            netloc = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{netloc}'
        return netloc

    @staticmethod
    def _title_from_partial_content(content: bytes) -> Optional[str]:
        bs = BeautifulSoup(content, features='html.parser', parse_only=SoupStrainer('title'))
        title_tag = bs.title
        if not title_tag:
            return None
        title_text = title_tag.text
        title_bytes = title_text.encode(bs.original_encoding)
        if content.endswith(title_bytes):
            return None  # Possibly incomplete title.
        title_text = title_text.strip()  # Required for https://www.ncbi.nlm.nih.gov/pubmed/12542348
        return title_text

    def _update_content_amount_guess_for_title(self, url: str, value: int) -> None:
        netloc = self._netloc(url)
        old_guess = self._guess_content_amount_for_title(url)
        if old_guess != value:
            new_guess = int(mean((old_guess, value)))  # May need a better technique, but let's see how well this works.
            new_guess = min(new_guess, config.REQUEST_SIZE_MAX)
            log.debug('Updating content amount guess for %s with observed value %s from %s to %s.',
                      netloc, humanize_bytes(value), humanize_bytes(old_guess), humanize_bytes(new_guess))
            self._content_amount_guesses[netloc] = new_guess
        else:
            log.debug('Content amount guess for %s of %s is unchanged.', netloc, humanize_bytes(old_guess))

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
            except (ValueError, HTTPError, URLError, RareTimeoutError) as exc:
                exception_desc = f'The error is: {exc.__class__.__qualname__}: {exc}'
                log.warning('Error in attempt %s processing %s. %s', num_attempt, request_desc, exception_desc)
                if isinstance(exc, ValueError) or (isinstance(exc, HTTPError) and (exc.code in (400, 401, 404))):
                    msg = f'Unrecoverable error processing {request_desc}. The request will not be reattempted. ' \
                        f'{exception_desc}'
                    raise URLTitleError(msg) from None
                if num_attempt == max_attempts:
                    msg = f'Exhausted all {max_attempts} attempts for {request_desc}. {exception_desc}'
                    raise URLTitleError(msg) from None
                continue
            else:
                break

        content_type = response.headers['Content-Type']
        content_len = humanize_bytes(response.headers.get('Content-Length'))
        log.debug('Received response in attempt %s with declared content type "%s" and content length %s in %.1fs.',
                  num_attempt, content_type, content_len, time_used)
        if not content_type.startswith('text/html'):
            # content_type = content_type.replace('; charset=utf-8', '')
            title = f'({content_type})'
            if content_len is not None:  # Is None for https://pastebin.com/raw/KKJNBgjt
                title += f' ({content_len})'
            log.info('Returning title "%s" for URL %s', title, url)
            return title

        # Iterate over content
        content = b''
        amt = self._guess_content_amount_for_title(url)
        read = True
        while read:
            log.debug(f'Reading %s in this iteration with a total of %s read so far.',
                      humanize_bytes(amt), humanize_len(content))
            start_time = time.monotonic()
            content_new = response.read(amt)  # or b''
            time_used = time.monotonic() - start_time
            read &= bool(content_new)
            content += content_new
            content_len = len(content)
            read &= (content_len <= config.REQUEST_SIZE_MAX)
            log.debug('Read %s in this iteration in %.1fs with a total of %s read so far.',
                      humanize_len(content_new), time_used, humanize_bytes(content_len))
            if not content_new:
                break
            title = self._title_from_partial_content(content)
            if not title:
                target_content_len = min(config.REQUEST_SIZE_MAX, content_len * 2)
                amt = max(0, target_content_len - content_len)
                read &= bool(amt)
                continue
            self._update_content_amount_guess_for_title(url, content_len)
            log.info('Returning title "%s" for URL %s after reading %s.', title, url, humanize_bytes(content_len))
            return title
        if not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)) and (b'distil_r_captcha.html' in content):
            log.info('Content of URL %s has a Distil captcha. A Google cache version will be attempted.', url)
            url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
            return self.title(url)
        raise URLTitleError(f'Unable to find title in HTML content of length {humanize_bytes(content_len)}.')
