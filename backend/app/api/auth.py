"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()


class RegisterRequest(BaseModel):
    """User registration request"""
    firebase_uid: str
    phone_number: str
    username: str | None = None
    language_preference: str = "fr"


class LoginRequest(BaseModel):
    """User login request"""
    firebase_uid: str
    device_id: str
    fcm_token: str
    platform: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement user registration
    # 1. Verify Firebase UID
    # 2. Check if user already exists
    # 3. Hash phone number
    # 4. Create user in database
    # 5. Return user data
    
    return {
        "success": True,
        "data": {
            "user_id": "placeholder-uuid",
            "username": request.username or "User",
            "trust_score": 0.00,
            "created_at": "2025-11-11T10:00:00Z"
        }
    }


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement user login
    # 1. Verify Firebase UID
    # 2. Get or create user
    # 3. Create/update session
    # 4. Store FCM token
    # 5. Return user data and session
    
    return {
        "success": True,
        "data": {
            "user": {
                "user_id": "placeholder-uuid",
                "username": "User",
                "trust_score": 0.00
            },
            "session_id": "placeholder-session-id"
        }
    }

