"""Thread-safe bounded TTL cache."""
import time
from collections import OrderedDict
from threading import RLock
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl: float = 60.0, maxsize: int = 256):
        if ttl < 0:
            raise ValueError("ttl must be >= 0")
        if maxsize < 1:
            raise ValueError("maxsize must be >= 1")
        self.ttl = float(ttl)
        self.maxsize = int(maxsize)
        self._items = OrderedDict()
        self._lock = RLock()

    def _purge_expired(self, now: float) -> None:
        expired = [key for key, (deadline, _) in self._items.items() if deadline <= now]
        for key in expired:
            self._items.pop(key, None)

    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        duration = self.ttl if ttl is None else float(ttl)
        if duration < 0:
            raise ValueError("ttl must be >= 0")
        with self._lock:
            now = time.monotonic()
            self._purge_expired(now)
            self._items.pop(key, None)
            if duration == 0:
                return
            self._items[key] = (now + duration, value)
            while len(self._items) > self.maxsize:
                self._items.popitem(last=False)

    def get(self, key: Any, default: Any = None) -> Any:
        with self._lock:
            now = time.monotonic()
            item = self._items.get(key)
            if item is None:
                return default
            deadline, value = item
            if deadline <= now:
                self._items.pop(key, None)
                return default
            self._items.move_to_end(key)
            return value

    def pop(self, key: Any, default: Any = None) -> Any:
        with self._lock:
            item = self._items.pop(key, None)
            if item is None or item[0] <= time.monotonic():
                return default
            return item[1]

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __len__(self) -> int:
        with self._lock:
            self._purge_expired(time.monotonic())
            return len(self._items)
