from redis import Redis


class EventCount(object):
    """
    Keep track of unique events in a system using bitsets. Events to track must
    have an associated unique integer id (eventid). This is useful for tracking
    things like user logins and other statistics.

    For a good read on the concept: goo.gl/OrDwU
    """

    def __init__(self, key, client=None):
        """
        key: A Redis key for storing event stats.
        client: A Redis client
        """
        if client is None:
            client = Redis()
        self._client = client
        self.key = key

    def initialize(self, maxevent):
        """
        Initialize storage for our event count given a maximal event id:
        maxevent.
        """
        self._client.setbit(self.key, maxevent, 1)
        self._client.setbit(self.key, maxevent, 0)

    def record(self, eventid):
        """
        Record an event occurence.

        eventid: The integr event id.
        """
        return self._client.setbit(self.key, eventid, 1)

    def count(self):
        """
        Return the number of ever occurences.
        """
        return self._client.bitcount(self.key)

    def happened(self, eventid):
        """
        Return True if event occurred, False otherwise.

        eventid: The integer event id
        """
        return self._client.getbit(self.key, eventid)
