# urltitle
**urltitle** returns the page title or other description for a given URL.
Its intended primary use is the inclusion of the returned value in conversations.

## Features
* It uses an in-memory cache with a default time of a week. The cache size and time are customizable.
* It reads approximately only the fraction of a page required to return a title, up to a maximum of 1 MiB.

## Links
* Code: https://github.com/impredicative/urltitle/
* Release: https://pypi.org/project/urltitle/


## Usage
Python 3.7 is required. To install the package, run:

    pip install urltitle

Usage examples:
```python
from urltitle import CachedURLTitle

cached_url_title = CachedURLTitle()

cached_url_title.title('https://www.cnn.com/2019/02/11/health/insect-decline-study-intl/index.html')
"Massive insect decline could have 'catastrophic' environmental impact, study says"
```

## To do
* Implement custom handling for some non-HTML content types such as PDF, etc.
