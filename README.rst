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
    from urllib.parse import urlsplit

    from crawler import Crawler, Request


    class TestCrawler(Crawler):
        re_title = re.compile(r'<title>([^<]+)</title>', re.S | re.I)

        def task_generator(self):
            for host in ('yandex.ru', 'github.com'):
                yield Request('page', 'https://%s/' % host, meta={'host': host})

        def handler_page(self, req, res):
            title = res.xpath('//title').text(default='N/A')
            print('Title of [%s]: %s' % (req.url, title))

            ext_urls = set()
            for elem in res.xpath('//a[@href]'):
                url = elem.attr('href')
                parts = urlsplit(url)
                if parts.netloc and req.meta['host'] not in parts.netloc:
                    ext_urls.add(url)

            print('External URLs:')
            for url in ext_urls:
                print(' * %s' % url)


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
