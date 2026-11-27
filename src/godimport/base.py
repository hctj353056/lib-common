"""Cross-language plugin base class and execution protocol."""
import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class Plugin(ABC):
    EXTENSIONS: tuple = ()
    INTERPRETER: Optional[str] = None

    def __init__(self, path: str, timeout: float = 30):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError("Plugin file not found: %s" % path)
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self.timeout = timeout

    @abstractmethod
    def build_command(self) -> list:
        """Return the command used to launch this plugin adapter."""

    def call(self, func_name: str, *args, **kwargs) -> Any:
        return self._execute({"action": "call", "function": func_name,
                             "args": args, "kwargs": kwargs})

    def run(self) -> Any:
        return self._execute({"action": "run"})

    def eval(self, code: str) -> Any:
        """Evaluate arbitrary code in the plugin runtime; only use trusted plugins."""
        return self._execute({"action": "eval", "code": code})

    def _execute(self, payload: dict) -> Any:
        command = self.build_command()
        if not command:
            raise PluginError("This adapter does not use the subprocess execution path")
        try:
            process = subprocess.run(command, input=json.dumps(payload), text=True,
                                     capture_output=True, timeout=self.timeout)
        except subprocess.TimeoutExpired as error:
            raise TimeoutError("Plugin timed out after %s seconds" % self.timeout) from error
        if process.returncode != 0:
            raise RuntimeError("Plugin execution failed (exit %s): %s" %
                               (process.returncode, process.stderr.strip()))
        try:
            result = json.loads(process.stdout)
        except json.JSONDecodeError as error:
            raise PluginError("Plugin returned invalid JSON: %s" % process.stdout[:300]) from error
        if result.get("error"):
            raise PluginError(result["error"])
        return result.get("result")


class PluginError(Exception):
    """Raised when a plugin reports a protocol or execution error."""


def detect_language(path: str) -> str:
    extension = Path(path).suffix.lower()
    return {".py": "python", ".js": "javascript", ".mjs": "javascript",
            ".lua": "lua", ".sh": "bash", ".bash": "bash"}.get(extension, "unknown")
