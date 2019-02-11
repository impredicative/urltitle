# urltitle
**urltitle** returns the page title or other description for a given URL.
Its primary purpose is the inclusion of the returned value in conversations.

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