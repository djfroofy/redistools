import os
import hashlib

import redis
from redis.exceptions import NoScriptError


_here = os.path.dirname(__file__)


class LuaScript(object):

    def __init__(self, path, client=None):
        if client is None:
            client = redis.Redis()
        self._client = client
        with open(path) as fd:
            self.source = fd.read()
        self.source_sha1 = hashlib.sha1(self.source).hexdigest()

    @classmethod
    def script_path(cls, name):
        relpath = os.path.join('scripts', name + '.lua')
        return os.path.join(_here, relpath)

    def eval(self, keys=(), args=()):
        try:
            return self._client.evalsha(self.source_sha1, keys=keys, args=args)
        except NoScriptError:
            return self._client.eval(self.source, keys=keys, args=args)
