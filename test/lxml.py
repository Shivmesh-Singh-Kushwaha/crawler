# coding: utf-8
from io import BytesIO
from unittest import TestCase

from lxml.html import fromstring, HTMLParser
from lxml.etree import ParserError, XMLSyntaxError
import defusedxml.lxml


class LXMLTestCase(TestCase):
    """
    Different version of lxml raises different exception for invalid HTML
    """
    def test_xmlsyntax_error_empty_string(self):
        with self.assertRaises((ParserError, XMLSyntaxError)) as cm:
            fromstring(b'')
        self.assertTrue(
            cm.exception.args[0] is None
            or
            'Document is empty' in cm.exception.args[0]
        )

    def test_document_is_empty_only_comment(self):
        self.assertRaises(
            ParserError, fromstring, b'<!--foo-->'
        )
        try:
            fromstring(b'<!--foo-->')
        except Exception as ex:
            self.assertTrue(
                'Document is empty' in str(ex)
            )

    def test_missing_root_only_comment_defusedxml(self):
        parser = HTMLParser()
        self.assertRaises(
            AssertionError,
            defusedxml.lxml.parse, BytesIO(b'<!-- foo -->'), parser=parser
        )
        try:
            defusedxml.lxml.parse(BytesIO(b'<!-- foo -->'), parser=parser)
        except Exception as ex:
            self.assertTrue(
                'ElementTree not initialized, missing root' in str(ex)
            )

    def test_missing_root_empty_string_defusedxml(self):
        parser = HTMLParser()
        with self.assertRaises((XMLSyntaxError, AssertionError)) as cm:
            defusedxml.lxml.parse(BytesIO(b''), parser=parser)
        self.assertTrue(
            cm.exception.args[0] is None
            or
            'ElementTree not initialized, missing root' in str(cm.exception)
        )
