from urllib.parse import urljoin
import threading
from io import BytesIO

import defusedxml.lxml
from lxml.html import HTMLParser
from selection import XpathSelector


__all__ = ('Response',)
THREAD_STORAGE = threading.local()


class Response(object):
    def __init__(self, body, url):
        self.body = body
        self.url = url

    def absolute_url(self, url=None):
        if url is None:
            return self.url
        else:
            return urljoin(self.url, url)

    def text(self):
        return self.body.decode('utf-8')

    def selector(self, backend):
        assert backend in ('lxml_xpath',)
        if backend == 'lxml_xpath':
            return XpathSelector(self._lxml_tree())

    def _lxml_tree(self):
        if not hasattr(THREAD_STORAGE, 'lxml_parser'):
            THREAD_STORAGE.lxml_parser = HTMLParser()
        parser = THREAD_STORAGE.lxml_parser
        tree = defusedxml.lxml.parse(BytesIO(self.body), parser=parser)
        return tree

    def xpath(self, query):
        return self.selector('lxml_xpath').select(query)
