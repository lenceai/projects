from dataclasses import dataclass, field
from typing import Dict, List
from .counter_shard import CounterShard, Visit

@dataclass
class RegionalAggregator:
    region_id: str
    shards: Dict[str, CounterShard] = field(default_factory=dict)
    aggregation_interval_ms: int = 1000  # 1 second by default
    
    def add_shard(self, shard: CounterShard) -> None:
        """Add a new counter shard to this region."""
        self.shards[shard.shard_id] = shard
        
    def get_total_count(self) -> int:
        """Get the total count across all shards in this region."""
        return sum(shard.get_count() for shard in self.shards.values())
    
    def get_all_visits(self) -> Dict[str, Visit]:
        """Combine all visits from all shards."""
        all_visits = {}
        for shard in self.shards.values():
            all_visits.update(shard.visits)
        return all_visits
    
    def is_any_shard_high_precision(self) -> bool:
        """Check if any shard is in high precision mode."""
        return any(shard.is_high_precision_mode() for shard in self.shards.values())
    
    def adjust_aggregation_interval(self) -> None:
        """Adjust aggregation interval based on high precision mode."""
        if self.is_any_shard_high_precision():
            self.aggregation_interval_ms = 100  # Switch to 100ms updates
        else:
            self.aggregation_interval_ms = 1000  # Normal 1s updates
            
    def get_metrics(self) -> Dict:
        """Get region metrics for monitoring."""
        return {
            "region_id": self.region_id,
            "total_count": self.get_total_count(),
            "shard_count": len(self.shards),
            "high_precision_mode": self.is_any_shard_high_precision(),
            "aggregation_interval_ms": self.aggregation_interval_ms
        } 