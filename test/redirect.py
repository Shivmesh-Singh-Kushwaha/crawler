# coding: utf-8
from unittest import TestCase
from test_server import TestServer
import multiprocessing

from crawler import Crawler, Request
from .util import BaseTestCase

class BasicTestCase(BaseTestCase, TestCase):
    def test_redirect_by_default(self):

        class TestCrawler(Crawler):
            def init_hook(self):
                self.data = None

            def handler_test(self, req, res):
                self.data = res.body

        self.server.response_once['data'] = 'foo'
        self.server.response_once['code'] = 301
        self.server.response_once['headers'] = [
            ('location', self.server.get_url())
        ]

        self.server.response['data'] = 'bar'

        bot = TestCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()
        self.assertEquals(b'bar', bot.data)

    def test_redirect_disabled(self):

        class TestCrawler(Crawler):
            def init_hook(self):
                self.data = None

            def handler_test(self, req, res):
                self.data = res.body

        self.server.response_once['data'] = 'foo'
        self.server.response_once['code'] = 301
        self.server.response_once['headers'] = [
            ('location', self.server.get_url())
        ]

        self.server.response['data'] = 'bar'

        bot = TestCrawler()
        bot.add_task(Request(
            'test', url=self.server.get_url(), follow_redirect=False
        ))
        bot.run()
        self.assertEquals(b'foo', bot.data)

    def test_too_many_redirects(self):

        class TestCrawler(Crawler):
            def init_hook(self):
                self.data = None

            def handler_test(self, req, res):
                self.data = res.body

        self.server.response['data'] = 'foo'
        self.server.response['code'] = 301
        self.server.response['headers'] = [
            ('location', self.server.get_url())
        ]

        bot = TestCrawler()
        bot.add_task(Request(
            'test', url=self.server.get_url()
        ))
        bot.run()
        self.assertEquals(10, bot.stat.counters['network:request-error-test'])
