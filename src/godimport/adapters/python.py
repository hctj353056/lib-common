"""
Python 适配器
"""
import sys
import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

from ..base import Plugin


class PythonPlugin(Plugin):
    """
    Python 插件适配器
    
    被加载的 Python 文件需要定义:
    - run(): 无参数执行
    - call(func_name, *args, **kwargs): 调用指定函数
    """
    
    EXTENSIONS = ('.py',)
    module = None
    
    def build_command(self):
        # Python 直接在当前进程执行，不需要子进程
        return None
    
    def _load_module(self):
        """加载模块到当前进程"""
        if self.module is None:
            spec = spec_from_file_location("plugin_module", self.path)
            self.module = module_from_spec(spec)
            sys.modules["plugin_module"] = self.module
            spec.loader.exec_module(self.module)
        return self.module
    
    def run(self):
        module = self._load_module()
        if hasattr(module, 'run'):
            return module.run()
        raise NotImplementedError("Plugin must define run() function")
    
    def call(self, func_name, *args, **kwargs):
        module = self._load_module()
        func = getattr(module, func_name, None)
        if func is None:
            raise AttributeError(f"Function '{func_name}' not found in plugin")
        return func(*args, **kwargs)
    
    def eval(self, code):
        """执行代码片段"""
        return exec(code, {"__builtins__": __builtins__})
