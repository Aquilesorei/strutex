"""
Cache system for strutex.

Provides caching to reduce API costs and improve response times for
repeated extractions.

Available Caches:
- MemoryCache: In-memory LRU cache (fast, ephemeral)
- SQLiteCache: Persistent SQLite cache (durable, lightweight)
- FileCache: File-based cache (simple, portable)
"""

from .base import CacheKey, CacheEntry, Cache
from .memory import MemoryCache
from .sqlite import SQLiteCache
from .file import FileCache

__all__ = [
    # Base
    "CacheKey",
    "CacheEntry", 
    "Cache",
    
    # Implementations
    "MemoryCache",
    "SQLiteCache",
    "FileCache",
]
