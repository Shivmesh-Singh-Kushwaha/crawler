import re

from crawler import Crawler, Request


class MyCrawler(Crawler):
    def task_generator(self):
        yield Request('foo', url='https://yandex.ru/')

    def handler_foo(self, req, res):
        print(re.search(r'<title>(.+)</title>', res.text()).group(1))


def main(**kwargs):
    bot = MyCrawler()
    bot.run()
