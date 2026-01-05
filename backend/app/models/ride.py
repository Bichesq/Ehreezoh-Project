"""
Ride model - Core ride-hailing functionality
"""

from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.core.database import Base


class Ride(Base):
    """Ride model for ride-hailing transactions"""
    
    __tablename__ = "rides"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Participants
    passenger_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    driver_id = Column(String, ForeignKey("drivers.id", ondelete="SET NULL"))
    
    # Ride details
    ride_type = Column(String(20), nullable=False, index=True)  # 'moto', 'economy_car', 'comfort_car'
    status = Column(String(20), nullable=False, default='requested', index=True)
    # Status flow: 'requested' -> 'accepted' -> 'driver_arrived' -> 'in_progress' -> 'completed' / 'cancelled'
    
    # Pickup location
    pickup_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    pickup_latitude = Column(Numeric(10, 8), nullable=False)
    pickup_longitude = Column(Numeric(11, 8), nullable=False)
    pickup_address = Column(Text)
    
    # Dropoff location
    dropoff_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    dropoff_latitude = Column(Numeric(10, 8), nullable=False)
    dropoff_longitude = Column(Numeric(11, 8), nullable=False)
    dropoff_address = Column(Text)
    
    # Fare and payment
    estimated_fare = Column(Numeric(10, 2))
    offered_fare = Column(Numeric(10, 2))  # Passenger's offer (for future fare negotiation)
    counter_offer_fare = Column(Numeric(10, 2))  # Driver's counter-offer
    final_fare = Column(Numeric(10, 2))
    payment_method = Column(String(20))  # 'cash', 'mtn_momo', 'orange_money'
    payment_status = Column(String(20), default='pending', index=True)  # 'pending', 'completed', 'failed'
    payment_transaction_id = Column(String(100))
    
    # Distance and duration
    estimated_distance_km = Column(Numeric(6, 2))
    estimated_duration_minutes = Column(Integer)
    actual_distance_km = Column(Numeric(6, 2))
    actual_duration_minutes = Column(Integer)
    
    # Ratings (stored here for quick access, also in separate rating tables)
    passenger_rating = Column(Integer)  # 1-5
    driver_rating = Column(Integer)  # 1-5
    passenger_review = Column(Text)
    driver_review = Column(Text)
    
    # Cancellation
    cancelled_by = Column(String(20))  # 'passenger', 'driver', 'system'
    cancellation_reason = Column(Text)
    cancellation_fee = Column(Numeric(10, 2), default=0.00)
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    accepted_at = Column(DateTime)
    driver_arrived_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    passenger = relationship("User", foreign_keys=[passenger_id], back_populates="rides_as_passenger")
    driver = relationship("Driver", foreign_keys=[driver_id], back_populates="rides")
    
    # Use list=True by default for relationships unless one-to-one is clearer, but Ride->Payment is usually 1-to-many (attempts) or 1-to-1 (success)
    # The model definition in `payment.py` says `back_populates="ride"`.
    payments = relationship("Payment", back_populates="ride")
    
    def __repr__(self):
        return f"<Ride {self.id} ({self.status})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "passenger_id": self.passenger_id,
            "driver_id": self.driver_id,
            "ride_type": self.ride_type,
            "status": self.status,
            "pickup_latitude": float(self.pickup_latitude),
            "pickup_longitude": float(self.pickup_longitude),
            "pickup_address": self.pickup_address,
            "dropoff_latitude": float(self.dropoff_latitude),
            "dropoff_longitude": float(self.dropoff_longitude),
            "dropoff_address": self.dropoff_address,
            "estimated_fare": float(self.estimated_fare) if self.estimated_fare else None,
            "final_fare": float(self.final_fare) if self.final_fare else None,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "estimated_distance_km": float(self.estimated_distance_km) if self.estimated_distance_km else None,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "passenger_rating": self.passenger_rating,
            "driver_rating": self.driver_rating,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
