# coding: utf-8
from unittest import TestCase
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.parse import urlsplit
from threading import Thread

from test_server import TestServer


class BaseTestCase(object):
    @classmethod
    def setUpClass(cls):
        cls.server = TestServer(port=9876)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.server.reset()


class ProxyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.process_request('GET')

    #def do_POST(self):
    #    self.process_request('POST')

    def process_request(self, method):
        host = self.headers['host']
        url_parts = urlsplit(self.path)
        req_url = 'http://%s%s' % (host, url_parts.path or '/')
        if url_parts.query:
            req_url += '?%s' % url_parts.query
        if method == 'GET':
            req_data = None
        else:
            req_data = self.rfile.read()
        req = Request(req_url)
        for key, val in self.headers.items():
            req.add_header(key, val)
        resp = urlopen(req, data=req_data)

        data = resp.read()

        self.send_response(200)
        for key, val in resp.info().items():
            if key.lower() == 'transfer-encoding':
                pass
            else:
                self.send_header(key, val)
        self.end_headers()
        self.wfile.write(data)
        self.server.num_requests += 1


class ProxyServer(HTTPServer):
    allow_reuse_address = True
    num_requests = 0


def start_proxy_server(host='127.0.0.1'):
    server = ProxyServer(
        (host, 0), ProxyRequestHandler
    )
    th = Thread(target=server.serve_forever)
    th.daemon = True
    th.start()
    return th, server
