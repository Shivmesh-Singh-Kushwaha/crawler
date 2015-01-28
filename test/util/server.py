import asyncio
from aiohttp import web
from threading import Thread
import time
import urllib.request
from urllib.parse import urljoin
from urllib.error import URLError

class DebugServer(object):
    def __init__(self, ip='127.0.0.1', port=9999):
        self.port = port
        self.ip = ip
        self.loop = asyncio.new_event_loop()
        self.app = web.Application(loop=self.loop)
        self.app.router.add_route('GET', '/', self.handler)
        self.app.router.add_route('GET', '/stop', self.stop_handler)
        self.reset()

    def reset(self):
        self.response = {
            'body': '',
        }

    @asyncio.coroutine
    def handler(self, request):
        return web.Response(body=self.response['body'].encode('utf-8'))

    @asyncio.coroutine
    def stop_handler(self, request):
        self.loop.stop()
        return web.Response(body=b'')

    def server_thread(self):
        fut = self.loop.create_server(self.app.make_handler(), self.ip, self.port)
        srv = self.loop.run_until_complete(fut)
        print('Serving on', srv.sockets[0].getsockname())
        self.loop.run_forever()

    def start(self):
        th = Thread(target=self.server_thread)
        th.start()
        # Wait for server to be ready
        for x in range(30):
            try:
                urllib.request.urlopen(self.get_url()).read()
            except URLError:
                time.sleep(0.01)
            else:
                break


    def stop(self):
        urllib.request.urlopen(self.get_url('/stop')).read()
        self.loop.stop()

    def get_url(self, extra=''):
        return urljoin('http://{}:{}/'.format(self.ip, self.port), extra)


server = DebugServer()
