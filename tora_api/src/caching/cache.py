from threading import Thread
from collections import defaultdict



class Cache(Thread):
    def __init__(self, cache_size):
        Thread.__init__(self)
        self.cache_size = cache_size
        self.cache = defaultdict(list)
        self.start()
