from crawler.error import RequestConfigurationError


__all__ = ('Request',)


class Request(object):
    def __init__(
            self,
            tag=None,
            url=None,
            meta=None,
            timeout=10,
            connect_timeout=2,
            network_try_count=1,
            task_try_count=1,
        ):
        self.url = url
        if tag is None:
            raise RequestConfigurationError('Tag parameter is required')
        self.tag = tag
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.network_try_count = network_try_count
        self.task_try_count = task_try_count
