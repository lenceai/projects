import pytest
import time
from cache import Cache, EvictionStrategy


def test_basic_operations():
    cache = Cache(max_size=2)
    
    # Test set and get
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    # Test missing key
    assert cache.get("nonexistent") is None
    
    # Test eviction
    cache.set("key2", "value2")
    cache.set("key3", "value3")  # Should evict key1
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"


def test_ttl():
    cache = Cache(max_size=1)
    
    # Test TTL expiration
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"
    
    time.sleep(1.1)  # Wait for expiration
    assert cache.get("key1") is None


def test_eviction_strategies():
    # Test FIFO
    fifo_cache = Cache(max_size=2, strategy=EvictionStrategy.FIFO)
    fifo_cache.set("key1", 1)
    fifo_cache.set("key2", 2)
    fifo_cache.set("key3", 3)  # Should evict key1
    assert fifo_cache.get("key1") is None
    assert fifo_cache.get("key2") == 2
    
    # Test LRU
    lru_cache = Cache(max_size=2, strategy=EvictionStrategy.LRU)
    lru_cache.set("key1", 1)
    lru_cache.set("key2", 2)
    lru_cache.get("key1")  # Access key1 to make it most recently used
    lru_cache.set("key3", 3)  # Should evict key2
    assert lru_cache.get("key1") == 1
    assert lru_cache.get("key2") is None
    assert lru_cache.get("key3") == 3
    
    # Test LFU
    lfu_cache = Cache(max_size=2, strategy=EvictionStrategy.LFU)
    lfu_cache.set("key1", 1)
    lfu_cache.set("key2", 2)
    lfu_cache.get("key1")  # Access key1 to increase its frequency
    lfu_cache.get("key1")
    lfu_cache.set("key3", 3)  # Should evict key2 (least frequently used)
    assert lfu_cache.get("key1") == 1
    assert lfu_cache.get("key2") is None
    assert lfu_cache.get("key3") == 3


def test_stats():
    cache = Cache(max_size=2)
    
    # Test hit/miss counting
    cache.set("key1", "value1")
    cache.get("key1")  # Hit
    cache.get("nonexistent")  # Miss
    
    stats = cache.stats
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["size"] == 1
    assert stats["max_size"] == 2


def test_clear():
    cache = Cache(max_size=2)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.size == 2
    
    cache.clear()
    assert cache.size == 0
    assert cache.get("key1") is None
    assert cache.get("key2") is None 