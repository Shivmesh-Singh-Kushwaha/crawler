import aiohttp
import asyncio
import logging
import janus
from queue import Empty
import multiprocessing
from threading import Thread

from .request import Request
from .response import Response
from .error import UnknownTaskType


__all__ = ('Crawler',)
logger = logging.getLogger('crawler.base')


class Crawler(object):
    def __init__(self, num_network_threads=10):
        self._loop = asyncio.get_event_loop()
        self._num_network_threads = num_network_threads
        self._request_queue = janus.Queue(loop=self._loop, maxsize=self._num_network_threads)
        # Number of parser should be num of cores divided by 2 because of hyperthreading
        self._num_parsers = max(1, multiprocessing.cpu_count() // 2)
        self._response_queue = janus.Queue(loop=self._loop, maxsize=self._num_parsers)
        self._free_network_threads = asyncio.Semaphore(value=self._num_network_threads)
        self._network_threads = {}
        self._parser_errors = janus.Queue(loop=self._loop)
        self.init_hook()

    def init_hook(self):
        pass

    def shutdown_hook(self):
        pass

    def run(self):
        self._loop.run_until_complete(self.main_loop())

    async def task_generator_processor(self):
        for task in self.task_generator():
            print('TASK', task)
            if isinstance(task, Request):
                await self._request_queue.async_q.put(task)
            else:
                raise UnknownTaskType('Unknown task got from task_generator: '
                                      '%s' % task)

    def add_task(self, task):
        self._request_queue.sync_q.put(task)

    async def perform_request(self, req):
        logging.debug('GET {}'.format(req.url))
        async with aiohttp.ClientSession() as session:
            try:
                    io_res = await asyncio.wait_for(
                        session.request('get', req.url),
                        req.timeout
                    )
            except Exception as ex:
                self.process_failed_request(req, ex)
            else:
                try:
                    body = await io_res.read()
                except Exception as ex:
                    self.process_failed_request(req, ex)
                else:
                    res = Response(
                        body=body,
                        # TODO: use effective URL (in case of redirect)
                        url=req.url,
                    )
                    await self._response_queue.async_q.put((req, res))

    def process_failed_request(self, req, ex):
        logging.error('', exc_info=ex)

    def register_handlers(self):
        self._handlers = {}
        for key in dir(self):
            if key.startswith('handler_'):
                thing = getattr(self, key)
                if callable(thing):
                    handler_tag = key[8:]
                    self._handlers[handler_tag] = thing

    def request_completed_callback(self, worker):
        self._free_network_threads.release()
        del self._network_threads[id(worker)]

    async def network_manager(self):
        while True:
            task = await self._request_queue.async_q.get()
            await self._free_network_threads.acquire()
            worker = self._loop.create_task(self.perform_request(task))
            worker.add_done_callback(self.request_completed_callback)
            self._network_threads[id(worker)] = worker

    def parser_thread(self):
        while True:
            try:
                req, resp = self._response_queue.sync_q.get()#True, 0.1)
            except Empty:
                pass
            else:
                handler = self._handlers[req.tag]
                ## Call handler with arguments: request, response
                ## Handler result could be generator or simple function
                ## If handler is simple function then it must return None
                try:
                    hdl_result = handler(req, resp)
                    if hdl_result is not None:
                        for item in hdl_result:
                            assert isinstance(item, Request)
                            self._request_queue.sync_q.put(item)
                except Exception as ex:
                    logging.exception('Exception in parser')
                    self._parser_errors.sync_q.put(ex)


    def start_parsers(self):
        pool = []
        for _ in range(self._num_parsers):
            th = Thread(target=self.parser_thread)
            th.daemon = True
            th.start()
            pool.append(th)
        return pool

    async def errors_monitor(self):
        ex = await self._parser_errors.async_q.get()
        if ex:
            raise ex

    async def shutdown(self):
        # TODO: stop all processes
        self._main_loop_enabled = False

    async def main_loop(self):
        self.register_handlers()
        task_generator_fut = self._loop.create_task(
            self.task_generator_processor())
        network_manager_future = self._loop.create_task(self.network_manager())
        pool = self.start_parsers()
        self._main_loop_enabled = True
        self._loop.create_task(self.errors_monitor())
        try:
            while self._main_loop_enabled:
                if task_generator_fut.done():
                    if task_generator_fut.exception():
                        raise task_generator_fut.exception()
                    if (
                            not len(self._network_threads)
                            and
                            not self._request_queue.async_q.qsize()
                        ):
                        self._main_loop_enabled = False
                await asyncio.sleep(0.05)
        finally:
            network_manager_future.cancel()
            self.shutdown_hook()

    def task_generator(self):
        if False:
            yield None
