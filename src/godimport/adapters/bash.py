"""Bash plugin adapter using a temporary JSON input file."""
import json, os, tempfile, subprocess
from pathlib import Path
from ..base import Plugin, PluginError

class BashPlugin(Plugin):
    EXTENSIONS = ('.sh', '.bash')
    INTERPRETER = 'bash'
    def build_command(self): return ['bash', str(self.path)]
    def _execute(self, payload):
        fd, input_name = tempfile.mkstemp(prefix='godimport_', suffix='.json')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as file: json.dump(payload, file)
            env = os.environ.copy(); env['GODIMPORT_INPUT'] = input_name
            try:
                process = subprocess.run(self.build_command(), env=env, text=True,
                                        capture_output=True, timeout=self.timeout)
            except subprocess.TimeoutExpired as error:
                raise TimeoutError('Bash plugin timed out after %s seconds' % self.timeout) from error
            if process.returncode != 0:
                raise RuntimeError('Bash plugin failed: %s' % process.stderr.strip())
            try: result = json.loads(process.stdout)
            except json.JSONDecodeError as error:
                raise PluginError('Bash plugin returned invalid JSON') from error
            if result.get('error'): raise PluginError(result['error'])
            return result.get('result')
        finally:
            try: os.unlink(input_name)
            except OSError: pass
    def run(self): return self._execute({'action': 'run'})
    def call(self, func_name, *args, **kwargs):
        return self._execute({'action': 'call', 'function': func_name, 'args': args, 'kwargs': kwargs})
