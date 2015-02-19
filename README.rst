===
Iob
===

.. image:: https://travis-ci.org/lorien/iob.png?branch=master
    :target: https://travis-ci.org/lorien/iob

.. image:: https://coveralls.io/repos/lorien/iob/badge.svg?branch=master
    :target: https://coveralls.io/r/lorien/iob?branch=master

.. image:: https://pypip.in/download/iob/badge.svg?period=month
    :target: https://pypi.python.org/pypi/iob

.. image:: https://pypip.in/version/iob/badge.svg
    :target: https://pypi.python.org/pypi/iob

.. image:: https://landscape.io/github/lorien/iob/master/landscape.png
   :target: https://landscape.io/github/lorien/iob/master

Web scraping framework based on py3 asyncio & aiohttp libraries.


Usage Example
=============

.. code:: python

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


Installation
============

.. code:: bash

    pip install iob


Dependencies
============

* Python>=3.4
* aiohttp
