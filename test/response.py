# coding: utf-8
from unittest import TestCase

from .util import temp_file
from crawler import Response


class ResponseTestCase(TestCase):
    def test_absolute_url(self):
        res = Response(body='', url='http://example.com')
        self.assertEquals('http://example.com', res.absolute_url(''))
        self.assertEquals('http://example.com/', res.absolute_url('/'))
        self.assertEquals('http://example.com', res.absolute_url())
        self.assertEquals('http://example.com/foo', res.absolute_url('/foo'))
        self.assertEquals('http://example.com/foo?1=2',
                          res.absolute_url('/foo?1=2'))
        self.assertEquals('http://domain.com/foo',
                          res.absolute_url('http://domain.com/foo'))

    def test_lxml_tree_realdata(self):
        import lxml.etree

        with open('crawler/data/awesome_python.html', 'rb') as inp:
            data = inp.read()
        res = Response(body=data, url=None)
        self.assertTrue(isinstance(res._lxml_tree(), lxml.etree._ElementTree))

    def test_selector(self):
        from selection import XpathSelector

        res = Response(body=b'<h1>test</h1>', url=None)

        self.assertTrue(isinstance(res.selector('lxml_xpath'), XpathSelector))

    def test_xpath(self):
        from selection import XpathSelector

        with open('crawler/data/awesome_python.html', 'rb') as inp:
            data = inp.read()
        res = Response(body=b'<title>foo</title>', url=None)

        self.assertEqual(res.xpath('//title').text(), 'foo')

    def test_text_method(self):
        res = Response(body='<h1>Ленин жив</h1>'.encode('utf-8'), url=None)
        self.assertEqual('<h1>Ленин жив</h1>', res.text())

    def test_save_method(self):
        data = '<h1>Ленин жив</h1>'.encode('utf-8')
        with temp_file() as file_:
            res = Response(body=data, url=None)
            res.save(file_)
            with open(file_, 'rb') as inp:
                self.assertEqual(
                    inp.read(),
                    data
                )
