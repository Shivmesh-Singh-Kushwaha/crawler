from crawler.error import RequestConfigurationError


__all__ = ('Request', 'SleepTask')


class Request(object):
    def __init__(self, tag=None, url=None, meta=None, timeout=10):
        self.url = url
        if tag is None:
            raise RequestConfigurationError('Tag parameter is required')
        self.tag = tag
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta
        self.timeout = timeout


class SleepTask(object):
    def __init__(self, delay):
        assert isinstance(delay, (int, float))
        self.delay = delay
