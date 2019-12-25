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
import zlib

from bs4 import BeautifulSoup, SoupStrainer
from cachetools.func import LFUCache, ttl_cache

from . import config
from .util.humanize import humanize_bytes, humanize_len
from .util.json import get_ipynb_title
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
        self._title_outer = ttl_cache(maxsize=title_cache_max_size, ttl=title_cache_ttl)(self._title_outer)  # type: ignore
        self.netloc = lru_cache(maxsize=title_cache_max_size)(self.netloc)  # type: ignore

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

    def _title_inner(self, url: str) -> str:
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
                    return self._title_outer(fixed_url)
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
                return self._title_outer(url)

        # Percent-encode Unicode to ASCII, preventing UnicodeEncodeError
        if not url.isascii():
            original_url = url
            url = quote(url, safe=':/')  # Approximation.
            if original_url != url:
                log.info('ASCII encoded URL %s as %s', original_url, url)
                return self._title_outer(url)

        # Use Google web cache as configured
        if overrides.get('google_webcache') and not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)):
            log.info('%s is configured to use Google web cache.', netloc)
            url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
            return self._title_outer(url)

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
                request = Request(url, headers={'User-Agent': user_agent, **overrides.get('extra_headers', {})})
                start_time = time.monotonic()
                response = opener.open(request, timeout=config.REQUEST_TIMEOUT)
                time_used = time.monotonic() - start_time
            except (ValueError, HTTPError, URLError, SocketTimeoutError, RemoteDisconnected) as exc:
                if isinstance(exc, HTTPError) and (exc.code == 308):  # Permanent Redirect
                    original_url = url
                    url = exc.headers['Location']
                    if url and (original_url != url):
                        log.info('Due to a permanent direct (code 308), substituted URL %s with %s', original_url, url)
                        return self._title_outer(url)
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
        content_encoding_header = response.headers.get('Content-Encoding')
        content_len_header = response.headers.get('Content-Length')
        content_len_header = cast(Union[int, str, None], content_len_header)
        content_len_header = int(content_len_header) if content_len_header is not None else None
        content_len_humanized = humanize_bytes(content_len_header)
        log.debug('Received response in attempt %s with declared content type %s, encoding %s, and content length %s '
                  'in %.1fs.',
                  num_attempt, repr(content_type_header), content_encoding_header, content_len_humanized, time_used)

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
                    content_decoded = zlib.decompressobj(wbits=zlib.MAX_WBITS | 16).decompress(content) if \
                        (content_encoding_header == 'gzip') else content  # https://stackoverflow.com/a/56719274/
                    title = self._title_from_partial_html_content(content_decoded, overrides.get('bs_title_selector'))
                    if not title:
                        target_content_len = min(max_request_size, content_len * 2)
                        amt = max(0, target_content_len - content_len)
                        read &= bool(amt)
                        continue
                    self._update_html_content_amount_guess_for_title(url, content, title)  # Don't use content_decoded.

                    if overrides.get('substitute_url_with_title'):
                        log.info('Substituted URL %s with %s', url, title)
                        return self._title_outer(title)
                    log.debug('Returning HTML title %s for URL %s after reading %s.', repr(title), url,
                              humanize_bytes(content_len))
                    return title
            finally:
                response.close()
            # Handle Distil captcha using Google web cache
            if not(url.startswith(config.GOOGLE_WEBCACHE_URL_PREFIX)) and (b'distil_r_captcha.html' in content):
                log.info('Content of URL %s has a Distil captcha. A Google cache version will be attempted.', url)
                url = f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}'
                return self._title_outer(url)
            log.warning('Unable to find title in HTML content of length %s for URL %s', humanize_bytes(content_len),
                        url)

        # Return title from PDF
        elif content_type_header_str_cf.startswith(cast(str, config.CONTENT_TYPE_PREFIXES['pdf'])):
            max_request_size = config.MAX_REQUEST_SIZES['pdf']
            if (content_len_header or 0) <= max_request_size:
                content = response.read(max_request_size)
                if len(content) < max_request_size:  # Is very likely an incomplete file if both sizes are equal.
                    title = get_pdf_title(content)
                    if title:
                        log.debug('Returning PDF title %s for URL %s', repr(title), url)
                        return title
                    else:
                        log.debug('Unable to find title in PDF content for URL %s', url)  # Quite common.
                else:
                    log.debug('Undeclared and unknown content length for URL %s likely exceeds the configured PDF max '
                              'of %s for reading it fully.',
                              url, humanize_bytes(max_request_size))
            else:
                log.debug('Declared content length of %s for URL %s exceeds the configured PDF max of %s for reading '
                          'it.',
                          content_len_humanized, url, humanize_bytes(max_request_size))
            # Try using Google web cache
            log.debug('A Google cache version of the PDF URL %s will be attempted.', url)
            try:
                return self._title_outer(f'{config.GOOGLE_WEBCACHE_URL_PREFIX}{url}')
            except URLTitleError as exc:
                log.debug('The Google cache version failed for the PDF URL %s. %s', url, exc)

        # Return title from IPYNB
        elif (url.endswith('.ipynb') and
              content_type_header_str_cf.startswith(cast(str, config.CONTENT_TYPE_PREFIXES['ipynb']))):
            max_request_size = config.MAX_REQUEST_SIZES['ipynb']
            if (content_len_header or 0) <= max_request_size:
                content = response.read(max_request_size)
                if len(content) < max_request_size:  # Is very likely an incomplete file if both sizes are equal.
                    title = get_ipynb_title(content)
                    if title:
                        log.debug('Returning IPYNB title %s for URL %s', repr(title), url)
                        return title
                    else:
                        log.warning('Unable to find an IPYNB title for URL %s', url)
                else:
                    log.debug('Undeclared and unknown content length for URL %s likely exceeds the configured IPYNB '
                              'max of %s for reading it fully.',
                              url, humanize_bytes(max_request_size))
            else:
                log.debug('Declared content length of %s for URL %s exceeds the configured IPYNB max of %s for reading '
                          'it.',
                          content_len_humanized, url, humanize_bytes(max_request_size))

        # Fallback to return headers-based title
        title_headers = content_type_header, content_encoding_header, content_len_humanized
        title = ' '.join(f'({h})' for h in title_headers if h is not None)
        log.debug('Returning headers-derived title %s for URL %s', repr(title), url)
        return title

    def _title_outer(self, url: str) -> str:
        netloc = self.netloc(url)
        overrides = config.NETLOC_OVERRIDES.get(netloc, {})
        overrides = cast(Dict, overrides)
        title = self._title_inner(url)

        # Note: This method is separate from self._title because the actions below would have to otherwise be performed
        # at multiple locations in self._title.

        # Replace consecutive whitespaces
        title = ' '.join(title.split())  # e.g. for https://t.co/wyGR7438TH

        # Substitute title as configured
        for pattern, replacement in overrides.get('title_subs', []):
            original_title = title
            title = sub(pattern, replacement, title)
            if original_title != title:
                log.info('Substituted title "%s" with "%s".', original_title, title)

        return title

    @staticmethod
    def _title_from_partial_html_content(content: bytes, title_selector: Optional[str] = None) -> Optional[str]:
        if title_selector:
            bs = BeautifulSoup(content, features='html.parser')
            try:
                title_text = eval(title_selector, {}, {'bs': bs})
                # Note: eval takes expression, globals, and locals, all as positional args.
            except (AttributeError, KeyError, TypeError):
                return None
        else:
            bs = BeautifulSoup(content, features='html.parser', parse_only=SoupStrainer('title'))
            tag = bs.title
            if not tag:
                return None
            title_text = tag.text

        if content.decode(bs.original_encoding, errors='ignore').endswith(title_text):
            # Note: Encoding title_text instead fails for https://www.childstats.gov/americaschildren/tables/pop1.asp
            # Note: This is an inexact check for an incomplete title.
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

    def netloc(self, url: str) -> str:
        parse_result = urlparse(url)
        if parse_result.scheme == '':
            return self.netloc(f'https://{url}')  # Without this, the returned netloc is erroneous.
        netloc = parse_result.netloc.casefold()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        return netloc

    def title(self, url: str) -> str:
        title = self._title_outer(url)
        log.info('Returning title %s for URL %s', repr(title), url)
        return title
