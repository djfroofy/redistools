from twisted.internet import protocol, reactor

from txredis.client import Redis


def get_redis_client(host='localhost', port=6379, redis_protocol=None):
    """
    Get a redis client connected to host and port with optional protocol.
    """
    if redis_protocol is None:
        redis_protocol = Redis
    client_creator = protocol.ClientCreator(reactor, redis_protocol)
    return client_creator.connectTCP(host, port)
