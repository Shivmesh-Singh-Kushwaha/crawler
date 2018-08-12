# coding: utf-8
import logging
import time
from unittest import TestCase
from test_server import TestServer
import multiprocessing

from crawler import Crawler, Request
from crawler.proxylist import ProxyList
from .util import (
    BaseTestCase, start_proxy_server, MemoryLoggingHandler,
    temp_file,
)

class BasicTestCase(BaseTestCase, TestCase):
    def test_proxylist_file_option(self):

        class TestCrawler(Crawler):
            pass

        with temp_file() as file_:
            proxy_server = '127.0.0.1:333'
            with open(file_, 'w') as out:
                out.write(proxy_server)
                out.flush()
            bot = TestCrawler(proxylist_file=file_)
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

        with temp_file() as file_:
            with open(file_, 'w') as out:
                out.write((':'.join(map(str, proxy_server.server_address))))
                out.flush()
            bot = TestCrawler(proxylist_file=file_)
            bot.run()
            self.assertEqual(1, proxy_server.num_requests)

    def test_crawler_proxylist_reload(self):

        server = self.server
        proxy_server1 = '127.0.0.1:444'
        proxy_server2 = '127.0.0.1:555'

        with temp_file() as pl_file:

            class TestCrawler(Crawler):
                def task_generator(self):
                    with open(pl_file, 'w') as out:
                        out.write(proxy_server2)
                    time.sleep(0.5)
                    yield Request('page', url=server.get_url())

                def handler_page(self, req, res):
                    pass

            with open(pl_file, 'w') as out:
                out.write(proxy_server1)
            bot = TestCrawler(
                proxylist_file=pl_file,
                proxylist_reload_time=0.1,
            )
            bot.run()
            self.assertEqual(
                proxy_server2,
                bot.proxylist.random_server().address()
            )

    def test_invalid_line_logging(self):

        class TestCrawler(Crawler):
            def task_generator(self):
                time.sleep(0.1)
                if False:
                    yield None

        logger = logging.getLogger('crawler.proxylist')
        hdl = MemoryLoggingHandler()
        logger.addHandler(hdl)

        self.server.response['data'] = (
            '127.0.0.1:444\n'
            'foo'
        )
        bot = TestCrawler(
            proxylist_url=self.server.get_url(),
            proxylist_reload_time=0.1,
        )
        bot.run()
        self.assertEqual(
            'Invalid proxy line: foo',
            hdl._messages[0]
        )

    def test_error_while_reloading(self):
        logger = logging.getLogger('crawler.proxylist')
        hdl = MemoryLoggingHandler()
        logger.addHandler(hdl)

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                server.response['code'] = 500
                time.sleep(0.5)
                if False:
                    yield None

        server.response['data'] = '127.0.0.1:444'
        bot = TestCrawler(
            proxylist_url=self.server.get_url(),
            proxylist_reload_time=0.1,
        )
        bot.run()
        print(hdl._messages)

    def test_next_server(self):
        pl = ProxyList.from_list(['foo:1', 'foo:2'])
        self.assertEqual('foo:1', pl.next_server().address())
        self.assertEqual('foo:2', pl.next_server().address())
        self.assertEqual('foo:1', pl.next_server().address())

    def test_random_server(self):
        pl = ProxyList.from_list(['foo:1', 'foo:2'])
        res = set()
        for _ in range(10):
            res.add(pl.random_server().address())
        self.assertTrue('foo:1' in res)
        self.assertTrue('foo:2' in res)

    def test_reload_from_list(self):
        pl = ProxyList.from_list(['foo:1', 'foo:2'])
        self.assertEqual('foo:1', pl.next_server().address())
        pl.reload()
        self.assertEqual('foo:2', pl.next_server().address())
        self.assertEqual('foo:1', pl.next_server().address())
