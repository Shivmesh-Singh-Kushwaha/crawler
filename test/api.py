# coding: utf-8
import time
from unittest import TestCase
import multiprocessing
from threading import Thread, Event
from urllib.request import urlopen, HTTPError
import json

from test_server import TestServer

from crawler import Crawler, Request
from .util import BaseTestCase

class BasicTestCase(BaseTestCase, TestCase):
    def test_api_get_info(self):

        server = self.server

        class TestCrawler(Crawler):
            def init_hook(self):
                self.unfreeze = Event()

            def task_generator(self):
                yield Request('page', url=server.get_url())
                self.unfreeze.wait()

            def handler_page(self, req, res):
                pass

        bot = TestCrawler()
        th = Thread(target=bot.run)
        th.daemon = True
        th.start()
        while bot.stat.counters['parser:handler-page'] == 0:
            time.sleep(0.01)

        res = urlopen('http://%s/api/info' % bot.api_server.address())
        data = json.loads(res.read().decode('utf-8'))
        self.assertEqual(
            data['counters']['parser:handler-page'],
            1
        )
        bot.unfreeze.set()

    def test_api_stop(self):

        server = self.server

        class TestCrawler(Crawler):
            def task_generator(self):
                yield Request('page', url=server.get_url())

            def handler_page(self, req, res):
                yield Request('page', url=server.get_url())

        bot = TestCrawler()
        th = Thread(target=bot.run)
        th.daemon = True
        th.start()
        while bot.stat.counters['parser:handler-page'] == 0:
            time.sleep(0.01)

        res = urlopen('http://%s/api/stop' % bot.api_server.address())
        self.assertEqual({}, json.loads(res.read().decode('utf-8')))
        th.join(1)
        self.assertEqual(False, th.is_alive())

    def test_api_home_page(self):

        server = self.server

        class TestCrawler(Crawler):
            def init_hook(self):
                self.unfreeze = Event()

            def task_generator(self):
                yield Request('page', url=server.get_url())
                self.unfreeze.wait()

            def handler_page(self, req, res):
                pass

        bot = TestCrawler()
        th = Thread(target=bot.run)
        th.daemon = True
        th.start()
        while bot.stat.counters['parser:handler-page'] == 0:
            time.sleep(0.01)

        res = urlopen('http://%s/' % bot.api_server.address())
        data = res.read().decode('utf-8')
        self.assertTrue(
            'unpkg.com/vue/dist/vue.js' in data
        )
        bot.unfreeze.set()

    def test_api_not_found(self):

        server = self.server

        class TestCrawler(Crawler):
            def init_hook(self):
                self.unfreeze = Event()

            def task_generator(self):
                yield Request('page', url=server.get_url())
                self.unfreeze.wait()

            def handler_page(self, req, res):
                pass

        bot = TestCrawler()
        th = Thread(target=bot.run)
        th.daemon = True
        th.start()
        while bot.stat.counters['parser:handler-page'] == 0:
            time.sleep(0.01)

        self.assertRaises(
            HTTPError, urlopen, 'http://%s/preved/medved' % bot.api_server.address()
        )
        bot.unfreeze.set()
