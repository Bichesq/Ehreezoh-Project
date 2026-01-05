"""
Chat models for Neighborhood Chat feature
"""

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ChatRoom(Base):
    """
    Chat room for a neighborhood.
    Auto-created when first user joins a neighborhood.
    """
    __tablename__ = "chat_rooms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    neighborhood_id = Column(String, ForeignKey("neighborhoods.id"), nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class ChatMessage(Base):
    """
    Individual chat message in a room.
    """
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default='text')  # text, incident_share, image
    reference_id = Column(String)  # For incident shares, etc.
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class ChatRoomMember(Base):
    """
    Tracks room membership and permissions.
    """
    __tablename__ = "chat_room_members"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, default='member')  # member, moderator, admin
    is_muted = Column(Boolean, default=False)
    joined_at = Column(DateTime, server_default=func.now())
    last_read_at = Column(DateTime)
