# Real-Time Marketplace System (Uber-like MVP)

A Python-based real-time marketplace system that demonstrates core functionality similar to Uber.

## Features

- User and driver registration/authentication
- Real-time location tracking
- Ride matching algorithm
- Trip management
- WebSocket-based real-time updates
- Basic payment simulation

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/marketplace
REDIS_URL=redis://localhost
SECRET_KEY=your-secret-key-here
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run the application:
```bash
uvicorn api.main:app --reload
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for the interactive API documentation.

## Architecture

The system is built using:
- FastAPI for the REST API
- Redis for geospatial operations and real-time data
- PostgreSQL for persistent storage
- WebSockets for real-time updates

## Testing

Run tests using:
```bash
pytest
```
