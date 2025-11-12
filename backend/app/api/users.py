"""
User endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db

router = APIRouter()


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    username: str
    trust_score: float
    total_reports: int
    verified_reports: int
    upvotes_received: int
    member_since: str


class UpdateSettingsRequest(BaseModel):
    """Update user settings request"""
    language_preference: Optional[str] = None
    username: Optional[str] = None


@router.get("/profile")
async def get_profile(db: Session = Depends(get_db)):
    """
    Get user profile
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement get profile
    # 1. Get current user from JWT token
    # 2. Fetch user data from database
    # 3. Calculate statistics
    # 4. Return profile data
    
    return {
        "success": True,
        "data": {
            "user_id": "placeholder-uuid",
            "username": "User",
            "trust_score": 4.5,
            "total_reports": 25,
            "verified_reports": 20,
            "upvotes_received": 100,
            "member_since": "2025-11-11"
        }
    }


@router.patch("/settings")
async def update_settings(
    request: UpdateSettingsRequest,
    db: Session = Depends(get_db)
):
    """
    Update user settings
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement update settings
    # 1. Get current user from JWT token
    # 2. Validate new settings
    # 3. Update user in database
    # 4. Return updated user data
    
    return {
        "success": True,
        "message": "Settings updated successfully"
    }

