from urllib.parse import urlsplit
import logging

from crawler import Crawler, Request


class TestCrawler(Crawler):

    def task_generator(self):
        with open('var/host.txt') as inp:
            for line in inp:
                if not line.startswith('#'):
                    host = line.strip()
                    yield Request(
                        'page', 'https://%s/' % host, meta={'host': host}
                    )

    def handler_page(self, req, res):
        try:
            title = res.xpath('//title').text(default='N/A')
        except Exception as ex:
            print('%s FAIL' % req.meta['host'])
            res.save('/tmp/x.html')
            raise
        else:
            print('%s: %s' % (req.meta['host'], title))


def main(**kwargs):
    logging.getLogger('crawler.control').propagate = False
    bot = TestCrawler(num_network_threads=10)
    bot.run()
