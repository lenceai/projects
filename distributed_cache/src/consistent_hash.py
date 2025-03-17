import hashlib
from typing import Optional, List, Dict, Any

class ConsistentHash:
    def __init__(self, nodes: Optional[List[str]] = None, replicas: int = 100):
        """
        Initialize the consistent hash ring.
        
        Args:
            nodes: List of initial node identifiers
            replicas: Number of virtual nodes per physical node
        """
        self.replicas = replicas
        self.ring: Dict[int, str] = {}  # Maps virtual node positions to physical nodes
        self.sorted_keys: List[int] = []  # Sorted list of virtual node positions
        
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def _hash(self, key: Any) -> int:
        """Hash a key to a point on the ring."""
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)
    
    def add_node(self, node: str) -> None:
        """
        Add a node with multiple virtual nodes on the ring.
        
        Args:
            node: Node identifier to add
        """
        for i in range(self.replicas):
            hash_key = self._hash(f"{node}:{i}")
            self.ring[hash_key] = node
            self.sorted_keys.append(hash_key)
        self.sorted_keys.sort()
    
    def remove_node(self, node: str) -> None:
        """
        Remove a node and its virtual nodes from the ring.
        
        Args:
            node: Node identifier to remove
        """
        for i in range(self.replicas):
            hash_key = self._hash(f"{node}:{i}")
            if hash_key in self.ring:
                del self.ring[hash_key]
                self.sorted_keys.remove(hash_key)
    
    def get_node(self, key: Any) -> Optional[str]:
        """
        Determine which node a key belongs to.
        
        Args:
            key: The key to look up
            
        Returns:
            The node identifier or None if the ring is empty
        """
        if not self.ring:
            return None
            
        hash_key = self._hash(key)
        
        # Find the first node on the ring that is >= the hashed key
        for ring_key in self.sorted_keys:
            if hash_key <= ring_key:
                return self.ring[ring_key]
        
        # If we've reached here, wrap around to the first node
        return self.ring[self.sorted_keys[0]]
    
    def get_nodes(self, key: Any, count: int) -> List[str]:
        """
        Get multiple nodes for replication.
        
        Args:
            key: The key to look up
            count: Number of nodes to return
            
        Returns:
            List of node identifiers
        """
        if not self.ring:
            return []
            
        nodes = []
        seen_nodes = set()
        
        # Start with the primary node
        primary = self.get_node(key)
        if primary:
            nodes.append(primary)
            seen_nodes.add(primary)
        
        # Find additional nodes by walking the ring
        if primary and count > 1:
            hash_key = self._hash(key)
            for ring_key in self.sorted_keys:
                node = self.ring[ring_key]
                if node not in seen_nodes:
                    nodes.append(node)
                    seen_nodes.add(node)
                    if len(nodes) >= count:
                        break
        
        return nodes 