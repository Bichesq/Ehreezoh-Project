"""
Social models - Thanks and Comments
"""

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class IncidentThanks(Base):
    """
    Tracks when a user thanks a reporter for a helpful incident report.
    """
    __tablename__ = "incident_thanks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)  # Who reported the incident
    thanker_id = Column(String, ForeignKey("users.id"), nullable=False)   # Who is saying thanks
    created_at = Column(DateTime, server_default=func.now())


class IncidentComment(Base):
    """
    Comments on incidents for community updates.
    """
    __tablename__ = "incident_comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # 280 character limit enforced in API
    upvotes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class CommentUpvote(Base):
    """
    Tracks upvotes on comments to prevent duplicate votes.
    """
    __tablename__ = "comment_upvotes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    comment_id = Column(String, ForeignKey("incident_comments.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class UserFollow(Base):
    """
    Tracks user follow relationships.
    Follower follows the followed user to get their reports first.
    """
    __tablename__ = "user_follows"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(String, ForeignKey("users.id"), nullable=False)  # Who is following
    followed_id = Column(String, ForeignKey("users.id"), nullable=False)  # Who is being followed
    created_at = Column(DateTime, server_default=func.now())
