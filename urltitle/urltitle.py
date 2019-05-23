from datetime import timedelta
from functools import lru_cache
from http.client import RemoteDisconnected
import logging
from re import sub
from socket import timeout as SocketTimeoutError
import ssl
# noinspection PyUnresolvedReferences
from ssl import SSLCertVerificationError
from statistics import mean
import time
from typing import cast, Dict, Optional, Tuple, Union
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, Request

from bs4 import BeautifulSoup, SoupStrainer
from cachetools.func import LFUCache, ttl_cache

from . import config
from .util.humanize import humanize_bytes, humanize_len
from .util.math import ceil_to_kib
from .util.pikepdf import get_pdf_title
from .util.urllib import CustomHTTPRedirectHandler

log = logging.getLogger(__name__)


class URLTitleError(Exception):
    def __init__(self, msg: str):
        log.error(msg)
        super().__init__(msg)


class URLTitleReader:
    def __init__(self, *,
                 title_cache_max_size: int = config.DEFAULT_CACHE_MAX_SIZE,
                 title_cache_ttl: float = config.DEFAULT_CACHE_TTL,
                 verify_ssl: bool = True):
        log.debug('Cache parameters: config.DEFAULT_CACHE_MAX_SIZE=%s, title_cache_max_size=%s, title_cache_ttl=%s',
                  config.DEFAULT_CACHE_MAX_SIZE, title_cache_max_size, timedelta(seconds=title_cache_ttl))

        self._content_amount_guesses = LFUCache(maxsize=config.DEFAULT_CACHE_TTL)  # Don't use title_cache_max_size.
        self.netloc = lru_cache(maxsize=title_cache_max_size)(self.netloc)  # type: ignore
        self.title = ttl_cache(maxsize=title_cache_max_size, ttl=title_cache_ttl)(self.title)  # type: ignore

        if verify_ssl:
            self._ssl_context = ssl.create_default_context()
            assert self._ssl_context.verify_mode == ssl.CERT_REQUIRED
            assert self._ssl_context.check_hostname
        else:
            self._ssl_context = ssl.SSLContext()
            assert self._ssl_context.verify_mode == ssl.CERT_NONE
            assert not self._ssl_context.check_hostname
            log.warning('SSL verification is disabled for all requests made using this instance of %s.',
                        self.__class__.__qualname__)

    def _guess_html_content_amount_for_title(self, url: str) -> int:
        netloc = self.netloc(url)
        guess = self._content_amount_guesses.get(netloc,  config.DEFAULT_REQUEST_SIZE)
        log.debug('Returning HTML content amount guess for %s of %s.', netloc, humanize_bytes(guess))
        return guess

    def _title(self, url: str) -> str:
        # Can raise: URLTitleError
        max_attempts = config.MAX_REQUEST_ATTEMPTS
        url = url.strip()
        request_desc = f'request for title of URL {url}'
        log.debug('Received %s with up to %s attempts.', request_desc, max_attempts)
        netloc = self.netloc(url)
        overrides = config.NETLOC_OVERRIDES.get(netloc, {})
        overrides = cast(Dict, overrides)

        # Add scheme if missing
        if urlparse(url).scheme == '':
            for scheme_guess in config.URL_SCHEME_GUESSES:
                log.info('The scheme %s will be attempted for URL %s', scheme_guess, url)
                fixed_url = f'{scheme_guess}://{url}'
                try:
                    return self.title(fixed_url)
                except URLTitleError as exc:
                    log.warning('The scheme %s failed for URL %s. %s', scheme_guess, url, exc)
            url_scheme_guesses_str = ', '.join(config.URL_SCHEME_GUESSES)
            msg = f'Exhausted all scheme guesses ({url_scheme_guesses_str}) for URL {url} with a missing scheme.'
            raise URLTitleError(msg)

        # Substitute path as configured
        for pattern, replacement in overrides.get('url_subs', []):
            original_url = url
            url = sub(pattern, replacement, url)
            if original_url != url:
                log.info('Substituted URL %s with %s', original_url, url)
                return self.title(url)

        # Percent-encode Unicode to ASCII, preventing UnicodeEncodeError
        if not url.isascii():
            original_url = url
            url = quote(url, safe=':/')  # Approximation.
            if original_url != url:
                log.info('ASCII encoded URL %s as %s', original_url, url)
                return self.title(url)

        # Use Google web cache as configured
        if overrides.get('google_webcache') and not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)):
            log.info('%s is configured to use Google web cache.', netloc)
            url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
            return self.title(url)

        # Set user agent as configured
        user_agent = overrides.get('user_agent', config.USER_AGENT)
        if user_agent != config.USER_AGENT:
            log.info('Using custom user agent for %s: %s', netloc, user_agent)

        # Read headers
        for num_attempt in range(1, max_attempts + 1):
            # Request
            log.debug('Starting attempt %s processing %s', num_attempt, request_desc)
            try:
                opener = build_opener(
                    CustomHTTPRedirectHandler(),  # Required for annemergmed.com
                    HTTPCookieProcessor(),  # Required for cell.com, tandfonline.com, etc.
                    HTTPSHandler(context=self._ssl_context),  # Required for https://verizon.net, etc.
                )
                request = Request(url, headers={'User-Agent': user_agent})
                start_time = time.monotonic()
                response = opener.open(request, timeout=config.REQUEST_TIMEOUT)
                time_used = time.monotonic() - start_time
            except (ValueError, HTTPError, URLError, SocketTimeoutError, RemoteDisconnected) as exc:
                exception_desc = f'The error is: {exc.__class__.__qualname__}: {exc}'
                log.warning('Error in attempt %s processing %s. %s', num_attempt, request_desc, exception_desc)
                if isinstance(exc, ValueError) or \
                        (isinstance(exc, URLError) and isinstance(exc.reason, SSLCertVerificationError)) or \
                        (isinstance(exc, HTTPError) and (exc.code in config.UNRECOVERABLE_HTTP_CODES)):
                    msg = f'Unrecoverable error processing {request_desc}. The request will not be reattempted. ' \
                        f'{exception_desc}'
                    raise URLTitleError(msg) from None
                if num_attempt == max_attempts:
                    msg = f'Exhausted all {max_attempts} attempts for {request_desc}. {exception_desc}'
                    raise URLTitleError(msg) from None
                continue
            else:
                break

        # Log headers
        content_type_header = response.headers.get('Content-Type')
        content_type_header = cast(Optional[str], content_type_header)
        content_type_header_str_cf = content_type_header.casefold() if content_type_header is not None else ''
        content_len_header = response.headers.get('Content-Length')
        content_len_header = cast(Union[int, str, None], content_len_header)
        content_len_header = int(content_len_header) if content_len_header is not None else None
        content_len_humanized = humanize_bytes(content_len_header)
        log.debug('Received response in attempt %s with declared content type "%s" and content length %s in %.1fs.',
                  num_attempt, content_type_header, content_len_humanized, time_used)

        # Return title from HTML
        if content_type_header_str_cf.startswith(cast(Tuple[str], config.CONTENT_TYPE_PREFIXES['html'])):
            # Iterate over content
            content = b''
            amt = self._guess_html_content_amount_for_title(url)
            read = True
            max_request_size = config.MAX_REQUEST_SIZES['html']
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
                    read &= (content_len <= max_request_size)
                    log.debug('Read %s in this iteration in %.1fs with a total of %s read so far.',
                              humanize_len(content_new), time_used, humanize_bytes(content_len))
                    if not content_new:
                        break
                    title = self._title_from_partial_html_content(content)
                    if not title:
                        target_content_len = min(max_request_size, content_len * 2)
                        amt = max(0, target_content_len - content_len)
                        read &= bool(amt)
                        continue
                    self._update_html_content_amount_guess_for_title(url, content, title)
                    log.info('Returning HTML title "%s" for URL %s after reading %s.', title, url,
                             humanize_bytes(content_len))
                    return title
            finally:
                response.close()
            # Handle Distil captcha using Google web cache
            if not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)) and (b'distil_r_captcha.html' in content):
                log.info('Content of URL %s has a Distil captcha. A Google cache version will be attempted.', url)
                url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
                return self.title(url)
            log.warning('Unable to find title in HTML content of length %s for URL %s', humanize_bytes(content_len),
                        url)

        # Return title from PDF
        elif content_type_header_str_cf.startswith(cast(str, config.CONTENT_TYPE_PREFIXES['pdf'])):
            max_request_size = config.MAX_REQUEST_SIZES['pdf']
            if (content_len_header or 0) <= config.MAX_REQUEST_SIZES['pdf']:
                content = response.read(max_request_size)
                if len(content) < max_request_size:  # Very likely an incomplete PDF if both sizes are equal.
                    title = get_pdf_title(content)
                    if title:
                        log.info('Returning PDF title "%s" for URL %s.', title, url)
                        return title
                    else:
                        log.debug('Unable to find title in PDF content for URL %s', url)  # Quite common.
                else:
                    log.debug('Undeclared and unknown content length of PDF for URL %s likely exceeds the configured '
                              'max of %s for reading it fully.',
                              url, humanize_bytes(max_request_size))
            else:
                log.debug('Declared content length %s of PDF for URL %s exceeds the configured max of %s for reading '
                          'it.',
                          content_len_humanized, url, humanize_bytes(max_request_size))
            # Try using Google web cache
            log.debug('A Google cache version of the PDF URL %s will be attempted.', url)
            try:
                return self.title(f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}')
            except URLTitleError as exc:
                log.debug('The Google cache version failed for the PDF URL %s. %s', url, exc)

        # Return headers-based title
        title = ' '.join(f'({h})' for h in (content_type_header, content_len_humanized) if h is not None)
        log.info('Returning headers-derived title "%s" for URL %s', title, url)
        return title

    @staticmethod
    def _title_from_partial_html_content(content: bytes) -> Optional[str]:
        bs = BeautifulSoup(content, features='html.parser', parse_only=SoupStrainer('title'))
        # Note: Technically, the title tag within the head tag is the one that's required.
        title_tag = bs.title
        if not title_tag:
            return None
        title_text = title_tag.text
        title_bytes = title_text.encode(bs.original_encoding)
        if content.endswith(title_bytes):
            # Note: This is a check for an incomplete title, although it is not entirely an accurate check.
            return None
        title_text = title_text.strip()  # Useful for https://www.ncbi.nlm.nih.gov/pubmed/12542348
        return title_text

    def _update_html_content_amount_guess_for_title(self, url: str, content: bytes, title: str) -> None:
        content_len = len(content)
        title = title.encode()

        observation = content.rfind(title)
        padding = config.KiB  # For whitespace, closing title tag, and any minor randomness leading up to the title.
        observation = (observation + len(title) + padding) if (observation != -1) else content_len
        observation = min(observation, content_len + padding)
        observation = ceil_to_kib(observation)

        netloc = self.netloc(url)
        # This section is not thread safe, but that's okay as these are just estimates, and it won't crash.
        old_guess = self._content_amount_guesses.get(netloc)
        if old_guess is None:
            new_guess = min(observation, config.MAX_REQUEST_SIZES['html'])
            self._content_amount_guesses[netloc] = new_guess
            log.info('Set HTML content amount guess for %s to %s.', netloc, humanize_bytes(new_guess))
        elif old_guess != observation:
            new_guess = int(mean((old_guess, observation)))  # May need a better technique.
            new_guess = ceil_to_kib(new_guess)
            new_guess = min(new_guess, config.MAX_REQUEST_SIZES['html'])
            if old_guess != new_guess:
                self._content_amount_guesses[netloc] = new_guess
                log.info('Updated HTML content amount guess for %s with observation %s from %s to %s.',
                         netloc, humanize_bytes(observation), humanize_bytes(old_guess), humanize_bytes(new_guess))
            else:
                log.debug('HTML content amount guess for %s of %s is unchanged.', netloc, humanize_bytes(old_guess))
        else:
            log.debug('HTML content amount guess for %s of %s remains unchanged.', netloc, humanize_bytes(old_guess))

    def netloc(self, url: str) -> str:  # type: ignore
        parse_result = urlparse(url)
        if parse_result.scheme == '':
            return self.netloc(f'https://{url}')  # Without this, the returned netloc is erroneous.
        netloc = parse_result.netloc.casefold()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        return netloc

    def title(self, url: str) -> str:  # type: ignore
        netloc = self.netloc(url)
        overrides = config.NETLOC_OVERRIDES.get(netloc, {})
        overrides = cast(Dict, overrides)
        title = self._title(url)

        # Substitute title as configured
        for pattern, replacement in overrides.get('title_subs', []):
            original_title = title
            title = sub(pattern, replacement, title)
            if original_title != title:
                log.info('Substituted title "%s" with "%s".', original_title, title)

        return title
