# Distributed Cache

A simple distributed cache implementation in Python, similar to Memcached. This implementation features:

- Consistent hashing for data distribution
- LRU eviction policy
- TTL support
- Memory management
- Thread-safe operations
- Asynchronous client/server communication
- Basic replication support
- Statistics tracking

## Features

- **Consistent Hashing**: Efficiently distributes data across multiple nodes
- **LRU Eviction**: Removes least recently used items when memory is full
- **TTL Support**: Automatic expiration of cache items
- **Memory Management**: Tracks memory usage and enforces limits
- **Thread Safety**: All operations are thread-safe
- **Replication**: Basic support for data replication across nodes
- **Statistics**: Tracks hits, misses, evictions, and memory usage

## Requirements

```
pytest==7.4.3
aiohttp==3.9.1
msgpack==1.0.7
python-dateutil==2.8.2
```

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Example

The `example.py` script demonstrates basic usage:

```bash
python example.py
```

### Using in Your Code

1. Start cache servers:

```python
from src.cache_server import CacheServer

# Create and run servers
server1 = CacheServer(max_memory_mb=100)
server2 = CacheServer(max_memory_mb=100)

# Run on different ports
server1.run(host='localhost', port=8001)
server2.run(host='localhost', port=8002)
```

2. Use the client:

```python
from src.cache_client import DistributedCacheClient

# Create client
nodes = ['http://localhost:8001', 'http://localhost:8002']
client = DistributedCacheClient(nodes)

# Set values
await client.set('key1', 'value1')
await client.set('key2', 'value2', ttl=60)  # Expires in 60 seconds

# Get values
value, success = await client.get('key1')

# Delete values
success = await client.delete('key1')

# Get statistics
stats = await client.get_stats()

# Close client when done
await client.close()
```

## Architecture

The distributed cache consists of three main components:

1. **Cache Node**: Handles the actual storage and retrieval of data
2. **Cache Server**: Provides HTTP API for interacting with a cache node
3. **Cache Client**: Manages communication with multiple cache servers

### Consistent Hashing

The system uses consistent hashing to distribute data across nodes:

- Each node is mapped to multiple points on a hash ring
- Keys are mapped to nodes based on their position on the ring
- Adding/removing nodes only affects a small portion of the keys

### Replication

Basic replication is supported:

- Data can be replicated to multiple nodes
- Read operations can fall back to replica nodes
- Write operations are performed on all replicas

### Memory Management

Each node manages its memory:

- Tracks memory usage of stored items
- Enforces a maximum memory limit
- Uses LRU eviction when memory is full

## Contributing

Feel free to submit issues and pull requests.

## License

MIT License 