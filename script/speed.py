import time
import logging

from crawler import Crawler, Request


class TestCrawler(Crawler):
    def task_generator(self):
        for x in range(self._meta['num_req']):
            yield Request('page', 'http://127.0.0.1/awesome_python.html')

    def init_hook(self):
        self.count = 0

    def handler_page(self, req, res):
        title = res.xpath('//title').text()
        assert title.startswith('awesome')
        self.count += 1


def main(**kwargs):
    logging.getLogger('crawler.network').propagate = False
    start = time.time()
    num_req = 1000
    bot = TestCrawler(num_network_threads=10, meta={'num_req': num_req})
    bot.run()
    assert bot.count == 1000
    print('Elapsed: %.2f' % (time.time() - start))
