from fastapi import FastAPI
from app.api.endpoints import router
from app.core.database import engine
from app.models import url

# Create database tables
url.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortening service",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to URL Shortener API",
        "endpoints": {
            "Shorten URL": "/shorten/",
            "Access shortened URL": "/{short_key}"
        }
    } 