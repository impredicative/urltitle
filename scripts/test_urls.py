import unittest

from urltitle import config, URLTitleReader

config.configure_logging()


TEST_CASES = {
    'https://www.amazon.com/Active-Wow-Whitening-Charcoal-Natural/dp/B01N8XF244/':
        'Amazon.com : Active Wow Teeth Whitening Charcoal Powder Natural : Beauty',
    'https://www.amazon.com/gp/product/B077YCC84H/':
        'Amazon.com : Crest 3D White Whitestrips Vivid Plus : Beauty',
    'https://arxiv.org/abs/1810.04805':
        '[1810.04805] BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
    'https://www.cell.com/cell-metabolism/fulltext/S1550-4131(18)30630-2':
        'Profound Perturbation of the Metabolome in Obesity Is Associated with Health Risk: Cell Metabolism',
    'https://www.cnn.com/2019/02/13/media/jeff-bezos-national-enquirer-leaker/index.html':
        "As questions linger around Jeff Bezos' explosive suggestions, identity of tabloid leaker is confirmed - CNN",
    'https://hackernoon.com/a-simple-introduction-to-pythons-asyncio-595d9c9ecf8c':
        'A simple introduction to Python’s asyncio – Hacker Noon',
    'https://www.kdnuggets.com/2019/02/ai-help-solve-humanity-challenges.html':
        'How AI can help solve some of humanity’s greatest challenges – and why we might fail',
    'https://www.imdb.com/title/tt0119177/':
        'Gattaca (1997) - IMDb',
    'https://jamanetwork.com/journals/jama/fullarticle/2725150':
        'Rationing of Health Care in the United States: An Inevitable Consequence of Increasing Health Care Costs. | Health Care Economics, Insurance, Payment | JAMA | JAMA Network',
    'https://www.marketwatch.com/story/everything-you-need-to-know-about-market-closures-on-washingtons-birthday-the-holiday-you-may-know-as-presidents-day-2019-02-15':
        'Presidents Day: Everything you need to know about market closures on Washington’s Birthday - MarketWatch',
    'https://medicalxpress.com/news/2019-01-dental-flossing-behaviors-linked-higher.html':
        'Dental flossing and other behaviors linked with higher levels of toxic chemicals in the body',
    'https://www.nature.com/articles/s41430-018-0326-4':
        'Can legal restrictions of prenatal exposure to industrial trans-fatty acids reduce risk of childhood hematopoietic neoplasms? A population-based study | European Journal of Clinical Nutrition',
    'https://www.nature.com/articles/s41586-018-0594-0.epdf':
        'Options for keeping the food system within environmental limits | Nature',
    'https://www.ncbi.nlm.nih.gov/pubmed/11204525':
        'Lycopenaemia.  - PubMed - NCBI',
    'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5334395/':
        'Fruitflow®: the first European Food Safety Authority-approved natural cardio-protective functional ingredient',
    'https://www.nbcnews.com/politics/donald-trump/trump-installs-state-art-golf-simulator-white-house-n971176':
        'Trump installs state-of-the-art golf simulator in the White House',
    'https://stackoverflow.com/questions/50842144/':
        'python - Requirements.txt greater than equal to and then less than? - Stack Overflow',
    'https://www.sciencedaily.com/releases/2019/02/190207142206.htm':
        'New pill can deliver insulin through the stomach -- ScienceDaily',
    'https://www.semanticscholar.org/paper/Nutrition-in-chronic-disease-Nutrition-in-the-of-Tapsell/ed29f5473a7100bbfe462301d2205f7263339564':
        'Nutrition in chronic disease Nutrition in the Prevention of Chronic Disease - Semantic Scholar',
    'https://www.tandfonline.com/doi/abs/10.1080/09637486.2018.1542666':
        'Oxidation of fish oil supplements in Australia: International Journal of Food Sciences and Nutrition: Vol 0, No 0',
    'https://www.swansonvitamins.com/swanson-premium-vitamin-c-rose-hips-1000-mg-250-caps':
        'Vitamin C with Rose Hips - 1,000 mg - Swanson Health Products',
    'https://towardsdatascience.com/introducing-ubers-ludwig-5bd275a73eda':
        'Introducing Uber’s Ludwig – Towards Data Science',
    'https://onlinelibrary.wiley.com/doi/epdf/10.1111/j.1365-2672.2006.03171.x':
        'Residence time and food contact time effects on transfer of Salmonella Typhimurium from tile, wood and carpet: testing the five‐second rule - Dawson - 2007 - Journal of Applied Microbiology - Wiley Online Library',
    'https://www.youtube.com/watch?v=53YvP6gdD7U':
        'Deep Learning State of the Art (2019) - MIT - YouTube',
    'https://m.youtube.com/watch?v=GltlJO56S1g':
        "Jeff Bezos In 1999 On Amazon's Plans Before The Dotcom Crash - YouTube",

    # Missing scheme:
    'neverssl.com':
        'NeverSSL - helping you get online',
    'reddit.com/r/FoodNerds/comments/arb6qj':
        'Paternal high-fat diet transgenerationally impacts hepatic immunometabolism. - PubMed - NCBI : FoodNerds',
    'www.reuters.com/article/us-usa-military-army/army-calls-base-housing-hazards-unconscionable-details-steps-to-protect-families-idUSKCN1Q4275':
        "Army calls base housing hazards 'unconscionable,' details steps to protect families | Reuters",

    # Unhandled types:
    'https://3c1703fe8d.site.internapcdn.net/newman/csz/news/800/2017/campylobacte.jpg': '(image/jpeg)',
    'https://export.arxiv.org/rss/eess.IV/recent': '(text/xml)',
    'https://static.arxiv.org/icons/cu/cornell-reduced-white-SMALL.svg': '(image/svg+xml) (10K)',
    'https://static.arxiv.org/icons/social/bibsonomy.png': '(image/png) (612B)',
    'https://distill.pub/rss.xml': '(application/xml) (6K)',
    'https://download.fedoraproject.org/pub/fedora/linux/releases/29/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-29-1.2.iso': '(application/octet-stream) (2G)',
    'https://raw.githubusercontent.com/python/cpython/master/setup.py': '(text/plain; charset=utf-8) (100K)',
    'https://i.imgur.com/2Bs7Xo6.jpg': '(image/jpeg) (980K)',
    'https://i.imgur.com/QkbaYDH.gif': '(image/gif) (553K)',
    'https://kdnuggets.com/rss': '(application/rss+xml; charset=UTF-8)',
    'https://www.sciencedaily.com/images/2019/02/190213142720_1_540x360.jpg': '(image/jpeg) (54K)',

    # Substituted URL:
    'https://arxiv.org/pdf/1902.04704.pdf':
        '[1902.04704] Neural network models and deep learning - a primer for biologists',
    'https://arxiv.org/pdf/1902.04705':
        '[1902.04705] Self-adaptive Single and Multi-illuminant Estimation Framework based on Deep Learning',
    'https://arxiv.org/pdf/1902.04706v1.pdf':
        '[1902.04706v1] Simultaneously Learning Vision and Feature-based Control Policies for Real-world Ball-in-a-Cup',
    'https://arxiv.org/pdf/1902.04707v1':
        '[1902.04707v1] Sampling networks by nodal attributes',
    'https://www.cell.com/action/showPdf?pii=S1550-4131(15)00333-2':
        'Indoleamine 2,3-Dioxygenase Fine-Tunes Immune Homeostasis in Atherosclerosis and Colitis through Repression of Interleukin-10 Production: Cell Metabolism',
    'http://www.cell.com/cell/pdf/S0092-8674(15)00186-5.pdf':
        'Promoting Health and Longevity through Diet: From Model Organisms to Humans: Cell',
    'http://www.cell.com/current-biology/pdf/S0960-9822(13)00363-1.pdf':
        'The evolution of human nutrition: Current Biology',
    'https://www.cell.com/cell-metabolism/pdfExtended/S1550-4131(18)30579-5':
        'Mast Cell-Derived Histamine Regulates Liver Ketogenesis via Oleoylethanolamide Signaling: Cell Metabolism',
    'https://www.cell.com/cell-reports/pdfExtended/S2211-1247(18)31503-1':
        'Salt-Responsive Metabolite, β-Hydroxybutyrate, Attenuates Hypertension: Cell Reports',
    'http://www.gastrojournal.org/article/S0016-5085(17)36302-3/pdf':
        'Fructan, Rather Than Gluten, Induces Symptoms in Patients With Self-Reported Non-Celiac Gluten Sensitivity - Gastroenterology',
    'https://iopscience.iop.org/article/10.1088/1748-9326/aa6cd5/pdf':
        'Comparative analysis of environmental impacts of agricultural production systems, agricultural input efficiency, and food choice - IOPscience',
    'https://www.nature.com/articles/s41430-018-0326-4.pdf':
        'Can legal restrictions of prenatal exposure to industrial trans-fatty acids reduce risk of childhood hematopoietic neoplasms? A population-based study | European Journal of Clinical Nutrition',
    'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3533942/pdf/1472-6920-12-117.pdf':
        'Attitudes toward statistics in medical postgraduates: measuring, evaluating and monitoring',
    'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5522867/pdf/':
        'Mathematics Anxiety and Statistics Anxiety. Shared but Also Unshared Components and Antagonistic Contributions to Performance in Statistics',
    'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3799466':
        'Multiple alignment-free sequence comparison',
    "https://www.researchgate.net/profile/Paola_Costa-Mallen/publication/230587812_A_Diet_Low_in_Animal_Fat_and_Rich_in_N-Hexacosanol_and_Fisetin_Is_Effective_in_Reducing_Symptoms_of_Parkinson's_Disease/links/55568cff08ae6943a873442d.pdf":
        "(PDF) A Diet Low in Animal Fat and Rich in N-Hexacosanol and Fisetin Is Effective in Reducing Symptoms of Parkinson's Disease",
    "https://www.researchgate.net/profile/Wolfgang_Dvoak/publication/51932977_Making_Use_of_Advances_in_Answer-Set_Programming_for_AbstractArgumentation_Systems/links/0c96052cff4bc7ed40000000/Making-Use-of-Advances-in-Answer-Set-Programming-for-Abstract-Argumentation-Systems.pdf":
        "(PDF) Making Use of Advances in Answer-Set Programming for Abstract Argumentation Systems",

    'https://pdfs.semanticscholar.org/deb3/8d87e4259c3b70a56be05efc611d11e85911.pdf':
        'Definition and classification of chronic kidney disease: a position statement from Kidney Disease: Improving Global Outcomes (KDIGO). - Semantic Scholar',
    'https://pdfs.semanticscholar.org/1d76/d4561b594b5c5b5250edb43122d85db07262.pdf':
        'Nutrition and health. The issue is not food, nor nutrients, so much as processing. - Semantic Scholar',

    'http://onlinelibrary.wiley.com/doi/10.1002/ptr.5583/pdf':
        'A Review of Natural Stimulant and Non‐stimulant Thermogenic Agents - Stohs - 2016 - Phytotherapy Research - Wiley Online Library',
    'https://onlinelibrary.wiley.com/doi/pdf/10.1002/ptr.5583':
        'A Review of Natural Stimulant and Non‐stimulant Thermogenic Agents - Stohs - 2016 - Phytotherapy Research - Wiley Online Library',

    # PDF
    'https://www.diabetes.org.br/publico/images/pdf/artificial-sweeteners-induce-glucose-intolerance-by-altering-the-gut-microbiota.pdf':
        'Artificial sweeteners induce glucose intolerance by altering the gut microbiota',
    'https://drdanenberg.com/wp-content/uploads/2015/09/Born-to-Be-Healthy.pdf':
        '1F. Born to Be Healthy 8.21.15',
    'https://www.fda.gov/downloads/ucm380325.pdf':  # Content-Type="Application/pdf" (not lowercase)
        '1755 POC',
    'https://www.hq.nasa.gov/alsj/a17/A17_FlightPlan.pdf':  # Content-Length=20M. Google web cache used.
        'Apollo 17 Flight Plan',
    'https://www.omicsonline.org/open-access/detection-of-glyphosate-in-malformed-piglets-2161-0525.1000230.pdf':
        'Detection of Glyphosate in Malformed Piglets',
    'http://www.pnas.org/content/pnas/suppl/2018/10/09/1809045115.DCSupplemental/pnas.1809045115.sapp.pdf':  # No Content-Length.
        'Microsoft Word - EN_PNAS_supportive information modified _9-26-18.docx',
    'https://extension.oregonstate.edu/sites/default/files/documents/1/glycemicindex.pdf':  # Google web cache used.
        'Glycemic index and glycemic load for 100+ foods',

    # Whitespace
    ' https://github.com/pikepdf/pikepdf/issues/26  ':
        'docinfo from incomplete PDF · Issue #26 · pikepdf/pikepdf · GitHub',
}
URL_FILTER = ''

reader = URLTitleReader()


class TestURLs(unittest.TestCase):
    def test_url_titles(self):
        for url, expected_title in TEST_CASES.items():
            if URL_FILTER and (URL_FILTER not in url):
                continue
            with self.subTest(url=url):
                self.assertEqual(expected_title, reader.title(url))
