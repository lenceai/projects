from pydantic import BaseModel, EmailStr, constr, confloat
from typing import Optional
from datetime import datetime
from models.models import UserType, TripStatus

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: constr(regex=r'^\+?1?\d{9,15}$')
    user_type: UserType

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class DriverBase(BaseModel):
    user_id: int
    vehicle_model: str
    vehicle_number: str

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: int
    current_lat: Optional[float]
    current_lng: Optional[float]
    is_available: bool
    rating: float
    created_at: datetime

    class Config:
        orm_mode = True

class TripBase(BaseModel):
    pickup_lat: confloat(ge=-90, le=90)
    pickup_lng: confloat(ge=-180, le=180)
    dropoff_lat: confloat(ge=-90, le=90)
    dropoff_lng: confloat(ge=-180, le=180)

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: int
    rider_id: int
    driver_id: Optional[int]
    status: TripStatus
    price: Optional[float]
    distance: Optional[float]
    duration: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

class LocationUpdate(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None 