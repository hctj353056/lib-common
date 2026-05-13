# -*- coding: utf-8 -*-
"""
lib-common: 通用Python工具库

一个标准化的、通用的Python工具集，支持：
- 网络请求 (HTTP, SSH, API调用)
- AI模型 (OpenAI兼容, DeepSeek, 火山引擎等)
- NLP处理 (分词, 解析, 形式化语言)
- 虚拟机 (解释器, 编译器)
- 通用工具 (加密, 文件操作等)

快速开始:
    from lib_common import ssh, ai, network
    
    # SSH连接
    result = ssh.quick_exec("host", "key.pem", "ls")
    
    # AI对话
    client = ai.OpenAICompatible("https://api.deepseek.com", "your-api-key")
    response = client.chat("deepseek-chat", "你好")

安装:
    pip install lib-common
    
或直接从源码使用:
    import sys
    sys.path.insert(0, 'path/to/lib-common')
"""

__version__ = "0.1.0"
__author__ = "灵镜"

from . import network
from . import ssh
from . import ai
from . import nlp
from . import vm
from . import utils

__all__ = [
    "network",
    "ssh", 
    "ai",
    "nlp",
    "vm",
    "utils",
    "version"
]

def version():
    """返回库版本"""
    return __version__
