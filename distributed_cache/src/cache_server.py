from aiohttp import web
import msgpack
from typing import Dict, Any
from .cache_node import CacheNode

class CacheServer:
    def __init__(self, max_memory_mb: int = 1024):
        """
        Initialize the cache server.
        
        Args:
            max_memory_mb: Maximum memory in megabytes
        """
        self.node = CacheNode(max_memory_mb)
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up the server routes."""
        self.app.router.add_get('/cache/{key}', self.get_handler)
        self.app.router.add_put('/cache/{key}', self.set_handler)
        self.app.router.add_delete('/cache/{key}', self.delete_handler)
        self.app.router.add_get('/stats', self.stats_handler)
    
    async def get_handler(self, request: web.Request) -> web.Response:
        """Handle GET requests for cache items."""
        key = request.match_info['key']
        value, success = self.node.get(key)
        
        if success:
            return web.json_response(
                {'value': value},
                dumps=msgpack.packb
            )
        else:
            return web.Response(status=404)
    
    async def set_handler(self, request: web.Request) -> web.Response:
        """Handle PUT requests to set cache items."""
        key = request.match_info['key']
        try:
            data = await request.json(loads=msgpack.unpackb)
            value = data['value']
            ttl = data.get('ttl')
            
            success = self.node.set(key, value, ttl)
            if success:
                return web.Response(status=200)
            else:
                return web.Response(status=507)  # Insufficient storage
        except Exception as e:
            return web.Response(status=400, text=str(e))
    
    async def delete_handler(self, request: web.Request) -> web.Response:
        """Handle DELETE requests for cache items."""
        key = request.match_info['key']
        success = self.node.delete(key)
        
        if success:
            return web.Response(status=200)
        else:
            return web.Response(status=404)
    
    async def stats_handler(self, request: web.Request) -> web.Response:
        """Handle GET requests for cache statistics."""
        stats = self.node.get_stats()
        return web.json_response(stats, dumps=msgpack.packb)
    
    def run(self, host: str = 'localhost', port: int = 8080):
        """Run the cache server."""
        web.run_app(self.app, host=host, port=port) 