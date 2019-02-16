from datetime import timedelta
from functools import lru_cache
import logging
from socket import timeout as RareTimeoutError
from statistics import mean
import time
from typing import cast, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import build_opener, HTTPCookieProcessor, Request

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
        log.debug('Cache TTL of title cache is %s.', timedelta(seconds=cache_ttl))
        self._content_amount_guesses = LFUCache(maxsize=cache_max_size)
        self._netloc = lru_cache(maxsize=cache_max_size)(self._netloc)
        self.title = ttl_cache(maxsize=cache_max_size, ttl=cache_ttl)(self.title)  # type: ignore

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
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        if is_webcache:
            netloc = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{netloc}'
        return netloc

    @staticmethod
    def _title_from_partial_content(content: bytes) -> Optional[str]:
        bs = BeautifulSoup(content, features='html.parser', parse_only=SoupStrainer('title'))
        # Note: Technically, the title tag within the head tag is the one that's required.
        title_tag = bs.title
        if not title_tag:
            return None
        title_text = title_tag.text
        title_bytes = title_text.encode(bs.original_encoding)
        if content.endswith(title_bytes):
            return None  # Possibly incomplete title.
        title_text = title_text.strip()  # Useful for https://www.ncbi.nlm.nih.gov/pubmed/12542348
        return title_text

    def _update_content_amount_guess_for_title(self, url: str, content: bytes, title: str) -> None:
        content_len = len(content)
        title = title.encode()

        observation = content.rfind(title)
        padding = config.KiB  # For whitespace, closing title tag, and any minor randomness leading up to the title.
        observation = (observation + len(title) + padding) if (observation != -1) else content_len
        observation = min(observation, content_len + padding)

        netloc = self._netloc(url)
        # This section is not thread safe, but that's okay as these are just estimates.
        old_guess = self._content_amount_guesses.get(netloc)
        if old_guess is None:
            new_guess = min(observation, config.REQUEST_SIZE_MAX)
            self._content_amount_guesses[netloc] = new_guess
            log.info('Set content amount guess for %s to observation %s.', netloc, humanize_bytes(new_guess))
        elif old_guess != observation:
            new_guess = int(mean((old_guess, observation)))  # May need a better technique.
            new_guess = min(new_guess, config.REQUEST_SIZE_MAX)
            self._content_amount_guesses[netloc] = new_guess
            log.info('Updated content amount guess for %s with observation %s from %s to %s.',
                     netloc, humanize_bytes(observation), humanize_bytes(old_guess), humanize_bytes(new_guess))
        else:
            log.debug('Content amount guess for %s of %s is unchanged.', netloc, humanize_bytes(old_guess))

    def title(self, url: str) -> str:  # type: ignore
        # Can raise: URLTitleError
        max_attempts = config.MAX_REQUEST_ATTEMPTS
        request_desc = f'request for title of URL {url}'
        log.debug('Received %s with up to %s attempts.', request_desc, max_attempts)
        overrides = config.NETLOC_OVERRIDES.get(self._netloc(url), {})
        overrides = cast(Dict, overrides)

        if overrides.get('google_webcache') and not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)):
            log.info('URL %s is configured to use Google web cache.', url)
            url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
            return self.title(url)

        user_agent = overrides.get('user_agent', config.USER_AGENT)
        for num_attempt in range(1, max_attempts + 1):
            # Request
            log.debug('Starting attempt %s processing %s', num_attempt, request_desc)
            try:
                opener = build_opener(HTTPCookieProcessor())
                request = Request(url, headers={'User-Agent': user_agent})
                start_time = time.monotonic()
                response = opener.open(request, timeout=config.REQUEST_TIMEOUT)
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

        content_type_header = response.headers['Content-Type']
        content_len_header = response.headers.get('Content-Length')
        content_len_header = cast(Optional[int], content_len_header)
        content_len_header = humanize_bytes(content_len_header)
        log.debug('Received response in attempt %s with declared content type "%s" and content length %s in %.1fs.',
                  num_attempt, content_type_header, content_len_header, time_used)
        if not cast(str, (content_type_header or '')).startswith('text/html'):
            title = ' '.join(f'({part})' for part in (content_type_header, content_len_header) if part is not None)
            # Note: Content-Length is None for https://pastebin.com/raw/KKJNBgjt
            log.info('Returning title "%s" for URL %s', title, url)
            return title

        # Iterate over content
        content = b''
        amt = self._guess_content_amount_for_title(url)
        read = True
        try:
            while read:
                log.debug(f'Reading %s in this iteration with a total of %s read so far.',
                          humanize_bytes(amt), humanize_len(content))
                start_time = time.monotonic()
                content_new = response.read(amt)
                time_used = time.monotonic() - start_time
                read &= bool(content_new)
                content += content_new
                content_len = len(content)
                read &= (content_len <= config.REQUEST_SIZE_MAX)
                log.debug('Read %s in this iteration in %.1fs with a total of %s read so far.',
                          humanize_len(content_new), time_used, humanize_bytes(content_len))
                if not content_new:
                    break
                title = self._title_from_partial_content(content)  # type: ignore
                if not title:
                    target_content_len = min(config.REQUEST_SIZE_MAX, content_len * 2)
                    amt = max(0, target_content_len - content_len)
                    read &= bool(amt)
                    continue
                self._update_content_amount_guess_for_title(url, content, title)
                log.info('Returning title "%s" for URL %s after reading %s.', title, url,
                         humanize_bytes(content_len))
                return title
            if not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)) and (b'distil_r_captcha.html' in content):
                log.info('Content of URL %s has a Distil captcha. A Google cache version will be attempted.', url)
                url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
                return self.title(url)
            raise URLTitleError(f'Unable to find title in HTML content of length {humanize_bytes(content_len)}.')
        finally:
            response.close()
