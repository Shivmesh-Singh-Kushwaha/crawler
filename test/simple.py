# coding: utf-8
from unittest import TestCase

from test.util.server import server
from iob import Crawler, Request

class SimpleCrawler(Crawler):
    data = {}

    def handler_test(self, req, res):
        self.data['response'] = res.body


class SimpleTestCase(TestCase):
    def setUp(self):
        server.reset()

    def test_single_request(self):
        token = 'Python'
        server.response['data'] = token

        bot = SimpleCrawler()
        bot.add_task(Request(server.get_url(), tag='test'))
        bot.run()
        self.assertEquals(token, bot.data['response'])
