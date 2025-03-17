from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin, PrimaryKeyMixin

class UserType(enum.Enum):
    RIDER = "rider"
    DRIVER = "driver"

class TripStatus(enum.Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base, TimestampMixin, PrimaryKeyMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    trips_as_rider = relationship("Trip", back_populates="rider", foreign_keys="Trip.rider_id")
    trips_as_driver = relationship("Trip", back_populates="driver", foreign_keys="Trip.driver_id")

class Driver(Base, TimestampMixin, PrimaryKeyMixin):
    __tablename__ = "drivers"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_model = Column(String(100), nullable=False)
    vehicle_number = Column(String(20), nullable=False)
    current_lat = Column(Float)
    current_lng = Column(Float)
    is_available = Column(Boolean, default=True)
    rating = Column(Float, default=5.0)

class Trip(Base, TimestampMixin, PrimaryKeyMixin):
    __tablename__ = "trips"

    rider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"))
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    dropoff_lat = Column(Float, nullable=False)
    dropoff_lng = Column(Float, nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.REQUESTED)
    price = Column(Numeric(10, 2))
    distance = Column(Float)  # in kilometers
    duration = Column(Integer)  # in seconds
    
    # Relationships
    rider = relationship("User", back_populates="trips_as_rider", foreign_keys=[rider_id])
    driver = relationship("User", back_populates="trips_as_driver", foreign_keys=[driver_id]) 