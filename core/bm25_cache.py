"""
File name: core/bm25_cache.py
Author: Luigi Saetta
Last modified: 25-02-2026
Python Version: 3.11

License: MIT

Description: 
    In-process cache manager for BM25 indexes to support stateless request handling.
"""

import os
import threading
import time
from dataclasses import dataclass

from core.bm25_search import BM25OracleSearch
from core.utils import get_console_logger

logger = get_console_logger()

# Default cache TTL disabled (can be overridden with env var).
# Use 0 to keep cache entries until explicit invalidate/force_refresh.
DEFAULT_BM25_CACHE_TTL_SECONDS = int(os.getenv("BM25_CACHE_TTL_SECONDS", "0"))


@dataclass
class _BM25CacheEntry:
    engine: BM25OracleSearch
    created_at: float
    ttl_seconds: int

    def is_expired(self) -> bool:
        if self.ttl_seconds <= 0:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds


class BM25Cache:
    """
    Thread-safe in-memory cache for BM25 engines.
    """

    def __init__(self, default_ttl_seconds: int = DEFAULT_BM25_CACHE_TTL_SECONDS):
        self.default_ttl_seconds = default_ttl_seconds
        self._entries: dict[tuple[str, str, int], _BM25CacheEntry] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _key(table_name: str, text_column: str, batch_size: int) -> tuple[str, str, int]:
        return (table_name.upper(), text_column.upper(), int(batch_size))

    def get_or_create(
        self,
        table_name: str,
        text_column: str,
        batch_size: int = 40,
        ttl_seconds: int | None = None,
        force_refresh: bool = False,
    ) -> BM25OracleSearch:
        """
        Return a cached BM25 engine, creating/rebuilding it when needed.
        """
        ttl = self.default_ttl_seconds if ttl_seconds is None else int(ttl_seconds)
        key = self._key(table_name, text_column, batch_size)

        with self._lock:
            entry = self._entries.get(key)
            if (
                entry is not None
                and not force_refresh
                and not entry.is_expired()
                and entry.engine.bm25 is not None
            ):
                return entry.engine

            logger.info(
                "Building BM25 cache entry for table=%s, column=%s, batch_size=%d",
                table_name,
                text_column,
                batch_size,
            )
            engine = BM25OracleSearch(
                table_name=table_name,
                text_column=text_column,
                batch_size=batch_size,
            )

            self._entries[key] = _BM25CacheEntry(
                engine=engine, created_at=time.time(), ttl_seconds=ttl
            )
            return engine

    def search(
        self,
        query: str,
        table_name: str,
        text_column: str,
        top_n: int = 5,
        batch_size: int = 40,
        ttl_seconds: int | None = None,
        force_refresh: bool = False,
    ) -> list[tuple[str, float]]:
        """
        Run BM25 search using a cached engine.
        """
        engine = self.get_or_create(
            table_name=table_name,
            text_column=text_column,
            batch_size=batch_size,
            ttl_seconds=ttl_seconds,
            force_refresh=force_refresh,
        )
        return engine.search(query=query, top_n=top_n)

    def search_docs(
        self,
        query: str,
        table_name: str,
        text_column: str,
        top_n: int = 5,
        batch_size: int = 40,
        ttl_seconds: int | None = None,
        force_refresh: bool = False,
    ) -> list[dict]:
        """
        Run BM25 search using a cached engine and return docs with metadata.
        """
        engine = self.get_or_create(
            table_name=table_name,
            text_column=text_column,
            batch_size=batch_size,
            ttl_seconds=ttl_seconds,
            force_refresh=force_refresh,
        )
        return engine.search_docs(query=query, top_n=top_n)

    def invalidate(self, table_name: str, text_column: str, batch_size: int = 40) -> bool:
        """
        Remove a single cache entry.
        """
        key = self._key(table_name, text_column, batch_size)
        with self._lock:
            return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        with self._lock:
            self._entries.clear()

    def stats(self) -> dict:
        """
        Return a lightweight snapshot of cache metadata.
        """
        with self._lock:
            items = []
            now = time.time()
            for (table_name, text_column, batch_size), entry in self._entries.items():
                age_seconds = int(now - entry.created_at)
                items.append(
                    {
                        "table_name": table_name,
                        "text_column": text_column,
                        "batch_size": batch_size,
                        "age_seconds": age_seconds,
                        "ttl_seconds": entry.ttl_seconds,
                        "expired": entry.is_expired(),
                        "indexed_docs": len(entry.engine.texts),
                        "is_initialized": entry.engine.bm25 is not None,
                    }
                )
            return {
                "default_ttl_seconds": self.default_ttl_seconds,
                "size": len(items),
                "entries": items,
            }


_bm25_cache_singleton: BM25Cache | None = None
_singleton_lock = threading.Lock()


def get_bm25_cache() -> BM25Cache:
    """
    Return process-wide BM25 cache singleton.
    """
    global _bm25_cache_singleton
    with _singleton_lock:
        if _bm25_cache_singleton is None:
            _bm25_cache_singleton = BM25Cache()
        return _bm25_cache_singleton
