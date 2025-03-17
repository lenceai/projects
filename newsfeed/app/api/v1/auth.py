from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...services.user_service import UserService
from ...schemas import Token, UserCreate, UserProfile

router = APIRouter()

@router.post("/signup", response_model=UserProfile)
async def signup(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Create new user."""
    user_service = UserService(db)
    user = user_service.create_user(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )
    return user_service.get_user_profile(user.id)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token."""
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = user_service.create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"} 