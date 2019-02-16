import logging

from urltitle import config, URLTitleReader

config.configure_logging()

log = logging.getLogger(config.PACKAGE_NAME + '.' + __name__)

TEST_URL = 'https://www.google.com/'

TEST_URLS = [
'https://www.amazon.com/Natures-Plus-Chewable-Iron-Supplement/dp/B00014DAFM',
'https://www.amazon.com/Bluebonnet-Earth-Vitamin-Chewable-Tablets/dp/B00ENYUIO2/',
'https://www.amazon.com/dp/B0749WVS7J/ref=ods_gw_ha_h1_d_rr_021519?pf_rd_p=8bf51e9c-a499-47ad-829e-a0b4afcae72e&pf_rd_r=9SHQNHFS1W35WG02P75M',
'https://www.amazon.com/dp/B0794W1SKP/ref=ods_mccc_lr',
'https://www.amazon.com/ProsourceFit-Tri-Fold-Folding-Exercise-Carrying/dp/B07NCJDHBM?',
]

reader = URLTitleReader()
for url in TEST_URLS:
    reader.title(url)
