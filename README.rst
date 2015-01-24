===
Iob
===

Yet another web scraping framewor


Usage Example
=============

    import re
    from itertools import islice

    from iob import Crawler, Request

    RE_TITLE = re.compile(r'<title>([^<]+)</title>', re.S | re.I)

    class TestCrawler(Crawler):
        def task_generator(self):
            for host in islice(open('var/domains.txt'), 100):
                host = host.strip()
                if host:
                    yield Request('http://%s/' % host, tag='page')

        def handler_page(self, req, res):
            print('Result of request to {}'.format(req.url))
            try:
                title = RE_TITLE.search(res.body).group(1)
            except AttributeError:
                title = 'N/A'
            print('Title: {}'.format(title))

    bot = TestCrawler(concurrency=10)
    bot.run()


Dependencies
============

* Python>=3.4
* aiohttp
