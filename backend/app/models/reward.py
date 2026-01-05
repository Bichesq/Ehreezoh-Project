"""
Incident Reward model - Tracks rewards earned by drivers for verified incident reports
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class IncidentReward(Base):
    __tablename__ = "incident_rewards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"))
    reporter_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    driver_id = Column(String, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    
    # Reward details
    amount = Column(Numeric(10, 2), default=100.00)  # 100 XAF
    status = Column(String(20), default='pending')  # 'pending', 'paid', 'rejected'
    
    # Verification criteria snapshot
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50))  # 'community', 'admin', 'automated'
    confirmations_at_payout = Column(Integer, default=0)
    
    # Payout info
    paid_at = Column(DateTime, nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    incident = relationship("Incident", backref="reward")
    reporter = relationship("User", foreign_keys=[reporter_id], backref="incident_rewards")
    driver = relationship("Driver", backref="incident_rewards")
