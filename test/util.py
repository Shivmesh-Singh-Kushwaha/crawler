# coding: utf-8
from contextlib import contextmanager
import time
import logging
from unittest import TestCase
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.parse import urlsplit
from threading import Thread
from tempfile import mkstemp
import os

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
        if 'X-Ping' in self.headers:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'pong')
        else:
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

    def address(self):
        return '%s:%d' % self.server_address


def start_proxy_server(host='127.0.0.1'):
    server = ProxyServer(
        (host, 0), ProxyRequestHandler
    )
    th = Thread(target=server.serve_forever)
    th.daemon = True
    th.start()

    # Wait for proxy server (not more than 1 second)
    for x in range(200):
        try:
            url = 'http://%s/' % server.address()
            req = Request(url, headers={'X-Ping': ''})
            urlopen(req, timeout=0.005)
        except OSError as ex:
            time.sleep(0.005)
        else:
            break
    else:
        raise Exception('Could not start proxy server')

    return th, server


class MemoryLoggingHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(MemoryLoggingHandler, self).__init__(*args, **kwargs)
        self._messages = []

    def emit(self, record):
        msg = self.format(record)
        self._messages.append(msg)


@contextmanager
def temp_file(root_dir=None):
    fdesc, file_ = mkstemp(dir=root_dir)
    yield file_
    os.close(fdesc)
    try:
        os.unlink(file_)
    except (IOError, OSError):
        if 'Windows' in platform.system():
            logger.error('Ignoring IOError raised when trying to delete'
                         ' temp file %s created in `temp_file` context'
                         ' manager', file_)
        else:
            raise
