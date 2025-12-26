
"""
Tests for caching system (v0.8.0).
"""

import os
import time
import pytest
import sqlite3
import json
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strutex.cache.base import CacheKey, CacheEntry
from strutex.cache.memory import MemoryCache
from strutex.cache.file import FileCache
from strutex.cache.sqlite import SQLiteCache

# --- Test Cache Key ---

class TestCacheKey:
    def test_key_generation(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        
        key1 = CacheKey.create(str(f), "prompt", {}, "gemini")
        key2 = CacheKey.create(str(f), "prompt", {}, "gemini")
        
        assert key1 == key2
        assert hash(key1) == hash(key2)
        assert key1.to_string() == key2.to_string()

    def test_key_differs(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        
        # Diff prompt
        k1 = CacheKey.create(str(f), "A", {}, "gemini")
        k2 = CacheKey.create(str(f), "B", {}, "gemini")
        assert k1 != k2
        
        # Diff schema
        k3 = CacheKey.create(str(f), "A", {"a": 1}, "gemini")
        assert k1 != k3

# --- Test Memory Cache ---

class TestMemoryCache:
    def test_basic_ops(self, tmp_path):
        cache = MemoryCache()
        key = CacheKey.create("doc.pdf", "p", {}, "g")
        
        # Get empty
        assert cache.get(key) is None
        assert cache._misses == 1
        
        # Set
        cache.set(key, {"data": 123})
        
        # Get hit
        assert cache.get(key) == {"data": 123}
        assert cache._hits == 1
        
        # Delete
        assert cache.delete(key) is True
        assert cache.get(key) is None
        
    def test_lru_eviction(self):
        cache = MemoryCache(max_size=2)
        k1 = CacheKey.create("1", "p", {}, "g")
        k2 = CacheKey.create("2", "p", {}, "g")
        k3 = CacheKey.create("3", "p", {}, "g")
        
        cache.set(k1, 1)
        cache.set(k2, 2)
        
        # Access k1 to make it MRU
        cache.get(k1)
        
        # Add k3, should evict k2 (LRU)
        cache.set(k3, 3)
        
        assert cache.get(k1) == 1
        assert cache.get(k3) == 3
        assert cache.get(k2) is None  # Evicted

    def test_ttl_expiration(self):
        cache = MemoryCache(ttl=0.1)
        key = CacheKey.create("1", "p", {}, "g")
        
        cache.set(key, 1)
        assert cache.get(key) == 1
        
        time.sleep(0.15)
        assert cache.get(key) is None  # Expired

# --- Test File Cache ---

class TestFileCache:
    def test_persistence(self, tmp_path):
        cache_dir = tmp_path / "cache"
        cache = FileCache(cache_dir=str(cache_dir))
        key = CacheKey.create("doc.pdf", "p", {}, "g")
        
        # Set
        cache.set(key, {"foo": "bar"})
        
        # Reload
        cache2 = FileCache(cache_dir=str(cache_dir))
        assert cache2.get(key) == {"foo": "bar"}

    def test_corrupt_file(self, tmp_path):
        cache_dir = tmp_path / "cache"
        cache = FileCache(cache_dir=str(cache_dir))
        key = CacheKey.create("doc.pdf", "p", {}, "g")
        
        # Create invalid file manually
        key_str = key.to_string()
        import hashlib
        fname = hashlib.sha256(key_str.encode()).hexdigest() + ".json"
        
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_dir / fname, "w") as f:
            f.write("{invalid json")
            
        # Should handle error gracefully
        assert cache.get(key) is None

# --- Test SQLite Cache ---

class TestSQLiteCache:
    def test_db_ops(self, tmp_path):
        db_path = tmp_path / "cache.db"
        cache = SQLiteCache(db_path=str(db_path))
        key = CacheKey.create("doc.pdf", "p", {}, "g")
        
        cache.set(key, {"data": 1})
        assert cache.get(key) == {"data": 1}
        
        # Recover
        cache2 = SQLiteCache(db_path=str(db_path))
        assert cache2.get(key) == {"data": 1}
        
    def test_eager_init(self, tmp_path):
        db_path = tmp_path / "eager.db"
        cache = SQLiteCache(db_path=str(db_path))
        
        # Init happens immediately
        assert os.path.exists(str(db_path))
        
        # Verify schema
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cache'")
            assert cursor.fetchone() is not None

    def test_concurrent_access(self, tmp_path):
        # Basic check that connection is thread-local or managed
        db_path = tmp_path / "shared.db"
        c1 = SQLiteCache(db_path=str(db_path))
        c2 = SQLiteCache(db_path=str(db_path))
        
        key = CacheKey.create("a", "b", {}, "c")
        c1.set(key, 1)
        assert c2.get(key) == 1
