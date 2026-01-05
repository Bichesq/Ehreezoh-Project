"""
Community models - Cities, Neighborhoods, and Verifications
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class City(Base):
    """City model for organizing neighborhoods"""
    
    __tablename__ = "cities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    country = Column(String(100), default="Cameroon")
    
    # Stats
    active_contributors = Column(Integer, default=0)
    total_reports = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    neighborhoods = relationship("Neighborhood", back_populates="city")


class Neighborhood(Base):
    """Neighborhood model - the core community unit"""
    
    __tablename__ = "neighborhoods"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    city_id = Column(String, ForeignKey("cities.id"), nullable=False)
    
    # Geographic boundary (optional, for future use)
    geojson = Column(JSONB, nullable=True)
    
    # Center point for distance calculations
    center_lat = Column(Numeric(10, 6), nullable=True)
    center_lng = Column(Numeric(10, 6), nullable=True)
    
    # Stats (updated periodically)
    active_contributors = Column(Integer, default=0)
    total_reports = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    city = relationship("City", back_populates="neighborhoods")


class UserNeighborhood(Base):
    """User-Neighborhood association - tracks where users contribute"""
    
    __tablename__ = "user_neighborhoods"
    
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    neighborhood_id = Column(String, ForeignKey("neighborhoods.id"), primary_key=True)
    
    is_home = Column(Boolean, default=False)
    report_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class IncidentVerification(Base):
    """Verification of incidents by community members"""
    
    __tablename__ = "incident_verifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Verification type: 'still_there' or 'all_clear'
    verification_type = Column(String(20), nullable=False)
    
    # Weight based on user trust score at time of verification
    weight = Column(Numeric(5, 2), default=1.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", backref="verifications")
    user = relationship("User", backref="verifications")
