from redistools.eventcount import EventCount
from redistools.tx.util import get_redis_client


class TxEventCount(EventCount):

    def initialize(self, maxevent):

        def unset(ignore):
            return self._client.setbit(self.key, maxevent, 0)

        d = self._client.setbit(self.key, maxevent, 1)
        return d.addCallback(unset)


def get_event_count(key, redis_host='localhost', redis_port=6379,
                    redis_protocol=None):

    def got_connection(client):
        return TxEventCount(key, client=client)

    d = get_redis_client(redis_host, redis_port, redis_protocol)
    d.addCallback(got_connection)
    return d
