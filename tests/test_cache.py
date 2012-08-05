import random

from twisted.internet.defer import maybeDeferred as md
from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase as TrialTestCase

from redis import Redis

from txredis.client import Redis as TxRedisClient

from redistools.cache import LruCache, LfuCache, RRCache
from redistools.tx.cache import get_cache

from tests.lib import RedisTestCase, TxRedisTestCase


class CacheTestsMixin(object):

    def test_default_client(self):
        cache = self.cache_class('unittest')
        self.assert_(isinstance(cache._client, Redis))

    def test_lru_cache_set_and_get(self):
        cache = self.cache_class('unittest', client=self.client)
        yield md(cache.set, 'a', 'hello')
        self.assertEquals((yield md(cache.get, 'a')), 'hello')


class LruTests(CacheTestsMixin):

    cache_class = LruCache

    @inlineCallbacks
    def test_lru_behavior(self):
        cache = LruCache('unittest', max_entries=10, client=self.client)
        for i in range(18):
            key = 'key_%2.2d' % i
            yield md(cache.set, key, 'test')
        yield md(cache.get, 'key_00')
        yield md(cache.set, 'key_01', 'apple')
        yield md(cache.set, 'key_18', 'test')
        yield md(cache.set, 'key_19', 'test')
        keys = yield md(self.client.keys, 'key_*')
        keys.sort()
        expected = ['key_00', 'key_01', 'key_12', 'key_13', 'key_14', 'key_15',
                    'key_16', 'key_17', 'key_18', 'key_19']
        self.assertEquals(keys, expected)


class LruCacheTestCase(RedisTestCase, LruTests):
    pass


class TxLruCacheTestCase(TxRedisTestCase, LruTests):
    pass


class LfuTests(CacheTestsMixin):

    cache_class = LfuCache

    @inlineCallbacks
    def test_lfu_behavior(self):
        cache = LfuCache('unittest', max_entries=10, client=self.client)
        for i in range(18):
            key = 'key_%2.2d' % i
            yield md(cache.set, key, 'test')
        for (index, loops) in enumerate(range(17, -1, -1)):
            key = 'key_%2.2d' % index
            for i in range(loops):
                op, args = random.choice([(cache.get, (key,)),
                                          (cache.set, (key, 'test',))])
                yield md(op, *args)
        yield md(cache.set, 'key_18', 'test')
        yield md(cache.set, 'key_19', 'test')
        keys = yield md(self.client.keys, 'key_*')
        keys.sort()
        expected = ['key_00', 'key_01', 'key_02', 'key_03', 'key_04', 'key_05',
                    'key_06', 'key_07', 'key_08', 'key_09']
        self.assertEquals(keys, expected)


class LfuCacheTestCase(RedisTestCase, LfuTests):
    pass


class TxLfuCacheTestCase(TxRedisTestCase, LfuTests):
    pass


class RRTests(CacheTestsMixin):

    cache_class = RRCache

    @inlineCallbacks
    def test_rr_behavior(self):
        random.seed(0)
        cache = RRCache('unittest', max_entries=10, client=self.client)
        for i in range(20):
            key = 'key_%2.2d' % i
            yield md(cache.set, key, 'test')
            yield md(cache.get, key)
        keys = yield md(self.client.keys, 'key_*')
        keys.sort()
        expected = ['key_00', 'key_01', 'key_04', 'key_07', 'key_09', 'key_11',
                    'key_13', 'key_16', 'key_17', 'key_19']
        self.assertEquals(keys, expected)


class RRCacheTestCase(RedisTestCase, RRTests):
    pass


class TxRRCacheTestCase(TxRedisTestCase, RRTests):
    pass


class TxRedisUtilityTestCase(TrialTestCase):

    @inlineCallbacks
    def test_get_cache(self):
        cache = yield get_cache(LruCache, 'test', max_entries=20000)
        self.addCleanup(cache._client.transport.loseConnection)
        self.assertIsInstance(cache, LruCache)
        self.assertIsInstance(cache._client, TxRedisClient)
