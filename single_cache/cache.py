from enum import Enum
from threading import Lock
from typing import Any, Dict, Optional
from collections import OrderedDict
import time
from dataclasses import dataclass


class EvictionStrategy(Enum):
    """Available cache eviction strategies."""
    LRU = "least_recently_used"
    FIFO = "first_in_first_out"
    LFU = "least_frequently_used"


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""
    value: Any
    timestamp: float
    access_count: int = 0
    expiry: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return self.expiry is not None and time.time() > self.expiry


class Cache:
    """
    A thread-safe cache implementation with multiple eviction strategies.
    
    Features:
    - Multiple eviction strategies (LRU, FIFO, LFU)
    - Thread-safe operations
    - TTL support
    - Access statistics
    """

    def __init__(self, max_size: int = 1000, strategy: EvictionStrategy = EvictionStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]
            
            if entry.is_expired():
                self._cache.pop(key)
                self._misses += 1
                return None

            self._hits += 1
            entry.access_count += 1

            if self.strategy == EvictionStrategy.LRU:
                # Move to end for LRU strategy
                self._cache.move_to_end(key)

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: The key to store the value under
            value: The value to store
            ttl: Time-to-live in seconds (optional)
        """
        with self._lock:
            # Calculate expiry time if TTL is provided
            expiry = time.time() + ttl if ttl is not None else None
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                expiry=expiry
            )

            # If key exists, update it
            if key in self._cache:
                self._cache.pop(key)
                self._cache[key] = entry
                return

            # Check if we need to evict
            if len(self._cache) >= self.max_size:
                self._evict()

            self._cache[key] = entry

    def _evict(self) -> None:
        """Remove an entry based on the chosen eviction strategy."""
        if not self._cache:
            return

        if self.strategy == EvictionStrategy.FIFO:
            # Remove the first item (oldest)
            self._cache.popitem(last=False)
        
        elif self.strategy == EvictionStrategy.LRU:
            # Remove the first item (least recently used)
            self._cache.popitem(last=False)
        
        elif self.strategy == EvictionStrategy.LFU:
            # Remove the least frequently used item
            min_count = float('inf')
            min_key = None
            
            for key, entry in self._cache.items():
                if entry.access_count < min_count:
                    min_count = entry.access_count
                    min_key = key
            
            if min_key:
                self._cache.pop(min_key)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        """Return the current number of entries in the cache."""
        return len(self._cache)

    @property
    def stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        with self._lock:
            return {
                "hits": self._hits,
                "misses": self._misses,
                "size": len(self._cache),
                "max_size": self.max_size
            } 