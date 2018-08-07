# coding: utf-8
from unittest import TestCase

from crawler import Crawler, Request
from .util import BaseTestCase


class BasicTestCase(BaseTestCase, TestCase):
    def test_handler_error(self):

        class SimpleCrawler(Crawler):
            data = {}

            def handler_test(self, req, res):
                1/0

        bot = SimpleCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()

        self.assertEqual(1, len(bot.stat.items['handler_error']))
        self.assertEqual(
            bot.stat.items['handler_error'][0],
            '%s|%s|%s|%s' % (
                'test',
                'ZeroDivisionError',
                'division by zero',
                self.server.get_url(),
            )
        )
