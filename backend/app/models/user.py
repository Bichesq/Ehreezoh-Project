"""
User model - Base user for both passengers and drivers
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """User model for passengers and drivers"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    phone_hash = Column(String(255), unique=True, nullable=False)  # bcrypt hash
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    
    # Profile
    full_name = Column(String(100))
    email = Column(String(255))
    profile_photo_url = Column(String(500))
    language_preference = Column(String(5), default='fr')  # 'fr' or 'en'
    
    # User roles (can be both passenger and driver)
    is_passenger = Column(Boolean, default=True)
    is_driver = Column(Boolean, default=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Relationships
    driver_profile = relationship("Driver", back_populates="user", uselist=False)
    rides_as_passenger = relationship("Ride", foreign_keys="Ride.passenger_id", back_populates="passenger")
    
    def __repr__(self):
        return f"<User {self.phone_number} ({self.full_name})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "full_name": self.full_name,
            "email": self.email,
            "profile_photo_url": self.profile_photo_url,
            "language_preference": self.language_preference,
            "is_passenger": self.is_passenger,
            "is_driver": self.is_driver,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
