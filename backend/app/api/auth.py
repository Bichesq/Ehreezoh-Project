"""
Ehreezoh - Authentication API
User registration, login, and profile management with Firebase Phone Auth
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.auth import (
    verify_firebase_token,
    create_access_token,
    get_current_user,
    hash_phone_number
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for request/response
class FirebaseTokenRequest(BaseModel):
    """Request model for Firebase token"""
    firebase_token: str = Field(..., description="Firebase ID token from client")


class UserRegistration(BaseModel):
    """User registration request"""
    firebase_token: str = Field(..., description="Firebase ID token")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")
    language_preference: str = Field("fr", description="Language preference (fr or en)")


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User profile response"""
    id: str
    phone_number: str
    full_name: Optional[str]
    email: Optional[str]
    profile_photo_url: Optional[str]
    language_preference: str
    is_passenger: bool
    is_driver: bool
    is_verified: bool
    created_at: datetime


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    registration: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Register a new user with Firebase authentication
    
    **Process:**
    1. Client authenticates with Firebase (phone number)
    2. Client sends Firebase ID token to this endpoint
    3. Server verifies token with Firebase
    4. Server creates user in database
    5. Server returns JWT access token
    
    **Returns:**
    - access_token: JWT token for API authentication
    - user: User profile information
    """
    # Verify Firebase token
    try:
        firebase_user = verify_firebase_token(registration.firebase_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Firebase verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )
    
    # Extract phone number from Firebase token
    phone_number = firebase_user.get("phone_number")
    firebase_uid = firebase_user.get("uid")
    
    if not phone_number or not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number not found in Firebase token"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.phone_number == phone_number) | (User.firebase_uid == firebase_uid)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    # Create new user
    new_user = User(
        phone_number=phone_number,
        phone_hash=hash_phone_number(phone_number),
        firebase_uid=firebase_uid,
        full_name=registration.full_name,
        email=registration.email,
        language_preference=registration.language_preference,
        is_passenger=True,  # All users start as passengers
        is_driver=False,
        is_active=True,
        is_verified=True,  # Phone verified via Firebase
        last_login_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✅ New user registered: {new_user.id} ({phone_number})")
    
    # Generate JWT access token
    access_token = create_access_token(
        data={"sub": new_user.id, "phone": phone_number}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user.to_dict()
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    token_request: FirebaseTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Login existing user with Firebase authentication
    
    **Process:**
    1. Client authenticates with Firebase (phone number)
    2. Client sends Firebase ID token to this endpoint
    3. Server verifies token with Firebase
    4. Server finds user in database
    5. Server returns JWT access token
    
    **Returns:**
    - access_token: JWT token for API authentication
    - user: User profile information
    """
    # Verify Firebase token
    try:
        firebase_user = verify_firebase_token(token_request.firebase_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Firebase verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )
    
    # Extract user info from Firebase token
    firebase_uid = firebase_user.get("uid")
    phone_number = firebase_user.get("phone_number")
    
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Firebase token"
        )
    
    # Find user in database
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first."
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned"
        )
    
    # Update last login time
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"✅ User logged in: {user.id} ({user.phone_number})")
    
    # Generate JWT access token
    access_token = create_access_token(
        data={"sub": user.id, "phone": user.phone_number}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:** Current user's profile information
    """
    return current_user.to_dict()



class UserUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    language_preference: Optional[str] = None
    profile_photo_url: Optional[str] = None


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:** Updated user profile
    """
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        current_user.email = user_update.email
        
    if user_update.profile_photo_url is not None:
        current_user.profile_photo_url = user_update.profile_photo_url
    
    if user_update.language_preference is not None:
        if user_update.language_preference not in ["fr", "en"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language must be 'fr' or 'en'"
            )
        current_user.language_preference = user_update.language_preference
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"✅ User profile updated: {current_user.id}")
    
    return current_user.to_dict()
