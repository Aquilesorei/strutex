"""
Base cache interface and common types.

Provides the abstract Cache interface and supporting data structures.
"""

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger("strutex.cache")


@dataclass
class CacheKey:
    """
    Unique key for cache entries.
    
    Computed from file content hash + prompt + schema + config.
    """
    file_hash: str
    prompt_hash: str
    schema_hash: str
    provider: str
    model: Optional[str] = None
    extra: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        file_path: str,
        prompt: str,
        schema: Any,
        provider: str = "unknown",
        model: Optional[str] = None,
        **kwargs
    ) -> "CacheKey":
        """
        Create a cache key from extraction parameters.
        
        Args:
            file_path: Path to file (will hash file content)
            prompt: Extraction prompt
            schema: Schema object or dict
            provider: Provider name
            model: Model name
            **kwargs: Additional config to include in key
        """
        # Hash file content
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            file_hash = hashlib.sha256(file_path.encode()).hexdigest()[:16]
        
        # Hash prompt
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        
        # Hash schema
        if hasattr(schema, "model_json_schema"):
            schema_str = json.dumps(schema.model_json_schema(), sort_keys=True)
        elif hasattr(schema, "to_dict"):
            schema_str = json.dumps(schema.to_dict(), sort_keys=True)
        elif isinstance(schema, dict):
            schema_str = json.dumps(schema, sort_keys=True)
        else:
            schema_str = str(schema)
        schema_hash = hashlib.sha256(schema_str.encode()).hexdigest()[:16]
        
        # Hash extra config
        extra = None
        if kwargs:
            extra = hashlib.sha256(
                json.dumps(kwargs, sort_keys=True, default=str).encode()
            ).hexdigest()[:8]
        
        return cls(
            file_hash=file_hash,
            prompt_hash=prompt_hash,
            schema_hash=schema_hash,
            provider=provider,
            model=model,
            extra=extra
        )
    
    def to_string(self) -> str:
        """Convert to string key."""
        parts = [
            self.file_hash,
            self.prompt_hash,
            self.schema_hash,
            self.provider
        ]
        if self.model:
            parts.append(self.model)
        if self.extra:
            parts.append(self.extra)
        return ":".join(parts)
    
    def __hash__(self) -> int:
        return hash(self.to_string())
    
    def __eq__(self, other) -> bool:
        if isinstance(other, CacheKey):
            return self.to_string() == other.to_string()
        return False


@dataclass
class CacheEntry:
    """A cached extraction result."""
    key: str
    result: Any
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    hit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    @property
    def age_seconds(self) -> float:
        """Age of entry in seconds."""
        return time.time() - self.created_at
    
    def touch(self) -> None:
        """Increment hit count."""
        self.hit_count += 1


class Cache(ABC):
    """
    Abstract base class for cache implementations.
    
    All cache implementations should inherit from this class.
    
    Example:
        >>> cache = MemoryCache(max_size=100, ttl=3600)
        >>> 
        >>> # Check cache
        >>> key = CacheKey.create("doc.pdf", "Extract", schema, "gemini")
        >>> cached = cache.get(key)
        >>> 
        >>> if cached is None:
        ...     result = processor.process(...)
        ...     cache.set(key, result)
        >>> else:
        ...     result = cached
    """
    
    @abstractmethod
    def get(self, key: CacheKey) -> Optional[Any]:
        """
        Get a cached result.
        
        Args:
            key: Cache key
            
        Returns:
            Cached result or None if not found/expired
        """
        pass
    
    @abstractmethod
    def set(self, key: CacheKey, result: Any, ttl: Optional[float] = None) -> None:
        """
        Store a result in cache.
        
        Args:
            key: Cache key
            result: Result to cache
            ttl: Optional TTL in seconds (overrides default)
        """
        pass
    
    @abstractmethod
    def delete(self, key: CacheKey) -> bool:
        """
        Delete a cached entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            Number of entries cleared
        """
        pass
    
    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with hits, misses, size, etc.
        """
        pass
    
    def has(self, key: CacheKey) -> bool:
        """Check if key exists in cache."""
        return self.get(key) is not None
