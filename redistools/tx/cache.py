from redistools.tx.util import get_redis_client


def get_cache(cache_class, namespace, max_entries=1000,
              redis_host='localhost', redis_port=6379, redis_protocol=None):
    """
    Utility API for get a cache instance with a txRedis client
    attached--instead of normal synchronous redis-py redis client.

    This returns a Deferred that will fire with a cache instance or errback if
    we cannot connect.

    Example:

        def got_cache_instance(cache):
            cache.get('a').addCallback(...)
            ...

        d = get_cache(LruCache, 'urls', max_entries=100000,
                      redis_host='example.com', redis_port=6379,
                      redis_protocol=HiRedisClient)
        d.addCallback(got_cache_instance)
    """

    def got_connection(client):
        return cache_class(namespace, max_entries=max_entries,
                           client=client)

    d = get_redis_client(redis_host, redis_port, redis_protocol)
    d.addCallback(got_connection)
    return d
