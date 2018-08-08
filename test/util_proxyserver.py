# coding: utf-8
from unittest import TestCase
from test_server import TestServer
from urllib.request import build_opener, ProxyHandler

from crawler import Crawler, Request
from .util import BaseTestCase, ProxyServer, start_proxy_server

class BasicTestCase(BaseTestCase,TestCase):
    def setUp(self):
        super(BasicTestCase, self).setUp()

        th, server = start_proxy_server()
        self.proxy_server = server

    def test_proxy_server_get(self):

        self.server.response['data'] = 'foo'

        proxies = {
            'http': ('%s:%s' % self.proxy_server.server_address),
        }
        opener = build_opener(ProxyHandler(proxies))
        res = opener.open(self.server.get_url())
        data = res.read()

        self.assertEqual(b'foo', data)
        self.assertEqual(1, self.proxy_server.num_requests)

    #def test_proxy_server_post(self):

    #    self.server.response['data'] = 'foo'

    #    proxies = {
    #        'http': ('%s:%s' % self.proxy_server.server_address),
    #    }
    #    opener = build_opener(ProxyHandler(proxies))
    #    res = opener.open(self.server.get_url(), data=b'send-foo')
    #    data = b''#res.read()

    #    self.assertEqual(b'foo', data)
    #    self.assertEqual(1, self.proxy_server.num_requests)
