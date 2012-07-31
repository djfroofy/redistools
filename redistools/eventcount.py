from redis import Redis


class EventCount(object):
    """
    Keep track of unique events in a system using bitsets. Events to track must
    have an associated unique integer id (eventid). This is useful for tracking
    things like user logins and other statistics.

    For a good read on the concept: goo.gl/OrDwU
    """

    def __init__(self, key, maxevent=None, client=None):
        """
        key: A Redis key for storing event stats.
        maxevent: Maximum event id. If given this will preemptively initialize
        the bitset.
        client: A Redis client
        """
        if client is None:
            client = Redis()
        self.client = client
        self.key = key
        if maxevent:
            self.client.setbit(key, maxevent, 1)
            self.client.setbit(key, maxevent, 0)

    def record(self, eventid):
        """
        Record an event occurence.

        eventid: The integr event id.
        """
        self.client.setbit(self.key, eventid, 1)

    def count(self):
        """
        Return the number of ever occurences.
        """
        return self.client.bitcount(self.key)

    def happened(self, eventid):
        """
        Return True if event occurred, False otherwise.

        eventid: The integer event id
        """
        return self.client.getbit(self.key, eventid)
