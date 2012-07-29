"""
Treat a string-type keyspace as an LRU cache.
"""
from time import time

import redis

from redistools.scripting import LuaScript


class LruCache(object):

    def __init__(self, namespace, max_entries=1000, client=None):
        if client is None:
            client = redis.Redis()
        self._client = client
        self.namespace = namespace
        self.max_entries = max_entries
        script_path = LuaScript.script_path('lru')
        self._lru_script = LuaScript(script_path, self._client)

    def get(self, key):
        ns = self.namespace
        ts = int(time() * 1000)
        max_entries = self.max_entries
        return self._lru_script.eval(keys=(key,),
                                     args=('GET', ts, ns, max_entries))

    def set(self, key, value):
        ns = self.namespace
        ts = int(time() * 1000)
        max_entries = self.max_entries
        return self._lru_script.eval(keys=(key,),
                                     args=('SET', ts, ns, max_entries, value))
