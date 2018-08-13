from crawler.error import CrawlerError


__all__ = ('Request',)


class Request(object):
    def __init__(
            self,
            tag=None,
            url=None,
            meta=None,
            timeout=10,
            connect_timeout=2,
            try_count=1,
            proxy=None,
            proxy_auth=None,
            proxy_type='http',
            follow_redirect=True,
            redirect_limit=10,
        ):
        self.url = url
        if tag is None:
            raise CrawlerError('Tag parameter is required')
        self.tag = tag
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.try_count = try_count
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.proxy_type = proxy_type
        self.follow_redirect = follow_redirect
        self.redirect_limit = redirect_limit
