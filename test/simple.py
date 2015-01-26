# coding: utf-8
from unittest import TestCase

from test.util.server import server
from iob import Crawler, Request


class SimpleTestCase(TestCase):
    def setUp(self):
        server.reset()

    def test_single_request(self):

        class SimpleCrawler(Crawler):
            data = {}

            def handler_test(self, req, res):
                self.data['response'] = res.body

        token = 'Python'
        server.response['data'] = token

        bot = SimpleCrawler()
        bot.add_task(Request(server.get_url(), tag='test'))
        bot.run()
        self.assertEquals(token, bot.data['response'])

    def test_simple_task_generator(self):

        class SimpleCrawler(Crawler):
            data = {'count': 0}

            def task_generator(self):
                for x in range(3):
                    yield Request(server.get_url(), tag='test')

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
