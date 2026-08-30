"""Performance Caching for Cycling Performance Studio Lab.

LRU cache with TTL (Time-To-Live) support for expensive computations.
Thread-safe implementation for concurrent access.

Usage:
    from caching import TTLCache, lru_ttl_cache

    # Simple TTL cache
    cache = TTLCache(maxsize=128, ttl=300)  # 5 min TTL
    result = cache.get_or_set("key", lambda: expensive_computation())

    # Decorator
    @lru_ttl_cache(maxsize=64, ttl=60)
    def compute_ftp(efforts):
        ...
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TTLCache:
    """Thread-safe LRU cache with TTL expiration."""

    def __init__(self, maxsize: int = 128, ttl: float = 300.0) -> None:
        self._maxsize = maxsize
        self._ttl = ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.monotonic() - timestamp < self._ttl:
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return value
                else:
                    del self._cache[key]
            self._misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, time.monotonic())
            while len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def get_or_set(self, key: str, factory: Callable[[], Any]) -> Any:
        value = self.get(key)
        if value is not None:
            return value
        value = factory()
        self.set(key, value)
        return value

    def invalidate(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def cleanup(self) -> int:
        now = time.monotonic()
        removed = 0
        with self._lock:
            keys_to_remove = [
                k for k, (_, ts) in self._cache.items()
                if now - ts >= self._ttl
            ]
            for k in keys_to_remove:
                del self._cache[k]
                removed += 1
        return removed

    @property
    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "maxsize": self._maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
        }

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None


class ProfileCache:
    """Per-profile cache manager."""

    def __init__(self, ttl: float = 300.0) -> None:
        self._caches: dict[str, TTLCache] = {}
        self._default_ttl = ttl
        self._lock = threading.Lock()

    def _get_cache(self, profile_id: str) -> TTLCache:
        if profile_id not in self._caches:
            with self._lock:
                if profile_id not in self._caches:
                    self._caches[profile_id] = TTLCache(maxsize=64, ttl=self._default_ttl)
        return self._caches[profile_id]

    def get(self, profile_id: str, key: str) -> Any | None:
        return self._get_cache(profile_id).get(key)

    def set(self, profile_id: str, key: str, value: Any) -> None:
        self._get_cache(profile_id).set(key, value)

    def get_or_set(self, profile_id: str, key: str, factory: Callable[[], Any]) -> Any:
        return self._get_cache(profile_id).get_or_set(key, factory)

    def invalidate_profile(self, profile_id: str) -> None:
        with self._lock:
            if profile_id in self._caches:
                self._caches[profile_id].clear()
                del self._caches[profile_id]

    def clear_all(self) -> None:
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
            self._caches.clear()

    def cleanup_all(self) -> int:
        total = 0
        with self._lock:
            for cache in self._caches.values():
                total += cache.cleanup()
        return total

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "profiles": len(self._caches),
            "total_entries": sum(len(c) for c in self._caches.values()),
            "per_profile": {
                pid: cache.stats for pid, cache in self._caches.items()
            },
        }


def make_cache_key(*args: Any, **kwargs: Any) -> str:
    key_parts = [repr(a) for a in args]
    key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
    raw = ":".join(key_parts)
    return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()


def lru_ttl_cache(maxsize: int = 64, ttl: float = 60.0) -> Callable:
    """Decorator: LRU cache with TTL expiration."""
    cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = make_cache_key(*args, **kwargs)
            result = cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        wrapper.cache_stats = lambda: cache.stats
        return wrapper

    return decorator


_global_cache = TTLCache(maxsize=256, ttl=300.0)
_profile_cache = ProfileCache(ttl=300.0)


def get_global_cache() -> TTLCache:
    return _global_cache


def get_profile_cache() -> ProfileCache:
    return _profile_cache
