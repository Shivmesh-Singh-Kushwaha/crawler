# coding: utf-8
from unittest import TestCase
from test_server import TestServer

from crawler import Crawler, Request
from crawler.error import CrawlerError, CrawlerFatalError
from crawler.util import make_str, make_bytes
from .util import BaseTestCase


class CrawlerUtilTestCase(BaseTestCase, TestCase):
    def test_make_bytes_from_str(self):
        self.assertEqual(
            'Цой'.encode('utf-8'),
            make_bytes('Цой')
        )

    def test_make_bytes_from_bytes(self):
        self.assertEqual(
            'Цой'.encode('utf-8'),
            make_bytes('Цой'.encode('utf-8'))
        )

    def test_make_bytes_from_int(self):
        self.assertEqual(b'666', make_bytes(666))

    def test_make_bytes_from_none(self):
        self.assertEqual(b'None', make_bytes(None))

    def test_make_bytes_from_dict(self):
        self.assertEqual(b"{'foo': 'bar'}", make_bytes({'foo': 'bar'}))

    def test_make_str_from_bytes(self):
        self.assertEqual(
            'Цой',
            make_str('Цой'.encode('utf-8'))
        )

    def test_make_str_from_str(self):
        self.assertEqual('Цой', make_str('Цой'))

    def test_make_str_from_int(self):
        self.assertEqual('666', make_str(666))

    def test_make_str_from_none(self):
        self.assertEqual('None', make_str(None))
        
    def test_make_str_from_dict(self):
        self.assertEqual("{'foo': 'bar'}", make_str({'foo': 'bar'}))
