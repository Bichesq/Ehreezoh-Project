"""
Rating models - Driver and passenger ratings
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class DriverRating(Base):
    """Driver rating model"""
    
    __tablename__ = "driver_ratings"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ride_id = Column(String, ForeignKey("rides.id", ondelete="CASCADE"), unique=True, nullable=False)
    driver_id = Column(String, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    passenger_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Rating
    rating = Column(Integer, nullable=False)  # 1-5
    review = Column(Text)
    
    # Optional detailed feedback
    cleanliness_rating = Column(Integer)  # 1-5
    driving_rating = Column(Integer)  # 1-5
    professionalism_rating = Column(Integer)  # 1-5
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    driver = relationship("Driver", back_populates="ratings")
    
    def __repr__(self):
        return f"<DriverRating {self.rating}/5 for Driver {self.driver_id}>"


class PassengerRating(Base):
    """Passenger rating model"""
    
    __tablename__ = "passenger_ratings"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ride_id = Column(String, ForeignKey("rides.id", ondelete="CASCADE"), unique=True, nullable=False)
    passenger_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(String, ForeignKey("drivers.id", ondelete="SET NULL"))
    
    # Rating
    rating = Column(Integer, nullable=False)  # 1-5
    review = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PassengerRating {self.rating}/5 for Passenger {self.passenger_id}>"
