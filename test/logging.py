# coding: utf-8
import logging
from unittest import TestCase
import multiprocessing

from test_server import TestServer

from crawler import Crawler, Request
from .util import BaseTestCase, start_proxy_server

class MemoryHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(MemoryHandler, self).__init__(*args, **kwargs)
        self._messages = []

    def emit(self, record):
        msg = self.format(record)
        self._messages.append(msg)


class BasicTestCase(BaseTestCase, TestCase):
    def test_request_logging(self):

        server = self.server
        th, proxy_server = start_proxy_server()

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                yield Request(
                    'page2', url=server.get_url(),
                    proxy=proxy_server.address()
                )

            def handler_page2(self, req, res):
                pass

        hdl = MemoryHandler()
        logger = logging.getLogger('crawler.network')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(hdl)

        bot = TestCrawler()
        bot.run()

        self.assertEqual(
            hdl._messages[0],
            'GET http://%s:%d/' % (self.server.address, self.server.port)
        )
        self.assertEqual(
            hdl._messages[1],
            'GET http://%s:%d/ via http proxy %s' % (
                self.server.address, self.server.port, proxy_server.address()
            )
        )
