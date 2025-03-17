from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
from .regional_aggregator import RegionalAggregator
from .counter_shard import Visit

@dataclass
class GlobalAggregator:
    regions: Dict[str, RegionalAggregator] = field(default_factory=dict)
    target_count: int = 100_000_000_000  # 100B
    winner: Optional[Visit] = None
    
    def add_region(self, region: RegionalAggregator) -> None:
        """Add a new region to the global aggregator."""
        self.regions[region.region_id] = region
        
    def get_global_count(self) -> int:
        """Get the total count across all regions."""
        return sum(region.get_total_count() for region in self.regions.values())
    
    def check_for_winner(self, visit: Visit) -> bool:
        """Check if this visit is the winner and store if so."""
        current_count = self.get_global_count()
        
        if current_count == self.target_count and not self.winner:
            self.winner = visit
            return True
        return False
    
    def is_approaching_target(self) -> bool:
        """Check if we're approaching the target count."""
        current_count = self.get_global_count()
        return current_count >= (self.target_count - 100_000_000)  # Within 100M
    
    def adjust_precision(self) -> None:
        """Adjust precision mode for all regions if approaching target."""
        if self.is_approaching_target():
            for region in self.regions.values():
                region.adjust_aggregation_interval()
                
    def get_winner_details(self) -> Optional[Dict]:
        """Get details about the winning visit if exists."""
        if not self.winner:
            return None
            
        return {
            "visit_id": self.winner.id,
            "timestamp": self.winner.timestamp.isoformat(),
            "metadata": self.winner.metadata
        }
        
    def get_metrics(self) -> Dict:
        """Get global metrics for monitoring."""
        return {
            "global_count": self.get_global_count(),
            "region_count": len(self.regions),
            "approaching_target": self.is_approaching_target(),
            "has_winner": self.winner is not None,
            "regions": {
                region_id: region.get_metrics()
                for region_id, region in self.regions.items()
            }
        } 