import redis

from unittest import TestCase


class RedisTestCase(TestCase):

    def setUp(self):
        self.client = redis.Redis(db=10)
        self.client.flushdb()
