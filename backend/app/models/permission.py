"""
User Permission model - Granular permissions for special features
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class UserPermission(Base):
    __tablename__ = "user_permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    permission_type = Column(String(50), nullable=False)  # 'view_police_checkpoints', 'report_police_checkpoints'
    granted_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="permissions")
    granter = relationship("User", foreign_keys=[granted_by])
