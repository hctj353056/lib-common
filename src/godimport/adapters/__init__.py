"""
语言适配器集合
"""
from .python import PythonPlugin
from .javascript import JavaScriptPlugin
from .lua import LuaPlugin
from .bash import BashPlugin

__all__ = [
    'PythonPlugin',
    'JavaScriptPlugin',
    'LuaPlugin',
    'BashPlugin',
]
