# coding: utf-8
from unittest import TestCase
import time
from test_server import TestServer

from crawler import Crawler
from crawler.request import Request
from crawler.error import CrawlerError, CrawlerFatalError
from .util import BaseTestCase


class TaskGeneratorTestCase(BaseTestCase, TestCase):
    def test_empty_task_generator(self):

        server = self.server

        class SimpleCrawler(Crawler):
            data = {'count': 0}

            def task_generator(self):
                if False:
                    yield None

        bot = SimpleCrawler()
        bot.run()

    def test_simple_task_generator(self):

        server = self.server

        class SimpleCrawler(Crawler):
            data = {'count': 0}

            def task_generator(self):
                for x in range(3):
                    yield Request('test', url=server.get_url())

            def handler_test(self, req, res):
                self.data['count'] += 1

        bot = SimpleCrawler()
        bot.run()
        self.assertEquals(3, bot.data['count'])

    def test_not_defined_task_generator(self):

        class SimpleCrawler(Crawler):
            pass

        bot = SimpleCrawler()
        bot.run()

    def test_broken_task_generator(self):
        class SimpleCrawler(Crawler):
            def task_generator(self):
                1/0

        bot = SimpleCrawler()
        self.assertRaises(CrawlerFatalError, bot.run)

    def test_unknown_task_type_error(self):
        class SimpleCrawler(Crawler):
            def task_generator(self):
                yield {'message': 'Show must go on!'}

        bot = SimpleCrawler()
        self.assertRaises(CrawlerError, bot.run)
