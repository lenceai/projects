from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Dict, Optional

@dataclass
class Visit:
    id: str
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)

@dataclass
class CounterShard:
    shard_id: str
    count: int = 0
    visits: Dict[str, Visit] = field(default_factory=dict)
    high_precision_mode: bool = False
    milestone_threshold: int = 99_900_000_000  # 99.9B

    def increment(self, metadata: Optional[Dict] = None) -> Visit:
        """Increment the counter and return visit details."""
        self.count += 1
        visit = Visit(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.visits[visit.id] = visit
        
        # Check if we should enter high precision mode
        if self.count >= self.milestone_threshold and not self.high_precision_mode:
            self.high_precision_mode = True
            
        return visit

    def get_count(self) -> int:
        """Get current count for this shard."""
        return self.count

    def merge(self, other: 'CounterShard') -> None:
        """Merge another counter shard into this one (CRDT-like behavior)."""
        self.count = max(self.count, other.count)
        self.visits.update(other.visits)
        
    def is_high_precision_mode(self) -> bool:
        """Check if counter is in high precision mode."""
        return self.high_precision_mode

    def get_recent_visits(self, limit: int = 100) -> Dict[str, Visit]:
        """Get most recent visits, useful for debugging and monitoring."""
        sorted_visits = sorted(
            self.visits.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )
        return dict(sorted_visits[:limit]) 