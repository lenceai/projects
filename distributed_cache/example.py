import asyncio
import time
from src.cache_server import CacheServer
from src.cache_client import DistributedCacheClient

async def run_example():
    # Start two cache servers
    server1 = CacheServer(max_memory_mb=100)
    server2 = CacheServer(max_memory_mb=100)
    
    # Run servers in the background
    runner1 = asyncio.create_task(server1.run(host='localhost', port=8001))
    runner2 = asyncio.create_task(server2.run(host='localhost', port=8002))
    
    # Wait for servers to start
    await asyncio.sleep(1)
    
    # Create a client
    nodes = ['http://localhost:8001', 'http://localhost:8002']
    client = DistributedCacheClient(nodes)
    
    try:
        # Set some values
        print("Setting values...")
        await client.set('key1', 'value1')
        await client.set('key2', 'value2', ttl=5)  # Expires in 5 seconds
        
        # Get values
        print("\nGetting values...")
        value1, success1 = await client.get('key1')
        print(f"key1: {value1} (success: {success1})")
        
        value2, success2 = await client.get('key2')
        print(f"key2: {value2} (success: {success2})")
        
        # Wait for TTL to expire
        print("\nWaiting for key2 to expire...")
        await asyncio.sleep(6)
        
        value2, success2 = await client.get('key2')
        print(f"key2 after expiry: {value2} (success: {success2})")
        
        # Delete a key
        print("\nDeleting key1...")
        success = await client.delete('key1')
        print(f"Delete success: {success}")
        
        # Get statistics
        print("\nGetting statistics...")
        stats = await client.get_stats()
        print("Stats:", stats)
    
    finally:
        # Cleanup
        await client.close()
        for task in [runner1, runner2]:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

if __name__ == '__main__':
    asyncio.run(run_example()) 