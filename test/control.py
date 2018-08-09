# coding: utf-8
from unittest import TestCase
import multiprocessing
from threading import Thread
import time

from test_server import TestServer

from crawler import Crawler, Request
from .util import BaseTestCase

class BasicTestCase(BaseTestCase, TestCase):
    def test_shutdown_frozen_task_generator(self):

        class TestCrawler(Crawler):
            data = {}

            def task_generator(self):
                time.sleep(666)
                yield 'nevermind'

        def stop_bot(bot):
            time.sleep(0.5)
            bot.shutdown()

        bot = TestCrawler()

        th = Thread(target=stop_bot, args=[bot])
        th.start()

        bot.run()

        # Well if all test process is not frozen, it passed

    def test_shutdown_active_task_generator(self):

        server = self.server

        class TestCrawler(Crawler):
            data = {}

            def task_generator(self):
                while True:
                    yield Request('page', url=server.get_url())
                    time.sleep(0.1)

            def handler_page(self, req, res):
                pass

        def stop_bot(bot):
            time.sleep(1)
            bot.shutdown()

        bot = TestCrawler()

        th = Thread(target=stop_bot, args=[bot])
        th.start()

        bot.run()

        # Well if all test process is not frozen, it passed

    def test_worker_network_kill_signal(self):

        class TestCrawler(Crawler):
            def task_generator(self):
                time.sleep(666)
                yield None

        bot = TestCrawler(num_network_threads=3)
        th = Thread(target=bot.run)
        th.start()
        
        time.sleep(0.5)
        self.assertEqual(3, len([
                x for x in bot._net_threads.values()
                if x['thread'].is_alive()
            ]))
        [bot._request_queue.put('kill') for x in bot._net_threads]

        time.sleep(0.5)
        self.assertEqual(0, len([
                x for x in bot._net_threads.values()
                if x['thread'].is_alive()
            ]))

        bot.shutdown()
