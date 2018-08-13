from urllib.parse import urljoin, urlsplit
import threading
from io import BytesIO

import defusedxml.lxml
from lxml.html import HTMLParser
from lxml.etree import ParserError, XMLSyntaxError
from selection import XpathSelector

__all__ = ('Response',)
THREAD_STORAGE = threading.local()


class Response(object):
    def __init__(
            self, body=None, url=None, effective_url=None,
            code=None, times=None, bytes_downloaded=None,
            bytes_uploaded=None,
            extra_valid_codes=None
        ):
        self.code = code
        self.body = body
        self.url = url
        self.effective_url = effective_url
        self.times = times
        self.bytes_downloaded = bytes_downloaded
        self.bytes_uploaded = bytes_uploaded
        self.extra_valid_codes = extra_valid_codes or []

    def absolute_url(self, url=None):
        base_url = self.effective_url or self.url
        if url is None:
            return base_url
        else:
            return urljoin(base_url, url)

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
        try:
            tree = defusedxml.lxml.parse(
                BytesIO(self.body or b'<body></body>'), parser=parser
            )
        except Exception as ex:
            if (
                    (
                        isinstance(ex, AssertionError)
                        and (
                            'ElementTree not initialized, missing root'
                            in str(ex)
                        )
                    ) or (
                        isinstance(ex, ParserError)
                        and 'Document is empty' in str(ex)
                    )
                ):
                fixed_body = b'<body>%s</body>' % self.body
                tree = defusedxml.lxml.parse(BytesIO(fixed_body), parser=parser)
            else:
                host = urlsplit(self.url).netloc
                with open('var/fail-%s.html' % host, 'wb') as out:
                    out.write(str(ex).encode() + b'\n')
                    out.write(b'----------------------------------\n')
                    out.write(self.body)
                raise
        return tree

    def xpath(self, query):
        return self.selector('lxml_xpath').select(query)

    def save(self, path):
        with open(path, 'wb') as out:
            out.write(self.body)
