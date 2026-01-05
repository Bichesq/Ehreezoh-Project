from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
import uuid

from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # Optional: Anonymously reported? Let's link to user for credibility.
    type = Column(String, nullable=False) # e.g. 'accident', 'police', 'traffic', 'roadblock'
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326))
    media_url = Column(String, nullable=True) # For photo/video
    
    # Vote/Confirmations count (for credibility)
    confirmations = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
    # Enhanced Route Guidance Fields
    severity_score = Column(Integer, default=50) # 0-100 calculated score
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(String, ForeignKey("users.id"), nullable=True)
    reward_status = Column(String(20), default='not_eligible') # 'not_eligible', 'pending', 'paid'
    affected_routes = Column(JSON, nullable=True) # Store route_ids affected (JSONB in Postgres)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(20), default='active') # 'active', 'resolved', 'expired'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reporter = relationship("User", foreign_keys=[user_id], backref="reported_incidents")
    verifier = relationship("User", foreign_keys=[verified_by], backref="verified_incidents")
