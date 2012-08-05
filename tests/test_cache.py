import random

from redis import Redis

from redistools.cache import LruCache, LfuCache, RRCache

from tests.lib import RedisTestCase


class CacheTestsMixin(object):

    def test_default_client(self):
        cache = self.cache_class('unittest')
        self.assert_(isinstance(cache._client, Redis))

    def test_lru_cache_set_and_get(self):
        cache = self.cache_class('unittest', client=self.client)
        cache.set('a', 'hello')
        self.assertEquals(cache.get('a'), 'hello')


class LruCacheTestCase(RedisTestCase, CacheTestsMixin):

    cache_class = LruCache

    def test_lru_behavior(self):
        cache = LruCache('unittest', max_entries=10, client=self.client)
        for i in range(18):
            key = 'key_%2.2d' % i
            cache.set(key, 'test')
        cache.get('key_00')
        cache.set('key_01', 'apple')
        cache.set('key_18', 'test')
        cache.set('key_19', 'test')
        keys = self.client.keys('key_*')
        keys.sort()
        expected = ['key_00', 'key_01', 'key_12', 'key_13', 'key_14', 'key_15',
                    'key_16', 'key_17', 'key_18', 'key_19']
        self.assertEquals(keys, expected)


class LfuCacheTestCase(RedisTestCase, CacheTestsMixin):

    cache_class = LfuCache

    def test_lfu_behavior(self):
        cache = LfuCache('unittest', max_entries=10, client=self.client)
        for i in range(18):
            key = 'key_%2.2d' % i
            cache.set(key, 'test')
        for (index, loops) in enumerate(range(17, -1, -1)):
            key = 'key_%2.2d' % index
            for i in range(loops):
                op, args = random.choice([(cache.get, (key,)),
                                          (cache.set, (key, 'test',))])
                op(*args)
        cache.set('key_18', 'test')
        cache.set('key_19', 'test')
        keys = self.client.keys('key_*')
        keys.sort()
        expected = ['key_00', 'key_01', 'key_02', 'key_03', 'key_04', 'key_05',
                    'key_06', 'key_07', 'key_08', 'key_09']
        self.assertEquals(keys, expected)


class RRCacheTestCase(RedisTestCase, CacheTestsMixin):

    cache_class = RRCache

    def test_rr_behavior(self):
        random.seed(0)
        cache = RRCache('unittest', max_entries=10, client=self.client)
        for i in range(20):
            key = 'key_%2.2d' % i
            cache.set(key, 'test')
        keys = self.client.keys('key_*')
        keys.sort()
        expected = ['key_00', 'key_01', 'key_04', 'key_06', 'key_07', 'key_10',
                    'key_12', 'key_13', 'key_15', 'key_19']
        self.assertEquals(keys, expected)
