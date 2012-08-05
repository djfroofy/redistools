from redis import Redis

from redistools.eventcount import EventCount

from tests.lib import RedisTestCase


class EventCountTestCase(RedisTestCase):

    def test_default_client(self):
        counter = EventCount('counter')
        self.assert_(isinstance(counter._client, Redis))

    def test_max_event_initializes_key(self):
        EventCount('counter', client=self.client)
        self.failIf(self.client.exists('counter'))
        EventCount('counter', 1000, client=self.client)
        self.assert_(self.client.exists('counter'))

    def test_count(self):
        counter = EventCount('a', client=self.client)
        for event in (1, 2, 5, 1, 7, 2, 1):
            counter.record(event)
        self.assertEquals(counter.count(), 4)

    def test_happened(self):
        counter = EventCount('a', client=self.client)
        for event in (0, 1, 3):
            counter.record(event)
        self.assert_(counter.happened(0))
        self.assert_(counter.happened(1))
        self.failIf(counter.happened(2))
        self.assert_(counter.happened(3))
        self.failIf(counter.happened(4))
