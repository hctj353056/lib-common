import time
from lib_common.cache import TTLCache


def test_cache_ttl_and_default():
    cache = TTLCache(ttl=0.02)
    cache.set("a", 1)
    assert cache.get("a") == 1
    time.sleep(0.03)
    assert cache.get("a", "missing") == "missing"


def test_cache_lru_bound():
    cache = TTLCache(ttl=10, maxsize=2)
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1
    cache.set("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 1
