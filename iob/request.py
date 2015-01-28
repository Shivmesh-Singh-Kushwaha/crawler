class Request(object):
    def __init__(self, tag=None, url=None, callback=None, meta=None):
        self.url = url
        self.callback = callback
        self.tag = tag
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta
