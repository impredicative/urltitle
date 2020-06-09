"""Test the titles of various URLs."""
import logging
import unittest

from urltitle import URLTitleReader, config

config.configure_logging()
log = logging.getLogger(f"{config.PACKAGE_NAME}.{__name__}")

# pylint: disable=line-too-long
TEST_CASES = {
    "https://www.aliexpress.com/item/33043594353.html": "One Channel Wemos D1 Mini Relay Shield for Wemos D1 Mini Relay Module for Arduino ESP8266 Development Board 1 Channel|Relays| - AliExpress",
    "https://www.aliexpress.com/wholesale?SearchText=d1+mini": "d1 mini – Buy d1 mini with free shipping on AliExpress version",
    "https://www.amazon.com/Active-Wow-Whitening-Charcoal-Natural/dp/B01N8XF244/": "Amazon.com : Active Wow Teeth Whitening Charcoal Powder Natural : Beauty",
    "https://www.amazon.com/gp/product/B077YCC84H/": "Amazon.com : Crest 3D White Whitestrips Vivid Plus Teeth Whitening Kit, 24 Individual Strips (10 Vivid Plus Treatments + 2 1hr Express Treatments) : Beauty",
    "https://www.amd.com/en/thermal-solutions-threadripper": "Thermal Solutions for Ryzen™ Threadripper™ Processors | AMD",
    "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/postgresql-kerberos-setting-up.html": "Setting Up Kerberos Authentication for PostgreSQL DB Instances - Amazon Relational Database Service",
    "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html": "What Is Amazon Relational Database Service (Amazon RDS)? - Amazon Relational Database Service",
    "https://docs.aws.amazon.com/batch/latest/userguide/multi-node-job-def.html": "Creating a Multi-node Parallel Job Definition - AWS Batch",
    "https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instance-types.html": "describe-instance-types — AWS CLI 1.18.75 Command Reference",
    "https://docs.aws.amazon.com/codepipeline/latest/APIReference/Welcome.html": "Welcome - AWS CodePipeline",
    "https://docs.aws.amazon.com/snowball/latest/developer-guide/transfer-petabytes.html": "How to Transfer Petabytes of Data Efficiently - AWS Snowball Edge",
    "https://www.annemergmed.com/article/S0196-0644(99)70271-4/abstract": "Agricultural Avermectins: An Uncommon But Potentially Fatal Cause of Pesticide Poisoning - Annals of Emergency Medicine",
    "https://arxiv.org/abs/1810.04805": "[1810.04805] BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    "https://bloomberg.com/opinion/articles/2019-06-25/allergan-deal-is-abbvie-s-63-billion-botox-job": "Allergan Deal Is AbbVie’s $63 Billion Botox Job - Bloomberg",
    "https://www.bloomberg.com/news/articles/2019-06-25/trump-picks-stephanie-grisham-as-next-white-house-spokeswoman?srnd=premium": "Stephanie Grisham Named Trump's Next White House Press Secretary - Bloomberg",
    "https://www.businessinsider.com/cocaine-ship-jpmorgan-owns-vessel-seized-by-us-cbp-2019-7": "US Customs just seized a ship owned by JPMorgan after authorities found $1 billion worth of drugs on it | Markets Insider",
    "https://www.cbc.ca/news/technology/ai-climate-change-1.5206402": "AI could better predict climate change impacts, some experts believe | CBC News",
    "https://www.cell.com/cell-metabolism/fulltext/S1550-4131(18)30630-2": "Profound Perturbation of the Metabolome in Obesity Is Associated with Health Risk: Cell Metabolism",
    "https://www.childstats.gov/americaschildren/tables/pop1.asp": "POP1 Child population: Number of children (in millions) ages 0–17 in the United States by age, 1950–2018 and projected 2019–2050",
    "https://www.cnn.com/2019/02/13/media/jeff-bezos-national-enquirer-leaker/index.html": "As questions linger around Jeff Bezos' explosive suggestions, identity of tabloid leaker is confirmed - CNN",
    "http://www.ekathimerini.com/241425/article/ekathimerini/business/piraeus-bank-offloads-507-mln-euros-of-impaired-corporate-loans": "Piraeus Bank offloads 507 mln euros of impaired corporate loans | Business | ekathimerini.com",
    "https://forum.effectivealtruism.org/posts/dCjz5mgQdiv57wWGz/ingredients-for-creating-disruptive-research-teams": "Ingredients for creating disruptive research teams - EA Forum",
    "https://eudl.eu/pdf/10.4108/eai.7-12-2018.159405": "Predictive Analytics In Weather Forecasting Using Machine Learning Algorithms - EUDL",
    "https://google.com": "Google",
    "https://hackernoon.com/a-simple-introduction-to-pythons-asyncio-595d9c9ecf8c": "A simple introduction to Python’s asyncio | Hacker Noon",
    "https://www.kdnuggets.com/2019/02/ai-help-solve-humanity-challenges.html": "How AI can help solve some of humanity’s greatest challenges – and why we might fail",
    "https://www.imdb.com/title/tt0119177/": "Gattaca (1997) - IMDb",
    "https://jamanetwork.com/journals/jama/fullarticle/2725150": "Rationing of Health Care in the United States: An Inevitable Consequence of Increasing Health Care Costs | Health Care Reform | JAMA | JAMA Network",
    "https://www.marketwatch.com/story/everything-you-need-to-know-about-market-closures-on-washingtons-birthday-the-holiday-you-may-know-as-presidents-day-2019-02-15": "Presidents Day: Everything you need to know about market closures on Washington’s Birthday - MarketWatch",
    "https://medicalxpress.com/news/2019-01-dental-flossing-behaviors-linked-higher.html": "Dental flossing and other behaviors linked with higher levels of toxic chemicals in the body",
    "https://www.medscape.com/viewarticle/909941": "What Do You Think of Medicare for All?",
    "https://mobile.twitter.com/KyivPost": "KyivPost (@KyivPost) | Twitter",
    "https://www.nationalgeographic.com/environment/2019/07/major-us-cities-will-face-unprecedente-climates-2050": "By 2050, many world cities will have weather like they’ve never seen, new study says",
    "https://www.nature.com/articles/s41430-018-0326-4": "Can legal restrictions of prenatal exposure to industrial trans-fatty acids reduce risk of childhood hematopoietic neoplasms? A population-based study | European Journal of Clinical Nutrition",
    "https://www.nature.com/articles/s41586-018-0594-0.epdf": "Options for keeping the food system within environmental limits | Nature",
    "https://www.nbcnews.com/politics/donald-trump/trump-installs-state-art-golf-simulator-white-house-n971176": "Trump installs state-of-the-art golf simulator in the White House",
    "https://www.ncbi.nlm.nih.gov/pubmed/11204525": "Lycopenaemia - PubMed",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5334395/": "Fruitflow®: the first European Food Safety Authority-approved natural cardio-protective functional ingredient",
    "https://www.newscientist.com/article/2143499-ships-fooled-in-gps-spoofing-attack-suggest-russian-cyberweapon/": "Ships fooled in GPS spoofing attack suggest Russian cyberweapon | New Scientist",
    "https://www.newsweek.com/china-warn-us-not-restart-nuclear-testing-1509437": "China Warns U.S. Not to Start Nuclear Testing Again After Trump Administration Reportedly Debates Defying 30-Year Ban",
    "https://seekingalpha.com/news/3473699-wayfair-minus-5-percent-employees-plan-walkout": "Wayfair -5% as some employees plan walkout (NYSE:W) | Seeking Alpha",
    "https://seekingalpha.com/symbol/GOOG": "Stock Picks, Stock Market Investing | Seeking Alpha",
    "https://stackoverflow.com/questions/50842144/": "python - Requirements.txt greater than equal to and then less than? - Stack Overflow",
    "https://www.sciencedaily.com/releases/2019/02/190207142206.htm": "New pill can deliver insulin through the stomach -- ScienceDaily",
    "https://www.semanticscholar.org/paper/Nutrition-in-chronic-disease-Nutrition-in-the-of-Tapsell/ed29f5473a7100bbfe462301d2205f7263339564": "[PDF] Nutrition in chronic disease Nutrition in the Prevention of Chronic Disease | Semantic Scholar",
    "https://www.tandfonline.com/doi/abs/10.1080/09637486.2018.1542666": "Oxidation of fish oil supplements in Australia: International Journal of Food Sciences and Nutrition: Vol 70, No 5",
    "https://www.swansonvitamins.com/swanson-premium-vitamin-c-rose-hips-1000-mg-250-caps": "Vitamin C with Rose Hips - 1,000 mg - Swanson Health Products",
    "https://towardsdatascience.com/a-visual-explanation-of-gradient-descent-methods-momentum-adagrad-rmsprop-adam-f898b102325c": "A Visual Explanation of Gradient Descent Methods (Momentum, AdaGrad, RMSProp, Adam)",
    "https://twitter.com/KyivPost": "KyivPost (@KyivPost) | Twitter",
    "https://twitter.com/KyivPost/status/1221139925363458048": 'KyivPost on Twitter: "Oleg Sukhov: "Fundamentally, little has changed since the rampant corruption and lawlessness under ex-President Petro Poroshenko or that of his predecessor, Viktor Yanukovych." https://t.co/A0KijQ3Wet"',
    "https://twitter.com/joycewhitevance/status/1143161956309884928": 'Joyce Alene on Twitter: "$775 per day, per kid & it doesn’t even cover a toothbrush, soap, a bed. https://t.co/CGiRNBbWIC"',
    "https://twitter.com/SenSanders/status/1143334860687388672/photo/1": 'Bernie Sanders on Twitter: "I don\'t often use this phrase, but today, we offered a truly revolutionary proposal to transform and improve our country in many ways. All of our people regardless of income deserve the education they need. #CollegeForAll #CancelStudentDebt… https://t.co/GER0DSFjf6"',
    "https://www.usnews.com/news/national-news/articles/2019-02-27/study-deep-sleep-best-for-brain-cleaning-emphasizes-link-between-sleep-and-alzheimers": "Study: Deep Sleep Best for Brain ‘Cleaning,’ Emphasizes Link Between Sleep and Alzheimer’s | National News | US News",
    "https://money.usnews.com/investing/news/articles/2019-06-30/preserve-your-ammunition-bis-urges-top-central-banks": "Preserve Your Ammunition, BIS Urges Top Central Banks | Investing News | US News",
    "https://onlinelibrary.wiley.com/doi/epdf/10.1111/j.1365-2672.2006.03171.x": "Residence time and food contact time effects on transfer of Salmonella Typhimurium from tile, wood and carpet: testing the five‐second rule",
    "https://www.wsj.com/articles/iran-says-new-sanctions-close-the-door-on-diplomacy-with-u-s-11561449138?mod=hp_lead_pos3": "Trump, Iran Step Up Rhetoric After Washington’s Sanctions Threat - WSJ",
    "https://www.youtube.com/watch?v=53YvP6gdD7U": "Deep Learning State of the Art (2019) - MIT - YouTube",
    "https://m.youtube.com/watch?v=GltlJO56S1g": "Jeff Bezos In 1999 On Amazon's Plans Before The Dotcom Crash - YouTube",
    # Missing scheme:
    "neverssl.com": "NeverSSL - Connecting ...",
    "reddit.com/r/FoodNerds/comments/arb6qj": "Paternal high-fat diet transgenerationally impacts hepatic immunometabolism. - PubMed - NCBI : FoodNerds",
    "www.reuters.com/article/us-usa-military-army/army-calls-base-housing-hazards-unconscionable-details-steps-to-protect-families-idUSKCN1Q4275": "Army calls base housing hazards 'unconscionable,' details steps to protect families - Reuters",
    # Non-ASCII:
    "https://en.wikipedia.org/wiki/Amanattō": "Amanattō - Wikipedia",
    "https://fr.wikipedia.org/wiki/Wikipédia:Accueil_principal": "WikipÃ©dia, l'encyclopÃ©die libre",
    # Unhandled types:
    "https://3c1703fe8d.site.internapcdn.net/newman/csz/news/800/2017/campylobacte.jpg": "(image/jpeg)",
    "https://export.arxiv.org/rss/eess.IV/recent": "(text/xml)",
    "https://static.arxiv.org/icons/cu/cornell-reduced-white-SMALL.svg": "(image/svg+xml) (10K)",
    "https://static.arxiv.org/icons/social/bibsonomy.png": "(image/png) (612B)",
    "https://raw.githubusercontent.com/python/cpython/v3.7.3/setup.py": "(text/plain; charset=utf-8) (100K)",
    "https://i.imgur.com/2Bs7Xo6.jpg": "(image/jpeg) (980K)",
    "https://i.imgur.com/QkbaYDH.gif": "(image/gif) (553K)",
    "https://kdnuggets.com/rss": "(application/rss+xml; charset=UTF-8)",
    "https://stmedia.stimg.co/ows_142533352086049.jpg": "(image/jpeg) (181K)",
    "https://storage.ning.com/topology/rest/1.0/file/get/3641314354?profile=RESIZE_710x": "(image/png;charset=UTF-8) (11K)",
    "https://tv.mathrubhumi.com/sitemap.xml": "(text/xml;charset=UTF-8) (1K)",
    # Substituted URL:
    "https://arxiv.org/pdf/1902.04704.pdf": "[1902.04704] Neural network models and deep learning - a primer for biologists",
    "https://arxiv.org/pdf/1902.04705": "[1902.04705] Self-adaptive Single and Multi-illuminant Estimation Framework based on Deep Learning",
    "https://arxiv.org/pdf/1902.04706v1.pdf": "[1902.04706v1] Simultaneously Learning Vision and Feature-based Control Policies for Real-world Ball-in-a-Cup",
    "https://arxiv.org/pdf/1902.04707v1": "[1902.04707v1] Sampling networks by nodal attributes",
    "https://www.cell.com/action/showPdf?pii=S1550-4131(15)00333-2": "Indoleamine 2,3-Dioxygenase Fine-Tunes Immune Homeostasis in Atherosclerosis and Colitis through Repression of Interleukin-10 Production: Cell Metabolism",
    "http://www.cell.com/cell/pdf/S0092-8674(15)00186-5.pdf": "Promoting Health and Longevity through Diet: From Model Organisms to Humans: Cell",
    "http://www.cell.com/current-biology/pdf/S0960-9822(13)00363-1.pdf": "The evolution of human nutrition: Current Biology",
    "https://www.cell.com/cell-metabolism/pdfExtended/S1550-4131(18)30579-5": "Mast Cell-Derived Histamine Regulates Liver Ketogenesis via Oleoylethanolamide Signaling: Cell Metabolism",
    "https://www.cell.com/cell-reports/pdfExtended/S2211-1247(18)31503-1": "Salt-Responsive Metabolite, β-Hydroxybutyrate, Attenuates Hypertension: Cell Reports",
    "https://colab.research.google.com/drive/1QB9IaXWsCHWfC94DzcZz-M4cTO2eczGY": "deepnude.ipynb - Colaboratory",
    "https://colab.research.google.com/drive/1QB9IaXWsCHWfC94DzcZz-M4cTO2eczGY#scrollTo=5NQctFLJMEy4": "deepnude.ipynb - Colaboratory",
    "http://www.gastrojournal.org/article/S0016-5085(17)36302-3/pdf": "Fructan, Rather Than Gluten, Induces Symptoms in Patients With Self-Reported Non-Celiac Gluten Sensitivity - Gastroenterology",
    "https://iopscience.iop.org/article/10.1088/1748-9326/aa6cd5/pdf": "Comparative analysis of environmental impacts of agricultural production systems, agricultural input efficiency, and food choice - IOPscience",
    "https://m.slashdot.org/story/361844": "Supreme Court Allows Blind People To Sue Retailers If Their Websites Are Not Accessible - Slashdot",
    "https://www.nature.com/articles/s41430-018-0326-4.pdf": "Can legal restrictions of prenatal exposure to industrial trans-fatty acids reduce risk of childhood hematopoietic neoplasms? A population-based study | European Journal of Clinical Nutrition",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3533942/pdf/1472-6920-12-117.pdf": "Attitudes toward statistics in medical postgraduates: measuring, evaluating and monitoring",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5522867/pdf/": "Mathematics Anxiety and Statistics Anxiety. Shared but Also Unshared Components and Antagonistic Contributions to Performance in Statistics",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3799466": "Multiple alignment-free sequence comparison",
    "https://pubs.acs.org/doi/abs/10.1021/acs.jafc.7b03118": "Effectiveness of Commercial and Homemade Washing Agents in Removing Pesticide Residues on and in Apples | Journal of Agricultural and Food Chemistry",
    "https://www.researchgate.net/profile/Paola_Costa-Mallen/publication/230587812_A_Diet_Low_in_Animal_Fat_and_Rich_in_N-Hexacosanol_and_Fisetin_Is_Effective_in_Reducing_Symptoms_of_Parkinson's_Disease/links/55568cff08ae6943a873442d.pdf": "(PDF) A Diet Low in Animal Fat and Rich in N-Hexacosanol and Fisetin Is Effective in Reducing Symptoms of Parkinson's Disease",
    "https://www.researchgate.net/profile/Wolfgang_Dvoak/publication/51932977_Making_Use_of_Advances_in_Answer-Set_Programming_for_AbstractArgumentation_Systems/links/0c96052cff4bc7ed40000000/Making-Use-of-Advances-in-Answer-Set-Programming-for-Abstract-Argumentation-Systems.pdf": "(PDF) Making Use of Advances in Answer-Set Programming for Abstract Argumentation Systems",
    "https://pdfs.semanticscholar.org/deb3/8d87e4259c3b70a56be05efc611d11e85911.pdf": "Definition and classification of chronic kidney disease: a position statement from Kidney Disease: Improving Global Outcomes (KDIGO). | Semantic Scholar",
    "https://pdfs.semanticscholar.org/1d76/d4561b594b5c5b5250edb43122d85db07262.pdf": "[PDF] Nutrition and health. The issue is not food, nor nutrients, so much as processing. | Semantic Scholar",
    "https://t.co/QjgZZVx4Nf": 'Joyce Alene on Twitter: "$775 per day, per kid & it doesn’t even cover a toothbrush, soap, a bed. https://t.co/CGiRNBbWIC"',
    "https://t.co/wyGR7438TH": 'Bernie Sanders on Twitter: "I don\'t often use this phrase, but today, we offered a truly revolutionary proposal to transform and improve our country in many ways. All of our people regardless of income deserve the education they need. #CollegeForAll #CancelStudentDebt… https://t.co/GER0DSFjf6"',
    "https://trends.google.com/trends/explore?date=all&q=soup": "soup - Google Trends",
    "http://onlinelibrary.wiley.com/doi/10.1002/ptr.5583/pdf": "A Review of Natural Stimulant and Non‐stimulant Thermogenic Agents - Stohs - 2016 - Phytotherapy Research - Wiley Online Library",
    "https://onlinelibrary.wiley.com/doi/pdf/10.1002/ptr.5583": "A Review of Natural Stimulant and Non‐stimulant Thermogenic Agents - Stohs - 2016 - Phytotherapy Research - Wiley Online Library",
    # IPYNB
    "https://colab.research.google.com/github/tensorflow/hub/blob/master/examples/colab/tf2_image_retraining.ipynb": "TF Hub for TF2: Retraining an image classifier (Python 3)",
    "https://colab.research.google.com/github/tensorflow/hub/blob/master/examples/colab/tf2_image_retraining.ipynb#scrollTo=dlauq-4FWGZM": "TF Hub for TF2: Retraining an image classifier (Python 3)",
    "https://colab.research.google.com/github/tensorflow/hub/blob/master/examples/colab/object_detection.ipynb": "Object detection (Python 3)",
    "https://raw.githubusercontent.com/tensorflow/hub/master/examples/colab/tf2_image_retraining.ipynb": "TF Hub for TF2: Retraining an image classifier (Python 3)",
    "https://raw.githubusercontent.com/tensorflow/hub/master/examples/colab/object_detection.ipynb": "Object detection (Python 3)",
    # PDF
    "https://www.diabetes.org.br/publico/images/pdf/artificial-sweeteners-induce-glucose-intolerance-by-altering-the-gut-microbiota.pdf": "Artificial sweeteners induce glucose intolerance by altering the gut microbiota",
    "https://drdanenberg.com/wp-content/uploads/2015/09/Born-to-Be-Healthy.pdf": "1F. Born to Be Healthy 8.21.15",
    "https://www.fda.gov/media/86193/download": "Contract Manufacturing Arrangements for Drugs: Quality Agreements Guidance for Industry",
    # Content-Length=20M. Google web cache used.
    "https://www.hq.nasa.gov/alsj/a17/A17_FlightPlan.pdf": "Apollo 17 Flight Plan",
    "https://www.omicsonline.org/open-access/pathophysiology-of-osgoodschlatter-disease-does-vitamin-d-have-a-role-2376-1318-1000177-102873.html": "Pathophysiology of Osgood-Schlatter Disease: Does Vitamin D have a Role?",
    "https://www.omicsonline.org/open-access/pathophysiology-of-osgoodschlatter-disease-does-vitamin-d-have-a-role-2376-1318-1000177.pdf": "Pathophysiology of Osgood-Schlatter Disease: Does Vitamin D have a Role?",
    # No Content-Length.
    "http://www.pnas.org/content/pnas/suppl/2018/10/09/1809045115.DCSupplemental/pnas.1809045115.sapp.pdf": "Microsoft Word - EN_PNAS_supportive information modified _9-26-18.docx",
    # Google web cache used.
    "https://extension.oregonstate.edu/sites/default/files/documents/1/glycemicindex.pdf": "Glycemic index and glycemic load for 100+ foods",
    # Whitespace
    " https://github.com/pikepdf/pikepdf/issues/26  ": "docinfo from incomplete PDF · Issue #26 · pikepdf/pikepdf · GitHub",
}
TEST_CASES_WITH_BAD_SSL = {
    "https://badssl.com": "badssl.com",  # Baseline with good SSL.
    "https://expired.badssl.com/": "expired.badssl.com",
    "https://wrong.host.badssl.com/": "wrong.host.badssl.com",
    "https://self-signed.badssl.com/": "self-signed.badssl.com",
    "https://neverssl.com/": "NeverSSL - Connecting ...",
    "https://verizon.net": "Pay Bill, See Offers with My Verizon Fios Login",
}
# pylint: enable=line-too-long

URL_FILTER = "https://google.com"


# pylint: disable=missing-class-docstring,missing-function-docstring
class TestURLs(unittest.TestCase):
    def test_url_titles(self):
        reader = URLTitleReader()
        for url, expected_title in TEST_CASES.items():
            if URL_FILTER and (URL_FILTER not in url):
                continue
            with self.subTest(url=url):
                log.info(f"Testing title for {url}")
                self.assertEqual(expected_title, reader.title(url))

    def test_url_titles_without_ssl_verification(self):
        reader = URLTitleReader(verify_ssl=False)
        for url, expected_title in TEST_CASES_WITH_BAD_SSL.items():
            if URL_FILTER and (URL_FILTER not in url):
                continue
            with self.subTest(url=url):
                log.info(f"Testing title for {url}")
                self.assertEqual(expected_title, reader.title(url))
