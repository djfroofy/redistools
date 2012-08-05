from unittest import TestCase

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet import protocol
from twisted.trial.unittest import TestCase as TrialTestCase

import redis

from txredis.client import Redis


class RedisTestCase(TestCase):

    def setUp(self):
        self.client = redis.Redis(db=10)
        self.client.flushdb()


class TxRedisTestCase(TrialTestCase):

    @inlineCallbacks
    def setUp(self):
        client_creator = protocol.ClientCreator(reactor, Redis)
        self.client = yield client_creator.connectTCP('localhost', 6379)
        yield self.client.select(10)
        yield self.client.flushdb()

    def tearDown(self):
        self.client.transport.loseConnection()
