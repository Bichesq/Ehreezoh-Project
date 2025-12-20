"""
Payment model - Payment processing for rides
"""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Payment(Base):
    """Payment model for ride transactions"""
    
    __tablename__ = "payments"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ride_id = Column(String, ForeignKey("rides.id", ondelete="CASCADE"), nullable=False)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='XAF')  # Central African CFA franc
    payment_method = Column(String(20), nullable=False)  # 'cash', 'mtn_momo', 'orange_money'
    
    # Mobile Money details
    phone_number = Column(String(20))
    transaction_id = Column(String(100), unique=True, index=True)
    external_reference = Column(String(100))
    
    # Status
    status = Column(String(20), default='pending', index=True)  # 'pending', 'processing', 'completed', 'failed', 'refunded'
    failure_reason = Column(Text)
    
    # Commission and payout
    platform_commission = Column(Numeric(10, 2))  # Ehreezoh's cut (12-15%)
    driver_payout = Column(Numeric(10, 2))  # Amount driver receives
    
    # Payout status
    payout_status = Column(String(20), default='pending')  # 'pending', 'completed', 'failed'
    payout_transaction_id = Column(String(100))
    payout_completed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    ride = relationship("Ride", back_populates="payment")
    
    def __repr__(self):
        return f"<Payment {self.id} ({self.status})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "ride_id": self.ride_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "platform_commission": float(self.platform_commission) if self.platform_commission else None,
            "driver_payout": float(self.driver_payout) if self.driver_payout else None,
            "payout_status": self.payout_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
