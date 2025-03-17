import time
import threading
from typing import Dict, Tuple, Any, Optional
from dataclasses import dataclass
import sys

@dataclass
class CacheItem:
    value: Any
    expiry: Optional[float]
    access_time: float
    size: int

class CacheNode:
    def __init__(self, max_memory_mb: int = 1024):
        """
        Initialize a cache node.
        
        Args:
            max_memory_mb: Maximum memory in megabytes
        """
        self.cache: Dict[str, CacheItem] = {}
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.current_memory = 0
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def _get_item_size(self, key: str, value: Any) -> int:
        """Calculate the approximate size of a cache item in bytes."""
        # This is a rough approximation
        return sys.getsizeof(key) + sys.getsizeof(value)
    
    def get(self, key: str) -> Tuple[Any, bool]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            Tuple of (value, success)
        """
        with self.lock:
            item = self.cache.get(key)
            if not item:
                self.stats['misses'] += 1
                return None, False
            
            # Check expiration
            if item.expiry and time.time() > item.expiry:
                del self.cache[key]
                self.current_memory -= item.size
                self.stats['misses'] += 1
                return None, False
            
            # Update access time
            item.access_time = time.time()
            self.stats['hits'] += 1
            return item.value, True
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The key to store
            value: The value to store
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            # Calculate size of new item
            size = self._get_item_size(key, value)
            
            # If key exists, remove its size from current_memory
            if key in self.cache:
                self.current_memory -= self.cache[key].size
            
            # Check if we need to make room
            while self.current_memory + size > self.max_memory:
                if not self._evict_one():
                    return False
            
            # Calculate expiry time if TTL is provided
            expiry = time.time() + ttl if ttl else None
            
            # Add/update the item
            self.cache[key] = CacheItem(
                value=value,
                expiry=expiry,
                access_time=time.time(),
                size=size
            )
            self.current_memory += size
            return True
    
    def _evict_one(self) -> bool:
        """
        Evict the least recently used item.
        
        Returns:
            True if an item was evicted, False if no items to evict
        """
        if not self.cache:
            return False
            
        # Find the least recently accessed item
        lru_key = min(self.cache.items(), key=lambda x: x[1].access_time)[0]
        item = self.cache[lru_key]
        
        # Remove it
        del self.cache[lru_key]
        self.current_memory -= item.size
        self.stats['evictions'] += 1
        return True
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: The key to delete
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        with self.lock:
            if key in self.cache:
                self.current_memory -= self.cache[key].size
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self.lock:
            self.cache.clear()
            self.current_memory = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self.lock:
            return {
                **self.stats,
                'current_memory': self.current_memory,
                'item_count': len(self.cache)
            } 