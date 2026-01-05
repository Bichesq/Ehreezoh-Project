from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class PaymentProvider(str, enum.Enum):
    MOMO = "momo"
    OM = "om"
    CASH = "cash"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ride_id = Column(String, ForeignKey("rides.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    provider = Column(String, nullable=False) # momo, om, cash
    status = Column(String, default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True) # External Transaction ID
    phone_number = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ride = relationship("Ride", back_populates="payments")
