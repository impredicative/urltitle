# urltitle
**urltitle** uses Python 3.7 to return the page title or other description for a given URL.
Its intended primary use is the inclusion of the returned value in conversations.

## Features
* An in-memory cache is used with a default time of a week. The cache size and time are customizable.
* Approximately only the fraction of a page required to return a title is read, up to a maximum of 1 MiB.
* Up to three attempts are made for resiliency except if there is an unrecoverable error, i.e. 400, 401, or 404.

## Links
* Code: https://github.com/impredicative/urltitle/
* Release: https://pypi.org/project/urltitle/


## Usage
Python ≥3.7 is required. To install the package, run:

    pip install urltitle

Usage examples:
```python
from urltitle import URLTitleReader

reader = URLTitleReader()

reader.title('https://www.cnn.com/2019/02/11/health/insect-decline-study-intl/index.html')
"Massive insect decline could have 'catastrophic' environmental impact, study says"

# Titles for non-HTML content showing Content-Type and Content-Length as available:
reader.title('https://www.sciencedaily.com/images/2019/02/190213142720_1_540x360.jpg')
'(image/jpeg) (54K)'

reader.title('https://kdnuggets.com/rss')
'(application/rss+xml; charset=UTF-8)'

reader.title('https://download.fedoraproject.org/pub/fedora/linux/releases/29/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-29-1.2.iso')
'(application/octet-stream) (2G)'
```

## To do
* Implement custom handling for some non-HTML content types such as PDF, etc.
