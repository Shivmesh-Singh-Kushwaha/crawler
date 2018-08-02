# coding: utf-8
from unittest import TestCase

from test_server import TestServer


class BaseTestCase(object):
    @classmethod
    def setUpClass(cls):
        cls.server = TestServer(port=9876)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.server.reset()

