# coding: utf-8
from unittest import TestCase
from test_server import TestServer

from weblib.error import RequiredDataNotFound

from crawler import Crawler, Request
from .util import BaseTestCase

class ErrorHandlingTestCase(BaseTestCase, TestCase):
    def test_required_data_not_found(self):

        class SimpleCrawler(Crawler):
            def init_hook(self):
                self.gen = iter([False, True])
                self.result = []

            def handler_test(self, req, res):
                if not next(self.gen):
                    raise RequiredDataNotFound
                else:
                    self.result.append('ok')


        bot = SimpleCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()
        self.assertEquals('ok', bot.result[0])


    def test_required_data_not_found_implicit(self):

        class SimpleCrawler(Crawler):
            def init_hook(self):
                self.gen = iter([False, True])
                self.result = []

            def handler_test(self, req, res):
                res.xpath('//h1').require()
                self.result.append('ok')


        self.server.response_once['data'] = '<h2>test</h2>'
        self.server.response['data'] = '<h1>test</h1>'
        bot = SimpleCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()
        self.assertEquals('ok', bot.result[0])
        print(bot.stat.counters)
        self.assertEquals(2, bot.stat.counters['network:request-ok-test'])
