=======
Crawler
=======

.. image:: https://travis-ci.org/lorien/crawler.png?branch=master
    :target: https://travis-ci.org/lorien/crawler

.. image:: https://coveralls.io/repos/lorien/crawler/badge.svg?branch=master
    :target: https://coveralls.io/r/lorien/crawler?branch=master

This project is about:

* 100% test coverage
* Speed
* Reasonable memory consumption
* SOCKS proxy support
* Runtime metrics API


Usage Example
=============

.. code:: python

    import re

    from crawler import Crawler, Request


    class TestCrawler(Crawler):
        re_title = re.compile(r'<title>([^<]+)</title>', re.S | re.I)

        def task_generator(self):
            for line in open('var/domains.txt'):
                host = line.strip()
                yield Request('page', 'http://%s/' % host)

        def handler_page(self, req, res):
            try:
                title = self.re_title.search(res.text()).group(1)
            except AttributeError:
                title = 'N/A'
            print('Title of [%s]: %s' % (req.url, title))

    bot = TestCrawler(num_network_threads=10)
    bot.run()


Quick Way to Start New Project
==============================

* Install crawler with `pip install crawler`
* Run command `crawler_start_project <project_name>`
* cd into new directory
* Run `make build`

That'll build virtualenv with all things you need to start using crawler.
To active virtualenv run `pipenv shell` command.

Put you crawler code into `crawlers/` directory.
Then run it with command `crawl <CrawlerClassName>`


Installation
============

.. code:: bash

    pip install crawler
