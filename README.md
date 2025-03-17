# Google's 100 Billionth Visitor Counter System

An MVP implementation of a distributed counting system designed to identify Google's 100 billionth visitor. This implementation demonstrates the core concepts of distributed counting using a hierarchical sharded counter system with CRDT-like properties.

## Features

- Edge-level counting with counter shards
- Regional aggregation of counts
- Global count management
- High-precision mode near milestone
- Visitor identification system
- REST API endpoints for counter operations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Redis:
```bash
redis-server
```

3. Run the application:
```bash
uvicorn src.main:app --reload
```

## Architecture

The system is composed of:
- Counter Shards: Distributed counters for handling concurrent visits
- Regional Aggregators: Combine counts from multiple shards
- Global Aggregator: Maintains the authoritative total count
- API Layer: REST endpoints for counter operations

## API Endpoints

- `POST /visit`: Register a new visitor
- `GET /count`: Get current global count
- `GET /winner`: Check if current visitor is the winner
- `GET /metrics`: Get system metrics

## Testing

Run tests with:
```bash
pytest
```
