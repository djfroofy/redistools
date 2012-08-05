import os
import hashlib

from redis import Redis

from redistools.scripting import LuaScript
from redistools import scripting as scripting_module

from tests.lib import RedisTestCase


_here = os.path.dirname(__file__)
test_script_path = os.path.join(_here, 'test.lua')


class LuaScriptTestCase(RedisTestCase):

    def test_script_path_classmethod(self):
        default_dir = os.path.dirname(scripting_module.__file__)
        path = LuaScript.script_path('example')
        self.assertEquals(path,
                          os.path.join(default_dir, 'scripts', 'example.lua'))

    def test_default_client(self):
        script = LuaScript(test_script_path)
        self.assert_(isinstance(script._client, Redis))

    def test_source_sha1(self):
        script = LuaScript(test_script_path)
        expected = hashlib.sha1(open(test_script_path).read()).hexdigest()
        self.assertEquals(script.source_sha1, expected)

    def test_eval(self):
        self.client['a'] = 10
        self.client['b'] = 9
        self.client.script_flush()
        script = LuaScript(test_script_path, self.client)
        result = script.eval(keys=('a',), args=(2,))
        self.assertEquals(result, 12)
        result = script.eval(keys=('b',), args=(5,))
        self.assertEquals(result, 14)
