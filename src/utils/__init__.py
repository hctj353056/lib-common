# -*- coding: utf-8 -*-
"""Common JSON, encoding, file, time and small functional utilities."""
import base64, hashlib, json, os, tempfile, time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, Type, Tuple

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file: return json.load(file)

def save_json(data: Any, path: str, indent: int = 2, *, atomic: bool = True) -> None:
    """Save UTF-8 JSON; atomic mode prevents partial files on interrupted writes."""
    if not atomic:
        with open(path, "w", encoding="utf-8") as file: json.dump(data, file, ensure_ascii=False, indent=indent)
        return
    directory = os.path.dirname(os.path.abspath(path))
    fd, temporary = tempfile.mkstemp(prefix=".json-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=indent); file.flush(); os.fsync(file.fileno())
        os.replace(temporary, path)
    except Exception:
        try: os.unlink(temporary)
        except OSError: pass
        raise

def md5(text: str) -> str:
    """MD5 for compatibility/integrity checks only; not for security."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def sha256(text: str) -> str: return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: str, chunk_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""): digest.update(chunk)
    return digest.hexdigest()

def base64_encode(text: str) -> str: return base64.b64encode(text.encode("utf-8")).decode("ascii")
def base64_decode(encoded: str) -> str: return base64.b64decode(encoded.encode("ascii"), validate=True).decode("utf-8")
def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True); return path

def list_files(dir_path: str, ext: Optional[str] = None, *, recursive: bool = False) -> List[str]:
    """List files deterministically, optionally descending into subdirectories."""
    result = []
    if recursive:
        for root, _, names in os.walk(dir_path):
            result.extend(os.path.join(root, name) for name in names if ext is None or name.endswith(ext))
    else:
        result.extend(os.path.join(dir_path, name) for name in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, name)) and (ext is None or name.endswith(ext)))
    return sorted(result)

def now() -> str: return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def today() -> str: return datetime.now().strftime("%Y-%m-%d")
def timestamp() -> int: return int(time.time())
def format_time(ts: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str: return datetime.fromtimestamp(ts).strftime(fmt)
def merge_dicts(*dicts: Dict) -> Dict:
    result = {}
    for mapping in dicts: result.update(mapping)
    return result

def chunks(lst: List, n: int) -> List[List]:
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0: raise ValueError("n must be a positive integer")
    return [lst[index:index+n] for index in range(0, len(lst), n)]

def retry_call(func: Callable, times: int = 3, delay: float = 1.0, *, backoff: float = 1.0, exceptions: Tuple[Type[BaseException], ...] = (Exception,)) -> Any:
    """Retry a zero-argument callable; times is the maximum total attempts."""
    if times < 1: raise ValueError("times must be >= 1")
    if delay < 0 or backoff < 1: raise ValueError("delay must be >= 0 and backoff must be >= 1")
    for attempt in range(times):
        try: return func()
        except exceptions:
            if attempt + 1 == times: raise
            time.sleep(delay * (backoff ** attempt))

def retry(func: Callable, times: int = 3, delay: float = 1.0):
    """Backward-compatible retry helper for a zero-argument callable."""
    return retry_call(func, times=times, delay=delay)

def retryable(times: int = 3, delay: float = 1.0, *, backoff: float = 1.0, exceptions: Tuple[Type[BaseException], ...] = (Exception,)):
    """Decorator that retries a function with the same arguments."""
    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return retry_call(lambda: func(*args, **kwargs), times, delay, backoff=backoff, exceptions=exceptions)
        return wrapped
    return decorate
