"""Small concurrency helpers built on the standard library."""
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, List, Optional, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def map_parallel(func: Callable[[T], R], items: Iterable[T], max_workers: Optional[int] = None) -> List[R]:
    """Map a function concurrently and preserve input order; exceptions propagate."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(func, items))
