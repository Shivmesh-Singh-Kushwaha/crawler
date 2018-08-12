import time

from crawler import Crawler, Request


class TestCrawler(Crawler):
    def task_generator(self):
        time.sleep(666666666)
        if False:
            yield None


def main(**kwargs):
    bot = TestCrawler()
    bot.run()
