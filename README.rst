=======
Crawler
=======

.. image:: https://travis-ci.org/lorien/crawler.png?branch=master
    :target: https://travis-ci.org/lorien/crawler

.. image:: https://coveralls.io/repos/lorien/crawler/badge.svg?branch=master
    :target: https://coveralls.io/r/lorien/crawler?branch=master

Web scraping framework based on py3 asyncio & aiohttp libraries.


Usage Example
=============

.. code:: python

    import re
    from itertools import islice

    from crawler import Crawler, Request

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


Installation
============

.. code:: bash

    pip install crawler


Dependencies
============

* Python>=3.4
* aiohttp
