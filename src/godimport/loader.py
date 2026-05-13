"""
godimport 主加载器
"""
from pathlib import Path
from typing import Type

from .base import Plugin, PluginError, detect_language
from .adapters import (
    PythonPlugin,
    JavaScriptPlugin,
    LuaPlugin,
    BashPlugin,
)


# 语言 -> 适配器映射
ADAPTERS = {
    'python': PythonPlugin,
    'javascript': JavaScriptPlugin,
    'lua': LuaPlugin,
    'bash': BashPlugin,
}


def import_plugin(path: str) -> Plugin:
    """
    导入插件，统一入口
    
    Usage:
        from godimport import import_plugin
        
        # Python 插件
        py = import_plugin("plugins/calc.py")
        result = py.call("add", 1, 2)
        
        # JavaScript 插件
        js = import_plugin("plugins/math.js")
        result = js.call("multiply", 3, 4)
        
        # Lua 插件
        lua = import_plugin("plugins/utils.lua")
        result = lua.call("greet", "World")
    """
    path = Path(path)
    
    # 检测语言
    lang = detect_language(str(path))
    
    if lang == 'unknown':
        raise PluginError(f"Unsupported file type: {path.suffix}")
    
    # 获取适配器
    adapter_cls = ADAPTERS.get(lang)
    
    if adapter_cls is None:
        raise PluginError(f"No adapter for language: {lang}")
    
    return adapter_cls(str(path))
