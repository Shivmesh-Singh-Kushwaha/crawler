from urllib.parse import urljoin


__all__ = ('Response',)


class Response(object):
    def __init__(self, body, url):
        self.body = body
        self.url = url

    def absolute_url(self, url):
        return urljoin(self.url, url)
