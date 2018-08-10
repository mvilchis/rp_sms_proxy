import redis

class PriorityQueue(object):
    def __init__(self, queue):
        self.queue = u'redis:pq:%s' % queue
        self._r = redis.StrictRedis(host='localhost', port=6379, db=5)

    def push(self, item, score=1):
        return self._r.zincrby(self.queue, item, score)

    @property
    def first(self):
        return self._r.zrevrange(self.queue, 0, 0)[0]

    def pop(self):
        try:
            _item = self.first
            while self._r.zrem(self.queue, _item) == 0:
                # Somebody else also got the same item and removed before us
                # Try again
                _item = self.first
            # We manager to pop the item from the queue
            return _item
        except IndexError:
            # Queue is empty
            pass
