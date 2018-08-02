# coding: utf-8
from unittest import TestCase
from test_server import TestServer

from crawler import Crawler, Request
from crawler.error import RequestConfigurationError
from .util import BaseTestCase


class RequestTestCase(BaseTestCase, TestCase):
    def test_constructor_arguments(self):
        req = Request('TAG')
        self.assertEqual(req.tag, 'TAG')
        self.assertEqual(req.url, None)

        req = Request('TAG', 'URL')
        self.assertEqual(req.tag, 'TAG')
        self.assertEqual(req.url, 'URL')

        req = Request(url='URL', tag='TAG')
        self.assertEqual(req.tag, 'TAG')
        self.assertEqual(req.url, 'URL')

    def test_constructor_meta_argument(self):
        req = Request('TAG')
        self.assertEqual(req.meta, {})
        req = Request('TAG', meta=1)
        self.assertEqual(req.meta, 1)
        req = Request('TAG', meta={'place': 'hell'})
        self.assertEqual(req.meta, {'place': 'hell'})

    def test_tag_not_provided(self):

        server = self.server

        class SimpleCrawler(Crawler):
            def task_generator(self):
                yield Request(url=server.get_url())

            def handler_test(self, req, res):
                pass

        bot = SimpleCrawler()
        self.assertRaises(RequestConfigurationError, bot.run)
