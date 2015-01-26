class Request(object):
    def __init__(self, url, callback=None, tag=None, meta=None):
        self.url = url
        self.callback = callback
        self.tag = tag
        self.meta = meta
