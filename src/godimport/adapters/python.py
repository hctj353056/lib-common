"""Python plugin adapter; plugins execute in-process and must be trusted."""
import hashlib, sys
from importlib.util import spec_from_file_location, module_from_spec
from ..base import Plugin

class PythonPlugin(Plugin):
    EXTENSIONS = ('.py',)
    def __init__(self, path, timeout=30):
        super().__init__(path, timeout=timeout)
        self.module = None
        self._module_name = 'lib_common_plugin_' + hashlib.sha256(str(self.path.resolve()).encode()).hexdigest()[:16]
    def build_command(self): return None
    def _load_module(self):
        if self.module is None:
            spec = spec_from_file_location(self._module_name, self.path)
            if spec is None or spec.loader is None: raise ImportError('Unable to load plugin: %s' % self.path)
            module = module_from_spec(spec); sys.modules[self._module_name] = module
            spec.loader.exec_module(module); self.module = module
        return self.module
    def run(self):
        module = self._load_module()
        if hasattr(module, 'run'): return module.run()
        raise NotImplementedError('Plugin must define run() function')
    def call(self, func_name, *args, **kwargs):
        module = self._load_module(); func = getattr(module, func_name, None)
        if not callable(func): raise AttributeError("Function '%s' not found in plugin" % func_name)
        return func(*args, **kwargs)
    def eval(self, code):
        """Execute trusted Python code in the plugin's namespace; not a sandbox."""
        module = self._load_module()
        try: return eval(code, module.__dict__)
        except SyntaxError:
            exec(code, module.__dict__)
            return module.__dict__.get('result')
