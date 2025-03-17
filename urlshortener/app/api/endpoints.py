from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.shortener import create_unique_short_key
from app.core.cache import get_url_from_cache, set_url_in_cache, increment_click_count
from app.core.config import settings
from app.models.url import URL
from app.schemas.url import URLCreate, URLResponse
from typing import Optional
from starlette.responses import RedirectResponse

router = APIRouter()

@router.post("/shorten/", response_model=URLResponse)
def create_short_url(url: URLCreate, db: Session = Depends(get_db)):
    # Create short URL
    short_key = create_unique_short_key(db, URL)
    
    # Create database entry
    db_url = URL(
        original_url=str(url.original_url),
        short_key=short_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    # Add to cache
    set_url_in_cache(short_key, str(url.original_url))
    
    # Create response
    short_url = f"{settings.BASE_URL}/{short_key}"
    return URLResponse(short_url=short_url, original_url=str(url.original_url))

@router.get("/{short_key}")
def redirect_to_url(short_key: str, db: Session = Depends(get_db)):
    # Try to get URL from cache
    cached_url = get_url_from_cache(short_key)
    if cached_url:
        increment_click_count(short_key)
        return RedirectResponse(url=cached_url.decode())
    
    # If not in cache, get from database
    db_url = db.query(URL).filter(URL.short_key == short_key).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Update click count
    db_url.click_count += 1
    db.commit()
    
    # Add to cache
    set_url_in_cache(short_key, db_url.original_url)
    
    return RedirectResponse(url=db_url.original_url) 