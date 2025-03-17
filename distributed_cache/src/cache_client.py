import asyncio
import aiohttp
import msgpack
from typing import Any, List, Optional, Dict, Tuple
from .consistent_hash import ConsistentHash

class DistributedCacheClient:
    def __init__(self, nodes: List[str], replicas: int = 100):
        """
        Initialize the distributed cache client.
        
        Args:
            nodes: List of node URLs (e.g., ['http://localhost:8001', 'http://localhost:8002'])
            replicas: Number of virtual nodes per physical node
        """
        self.consistent_hash = ConsistentHash(nodes, replicas)
        self._session: Optional[aiohttp.ClientSession] = None
        self.default_timeout = 5.0  # seconds
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                json_serialize=msgpack.packb,
                json_deserialize=msgpack.unpackb
            )
        return self._session
    
    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get(self, key: str) -> Tuple[Any, bool]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            Tuple of (value, success)
        """
        node = self.consistent_hash.get_node(key)
        if not node:
            return None, False
        
        session = await self._get_session()
        try:
            async with session.get(
                f"{node}/cache/{key}",
                timeout=self.default_timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['value'], True
                elif response.status == 404:
                    return None, False
                else:
                    # Try backup nodes in case of failure
                    backup_nodes = self.consistent_hash.get_nodes(key, 2)[1:]
                    for backup_node in backup_nodes:
                        try:
                            async with session.get(
                                f"{backup_node}/cache/{key}",
                                timeout=self.default_timeout
                            ) as backup_response:
                                if backup_response.status == 200:
                                    data = await backup_response.json()
                                    return data['value'], True
                        except:
                            continue
                    return None, False
        except:
            return None, False
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        replicas: int = 2
    ) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The key to store
            value: The value to store
            ttl: Time-to-live in seconds
            replicas: Number of replicas to maintain
            
        Returns:
            True if successful on at least one node
        """
        nodes = self.consistent_hash.get_nodes(key, replicas)
        if not nodes:
            return False
        
        session = await self._get_session()
        data = {
            'value': value,
            'ttl': ttl
        }
        
        success = False
        for node in nodes:
            try:
                async with session.put(
                    f"{node}/cache/{key}",
                    json=data,
                    timeout=self.default_timeout
                ) as response:
                    if response.status == 200:
                        success = True
            except:
                continue
        
        return success
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from all nodes.
        
        Args:
            key: The key to delete
            
        Returns:
            True if deleted from at least one node
        """
        nodes = self.consistent_hash.get_nodes(key, 2)
        if not nodes:
            return False
        
        session = await self._get_session()
        success = False
        
        for node in nodes:
            try:
                async with session.delete(
                    f"{node}/cache/{key}",
                    timeout=self.default_timeout
                ) as response:
                    if response.status == 200:
                        success = True
            except:
                continue
        
        return success
    
    async def get_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Get statistics from all nodes.
        
        Returns:
            Dictionary mapping node URLs to their statistics
        """
        session = await self._get_session()
        stats = {}
        
        for node in set(self.consistent_hash.ring.values()):
            try:
                async with session.get(
                    f"{node}/stats",
                    timeout=self.default_timeout
                ) as response:
                    if response.status == 200:
                        stats[node] = await response.json()
            except:
                continue
        
        return stats 