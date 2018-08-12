import logging
import os
import json
from threading import Thread

import psutil

from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger('crawler.api')
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


class ApiRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self): # pylint: disable=invalid-name
        if self.path == '/':
            self.home()
        elif self.path == '/api/info':
            self.api_info()
        elif self.path == '/api/stop':
            self.api_stop()
        else:
            self.not_found()

    def response(self, code=200, content=b'',
                 content_type='text/html; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)

    def not_found(self):
        self.response(404)

    def api_info(self):
        pid = os.getpid()
        proc = psutil.Process(pid)
        mem = proc.memory_info()
        info = {
            'counters': self._bot.stat.counters,
            #'collections': dict((x, len(y)) for (x, y)
            #                    in self._bot.stat.collections.items()),
            'num_network_threads': self._bot.config['num_network_threads'],
            'num_parsers': self._bot.config['num_parsers'],
            'request_queue_size': self._bot._request_queue.qsize(),
            'response_queue_size': self._bot._response_queue.qsize(),
            'rss_memory_mb': round(mem.rss / (1024 * 1024), 1)
            #'task_dispatcher_input_queue': (
            #    self._bot.task_dispatcher.input_queue.qsize()
            #),
            #'parser_service_input_queue': (
            #    self._bot.parser_service.input_queue.qsize()
            #),
            #'network_service_active_threads': (
            #    self._bot.network_service.get_active_threads_number()
            #),
            #'cache_reader_input_queue': (
            #    self._bot.cache_reader_service.input_queue.size()
            #    if self._bot.cache_reader_service else '--'
            #),
            #'cache_writer_input_queue': (
            #    self._bot.cache_writer_service.input_queue.qsize()
            #    if self._bot.cache_writer_service else '--'
            #),
        }
        content = json.dumps(info).encode('utf-8')
        self.response(content=content)

    def api_stop(self):
        content = json.dumps({}).encode('utf-8')
        self.response(content=content)
        self._bot.shutdown()

    def home(self):
        html_file = os.path.join(PACKAGE_DIR, 'static/api.html')
        content = open(html_file, 'rb').read()
        self.response(content=content)


class ReuseTCPServer(HTTPServer):
    allow_reuse_address = True

    def server_activate(self):
        super(ReuseTCPServer, self).server_activate()
        logger.debug(
            'API server listens on http://%s:%d/' % self.server_address
        )

    def address(self):
        return '%s:%d' % self.server_address


def build_api_server(bot):
    ApiRequestHandler._bot = bot
    server = ReuseTCPServer(
        ("127.0.0.1", 0), ApiRequestHandler
    )
    return server
