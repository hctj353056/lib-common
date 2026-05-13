# -*- coding: utf-8 -*-
"""
lib-common.utils: 通用工具函数

包含：
- 文件操作
- 加密编码
- 时间日期
- JSON处理
"""

import json
import hashlib
import base64
import os
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


# ========== JSON处理 ==========

def load_json(path: str) -> Any:
    """加载JSON文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Any, path: str, indent: int = 2):
    """保存JSON文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


# ========== 加密编码 ==========

def md5(text: str) -> str:
    """MD5哈希"""
    return hashlib.md5(text.encode()).hexdigest()

def sha256(text: str) -> str:
    """SHA256哈希"""
    return hashlib.sha256(text.encode()).hexdigest()

def base64_encode(text: str) -> str:
    """Base64编码"""
    return base64.b64encode(text.encode()).decode()

def base64_decode(encoded: str) -> str:
    """Base64解码"""
    return base64.b64decode(encoded.encode()).decode()


# ========== 文件操作 ==========

def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)

def list_files(dir_path: str, ext: Optional[str] = None) -> List[str]:
    """列出目录下的文件"""
    files = []
    for f in os.listdir(dir_path):
        full_path = os.path.join(dir_path, f)
        if os.path.isfile(full_path):
            if ext is None or f.endswith(ext):
                files.append(full_path)
    return files


# ========== 时间日期 ==========

def now() -> str:
    """当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today() -> str:
    """今天的日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")

def timestamp() -> int:
    """当前时间戳"""
    return int(time.time())

def format_time(ts: int, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间戳"""
    return datetime.fromtimestamp(ts).strftime(fmt)


# ========== 通用 ==========

def merge_dicts(*dicts: Dict) -> Dict:
    """合并多个字典"""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def chunks(lst: List, n: int) -> List[List]:
    """将列表分块"""
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def retry(func, times: int = 3, delay: float = 1.0):
    """重试装饰器逻辑"""
    for i in range(times):
        try:
            return func()
        except Exception as e:
            if i == times - 1:
                raise e
            time.sleep(delay)
