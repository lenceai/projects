from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.v1 import auth, users, content, feed

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

app.include_router(
    content.router,
    prefix=f"{settings.API_V1_STR}/content",
    tags=["content"]
)

app.include_router(
    feed.router,
    prefix=f"{settings.API_V1_STR}/feed",
    tags=["feed"]
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the News Feed API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

# Initialize database tables
from .core.database import init_db
init_db() 