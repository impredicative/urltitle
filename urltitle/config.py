import datetime
import logging.config
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


KiB = 1024
MiB = KiB ** 2

DEFAULT_CACHE_TTL = datetime.timedelta(weeks=1).total_seconds()
DEFAULT_CACHE_MAX_SIZE = 4 * KiB
DEFAULT_REQUEST_SIZE = 8 * KiB
GOOGLE_WEBCACHE_URL_PREFIX = 'https://webcache.googleusercontent.com/search?q=cache:'
CONTENT_TYPE_PREFIXES = {'html': ('text/html', '*/*'),  # Nature.com EPDFs are HTML but use */*
                         'pdf': 'application/pdf'}  # Values must be lowercase.
MAX_REQUEST_ATTEMPTS = 3
MAX_REQUEST_SIZES = {'html': MiB, 'pdf': 8 * MiB}
#   Note: Amazon product links, for example, have the title between 512K and 1M in the HTML content.
PACKAGE_NAME = Path(__file__).parent.stem
REQUEST_SIZE_MAX = MiB
REQUEST_TIMEOUT = 15
UNRECOVERABLE_HTTP_CODES = 400, 401, 404
URL_SCHEME_GUESSES = 'https', 'http'
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        PACKAGE_NAME: {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

NETLOC_OVERRIDES = {  # Site-specific overrides (without www prefix). Sites must be in lowercase.
    'arxiv.org': {'url_subs': [(r'/pdf/(?P<id>.+?)(?:\.pdf)?$', '/abs/\g<id>')]},
    'cell.com': {'url_subs': [(r'cell\.com/(?P<path>.+?)/pdf(?:Extended)*/(?P<id>.+?)(?:\.pdf)?$',
                               'cell.com/\g<path>/fulltext/\g<id>'),
                              (r'cell\.com/action/showPdf\?pii=(?P<id>.+)$',
                               'cell.com/cell/fulltext/\g<id>')]},
    'citeseerx.ist.psu.edu': {'url_subs': [(r'/viewdoc/download\?doi=(?P<doi>.+?)\&.+$',
                                           '/viewdoc/summary?doi=\g<doi>')]},
    'colab.research.google.com': {'url_subs': [(r'//colab\.research\.google\.com/drive/(?P<id>[\w\-]+)(?:\#.*)?$',
                                                '//drive.google.com/file/d/\g<id>')],
                                  'title_subs': [(r'(?P<name>.+?) \- Google Drive$',
                                                  '\g<name> - Colaboratory')]},
    'ft.com': {'user_agent': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'},  # Iffy.
    'gastrojournal.org': {'url_subs': [(r'gastrojournal\.org/article/(?P<id>.+?)/pdf$',
                                        'gastrojournal.org/article/\g<id>/')]},
    'iopscience.iop.org': {'url_subs': [(r'iopscience\.iop\.org/article/(?P<id>.+?)/pdf$',
                                         'iopscience.iop.org/article/\g<id>')]},
    'medscape.com': {'user_agent': 'Googlebot-News'},
    'm.youtube.com': {'user_agent': 'Mozilla/5.0'},
    'nature.com': {'url_subs': [(r'nature\.com/articles/(?P<id>.+?)\.pdf$',
                                 'nature.com/articles/\g<id>')]},
    'ncbi.nlm.nih.gov': {'url_subs': [(r'/pmc/articles/PMC(?P<id>.+?)/pdf/?(?:.+?\.pdf)?$',
                                       '/pmc/articles/PMC\g<id>/')]},
    'omicsonline.org': {'google_webcache': True},
    'onlinelibrary.wiley.com': {'url_subs': [(r'onlinelibrary\.wiley\.com/doi/(?P<doi>.+?)/pdf$',
                                              'onlinelibrary.wiley.com/doi/\g<doi>'),
                                             (r'onlinelibrary\.wiley\.com/doi/pdf/(?P<doi>.+)$',
                                              'onlinelibrary.wiley.com/doi/\g<doi>')]},
    'pdfs.semanticscholar.org': {'url_subs': [(r'//pdfs\.semanticscholar.org/(?P<id1>.+?)/(?P<id2>.+?)\.pdf$',
                                               '//semanticscholar.org/paper/\g<id1>\g<id2>')]},
    'pubs.acs.org': {'url_subs': [(r'^https://(?P<url>.+)$',
                                   'http://\g<url>')]},
    'researchgate.net': {'url_subs':
                             [(r'researchgate\.net/profile/(?P<author>.+?)/publication/(?P<pub>.+?)/links/.+?\.pdf$',
                               'researchgate.net/profile/\g<author>/publication/\g<pub>')]},
    'swansonvitamins.com': {'user_agent': 'FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)'},
    'trends.google.com': {'url_subs': [(r'^https://(?P<url>.+)$',
                                        'http://\g<url>')]},
    'usnews.com': {'user_agent': 'FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)'},
    'youtu.be': {'user_agent': 'Mozilla/5.0'},
    'youtube.com': {'user_agent': 'Mozilla/5.0'},
}
