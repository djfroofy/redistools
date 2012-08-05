"""
Some common caching patterns (beyond simple key expiry). This is useful if you
want to cache arbitrarily many strings (request or session information, for
example) in Redis and don't want to worry about capacity issues; i.e. you want
to confine the keyspace to a maximum number of entries.

Cache replacment strategies:

    LRU (LruCache) - Least Recently Used
    LFU (LfuCache) - Least Frequently Used
    RR (RRCache) - Random Replacement
"""
import random
from time import time

import redis

from redistools.scripting import LuaScript


class BaseCache(object):

    script_name = None

    def __init__(self, namespace, max_entries=1000, client=None):
        if client is None:
            client = redis.Redis()
        self._client = client
        self.namespace = namespace
        self.max_entries = max_entries
        script_path = LuaScript.script_path(self.script_name)
        self._script = LuaScript(script_path, self._client)


class LruCache(BaseCache):
    """
    Least Recently Used cache replacement strategy.
    """

    script_name = 'lru'

    def get(self, key):
        ns = self.namespace
        ts = int(time() * 1000)
        max_entries = self.max_entries
        return self._script.eval(keys=(key,),
                                 args=('GET', ts, ns, max_entries))

    def set(self, key, value):
        ns = self.namespace
        ts = int(time() * 1000)
        max_entries = self.max_entries
        return self._script.eval(keys=(key,),
                                 args=('SET', ts, ns, max_entries, value))


class LfuCache(BaseCache):
    """
    Least Frequently Used cache replacement strategy.
    """

    script_name = 'lfu'

    def get(self, key):
        ns = self.namespace
        max_entries = self.max_entries
        return self._script.eval(keys=(key,),
                                 args=('GET', ns, max_entries))

    def set(self, key, value):
        ns = self.namespace
        max_entries = self.max_entries
        return self._script.eval(keys=(key,),
                                 args=('SET', ns, max_entries, value))


class RRCache(BaseCache):
    """
    Random Replacement cache replacment strategy.
    """

    script_name = 'rr'

    def __init__(self, namespace, max_entries=1000, client=None):
        super(RRCache, self).__init__(namespace, max_entries, client)
        self._cachekey = '_RR_::%s' % self.namespace

    def get(self, key):
        ns = self.namespace
        max_entries = self.max_entries
        replace = random.randint(0, self.max_entries)
        return self._script.eval(keys=(key,),
                                 args=('GET', replace, ns, max_entries))

    def set(self, key, value):
        ns = self.namespace
        max_entries = self.max_entries
        replace = random.randint(0, self.max_entries)
        return self._script.eval(keys=(key,),
                                 args=('SET', replace, ns, max_entries, value))
