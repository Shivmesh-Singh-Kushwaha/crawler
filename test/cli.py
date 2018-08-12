# coding: utf-8
from unittest import TestCase
from test_server import TestServer
import multiprocessing
import sys
import os.path

from crawler import Crawler, Request
from .util import BaseTestCase, temp_file, temp_dir
from crawler.cli import find_crawlers_in_module


class BasicTestCase(BaseTestCase, TestCase):
    def test_find_crawlers_in_module(self):
        
        with temp_dir() as dir_:
            mod_path = os.path.join(dir_, 'foo1.py')
            with open(mod_path, 'w') as out:
                out.write(
                    'from crawler import Crawler\n'
                    '\n'
                    'class TestCrawler(Crawler):\n'
                    '    pass\n'
                    'class NotCrawler(object):\n'
                    '    pass\n'
                )
            sys.path.insert(0, dir_)
            try:
                reg = {}
                import foo1
                find_crawlers_in_module(foo1, reg)
                self.assertEqual(['TestCrawler'], list(reg.keys()))
            finally:
                sys.path.remove(dir_)
