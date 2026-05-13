"""
Lua 适配器
"""
import shutil
import json
from pathlib import Path

from ..base import Plugin


# Lua 通信桥脚本
LUA_BRIDGE = """
local json = require('cjson')
local plugin_path = arg[1]

-- 读取输入
local input = io.read("*all")
local payload = json.decode(input)

-- 加载插件
local plugin = dofile(plugin_path)

local result = nil
local error_msg = nil

local success, res = pcall(function()
    if payload.action == "run" then
        if type(plugin.run) == "function" then
            return plugin:run()
        else
            return plugin
        end
    elseif payload.action == "call" then
        local func = plugin[payload.function]
        if type(func) == "function" then
            return func(unpack(payload.args))
        else
            error("Function '" .. payload.function .. "' not found")
        end
    elseif payload.action == "eval" then
        return assert(load(payload.code))()
    end
end)

if success then
    result = res
else
    error_msg = res
end

print(json.encode({result = result, error = error_msg}))
"""


class LuaPlugin(Plugin):
    """
    Lua 插件适配器
    
    需要 lua 或 luarocks 环境
    依赖 cjson 库
    """
    
    EXTENSIONS = ('.lua',)
    INTERPRETER = 'lua'
    
    def __init__(self, path):
        super().__init__(path)
        # 检查 lua 是否可用
        if not shutil.which('lua'):
            raise EnvironmentError("Lua is not installed")
    
    def build_command(self):
        bridge_path = Path(__file__).parent / '_lua_bridge.lua'
        bridge_path.write_text(LUA_BRIDGE)
        return ['lua', str(bridge_path), str(self.path)]
