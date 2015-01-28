# coding: utf-8
from unittest import TestCase

from test.util.server import server
from iob import Crawler, Request


class RequestTestCase(TestCase):
    def test_constructor_arguments(self):
        req = Request()
        self.assertEqual(req.tag, None)
        self.assertEqual(req.url, None)
        self.assertEqual(req.callback, None)

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
        req = Request()
        self.assertEqual(req.meta, {})
        req = Request(meta=1)
        self.assertEqual(req.meta, 1)
        req = Request(meta={'place': 'hell'})
        self.assertEqual(req.meta, {'place': 'hell'})
