from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import maybeDeferred as md

from redis import Redis

from txredis.client import Redis as TxRedisClient

from redistools.eventcount import EventCount
from redistools.tx.eventcount import get_event_count, TxEventCount

from tests.lib import RedisTestCase, TxRedisTestCase


class EventCountTests(object):

    event_count_class = EventCount

    @inlineCallbacks
    def test_max_event_initializes_key(self):
        eventcount = self.event_count_class('counter', client=self.client)
        self.failIf((yield md(self.client.exists, 'counter')))
        yield md(eventcount.initialize, 1000)
        self.assert_((yield md(self.client.exists, 'counter')))

    @inlineCallbacks
    def test_count(self):
        counter = self.event_count_class('a', client=self.client)
        for event in (1, 2, 5, 1, 7, 2, 1):
            yield md(counter.record, event)
        self.assertEquals((yield md(counter.count)), 4)

    @inlineCallbacks
    def test_happened(self):
        counter = self.event_count_class('a', client=self.client)
        for event in (0, 1, 3):
            yield md(counter.record, event)
        self.assert_((yield md(counter.happened, 0)))
        self.assert_((yield md(counter.happened, 1)))
        self.failIf((yield md(counter.happened, 2)))
        self.assert_((yield md(counter.happened, 3)))
        self.failIf((yield md(counter.happened, 4)))


class EventCountTestCase(RedisTestCase, EventCountTests):

    def test_default_client(self):
        counter = EventCount('counter')
        self.assert_(isinstance(counter._client, Redis))


class TxEventCountTests(TxRedisTestCase, EventCountTests):

    event_count_class = TxEventCount

    @inlineCallbacks
    def test_get_event_count(self):
        counter = yield get_event_count('counter')
        self.addCleanup(counter._client.transport.loseConnection)
        self.assertIsInstance(counter, TxEventCount)
        self.assertIsInstance(counter._client, TxRedisClient)
