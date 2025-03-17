# Single Cache Implementation

A Python implementation of a caching system demonstrating different caching strategies and patterns.

## Features

- Multiple eviction strategies (LRU, FIFO, LFU)
- Thread-safe operations
- Configurable cache size
- TTL (Time-To-Live) support
- Statistics tracking

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Basic usage example:

```python
from cache import Cache, EvictionStrategy

# Create an LRU cache with size 1000
cache = Cache(max_size=1000, strategy=EvictionStrategy.LRU)

# Set a value
cache.set("key", "value")

# Get a value
value = cache.get("key")

# Set with TTL (5 seconds)
cache.set("key2", "value2", ttl=5)
```

## Running Tests

```bash
pytest tests/
```

## Design Considerations

This implementation focuses on:
- Clean, extensible design
- Thread safety
- Performance optimization
- Memory efficiency

See the documentation in the code for detailed explanations of each component. 