import sys
import os.path
import logging
from argparse import ArgumentParser

from grab.spider.base import Spider
from grab.spider.error import SpiderInternalError
from grab.util.config import build_root_config, build_spider_config

from crawler import Crawler

logger = logging.getLogger('crawler.cli')


def process_module(mod, reg):
    for key in dir(mod):
        val = getattr(mod, key)
        if (
                isinstance(val, type)
                and issubclass(val, Crawler)
                and val is not Crawler
            ):
            logger.debug(
                'Found crawler %s in module %s',
                val.__name__, mod.__file__
            )
            reg[val.__name__] = val


def collect_crawlers():
    reg = {}

    for location in ('crawlers',):
        try:
            mod = __import__(location, None, None, ['foo'])
        except ImportError as ex:
            #if path not in str(ex):
            logger.exception('Failed to import %s', location)
        else:
            if mod.__file__.endswith('__init__.py'):
                dir_ = os.path.split(mod.__file__)[0]
                for fname in os.listdir(dir_):
                    if (
                        fname.endswith('.py')
                        and not fname.endswith('__init__.py')
                    ):
                        target_mod = '%s.%s' % (location, fname[:-3])
                        try:
                            mod = __import__(target_mod, None, None, ['foo'])
                        except ImportError as ex:
                            #if path not in str(ex):
                            logger.exception('Failed to import %s', target_mod)
                        else:
                            process_module(mod, reg)
            else:
                process_module(mod, reg)

    return reg


def setup_logging(network_logs=False):
    logging.basicConfig(level=logging.DEBUG)
    if not network_logs:
        logging.getLogger('crawler.network').propagate = False


def run_command_crawl():

    parser = ArgumentParser()
    parser.add_argument('crawler_id')
    parser.add_argument('-n', '--network-logs', action='store_true', default=False)
    opts = parser.parse_args()

    setup_logging(network_logs=opts.network_logs)

    reg = collect_crawlers()
    if opts.crawler_id not in reg:
        sys.stderr.write(
            'Could not load %s crawler\n' % opts.crawler_id
        )
        sys.exit(1)
    else:
        cls = reg[opts.crawler_id]
        bot = cls()
        bot.run()
