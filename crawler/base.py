from copy import deepcopy
import os.path
import time
import logging
from queue import Empty
import multiprocessing
from threading import Thread, Event, get_ident, current_thread
from queue import Queue, Empty
from collections import deque

from weblib.error import RequiredDataNotFound

from .request import Request
from .response import Response
from .stat import Stat
from .error import CrawlerError, CrawlerBadStatusCode, CrawlerFatalError
from .curl_transport import CurlTransport, CrawlerNetworkError
from .api import build_api_server
from .proxylist import ProxyList


__all__ = ('Crawler',)
logger = logging.getLogger('crawler.base')
control_logger = logging.getLogger('crawler.control')
network_logger = logging.getLogger('crawler.network')
stat_logger = logging.getLogger('crawler.stat')


class Crawler(object):
    def __init__(
            self,
            num_network_threads=10,
            num_parsers=None,
            try_limit=10,
            meta=None,
            speed_metrics=None,
            proxylist_type='http',
            proxylist_file=None,
            proxylist_url=None,
            proxylist_reload_time=(60 * 10),
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
            'try_limit': try_limit,
            'speed_metrics': (
                speed_metrics if speed_metrics is not None
                else ['network:request', 'network:request-ok']
            ),
            'proxylist_type': proxylist_type,
            'proxylist_file': proxylist_file,
            'proxylist_url': proxylist_url,
            'proxylist_reload_time': proxylist_reload_time,
        }
        self._request_queue = Queue(
            maxsize=0,#self.config['num_network_threads']
        )
        self._response_queue = Queue(
            maxsize=self.config['num_parsers'],
        )
        self._fatal_errors = Queue()
        self.stat = Stat()
        self.network_transport = CurlTransport()
        self._work_allowed = True
        self._resume_event = Event()
        self._net_threads = {}
        self._parser_threads = {}
        self.proxylist = None
        if self.config['proxylist_file']:
            self.proxylist = ProxyList.from_file(
                self.config['proxylist_file'],
                proxy_type=self.config['proxylist_type'],
            )
        if self.config['proxylist_url']:
            self.proxylist = ProxyList.from_url(
                self.config['proxylist_url'],
                proxy_type=self.config['proxylist_type'],
            )
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

    def process_request_proxy(self, req):
        if self.proxylist:
            proxy = self.proxylist.random_server()
            req.proxy = proxy.address()
            req.proxy_auth = proxy.auth()
            req.proxy_type = proxy.proxy_type

    def worker_network(self):
        try:
            while True:
                req = self._request_queue.get()
                if req == 'kill':
                    return
                if not isinstance(req, Request):
                    raise CrawlerError('Network thread got request of unexpected type: %s' % req)
                #print('GOT NETWORK REQ', req.url)
                self._net_threads[id(current_thread())]['active'] = True
                if req.proxy:
                    via_proxy = ' via %s proxy %s' % (req.proxy_type, req.proxy)
                else:
                    via_proxy = ''
                network_logger.debug('GET %s%s' % (req.url, via_proxy))
                try:
                    self.stat.inc('network:request')
                    self.stat.inc('network:request-%s' % req.tag)
                    net_error = None
                    try:
                        self.process_request_proxy(req)
                        resp = self.network_transport.process_request(req)
                    except CrawlerNetworkError as ex:
                        net_error = ex
                    else:
                        if (
                                resp.code >= 400
                                and resp.code != 404
                                and resp.code not in resp.extra_valid_codes
                            ):
                            net_error = CrawlerBadStatusCode

                    if net_error:
                        self.stat.inc('network:request-error')
                        self.stat.inc('network:request-error-%s' % req.tag)
                        #print('NET ERROR (%s) %s' % (ex, req.url))
                        req.try_count += 1
                        if req.try_count > self.config['try_limit']:
                            self.stat.store(
                                'try_rejected', '%s|%s' % (req.url, net_error)
                            )
                            self.process_rejected_request(req, None, net_error)
                        else:
                            self._request_queue.put(req)
                    else:
                        #print('Sending response to queue: %s' % req.url)
                        self.stat.inc('network:request-ok')
                        self.stat.inc('network:request-ok-%s' % req.tag)
                        self.stat.inc('network:bytes_downloaded', resp.bytes_downloaded)
                        self.stat.inc('network:bytes_uploaded', resp.bytes_uploaded)
                        self._response_queue.put((req, resp))
                finally:
                    #print('Finish processing %s' % req.url)
                    self._net_threads[id(current_thread())]['active'] = False
        except Exception as ex:
            self._fatal_errors.put(ex)


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
        try:
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
                    self.stat.inc('parser:handler-%s' % req.tag)
                    try:
                        hdl_result = handler(req, resp)
                        if hdl_result is not None:
                            for item in hdl_result:
                                assert isinstance(item, Request)
                                self._request_queue.put(item)
                    except RequiredDataNotFound as ex:
                        req.try_count += 1
                        if req.try_count > self.config['try_limit']:
                            self.stat.store(
                                'try_rejected', '%s|%s' % (req.url, ex)
                            )
                            self.process_rejected_request(req, resp, ex)
                        else:
                            self.stat.inc('parser:request-data-retry')
                            self.stat.inc(
                                'parser:request-data-retry-%s' % req.tag
                            )
                            self._request_queue.put(req)
                    except Exception as ex:
                        logging.exception('Response handler error')
                        #self._fatal_errors.put(ex)
                        self.stat.store('handler_error', '%s|%s|%s|%s' % (
                            req.tag, ex.__class__.__name__, str(ex), req.url
                        ))
        except Exception as ex:
            self._fatal_errors.put(ex)

    def start_threads(
            self, pool, num, func, daemon=False, args=None, kwargs=None
        ):
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

    def worker_stat(self):
        try:
            history = []
            minute_shots = deque(maxlen=12)
            sleep_time = 1
            while self._work_allowed:
                history_ts = None
                if history_ts is None or time.time() - history_ts >= 60:
                    shot = deepcopy(self.stat.counters)
                    history.append(shot)
                speed_shot = {
                    x: self.stat.counters[x]
                    for x in self.config['speed_metrics']
                }
                minute_shots.append(speed_shot)
                avg_speed = {}
                if len(minute_shots) > 1:
                    for key in self.config['speed_metrics']:
                        alias = {
                            'network:request': 'req',
                            'network:request-ok': 'req-ok',
                        }.get(key, key)
                        avg_speed[alias] = (
                            (minute_shots[-1][key] - minute_shots[0][key])
                            / (sleep_time * (len(minute_shots) - 1))
                        )
                    ignore_prefixes = ('network:', 'parser:')
                    output = '%s [%s]' % (
                        ', '.join('%s: %d/s' % x for x in avg_speed.items()),
                        ', '.join(
                            '%s: %d' % x for x in self.stat.counters.items()
                            if not x[0].startswith(ignore_prefixes)
                        ),
                    )
                    stat_logger.debug(output)
                time.sleep(sleep_time)

        except Exception as ex:
            self._fatal_errors.put(ex)

    def worker_proxylist(self):
        try:
            while self._work_allowed:
                time.sleep(self.config['proxylist_reload_time'])
                try:
                    self.proxylist.reload()
                except Exception as ex:
                    self.stat.inc('proxylist:reload-error')
                    logging.exception('Failed to reload proxy list')
                else:
                    self.stat.inc('proxylist:reload-ok')
        except Exception as ex:
            self._fatal_errors.put(ex)

    def run(self):
        self.register_handlers()

        task_generator_thread = Thread(target=self.worker_task_generator)
        task_generator_thread.daemon = True
        task_generator_thread.start()

        stat_thread = Thread(target=self.worker_stat)
        stat_thread.daemon = True
        stat_thread.start()

        if self.proxylist:
            proxylist_thread = Thread(target=self.worker_proxylist)
            proxylist_thread.daemon = True
            proxylist_thread.start()

        api_server = build_api_server(self)
        api_thread = Thread(target=api_server.serve_forever)
        api_thread.daemon = True
        api_thread.start()

        if os.path.exists('var') and os.path.isdir('var'):
            with open('var/api_url.txt', 'w') as out:
                out.write('http://%s/' % api_server.address())

        self.start_threads(
            self._net_threads,
            self.config['num_network_threads'],
            self.worker_network,
            daemon=True
        )
        self.start_threads(
            self._parser_threads,
            self.config['num_parsers'],
            self.worker_parser,
            daemon=True
        )
        try:
            while self._work_allowed:
                try:
                    ex = self._fatal_errors.get(True, 0.01)
                except Empty:
                    pass
                else:
                    raise CrawlerFatalError() from ex
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
            api_server.shutdown()
            control_logger.debug('Inside finally')
            ## for x in range(self.config['num_network_threads']):
            ##     self._request_queue.put('kill')
            ## for x in range(self.config['num_parsers']):
            ##     self._response_queue.put('kill')
            ## # Wait for threads with `.join(timeout)`
            ## # If timeout happens threads will stop anyway
            ## # because they are `.daemon=True`
            ## control_logger.debug('Waiting for net threads')
            ## [x['thread'].join(1) for x in self._net_threads.values()]
            ## control_logger.debug('Waiting for parser threads')
            ## [x['thread'].join(1) for x in self._parser_threads.values()]
            #  Last check for some unhandled fatal exceptions
            #try:
            #    ex = self._fatal_errors.get(block=False)
            #except Empty:
            #    pass
            #else:
            #    raise CrawlerFatalError() from ex
            self.shutdown_hook()
            logger.debug('done')
