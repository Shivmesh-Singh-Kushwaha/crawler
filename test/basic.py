# coding: utf-8
from unittest import TestCase

from test.util.server import server
from iob import Crawler, Request


class BasicTestCase(TestCase):
    def setUp(self):
        server.reset()

    def test_single_request(self):

        class SimpleCrawler(Crawler):
            data = {}

            def handler_test(self, req, res):
                self.data['response'] = res.body

        token = 'Python'
        server.response['body'] = token

        bot = SimpleCrawler()
        bot.add_task(Request('test', url=server.get_url()))
        bot.run()
        self.assertEquals(token, bot.data['response'])

    def test_concurrency(self):
        """
        The idea of that test that each response handler should
        logs the number of active network operations.
        If concurrency=1 then logged numbers will contain only 0 or 1
        If concurrency=10 then logged numbers should contain 9 or 10
        """

        class SimpleCrawler(Crawler):
            def prepare(self):
                self.counters = []

            def task_generator(self):
                for x in range(10):
                    yield Request('test', url=server.get_url())

            def handler_test(self, req, res):
                self.counters.append(len(self._workers))

        bot = SimpleCrawler(concurrency=1)
        bot.run()
        self.assertEqual(len(bot.counters), 10)
        self.assertTrue(all(x in [0, 1] for x in bot.counters))

        bot = SimpleCrawler(concurrency=4)
        bot.run()
        self.assertEqual(len(bot.counters), 10)
        self.assertTrue(any(x in [3, 4] for x in bot.counters))
        self.assertFalse(any(x in [9, 10] for x in bot.counters))

        bot = SimpleCrawler(concurrency=10)
        bot.run()
        self.assertEqual(len(bot.counters), 10)
        self.assertTrue(any(x in [9, 10] for x in bot.counters))

    def test_prepare_method(self):

        class SimpleCrawler(Crawler):
            def prepare(self):
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

    def test_shutdown_method(self):

        class SimpleCrawler(Crawler):
            def prepare(self):
                self.points = []

            def shutdown(self):
                self.points.append('done')

            def task_generator(self):
                yield Request('test', url=server.get_url())

            def handler_test(self, req, res):
                self.points.append(res.body)

        server.response['body'] = 'Moon'
        bot = SimpleCrawler()
        bot.run()
        self.assertEqual(bot.points, ['Moon', 'done'])

    def test_timeout(self):

        class SimpleCrawler(Crawler):
            def prepare(self):
                self.points = []
                self.errors = []

            def task_generator(self):
                yield Request('test', url=server.get_url(), timeout=0.1,
                              meta={'id': 1})
                yield Request('test', url=server.get_url(), timeout=0.5,
                              meta={'id': 2})

            def handler_test(self, req, res):
                self.points.append(req.meta['id'])

            def process_failed_request(self, req, ex):
                super(SimpleCrawler, self).process_failed_request(req, ex)
                self.errors.append(req.meta['id'])

        server.response['sleep'] = 0.2
        bot = SimpleCrawler()
        bot.run()
        self.assertEqual(bot.points, [2])
        self.assertEqual(bot.errors, [1])
