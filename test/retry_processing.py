# coding: utf-8
import logging
from unittest import TestCase
import multiprocessing

from test_server import TestServer
from weblib.error import RequiredDataNotFound

from crawler import Crawler, Request
from .util import BaseTestCase, start_proxy_server


class RequestRetryTestCase(BaseTestCase, TestCase):
    def test_retry_success(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                pass

        server.response_once['code'] = 500

        bot = TestCrawler(try_limit=10)
        bot.run()
        self.assertEqual(2, bot.stat.counters['network:request-page'])
        self.assertEqual(1, bot.stat.counters['network:request-ok-page'])
        self.assertEqual(1, bot.stat.counters['network:request-error-page'])

    def test_retry_limit_reached(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                pass

        server.response['code'] = 500

        bot = TestCrawler(try_limit=2)
        bot.run()
        self.assertEqual(2, bot.stat.counters['network:request-page'])
        self.assertEqual(2, bot.stat.counters['network:request-error-page'])
        self.assertEqual(1, bot.stat.counters['try_rejected'])

    def test_retry_required_data_not_found_successful(self):

        server = self.server

        class TestCrawler(Crawler):
            def init_hook(self):
                self.history = []

            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                if not self.history:
                    self.history.append(1)
                    raise RequiredDataNotFound

        bot = TestCrawler(try_limit=10)
        bot.run()
        self.assertEqual(2, bot.stat.counters['network:request-page'])
        self.assertEqual(2, bot.stat.counters['network:request-ok-page'])
        self.assertEqual(1, bot.stat.counters['parser:request-data-retry-page'])

    def test_retry_required_data_not_limit_reached(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                raise RequiredDataNotFound

        bot = TestCrawler(try_limit=2)
        bot.run()
        self.assertEqual(2, bot.stat.counters['network:request-page'])
        self.assertEqual(2, bot.stat.counters['network:request-ok-page'])
        self.assertEqual(1, bot.stat.counters['parser:request-data-retry-page'])
        self.assertEqual(1, bot.stat.counters['try_rejected'])
