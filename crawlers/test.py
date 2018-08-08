import time
from threading import Thread
import logging
import re

from lxml.html import fromstring, HTMLParser
from selectolax.parser import HTMLParser as FastHTMLParser
from pympler import asizeof

from crawler import Crawler, Request
from crawler.api import start_api_server_thread


class TestCrawler(Crawler):
    def task_generator(self):
        for x in range(2000):
            yield Request('page', url='http://127.0.0.1/awesome_python.html?%d' % x)

    def handler_page(self, req, res):
        # 1
        #parser = HTMLParser()
        #dom = fromstring(res.body, parser=parser)
        #title = dom.xpath('//title')[0].text
        # 2
        #fast_parser= FastHTMLParser(res.body)
        #title = fast_parser.css('title')[0].text()
        #assert title.startswith('awesome-web-scraping')
        # 3
        title = res.xpath('//title').text()
        assert title.startswith('awesome-web-scraping')


#def main(**kwargs):
#    logging.getLogger('crawler.network').propagate = False
#    bot = MyCrawler(num_network_threads=100, num_parsers=2)
#    bot.run()
