# coding: utf-8
from unittest import TestCase
from test_server import TestServer

from crawler import Crawler, Request
from .util import BaseTestCase

class BasicTestCase(BaseTestCase, TestCase):
    def test_single_request(self):

        class SimpleCrawler(Crawler):
            data = {}

            def handler_test(self, req, res):
                self.data['response'] = res.body

        token = b'Python'
        self.server.response['data'] = token

        bot = SimpleCrawler()
        bot.add_task(Request('test', url=self.server.get_url()))
        bot.run()
        self.assertEquals(token, bot.data['response'])

    def test_num_network_threads(self):
        """
        The idea of that test that each response handler should
        log number of active network threads.
        If num_network_threads=1 then logged numbers will contain only 0 or 1
        If num_network_threads=10 then logged numbers should contain 9 or 10
        """

        server = self.server

        class SimpleCrawler(Crawler):
            def init_hook(self):
                self.counters = []

            def task_generator(self):
                for x in range(20):
                    yield Request('test', url=server.get_url())

            def handler_test(self, req, res):
                self.counters.append(len([
                    x['active'] for x in self._net_threads.values()
                ]))

        bot = SimpleCrawler(num_network_threads=1)
        bot.run()
        self.assertEqual(len(bot.counters), 20)
        self.assertTrue(all(x in [0, 1] for x in bot.counters))

        bot = SimpleCrawler(num_network_threads=4)
        bot.run()
        self.assertEqual(len(bot.counters), 20)
        self.assertTrue(any(x in [3, 4] for x in bot.counters))
        self.assertFalse(any(x in [9, 10] for x in bot.counters))

        bot = SimpleCrawler(num_network_threads=10)
        bot.run()
        self.assertEqual(len(bot.counters), 20)
        self.assertTrue(any(x in [9, 10] for x in bot.counters))

    def test_prepare_method(self):

        server = self.server

        class SimpleCrawler(Crawler):
            def init_hook(self):
                self._urls_todo = [server.get_url()] * 10
                self.counter = 0

            def task_generator(self):
                for url in self._urls_todo:
                    yield Request('test', url=url)

            def handler_test(self, req, res):
                self.counter += 1

        bot = SimpleCrawler()
        bot.run()
        self.assertEqual(bot.counter, 10)

    def test_shutdown_hook(self):

        server = self.server

        class SimpleCrawler(Crawler):
            def init_hook(self):
                self.points = []

            def shutdown_hook(self):
                self.points.append('done')

            def task_generator(self):
                yield Request('test', url=server.get_url())

            def handler_test(self, req, res):
                self.points.append(res.body)

        self.server.response['data'] = 'Moon'
        bot = SimpleCrawler()
        bot.run()
        self.assertEqual(bot.points, [b'Moon', 'done'])

    def test_timeout(self):

        server = self.server

        class SimpleCrawler(Crawler):
            def init_hook(self):
                self.points = []
                self.errors = []

            def task_generator(self):
                yield Request('test', url=server.get_url(), timeout=0.1,
                              meta={'id': 1})
                yield Request('test', url=server.get_url(), timeout=1,
                              meta={'id': 2})

            def handler_test(self, req, res):
                self.points.append(req.meta['id'])

            def process_rejected_request(self, req, resp, ex):
                self.errors.append(req.meta['id'])

        self.server.response['sleep'] = 0.3
        bot = SimpleCrawler(network_try_limit=1)
        bot.run()
        self.assertEqual(set(bot.points), set([2]))
        self.assertEqual(set(bot.errors), set([1]))
