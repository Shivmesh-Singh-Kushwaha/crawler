import aiohttp
import asyncio
from asyncio import Queue, QueueEmpty
import logging

from .request import Request
from .response import Response


logger = logging.getLogger('iob.base')

class Crawler(object):
    def __init__(self, concurrency=10):
        self._loop = asyncio.get_event_loop()
        self._task_queue = asyncio.Queue(maxsize=concurrency * 2)
        self._concurrency = concurrency
        self._free_workers = asyncio.Semaphore(value=concurrency)
        self._workers = {}

    def run(self):
        self._loop.run_until_complete(self.main_loop())

    @asyncio.coroutine
    def task_generator_processor(self):
        for task in self.task_generator():
            yield from self._task_queue.put(task)

    def add_task(self, task):
        for x in self._task_queue.put(task):
            pass

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
            elif req.tag and req.tag in self._handlers:
                self._handlers[req.tag](req, res)

    def register_handlers(self):
        self._handlers = {}
        for key in dir(self):
            if key.startswith('handler_'):
                thing = getattr(self, key)
                if callable(thing):
                    handler_tag = key[8:]
                    self._handlers[handler_tag] = thing

    def process_done_worker(self, worker):
        self._free_workers.release()
        del self._workers[id(worker)]

    @asyncio.coroutine
    def worker_manager(self):
        while True:
            task = yield from self._task_queue.get()
            ok = yield from self._free_workers.acquire()
            worker = self._loop.create_task(self.perform_request(task))
            worker.add_done_callback(self.process_done_worker)
            self._workers[id(worker)] = worker

    @asyncio.coroutine
    def main_loop(self):
        self.register_handlers()
        task_gen_future = self._loop.create_task(self.task_generator_processor())
        worker_man_future = self._loop.create_task(self.worker_manager())
        self._main_loop_enabled = True
        while self._main_loop_enabled:
            if (not len(self._workers)
                and task_gen_future.done()
                and not self._task_queue.qsize()):
                self._main_loop_enabled = False
            else:
                yield from asyncio.sleep(0.5)
        worker_man_future.cancel()
        self.shutdown()

    def shutdown(self):
        logger.debug('Work done!')

    def task_generator(self):
        if False:
            yield None
