"""
Bash 适配器
"""
import json
import os
from pathlib import Path

from ..base import Plugin, PluginError


class BashPlugin(Plugin):
    """
    Bash 脚本适配器
    
    通过环境变量传递参数
    脚本需要输出 JSON 格式结果
    """
    
    EXTENSIONS = ('.sh', '.bash')
    INTERPRETER = 'bash'
    
    def build_command(self):
        return ['bash', str(self.path)]
    
    def _execute(self, payload):
        """
        Bash 通过环境变量 + JSON 文件通信
        因为 bash 不方便 stdin/stdout 复杂交互
        """
        import tempfile
        import uuid
        
        # 生成临时 JSON 文件传递输入
        input_file = Path(tempfile.gettempdir()) / f"godimport_{uuid.uuid4().hex}.json"
        input_file.write_text(json.dumps(payload))
        
        # 设置环境变量
        env = os.environ.copy()
        env['GODIMPORT_INPUT'] = str(input_file)
        
        # 执行脚本
        import subprocess
        try:
            proc = subprocess.Popen(
                ['bash', str(self.path)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired as error:
            proc.kill()
            proc.communicate()
            raise TimeoutError("Bash plugin execution timed out after 30 seconds") from error
        finally:
            input_file.unlink(missing_ok=True)
        
        if proc.returncode != 0:
            raise RuntimeError(f"Bash plugin failed: {stderr}")
        
        # 脚本应输出 JSON
        result = json.loads(stdout)
        
        if result.get("error"):
            raise PluginError(result["error"])
        
        return result.get("result")
    
    def run(self):
        return self._execute({"action": "run"})
    
    def call(self, func_name, *args, **kwargs):
        return self._execute({
            "action": "call",
            "function": func_name,
            "args": args,
            "kwargs": kwargs
        })
