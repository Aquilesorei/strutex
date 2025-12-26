"""
In-memory LRU cache implementation.

Fast, ephemeral cache using OrderedDict for LRU eviction.
"""

import time
import logging
from collections import OrderedDict
from threading import Lock
from typing import Any, Dict, Optional

from .base import Cache, CacheKey, CacheEntry

logger = logging.getLogger("strutex.cache.memory")


class MemoryCache(Cache):
    """
    In-memory LRU cache.
    
    Features:
    - LRU eviction when max_size reached
    - Optional TTL (time-to-live)
    - Thread-safe operations
    - Hit/miss statistics
    
    Example:
        >>> cache = MemoryCache(max_size=100, ttl=3600)  # 1 hour TTL
        >>> 
        >>> key = CacheKey.create("doc.pdf", "Extract", schema, "gemini")
        >>> cache.set(key, {"invoice_number": "INV-001"})
        >>> 
        >>> result = cache.get(key)  # Returns cached value
    """
    
    def __init__(
        self,
        max_size: int = 100,
        ttl: Optional[float] = None
    ):
        """
        Args:
            max_size: Maximum number of entries to cache
            ttl: Default TTL in seconds (None = never expire)
        """
        self.max_size = max_size
        self.default_ttl = ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: CacheKey) -> Optional[Any]:
        """Get a cached result, moving to end of LRU."""
        key_str = key.to_string()
        
        with self._lock:
            entry = self._cache.get(key_str)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired:
                del self._cache[key_str]
                self._misses += 1
                logger.debug(f"Cache expired: {key_str[:32]}")
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key_str)
            entry.touch()
            self._hits += 1
            
            logger.debug(f"Cache hit: {key_str[:32]}")
            return entry.result
    
    def set(self, key: CacheKey, result: Any, ttl: Optional[float] = None) -> None:
        """Store a result, evicting LRU if needed."""
        key_str = key.to_string()
        actual_ttl = ttl if ttl is not None else self.default_ttl
        
        expires_at = None
        if actual_ttl is not None:
            expires_at = time.time() + actual_ttl
        
        entry = CacheEntry(
            key=key_str,
            result=result,
            expires_at=expires_at
        )
        
        with self._lock:
            # Evict LRU if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"Cache evicted: {oldest_key[:32]}")
            
            self._cache[key_str] = entry
            self._cache.move_to_end(key_str)
        
        logger.debug(f"Cache set: {key_str[:32]}")
    
    def delete(self, key: CacheKey) -> bool:
        """Delete a cached entry."""
        key_str = key.to_string()
        
        with self._lock:
            if key_str in self._cache:
                del self._cache[key_str]
                logger.debug(f"Cache deleted: {key_str[:32]}")
                return True
            return False
    
    def clear(self) -> int:
        """Clear all cached entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info(f"Cache cleared: {count} entries")
            return count
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0.0
            
            return {
                "type": "memory",
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "ttl": self.default_ttl,
            }
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        with self._lock:
            expired = [
                k for k, v in self._cache.items()
                if v.is_expired
            ]
            for k in expired:
                del self._cache[k]
            
            if expired:
                logger.debug(f"Cleaned up {len(expired)} expired entries")
            
            return len(expired)
