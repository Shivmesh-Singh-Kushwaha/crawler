import time
from lxml.html import fromstring
from selection import XpathSelector


def main(**kwargs):
    data = open('data/awesome_python.html', 'rb').read()

    start = time.time()
    for x in range(500):
        tree = fromstring(data)
        assert tree.xpath('//title')[0].text.startswith('awesome-web-scraping')
    print('lxml:xpath %.2f' % (time.time() - start))

    start = time.time()
    for x in range(500):
        tree = fromstring(data)
        assert XpathSelector(tree).select('//title').text().startswith('awesome-web-scraping')
    print('selection:select %.2f' % (time.time() - start))
