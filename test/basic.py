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
        server.response['data'] = token

        bot = SimpleCrawler()
        bot.add_task(Request('test', url=server.get_url()))
        bot.run()
        self.assertEquals(token, bot.data['response'])

    def test_simple_task_generator(self):

        class SimpleCrawler(Crawler):
            data = {'count': 0}

            def task_generator(self):
                for x in range(3):
                    yield Request('test', url=server.get_url())

            def handler_test(self, req, res):
                self.data['count'] += 1

        bot = SimpleCrawler()
        bot.run()
        self.assertEquals(3, bot.data['count'])

    def test_not_defined_task_generator(self):

        class SimpleCrawler(Crawler):
            pass

        bot = SimpleCrawler()
        bot.run()

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
