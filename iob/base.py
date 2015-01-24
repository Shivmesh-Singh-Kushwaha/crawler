import aiohttp
import asyncio
from asyncio import Queue, QueueEmpty
import logging


logger = logging.getLogger('iob.base')

class Request(object):
    def __init__(self, url, callback=None, tag=None):
        self.url = url
        self.callback = callback
        self.tag = tag


class Response(object):
    def __init__(self, body):
        self.body = body


class Crawler(object):
    def __init__(self, concurrency=10):
        self._loop = asyncio.get_event_loop()
        self._task_queue = asyncio.Queue(maxsize=concurrency * 2)
        self._concurrency = concurrency

    def run(self):
        self._loop.run_until_complete(self.main_loop())

    @asyncio.coroutine
    def task_generator_processor(self):
        for task in self.task_generator():
            yield from self._task_queue.put(task)
        self._task_generator_enabled = False

    def start_task_generator(self):
        self._task_generator_enabled = True
        self._loop.create_task(self.task_generator_processor())

    @asyncio.coroutine
    def perform_request(self, req):
        logging.debug('Requesting {}'.format(req.url))
        try:
            io_res = yield from aiohttp.request('get', req.url)
        except Exception as ex:
            logging.error('', exc_info=ex)
        else:
            try:
                body = yield from io_res.text()
            except Exception as ex:
                logging.error('', exc_info=ex)
                body = ''
            res = Response(
                body=body,
            )
            if req.callback:
                req.callback(req, res)
            elif req.tag and req.tag in self._request_handlers:
                self._request_handlers[req.tag](req, res)

    def register_request_handlers(self):
        handlers = {}
        for key in dir(self):
            if key.startswith('handler_'):
                thing = getattr(self, key)
                if callable(thing):
                    handler_tag = key[8:]
                    handlers[handler_tag] = thing
        self._request_handlers = handlers

    @asyncio.coroutine
    def main_loop(self):
        self.start_task_generator()
        self.register_request_handlers()
        workers = []
        self._main_loop_enabled = True
        while self._main_loop_enabled:
            workers = [x for x in workers if not x.done()]
            if len(workers) < self._concurrency:
                try:
                    task = self._task_queue.get_nowait()
                except QueueEmpty:
                    if len(workers) == 0 and not self._task_generator_enabled:
                        self._main_loop_enabled = False
                else:
                    worker = self._loop.create_task(self.perform_request(task))
                    workers.append(worker)

            # TODO: Refactor this code to avoid explicit sleep
            yield from asyncio.sleep(0.001)
