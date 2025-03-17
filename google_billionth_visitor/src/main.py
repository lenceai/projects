from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import uuid

from .counter_shard import CounterShard
from .regional_aggregator import RegionalAggregator
from .global_aggregator import GlobalAggregator

app = FastAPI(title="Google's 100 Billionth Visitor Counter")

# Initialize our system with some example regions and shards
def initialize_system():
    # Create global aggregator
    global_agg = GlobalAggregator()
    
    # Create some example regions
    regions = ["us-west", "us-east", "europe", "asia"]
    for region_id in regions:
        region = RegionalAggregator(region_id=region_id)
        
        # Add some shards to each region
        for i in range(3):  # 3 shards per region
            shard = CounterShard(shard_id=f"{region_id}-shard-{i}")
            region.add_shard(shard)
            
        global_agg.add_region(region)
    
    return global_agg

# Initialize our system
global_aggregator = initialize_system()

class VisitRequest(BaseModel):
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    region_id: str
    shard_id: str

class VisitResponse(BaseModel):
    visit_id: str
    is_winner: bool
    global_count: int

@app.post("/visit", response_model=VisitResponse)
async def register_visit(visit_req: VisitRequest):
    """Register a new visit and check if it's the winner."""
    # Find the appropriate region and shard
    region = global_aggregator.regions.get(visit_req.region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
        
    shard = region.shards.get(visit_req.shard_id)
    if not shard:
        raise HTTPException(status_code=404, detail="Shard not found")
    
    # Record the visit
    metadata = {
        "user_agent": visit_req.user_agent,
        "ip_address": visit_req.ip_address,
        "region_id": visit_req.region_id,
        "shard_id": visit_req.shard_id
    }
    visit = shard.increment(metadata=metadata)
    
    # Check if this is the winning visit
    is_winner = global_aggregator.check_for_winner(visit)
    
    # Adjust precision if needed
    global_aggregator.adjust_precision()
    
    return VisitResponse(
        visit_id=visit.id,
        is_winner=is_winner,
        global_count=global_aggregator.get_global_count()
    )

@app.get("/count")
async def get_count():
    """Get the current global count."""
    return {
        "count": global_aggregator.get_global_count(),
        "approaching_target": global_aggregator.is_approaching_target()
    }

@app.get("/winner")
async def get_winner():
    """Get information about the winner if exists."""
    winner_details = global_aggregator.get_winner_details()
    if not winner_details:
        raise HTTPException(status_code=404, detail="No winner yet")
    return winner_details

@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    return global_aggregator.get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 