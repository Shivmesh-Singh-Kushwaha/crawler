# Crawler - framework to build... crawlers!

.. image:: https://travis-ci.org/lorien/crawler.png?branch=master
    :target: https://travis-ci.org/lorien/crawler

.. image:: https://coveralls.io/repos/lorien/crawler/badge.svg?branch=master
    :target: https://coveralls.io/r/lorien/crawler?branch=master

## Main goals of project:

* stability
* speed
* reasonable memory usage
* SOCKS proxy support
* runtime metrics API


## Usage Example

```python
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
```


## Run Crawler from Command Line

* Create package `crawlers`, just a directory `crawlers` with `__init__.py` file
* Put your spider in any `.py` file in this directory
* Run `crawl YouSpiderClassName`


## Installation

Run `pip install crawler`
