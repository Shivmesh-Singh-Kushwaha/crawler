# coding: utf-8
import logging
import time
from unittest import TestCase
from test_server import TestServer
import multiprocessing
from tempfile import NamedTemporaryFile

from crawler import Crawler, Request
from .util import BaseTestCase, start_proxy_server, MemoryLoggingHandler

class BasicTestCase(BaseTestCase, TestCase):
    def test_proxylist_file_option(self):

        class TestCrawler(Crawler):
            pass

        file_ = NamedTemporaryFile()
        proxy_server = '127.0.0.1:333'
        file_.write(proxy_server.encode())
        file_.flush()
        bot = TestCrawler(proxylist_file=file_.name)
        self.assertEquals(
            proxy_server,
            bot.proxylist._servers[0].address()
        )

    def test_proxylist_url_option(self):

        class TestCrawler(Crawler):
            pass

        proxy_server = '127.0.0.1:444'
        self.server.response['data'] = proxy_server
        bot = TestCrawler(proxylist_url=self.server.get_url())
        self.assertEquals(
            proxy_server,
            bot.proxylist._servers[0].address()
        )

    def test_proxylist_request(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                pass

        th, proxy_server = start_proxy_server()

        file_ = NamedTemporaryFile()
        file_.write((':'.join(map(str, proxy_server.server_address))).encode())
        file_.flush()
        bot = TestCrawler(proxylist_file=file_.name)
        bot.run()
        self.assertEqual(1, proxy_server.num_requests)

    def test_proxylist_reload(self):

        class TestCrawler(Crawler):
            def task_generator(self):
                time.sleep(0.5)
                if False:
                    yield None

        proxy_server1 = '127.0.0.1:444'
        proxy_server2 = '127.0.0.1:555'
        self.server.response_once['data'] = proxy_server1
        self.server.response['data'] = proxy_server2
        bot = TestCrawler(
            proxylist_url=self.server.get_url(),
            proxylist_reload_time=0.1,
        )
        bot.run()
        self.assertEqual(
            proxy_server2,
            bot.proxylist.random_server().address()
        )

    #def test_invalid_line_logging(self):

    #    class TestCrawler(Crawler):
    #        def task_generator(self):
    #            time.sleep(0.1)
    #            if False:
    #                yield None

    #    logger = logging.getLogger('crawler.proxylist')
    #    hdl = MemoryLoggingHandler()
    #    logger.addHandler(hdl)

    #    self.server.response['data'] = (
    #        '127.0.0.1:444\n'
    #        'foo'
    #    )
    #    bot = TestCrawler(
    #        proxylist_url=self.server.get_url(),
    #        proxylist_reload_time=0.1,
    #    )
    #    bot.run()
    #    self.assertEqual(
    #        'Invalid proxy line: foo',
    #        hdl._messages[0]
    #    )
