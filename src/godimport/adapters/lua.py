"""Lua plugin adapter executed through a temporary Lua bridge."""
import os, shutil, tempfile
from pathlib import Path
from ..base import Plugin

LUA_BRIDGE = r'''
local json = require('cjson')
local plugin_path = arg[1]
local payload = json.decode(io.read('*all'))
local plugin = dofile(plugin_path)
local ok, result = pcall(function()
  if payload.action == 'run' then
    if type(plugin.run) == 'function' then return plugin:run() end
    return plugin
  elseif payload.action == 'call' then
    local fn = plugin[payload.function]
    if type(fn) ~= 'function' then error('Function not found: ' .. payload.function) end
    local args = payload.args or {}
    if payload.kwargs and next(payload.kwargs) then table.insert(args, payload.kwargs) end
    return fn(unpack(args))
  elseif payload.action == 'eval' then return assert(load(payload.code))() end
  error('Unknown action: ' .. tostring(payload.action))
end)
if ok then print(json.encode({result=result, error=nil}))
else print(json.encode({result=nil, error=tostring(result)})) end
'''

class LuaPlugin(Plugin):
    EXTENSIONS = ('.lua',)
    INTERPRETER = 'lua'
    def __init__(self, path, timeout=30):
        super().__init__(path, timeout=timeout)
        if not shutil.which('lua'): raise EnvironmentError("Lua is not installed")
        self._bridge_path = None
    def build_command(self):
        fd, bridge_path = tempfile.mkstemp(prefix='lib_common_lua_', suffix='.lua')
        os.close(fd)
        Path(bridge_path).write_text(LUA_BRIDGE, encoding='utf-8')
        self._bridge_path = bridge_path
        return ['lua', bridge_path, str(self.path.resolve())]
    def _execute(self, payload):
        try: return super()._execute(payload)
        finally:
            if self._bridge_path:
                try: os.unlink(self._bridge_path)
                except OSError: pass
                self._bridge_path = None
