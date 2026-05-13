"""
Plugin 基类 - 定义统一接口
"""
import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class Plugin(ABC):
    """插件基类，所有语言适配器继承此类"""
    
    # 支持的文件扩展名
    EXTENSIONS: tuple = ()
    
    # 解释器命令（可选）
    INTERPRETER: Optional[str] = None
    
    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Plugin file not found: {path}")
    
    @abstractmethod
    def build_command(self) -> list:
        """构建执行命令"""
        pass
    
    def call(self, func_name: str, *args, **kwargs) -> Any:
        """
        调用插件中的函数
        统一通过 JSON-RPC 通信
        """
        payload = {
            "action": "call",
            "function": func_name,
            "args": args,
            "kwargs": kwargs
        }
        return self._execute(payload)
    
    def run(self) -> Any:
        """执行插件（无参数）"""
        payload = {"action": "run"}
        return self._execute(payload)
    
    def eval(self, code: str) -> Any:
        """执行代码片段"""
        payload = {
            "action": "eval",
            "code": code
        }
        return self._execute(payload)
    
    def _execute(self, payload: Dict) -> Any:
        """通过子进程执行，返回结果"""
        cmd = self.build_command()
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = proc.communicate(
            input=json.dumps(payload),
            timeout=30
        )
        
        if proc.returncode != 0:
            raise RuntimeError(f"Plugin execution failed: {stderr}")
        
        result = json.loads(stdout)
        
        if result.get("error"):
            raise PluginError(result["error"])
        
        return result.get("result")


class PluginError(Exception):
    """插件执行错误"""
    pass


def detect_language(path: str) -> str:
    """根据扩展名检测语言"""
    ext = Path(path).suffix.lower()
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.mjs': 'javascript',
        '.lua': 'lua',
        '.rb': 'ruby',
        '.php': 'php',
        '.sh': 'bash',
        '.go': 'go',
        '.rs': 'rust',
    }
    return lang_map.get(ext, 'unknown')
