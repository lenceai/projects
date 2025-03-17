from cache import Cache, EvictionStrategy
import time
from threading import Thread


def demonstrate_basic_operations():
    """Demonstrate basic cache operations."""
    print("\n=== Basic Cache Operations ===")
    cache = Cache(max_size=3, strategy=EvictionStrategy.LRU)
    
    # Set some values
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    
    print(f"Cache size: {cache.size}")
    print(f"Get 'a': {cache.get('a')}")
    print(f"Get 'b': {cache.get('b')}")
    
    # This should trigger eviction
    cache.set("d", 4)
    print(f"After adding 'd', get 'c': {cache.get('c')}")  # Should be None due to LRU eviction
    print(f"Cache stats: {cache.stats}")


def demonstrate_ttl():
    """Demonstrate TTL functionality."""
    print("\n=== TTL Functionality ===")
    cache = Cache(max_size=2)
    
    cache.set("key1", "value1", ttl=2)  # Expires in 2 seconds
    print(f"Initial value: {cache.get('key1')}")
    
    time.sleep(3)  # Wait for expiration
    print(f"After expiration: {cache.get('key1')}")


def demonstrate_concurrent_access():
    """Demonstrate thread-safe operations."""
    print("\n=== Concurrent Access ===")
    cache = Cache(max_size=100)

    def worker(start: int):
        for i in range(start, start + 50):
            cache.set(f"key{i}", i)
            time.sleep(0.01)
            cache.get(f"key{i}")

    # Create two threads that will access the cache concurrently
    t1 = Thread(target=worker, args=(0,))
    t2 = Thread(target=worker, args=(50,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"Final cache stats: {cache.stats}")


def demonstrate_eviction_strategies():
    """Demonstrate different eviction strategies."""
    print("\n=== Eviction Strategies ===")
    
    # FIFO demonstration
    fifo_cache = Cache(max_size=3, strategy=EvictionStrategy.FIFO)
    print("FIFO Strategy:")
    for i in range(4):
        fifo_cache.set(f"key{i}", i)
    print(f"FIFO cache after inserting 4 items: {[fifo_cache.get(f'key{i}') for i in range(4)]}")
    
    # LFU demonstration
    lfu_cache = Cache(max_size=3, strategy=EvictionStrategy.LFU)
    print("\nLFU Strategy:")
    for i in range(3):
        lfu_cache.set(f"key{i}", i)
    
    # Access key0 multiple times
    for _ in range(3):
        lfu_cache.get("key0")
    
    # Add new item, should evict least frequently used
    lfu_cache.set("key3", 3)
    print(f"LFU cache after operations: {[lfu_cache.get(f'key{i}') for i in range(4)]}")


if __name__ == "__main__":
    demonstrate_basic_operations()
    demonstrate_ttl()
    demonstrate_concurrent_access()
    demonstrate_eviction_strategies() 