# coding: utf-8
import time
from unittest import TestCase
from test_server import TestServer

from weblib.error import RequiredDataNotFound

from crawler import Crawler, Request
from crawler.error import CrawlerError, CrawlerFatalError
from .util import BaseTestCase

class ErrorHandlingTestCase(BaseTestCase, TestCase):
    def test_required_data_not_found(self):

        class TestCrawler(Crawler):
            def init_hook(self):
                self.gen = iter([False, True])
                self.result = []

            def handler_test(self, req, res):
                if not next(self.gen):
                    raise RequiredDataNotFound
                else:
                    self.result.append('ok')


        bot = TestCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()
        self.assertEquals('ok', bot.result[0])


    def test_required_data_not_found_implicit(self):

        class TestCrawler(Crawler):
            def init_hook(self):
                self.gen = iter([False, True])
                self.result = []

            def handler_test(self, req, res):
                res.xpath('//h1').require()
                self.result.append('ok')


        self.server.response_once['data'] = '<h2>test</h2>'
        self.server.response['data'] = '<h1>test</h1>'
        bot = TestCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()
        self.assertEquals('ok', bot.result[0])
        self.assertEquals(2, bot.stat.counters['network:request-ok-test'])

    def test_network_request_unexpected_type(self):

        class TestCrawler(Crawler):
            pass

        bot = TestCrawler()
        bot.add_task('foo')
        self.assertRaises(CrawlerFatalError, bot.run)

    def test_fatal_error_in_worker_parser(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                # Adding "foo" in response queue
                # raises ValueError in `req, res = resp_queue.get()`
                self._response_queue.put('foo')

        bot = TestCrawler()
        self.assertRaises(CrawlerFatalError, bot.run)

    def test_fatal_error_in_worker_stat(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                pass

        # Let's break stats thread by sending incorrect value
        # for speed_metrics option
        bot = TestCrawler(speed_metrics=7)
        self.assertRaises(CrawlerFatalError, bot.run)

    def test_fatal_error_in_worker_proxylist(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                pass

        self.server.response['data'] = '127.0.0.1:444'

        # Let's break proxylist thread by setting
        # incorrect value to config['proxylist_reload_time']
        bot = TestCrawler(
            proxylist_reload_time='foo',
            proxylist_url=self.server.get_url(),
        )
        self.assertRaises(CrawlerFatalError, bot.run)
