from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import redis
import os
from dotenv import load_dotenv

from models.models import User, Driver, Trip, UserType, TripStatus
from .database import get_db
from .schemas import (
    UserCreate,
    UserResponse,
    DriverCreate,
    DriverResponse,
    TripCreate,
    TripResponse,
    LocationUpdate
)
from .auth import get_current_user, create_access_token

load_dotenv()

app = FastAPI(title="Real-Time Marketplace API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost"))

# WebSocket connections store
active_connections = {}

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        email=user.email,
        password_hash=user.password,  # In production, hash the password
        full_name=user.full_name,
        phone=user.phone,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/drivers/", response_model=DriverResponse)
async def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    db_driver = Driver(
        user_id=driver.user_id,
        vehicle_model=driver.vehicle_model,
        vehicle_number=driver.vehicle_number
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@app.post("/trips/", response_model=TripResponse)
async def create_trip(trip: TripCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != UserType.RIDER:
        raise HTTPException(status_code=403, detail="Only riders can create trips")

    # Find nearest available driver using Redis geospatial
    nearest_driver = find_nearest_driver(trip.pickup_lat, trip.pickup_lng)
    
    db_trip = Trip(
        rider_id=current_user.id,
        driver_id=nearest_driver.id if nearest_driver else None,
        pickup_lat=trip.pickup_lat,
        pickup_lng=trip.pickup_lng,
        dropoff_lat=trip.dropoff_lat,
        dropoff_lng=trip.dropoff_lng,
        status=TripStatus.REQUESTED
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    
    # Notify driver if found
    if nearest_driver and nearest_driver.id in active_connections:
        await notify_driver(nearest_driver.id, db_trip)
    
    return db_trip

@app.put("/trips/{trip_id}/status")
async def update_trip_status(
    trip_id: int,
    status: TripStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if current_user.id not in (trip.rider_id, trip.driver_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    trip.status = status
    db.commit()
    
    # Notify both rider and driver
    await notify_trip_update(trip)
    
    return {"status": "success"}

@app.post("/drivers/location")
async def update_driver_location(
    location: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.DRIVER:
        raise HTTPException(status_code=403, detail="Only drivers can update location")
    
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Update driver location in database
    driver.current_lat = location.latitude
    driver.current_lng = location.longitude
    db.commit()
    
    # Update driver location in Redis for geospatial queries
    redis_client.geoadd(
        "driver_locations",
        [location.longitude, location.latitude, str(driver.id)]
    )
    
    return {"status": "success"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    active_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time messages
            await handle_websocket_message(client_id, data)
    except WebSocketDisconnect:
        del active_connections[client_id]

def find_nearest_driver(lat: float, lng: float) -> Optional[Driver]:
    # Search for nearest driver using Redis geospatial
    result = redis_client.georadius(
        "driver_locations",
        lng,
        lat,
        5,  # 5km radius
        unit="km",
        withcoord=True
    )
    if not result:
        return None
    
    # Get the first (nearest) driver
    driver_id = int(result[0][0])
    return driver_id

async def notify_driver(driver_id: int, trip: Trip):
    if driver_id in active_connections:
        websocket = active_connections[driver_id]
        await websocket.send_json({
            "type": "new_trip_request",
            "trip_id": trip.id,
            "pickup": {
                "lat": trip.pickup_lat,
                "lng": trip.pickup_lng
            },
            "dropoff": {
                "lat": trip.dropoff_lat,
                "lng": trip.dropoff_lng
            }
        })

async def notify_trip_update(trip: Trip):
    # Notify both rider and driver about trip updates
    for user_id in (trip.rider_id, trip.driver_id):
        if user_id in active_connections:
            websocket = active_connections[user_id]
            await websocket.send_json({
                "type": "trip_update",
                "trip_id": trip.id,
                "status": trip.status.value
            })

async def handle_websocket_message(client_id: int, message: str):
    try:
        data = json.loads(message)
        # Handle different types of real-time messages
        if data["type"] == "location_update":
            # Handle driver location updates
            pass
        elif data["type"] == "trip_action":
            # Handle trip-related actions
            pass
    except json.JSONDecodeError:
        pass 