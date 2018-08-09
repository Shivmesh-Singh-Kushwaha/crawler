from itertools import cycle
import re
from urllib.request import urlopen
from random import choice

RE_PROXYLINE = re.compile(r'^([^:]+):(\d+)$')

class Proxy(object):
    __slots__ = ('host', 'port', 'user', 'password', 'proxy_type')

    def __init__(
            self, host=None, port=None, user=None,
            password=None, proxy_type=None
        ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.proxy_type = proxy_type

    def address(self):
        return '%s:%s' % (self.host, self.port)

    def auth(self):
        return '%s:%s' % (self.user, self.password)


class ProxyList(object):
    def __init__(self, proxy_type='http'):
        self._servers = []
        self._source = None
        self.proxy_type = proxy_type

    @classmethod
    def from_file(cls, path, **kwargs):
        pl = ProxyList(**kwargs)
        pl.load_file(path)
        return pl

    @classmethod
    def from_url(cls, url, **kwargs):
        pl = ProxyList(**kwargs)
        pl.load_url(url)
        return pl

    def load_file(self, path):
        self._source = ('file', path)
        with open(path) as inp:
            self.load_from_rawdata(inp.read())
            
    def load_url(self, url):
        self._source = ('url', url)
        return self.load_from_rawdata(
            urlopen(url).read().decode('utf-8')
        )

    def load_from_rawdata(self, data): 
        servers = []
        for line in data.splitlines():
            line = line.strip()
            match = RE_PROXYLINE.match(line)
            if not match:
                logging.error('Invalid proxy line: %s' % line)
            else:
                host, port = match.groups()
                port = int(port)
                servers.append(
                    Proxy(host=host, port=port, proxy_type=self.proxy_type)
                )
        if servers:
            self._servers = servers
            self._servers_iter = cycle(self._servers)

    def random_server(self):
        return choice(self._servers)

    def next_server(self):
        return next(self._servers_iter)

    def reload(self):
        if self._source[0] == 'file':
            self.load_file(self._source[1])
        elif self._source[0] == 'url':
            self.load_url(self._source[1])
