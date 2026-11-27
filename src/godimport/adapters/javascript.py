"""JavaScript plugin adapter executed through a temporary Node bridge."""
import os, shutil, tempfile
from pathlib import Path
from ..base import Plugin

JS_BRIDGE = r'''
const path = require('path');
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const payload = JSON.parse(input);
    const pluginPath = path.resolve(process.argv[2]);
    const plugin = require(pluginPath);
    let result = null;
    if (payload.action === 'run') result = typeof plugin.run === 'function' ? plugin.run() : plugin;
    else if (payload.action === 'call') {
      const fn = plugin[payload.function];
      if (typeof fn !== 'function') throw new Error("Function not found: " + payload.function);
      const args = [...(payload.args || [])];
      if (payload.kwargs && Object.keys(payload.kwargs).length) args.push(payload.kwargs);
      result = fn.apply(null, args);
    } else if (payload.action === 'eval') result = eval(payload.code);
    else throw new Error("Unknown action: " + payload.action);
    console.log(JSON.stringify({result, error: null}));
  } catch (error) { console.log(JSON.stringify({result: null, error: error.message})); }
});
'''

class JavaScriptPlugin(Plugin):
    EXTENSIONS = ('.js', '.mjs')
    INTERPRETER = 'node'
    def __init__(self, path, timeout=30):
        super().__init__(path, timeout=timeout)
        if not shutil.which('node'): raise EnvironmentError("Node.js is not installed")
        self._bridge_path = None
    def build_command(self):
        fd, bridge_path = tempfile.mkstemp(prefix='lib_common_js_', suffix='.js')
        os.close(fd)
        Path(bridge_path).write_text(JS_BRIDGE, encoding='utf-8')
        self._bridge_path = bridge_path
        return ['node', bridge_path, str(self.path.resolve())]
    def _execute(self, payload):
        try: return super()._execute(payload)
        finally:
            if self._bridge_path:
                try: os.unlink(self._bridge_path)
                except OSError: pass
                self._bridge_path = None
