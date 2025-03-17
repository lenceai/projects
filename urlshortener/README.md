# URL Shortener Service

A simple, scalable URL shortening service built with FastAPI, SQLAlchemy, and Redis.

## Features

- Shorten long URLs to compact, easily shareable links
- Fast redirects using Redis caching
- Click tracking for shortened URLs
- RESTful API
- SQLite database (can be easily switched to PostgreSQL for production)

## Prerequisites

- Python 3.11+
- Redis server
- Conda environment

## Setup

1. Clone the repository
2. Create and activate the conda environment:
```bash
conda activate projects
```

3. Install dependencies:
```bash
pip install fastapi uvicorn sqlalchemy redis python-dotenv pydantic alembic
```

4. Configure environment variables in `.env`:
```
DATABASE_URL=sqlite:///./shortener.db
REDIS_URL=redis://localhost:6379
BASE_URL=http://localhost:8000
```

5. Start the Redis server:
```bash
redis-server
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### 1. Shorten URL
- **POST** `/shorten/`
- **Body**: `{"original_url": "https://example.com/very/long/url"}`
- **Response**: `{"short_url": "http://localhost:8000/abc123", "original_url": "https://example.com/very/long/url"}`

### 2. Access Shortened URL
- **GET** `/{short_key}`
- Redirects to the original URL

### 3. API Documentation
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Architecture

- FastAPI for the web framework
- SQLAlchemy for database ORM
- Redis for caching
- Pydantic for data validation
- SQLite for development database

## Scaling Considerations

For production deployment, consider:
1. Switching to PostgreSQL
2. Using multiple Redis instances
3. Adding monitoring and analytics
4. Implementing rate limiting
5. Adding user authentication
6. Using a CDN for global distribution 