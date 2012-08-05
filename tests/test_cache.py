from redistools.cache import LruCache

from tests.lib import RedisTestCase


class LruCacheTestCase(RedisTestCase):

    def test_lru_cache_set_and_get(self):
        cache = LruCache('unittest')
        cache.set('a', 'hello')
        self.assertEquals(cache.get('a'), 'hello')

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
