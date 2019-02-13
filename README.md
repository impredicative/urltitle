# urltitle
**urltitle** returns the page title or other description for a given URL.
Its intended primary use is the inclusion of the returned value in conversations.

## Features
* It uses an in-memory cache with a default time of a week. The cache size and time are customizable.
* It reads only the fraction of a page required to return a title, up to a maximum of 128 KiB.

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
* Handle failing sites:
  - swansonvitamins.com
  - cell.com
  - https://wordpress.com/post/johnflux.com/2880
  - https://scikit-learn.org/stable/auto_examples/svm/plot_weighted_samples.html
  - https://techcrunch.com/2019/02/12/ubisoft-and-mozilla-team-up-to-develop-clever-commit-an-ai-coding-assistant/
* Handle some non-HTML content types such as PDF, etc.
