"""
Driver model - Extended profile for drivers with geospatial support
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.core.database import Base


class Driver(Base):
    """Driver model with vehicle info and location tracking"""
    
    __tablename__ = "drivers"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Driver details
    driver_license_number = Column(String(50), unique=True, nullable=False)
    driver_license_photo_url = Column(String(500))
    national_id_number = Column(String(50))
    national_id_photo_url = Column(String(500))
    
    # Vehicle information
    vehicle_type = Column(String(20), nullable=False, index=True)  # 'moto', 'economy_car', 'comfort_car'
    vehicle_make = Column(String(50))
    vehicle_model = Column(String(50))
    vehicle_year = Column(Integer)
    vehicle_color = Column(String(30))
    vehicle_plate_number = Column(String(20), unique=True, nullable=False)
    vehicle_photo_url = Column(String(500))
    
    # Driver status
    is_online = Column(Boolean, default=False, index=True)
    is_available = Column(Boolean, default=True, index=True)  # Can accept rides
    is_verified = Column(Boolean, default=False)  # Admin verified
    verification_status = Column(String(20), default='pending', index=True)  # 'pending', 'approved', 'rejected'
    verification_notes = Column(String(500))
    
    # Performance metrics
    total_rides = Column(Integer, default=0)
    completed_rides = Column(Integer, default=0)
    cancelled_rides = Column(Integer, default=0)
    average_rating = Column(Numeric(3, 2), default=0.00)
    total_earnings = Column(Numeric(10, 2), default=0.00)
    
    # Current location (updated frequently via mobile app)
    current_location = Column(Geography(geometry_type='POINT', srid=4326))
    current_latitude = Column(Numeric(10, 8))
    current_longitude = Column(Numeric(11, 8))
    last_location_update = Column(DateTime)
    
    # Availability preferences
    accepts_moto_requests = Column(Boolean, default=True)
    accepts_car_requests = Column(Boolean, default=True)
    max_pickup_distance_km = Column(Integer, default=5)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)
    last_online_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="driver_profile")
    rides = relationship("Ride", foreign_keys="Ride.driver_id", back_populates="driver")
    ratings = relationship("DriverRating", back_populates="driver")
    
    def __repr__(self):
        return f"<Driver {self.vehicle_plate_number} ({self.vehicle_type})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vehicle_type": self.vehicle_type,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_color": self.vehicle_color,
            "vehicle_plate_number": self.vehicle_plate_number,
            "is_online": self.is_online,
            "is_available": self.is_available,
            "is_verified": self.is_verified,
            "verification_status": self.verification_status,
            "average_rating": float(self.average_rating) if self.average_rating else 0.0,
            "total_rides": self.total_rides,
            "current_latitude": float(self.current_latitude) if self.current_latitude else None,
            "current_longitude": float(self.current_longitude) if self.current_longitude else None,
            "last_location_update": self.last_location_update.isoformat() if self.last_location_update else None
        }
