from collections import defaultdict


class Stat(object):
    def __init__(self):
        self.counters = defaultdict(int)
        self.items = defaultdict(list)

    def inc(self, key, value=1):
        self.counters[key] += value

    def store(self, key, value):
        self.stat.inc('key')
        self.items[key].append(value)
