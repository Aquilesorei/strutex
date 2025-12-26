"""
File-based cache implementation.

Simple, portable cache using JSON files.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .base import Cache, CacheKey, CacheEntry

logger = logging.getLogger("strutex.cache.file")


class FileCache(Cache):
    """
    File-based JSON cache.
    
    Features:
    - Simple JSON files (one per entry)
    - Easy to inspect and debug
    - Portable across systems
    - TTL support
    
    Example:
        >>> cache = FileCache("~/.cache/strutex/", ttl=86400)
        >>> 
        >>> key = CacheKey.create("doc.pdf", "Extract", schema, "gemini")
        >>> cache.set(key, {"invoice_number": "INV-001"})
        >>> 
        >>> # Files stored at ~/.cache/strutex/{hash}.json
        >>> result = cache.get(key)
    """
    
    def __init__(
        self,
        cache_dir: str = "~/.cache/strutex/files/",
        ttl: Optional[float] = None
    ):
        """
        Args:
            cache_dir: Directory for cache files
            ttl: Default TTL in seconds (None = never expire)
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = ttl
        self._hits = 0
        self._misses = 0
        
        logger.debug(f"File cache initialized: {self.cache_dir}")
    
    def _key_to_path(self, key: CacheKey) -> Path:
        """Convert cache key to file path."""
        # Use first 32 chars of key string as filename
        key_str = key.to_string()
        safe_name = key_str.replace(":", "_")[:64]
        return self.cache_dir / f"{safe_name}.json"
    
    def get(self, key: CacheKey) -> Optional[Any]:
        """Get a cached result."""
        path = self._key_to_path(key)
        
        if not path.exists():
            self._misses += 1
            return None
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            # Check expiration
            expires_at = data.get("expires_at")
            if expires_at is not None and time.time() > expires_at:
                path.unlink(missing_ok=True)
                self._misses += 1
                logger.debug(f"Cache expired: {path.name}")
                return None
            
            self._hits += 1
            logger.debug(f"Cache hit: {path.name}")
            return data["result"]
            
        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.warning(f"Cache read error: {e}")
            self._misses += 1
            return None
    
    def set(self, key: CacheKey, result: Any, ttl: Optional[float] = None) -> None:
        """Store a result."""
        path = self._key_to_path(key)
        actual_ttl = ttl if ttl is not None else self.default_ttl
        
        now = time.time()
        data = {
            "key": key.to_string(),
            "result": result,
            "created_at": now,
            "expires_at": now + actual_ttl if actual_ttl else None,
        }
        
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug(f"Cache set: {path.name}")
            
        except IOError as e:
            logger.warning(f"Cache write error: {e}")
    
    def delete(self, key: CacheKey) -> bool:
        """Delete a cached entry."""
        path = self._key_to_path(key)
        
        if path.exists():
            path.unlink()
            logger.debug(f"Cache deleted: {path.name}")
            return True
        return False
    
    def clear(self) -> int:
        """Clear all cached entries."""
        count = 0
        for path in self.cache_dir.glob("*.json"):
            try:
                path.unlink()
                count += 1
            except IOError:
                pass
        
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache cleared: {count} entries")
        return count
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        
        return {
            "type": "file",
            "path": str(self.cache_dir),
            "size": len(files),
            "size_bytes": total_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "ttl": self.default_ttl,
        }
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        now = time.time()
        count = 0
        
        for path in self.cache_dir.glob("*.json"):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                
                expires_at = data.get("expires_at")
                if expires_at is not None and now > expires_at:
                    path.unlink()
                    count += 1
                    
            except (json.JSONDecodeError, IOError):
                pass
        
        if count > 0:
            logger.debug(f"Cleaned up {count} expired entries")
        
        return count
