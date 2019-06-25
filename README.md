# urltitle
**urltitle** uses Python 3.7 to return the page title or header-based description for a given URL.
Its intended primary use is the inclusion of the returned value in conversations.
As a disclaimer, note that the returned title is not guaranteed to be accurate due to many possible factors.

## Features
* An in-memory cache is used with a default time of a week. The cache size and time are customizable.
* Approximately only the fraction of a HTML page required to return a title is read, up to a customizable maximum of 1 MiB.
* A PDF title metadata extractor is used for PDF files of up to a customizable maximum size of 8 MiB.
* Up to three attempts are made for resiliency except if there is an unrecoverable error, i.e. 400, 401, 404, etc.
* A guess of `https` and otherwise `http` is made for a URL with a missing scheme, e.g. git-scm.com/downloads.
* SSL verification for https sites can optionally be disabled.
* A fallback to Google web cache is used if a HTML page presents a Distil captcha.
It is also used for a PDF which is too large or doesn't have title metadata.
* Diagnostic logging can be optionally enabled for the logger named `urltitle` at the desired level.
* Some site-specific customizations are configurable:
  - Multiple regular expression based URL and title substitutions
  - Use of Google web cache
  - User-Agent
  - Additional headers

## Links
* Code: https://github.com/impredicative/urltitle/
* Release: https://pypi.org/project/urltitle/

## Usage
### Installation
Python ≥3.7 is required due to a reference 
to [`SSLCertVerificationError`](https://docs.python.org/3/library/ssl.html#ssl.SSLCertVerificationError).

To install the package, run:

    pip install urltitle

### Examples
```python
from urltitle import URLTitleReader

reader = URLTitleReader(verify_ssl=True)

# Titles for HTML content
reader.title('https://www.cnn.com/2019/02/11/health/insect-decline-study-intl/index.html')
"Insect numbers in precipitous decline could have 'catastrophic' consequences, warns study - CNN"

reader.title('https://www.youtube.com/watch?v=53YvP6gdD7U')
'Deep Learning State of the Art (2019) - MIT - YouTube'

# Titles for URLs with a missing scheme
reader.title('www.reuters.com/article/us-usa-military-army/army-calls-base-housing-hazards-unconscionable-details-steps-to-protect-families-idUSKCN1Q4275')
"Army calls base housing hazards 'unconscionable,' details steps to protect families | Reuters"

reader.title('reddit.com/r/FoodNerds/comments/arb6qj')
'Paternal high-fat diet transgenerationally impacts hepatic immunometabolism. - PubMed - NCBI : FoodNerds'

reader.title('neverssl.com')
'NeverSSL - helping you get online'

# Titles for non-ASCII URLs
reader.title('https://en.wikipedia.org/wiki/Amanattō')
'Amanattō - Wikipedia'

reader.title('https://fr.wikipedia.org/wiki/Wikipédia:Accueil_principal')
"Wikipédia, l'encyclopédie libre"

# Titles for PDFs having title metadata
reader.title('https://www.diabetes.org.br/publico/images/pdf/artificial-sweeteners-induce-glucose-intolerance-by-altering-the-gut-microbiota.pdf')
'Artificial sweeteners induce glucose intolerance by altering the gut microbiota'

reader.title('https://www.omicsonline.org/open-access/detection-of-glyphosate-in-malformed-piglets-2161-0525.1000230.pdf')
'Detection of Glyphosate in Malformed Piglets'

# Titles for other content showing Content-Type and Content-Length as available:
reader.title('https://www.sciencedaily.com/images/2019/02/190213142720_1_540x360.jpg')
'(image/jpeg) (54K)'

reader.title('https://kdnuggets.com/rss')
'(application/rss+xml; charset=UTF-8)'

reader.title('https://download.fedoraproject.org/pub/fedora/linux/releases/29/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-29-1.2.iso')
'(application/octet-stream) (2G)'

# Titles for substituted URLs as per configuration:
reader.title('https://arxiv.org/pdf/1902.04704.pdf')
'[1902.04704] Neural network models and deep learning - a primer for biologists'

reader.title('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2495396/pdf/postmedj00315-0056.pdf')
"Features of a successful therapeutic fast of 382 days' duration"

reader.title('https://pdfs.semanticscholar.org/1d76/d4561b594b5c5b5250edb43122d85db07262.pdf')
'Nutrition and health. The issue is not food, nor nutrients, so much as processing. - Semantic Scholar'
```

### Exceptions
An error is expected to raise the `urltitle.URLTitleError` exception.

### Customizations
For any site-specific customizations, update (but ideally not replace) `urltitle.config.NETLOC_OVERRIDES` with the
relevant sites using the preexisting entries in it as examples. Refer to [`config.py`](urltitle/config.py).
The site of a URL is as defined and returned by the `URLTitleReader().netloc(url)` method in
[`urltitle.py`](urltitle/urltitle.py).

The following examples show various URLs and their corresponding sites for the purpose of entering site-specific
customizations:

| URL | Site |
| --- | ---- |
| `https://www.google.com/search?q=asdf` | `google.com` |
| `https://google.com/search?q=hjkl` | `google.com` |
| `google.com/search?q=qwer` | `google.com` |
| `google.com` | `google.com` |
| `GOOGLE.COM` | `google.com` |
| `gOogLE.com` | `google.com` |
| `https://drive.google.com/drive/my-drive` | `drive.google.com` |
| `https://help.github.com/en/` | `help.github.com` |
| `https://github.com/pytorch/pytorch` | `github.com`
| `https://www.amazon.com/gp/product/B01F8POA7U` | `amazon.com`
| `https://rise.cs.berkeley.edu/blog/` | `rise.cs.berkeley.edu` |
| `https://www.swansonvitamins.com/web-specials` | `swansonvitamins.com` |
