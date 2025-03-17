import pytest
from datetime import datetime
from .counter_shard import CounterShard, Visit
from .regional_aggregator import RegionalAggregator
from .global_aggregator import GlobalAggregator

def test_counter_shard():
    shard = CounterShard(shard_id="test-shard")
    
    # Test basic increment
    visit = shard.increment()
    assert shard.get_count() == 1
    assert isinstance(visit, Visit)
    
    # Test high precision mode
    shard.count = 99_900_000_000  # Set count near threshold
    visit = shard.increment()
    assert shard.is_high_precision_mode() == True

def test_regional_aggregator():
    region = RegionalAggregator(region_id="test-region")
    
    # Add multiple shards
    shard1 = CounterShard(shard_id="shard1")
    shard2 = CounterShard(shard_id="shard2")
    
    region.add_shard(shard1)
    region.add_shard(shard2)
    
    # Test counting across shards
    shard1.increment()
    shard2.increment()
    shard2.increment()
    
    assert region.get_total_count() == 3
    
    # Test high precision propagation
    shard1.count = 99_900_000_000
    shard1.increment()
    assert region.is_any_shard_high_precision() == True

def test_global_aggregator():
    global_agg = GlobalAggregator()
    
    # Create and add regions
    region1 = RegionalAggregator(region_id="region1")
    region2 = RegionalAggregator(region_id="region2")
    
    shard1 = CounterShard(shard_id="shard1")
    shard2 = CounterShard(shard_id="shard2")
    
    region1.add_shard(shard1)
    region2.add_shard(shard2)
    
    global_agg.add_region(region1)
    global_agg.add_region(region2)
    
    # Test global counting
    visit1 = shard1.increment()
    visit2 = shard2.increment()
    
    assert global_agg.get_global_count() == 2
    
    # Test winner detection
    global_agg.target_count = 2  # Set low target for testing
    assert global_agg.check_for_winner(visit2) == True
    assert global_agg.winner == visit2
    
    # Test metrics
    metrics = global_agg.get_metrics()
    assert metrics["global_count"] == 2
    assert metrics["has_winner"] == True
    assert len(metrics["regions"]) == 2

def test_approaching_target():
    global_agg = GlobalAggregator(target_count=100)
    region = RegionalAggregator(region_id="test-region")
    shard = CounterShard(shard_id="test-shard")
    
    region.add_shard(shard)
    global_agg.add_region(region)
    
    # Set count to approach target
    shard.count = 90
    assert global_agg.is_approaching_target() == True
    
    # Test precision adjustment
    global_agg.adjust_precision()
    assert region.aggregation_interval_ms == 100  # Should be in high precision mode 