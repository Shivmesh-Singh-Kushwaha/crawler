import time
import logging
from queue import Empty
import multiprocessing
from threading import Thread, Event, get_ident, current_thread

from queue import Queue, Empty

from .request import Request
from .response import Response
from .stat import Stat
from .error import CrawlerError
from .curl_transport import CurlTransport, NetworkError
from .api import start_api_server_thread


__all__ = ('Crawler',)
logger = logging.getLogger('crawler.base')
control_logger = logging.getLogger('crawler.control')


class Crawler(object):
    def __init__(
            self,
            num_network_threads=10,
            num_parsers=None,
            network_try_limit=10,
            task_try_limit=10,
            meta=None,
        ):
        self._meta = meta if meta is not None else {}
        self.config = {
            'num_network_threads': num_network_threads,
            # Number of parser should be num of cores
            # divided by 2 because of hyperthreading
            'num_parsers': (
                num_parsers if num_parsers is not None
                else max(1, multiprocessing.cpu_count() // 2)
            ),
            'network_try_limit': network_try_limit,
            'task_try_limit': task_try_limit,
        }
        self._request_queue = Queue(
            maxsize=0,#self.config['num_network_threads']
        )
        self._response_queue = Queue(
            maxsize=self.config['num_parsers'],
        )
        self._fatal_errors = Queue()
        self._stat = Stat()
        self.network_transport = CurlTransport()
        self._work_allowed = True
        self._resume_event = Event()
        self._net_threads = {}
        self._parser_threads = {}
        self.init_hook()

    def init_hook(self):
        pass

    def shutdown_hook(self):
        pass

    def task_generator(self):
        if False:
            yield None

    def worker_task_generator(self):
        """
        Put new requests from task generator into request queue
        Make a pause if there are more than (10 * number of network threads)
        requests in queue.
        """
        try:
            gen = self.task_generator()
            while True:
                if not self._work_allowed:
                    return
                if self._request_queue.qsize() > (10 * self.config['num_network_threads']):
                    time.sleep(0.1)
                try:
                    task = next(gen)
                except StopIteration:
                    break
                else:
                    if isinstance(task, Request):
                        self._request_queue.put(task)
                    else:
                        raise CrawlerError(
                            'Unknown task got from task_generator: %s' % task
                        )
        except Exception as ex:
            self._fatal_errors.put(ex)

    def add_task(self, task):
        self._request_queue.put(task)

    def worker_network(self):
        while True:
            req = self._request_queue.get()
            if req == 'kill':
                return
            #print('GOT NETWORK REQ', req.url)
            self._net_threads[id(current_thread())]['active'] = True
            logging.debug('GET %s' % req.url)
            try:
                try:
                    resp = self.network_transport.process_request(req)
                except NetworkError as ex:
                    #print('NET ERROR (%s) %s' % (ex, req.url))
                    req.network_try_count += 1
                    if req.network_try_count > self.config['network_try_limit']:
                        self._stat.store(
                            'network_try_limit', '%s|%s' % (req.url, ex)
                        )
                        self.process_rejected_request(req, None, ex)
                    else:
                        self._request_queue.put(req)
                except Exception as ex:
                    #print('UNEXPECTED ERROR (%s) %s' % (ex, req.url))
                    self._fatal_errors.put(ex)
                else:
                    #print('Sending response to queue: %s' % req.url)
                    self._response_queue.put((req, resp))
            finally:
                #print('Finish processing %s' % req.url)
                self._net_threads[id(current_thread())]['active'] = False


    def process_rejected_request(self, req, resp, ex):
        pass

    def register_handlers(self):
        self._handlers = {}
        for key in dir(self):
            if key.startswith('handler_'):
                thing = getattr(self, key)
                if callable(thing):
                    handler_tag = key[8:]
                    self._handlers[handler_tag] = thing

    def worker_parser(self):
        while True:
            task = self._response_queue.get()
            if task == 'pause':
                self._parser_threads[id(current_thread())]['paused'] = True
                self._resume_event.wait()
                self._parser_threads[id(current_thread())]['paused'] = False
            elif task == 'kill':
                return
            else:
                req, resp = task
                handler = self._handlers[req.tag]
                ## Call handler with arguments: request, response
                ## Handler result could be generator or simple function
                ## If handler is simple function then it must return None
                try:
                    hdl_result = handler(req, resp)
                    if hdl_result is not None:
                        for item in hdl_result:
                            assert isinstance(item, Request)
                            self._request_queue.put(item)
                except Exception as ex:
                    logging.exception('Exception in parser')
                    self._fatal_errors.put(ex)

    def start_threads(self, pool, num, func, daemon=False, args=None, kwargs=None):
        for _ in range(num):
            th = Thread(target=func, args=(args or ()), kwargs=(kwargs or {}))
            th.daemon = daemon
            pool[id(th)] = {
                'thread': th,
                'active': False,
                'paused': False,
            }
            th.start()

    def shutdown(self):
        # TODO: stop all processes
        self._work_allowed = False

    def run(self):
        self.register_handlers()

        task_generator_thread = Thread(target=self.worker_task_generator)
        task_generator_thread.daemon = True
        task_generator_thread.start()

        th, address = start_api_server_thread(self)
        with open('var/api_url.txt', 'w') as out:
            out.write('http://%s:%d/' % address)

        self.start_threads(
            self._net_threads,
            self.config['num_network_threads'],
            self.worker_network
        )
        self.start_threads(
            self._parser_threads,
            self.config['num_parsers'],
            self.worker_parser,
        )
        try:
            while self._work_allowed:
                try:
                    ex = self._fatal_errors.get(True, 0.01)
                except Empty:
                    pass
                else:
                    raise ex
                #print('main loop')
                if not task_generator_thread.is_alive():
                    if (
                            not self._request_queue.qsize()
                            and not self._response_queue.qsize()
                        ):
                        control_logger.debug('pause')
                        [self._response_queue.put('pause')
                            for x in self._parser_threads]
                        while any(
                                not x['paused']
                                for x in self._parser_threads.values()
                            ):
                            control_logger.debug('wait all parser threads is paused')
                            time.sleep(0.001)
                        control_logger.debug('all parsers are paused')
                        # At this point task generator is not active
                        # and all parsers are paused
                        # => nobody can put new tasks into request queue
                        # => if all net threads are not active then
                        # it is time to shutdown system
                        if (
                                not self._request_queue.qsize()
                                and not self._response_queue.qsize()
                                and all(
                                    not x['active']
                                    for x in self._net_threads.values()
                                )
                            ):
                            control_logger.debug('Shutdown allowed')
                            self._work_allowed = False
                        # Unpause parsers to allow them to process
                        # new data (shutdown procedure also requires this)
                        control_logger.debug('Unpausing')
                        self._resume_event.set()
                        control_logger.debug('Wating all parsers unpaused')
                        while any(
                                x['paused']
                                for x in self._parser_threads.values()
                            ):
                            control_logger.debug('wait all parser threads is un-paused')
                            time.sleep(0.001)
                        self._resume_event.clear()
        finally:
            control_logger.debug('Inside finally')
            for x in range(self.config['num_network_threads']):
                self._request_queue.put('kill')
            for x in range(self.config['num_parsers']):
                self._response_queue.put('kill')
            # Wait for threads with `.join(timeout)`
            # If timeout happens threads will stop anyway
            # because they are `.daemon=True`
            control_logger.debug('Waiting for net threads')
            [x['thread'].join(1) for x in self._net_threads.values()]
            control_logger.debug('Waiting for parser threads')
            [x['thread'].join(1) for x in self._parser_threads.values()]
            # Last check for some unhandled fatal exceptions
            try:
                ex = self._fatal_errors.get(block=False)
            except Empty:
                pass
            else:
                raise ex
            self.shutdown_hook()
