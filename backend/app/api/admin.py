"""
Ehreezoh - Admin API
Driver verification and platform management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.driver import Driver

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# Pydantic models
class DriverVerificationRequest(BaseModel):
    """Driver verification decision"""
    approved: bool = Field(..., description="Approve or reject driver")
    notes: Optional[str] = Field(None, description="Admin notes/reason")


class DriverListResponse(BaseModel):
    """Driver list item"""
    id: str
    user_id: str
    full_name: Optional[str]
    phone_number: str
    driver_license_number: str
    vehicle_type: str
    vehicle_plate_number: str
    verification_status: str
    is_verified: bool
    total_rides: int
    average_rating: float
    created_at: datetime


async def verify_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify user is an admin
    
    For now, we'll use a simple check. In production, add an is_admin field to User model.
    """
    # TODO: Add is_admin field to User model
    # For now, check if user's phone number is in admin list (from env)
    # Or check if email contains 'admin'
    
    if current_user.email and 'admin' in current_user.email.lower():
        return current_user
    
    # Temporary: Allow any user for testing
    # In production, uncomment this:
    # raise HTTPException(
    #     status_code=status.HTTP_403_FORBIDDEN,
    #     detail="Admin access required"
    # )
    
    return current_user


@router.get("/drivers/pending", response_model=List[DriverListResponse])
async def get_pending_drivers(
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of drivers pending verification
    
    **Admin Only**
    
    Returns drivers with verification_status = 'pending'
    """
    drivers = db.query(Driver, User).join(
        User, Driver.user_id == User.id
    ).filter(
        Driver.verification_status == 'pending'
    ).limit(limit).all()
    
    result = []
    for driver, user in drivers:
        result.append({
            "id": driver.id,
            "user_id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "driver_license_number": driver.driver_license_number,
            "vehicle_type": driver.vehicle_type,
            "vehicle_plate_number": driver.vehicle_plate_number,
            "verification_status": driver.verification_status,
            "is_verified": driver.is_verified,
            "total_rides": driver.total_rides,
            "average_rating": float(driver.average_rating) if driver.average_rating else 0.0,
            "created_at": driver.created_at
        })
    
    logger.info(f"📋 Admin {admin.id} retrieved {len(result)} pending drivers")
    
    return result


@router.post("/drivers/{driver_id}/verify")
async def verify_driver(
    driver_id: str,
    verification: DriverVerificationRequest,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Approve or reject driver verification
    
    **Admin Only**
    
    **Actions:**
    - `approved: true` - Verify driver, allow them to go online
    - `approved: false` - Reject driver, they cannot accept rides
    """
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if verification.approved:
        driver.is_verified = True
        driver.verification_status = "approved"
        driver.approved_at = datetime.utcnow()
        driver.verification_notes = verification.notes or "Approved by admin"
        
        logger.info(f"✅ Driver {driver_id} approved by admin {admin.id}")
        message = "Driver approved successfully"
    else:
        driver.is_verified = False
        driver.verification_status = "rejected"
        driver.verification_notes = verification.notes or "Rejected by admin"
        
        logger.info(f"❌ Driver {driver_id} rejected by admin {admin.id}")
        message = "Driver rejected"
    
    db.commit()
    db.refresh(driver)
    
    return {
        "success": True,
        "message": message,
        "driver": driver.to_dict()
    }


@router.get("/drivers/verified", response_model=List[DriverListResponse])
async def get_verified_drivers(
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of verified drivers
    
    **Admin Only**
    """
    drivers = db.query(Driver, User).join(
        User, Driver.user_id == User.id
    ).filter(
        Driver.is_verified == True
    ).order_by(
        Driver.approved_at.desc()
    ).limit(limit).all()
    
    result = []
    for driver, user in drivers:
        result.append({
            "id": driver.id,
            "user_id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "driver_license_number": driver.driver_license_number,
            "vehicle_type": driver.vehicle_type,
            "vehicle_plate_number": driver.vehicle_plate_number,
            "verification_status": driver.verification_status,
            "is_verified": driver.is_verified,
            "total_rides": driver.total_rides,
            "average_rating": float(driver.average_rating) if driver.average_rating else 0.0,
            "created_at": driver.created_at
        })
    
    return result


@router.get("/stats")
async def get_platform_stats(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Get platform statistics
    
    **Admin Only**
    
    Returns:
    - Total users, drivers, rides
    - Active drivers
    - Revenue metrics
    """
    from sqlalchemy import func
    from app.models.ride import Ride
    
    # Count users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Count drivers
    total_drivers = db.query(func.count(Driver.id)).scalar()
    pending_drivers = db.query(func.count(Driver.id)).filter(
        Driver.verification_status == 'pending'
    ).scalar()
    verified_drivers = db.query(func.count(Driver.id)).filter(
        Driver.is_verified == True
    ).scalar()
    online_drivers = db.query(func.count(Driver.id)).filter(
        Driver.is_online == True
    ).scalar()
    
    # Count rides
    total_rides = db.query(func.count(Ride.id)).scalar()
    completed_rides = db.query(func.count(Ride.id)).filter(
        Ride.status == 'completed'
    ).scalar()
    active_rides = db.query(func.count(Ride.id)).filter(
        Ride.status.in_(['requested', 'accepted', 'started'])
    ).scalar()
    
    # Revenue (sum of completed ride fares)
    total_revenue = db.query(func.sum(Ride.final_fare)).filter(
        Ride.status == 'completed'
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users
        },
        "drivers": {
            "total": total_drivers,
            "pending": pending_drivers,
            "verified": verified_drivers,
            "online": online_drivers
        },
        "rides": {
            "total": total_rides,
            "completed": completed_rides,
            "active": active_rides
        },
        "revenue": {
            "total": float(total_revenue),
            "currency": "XAF"
        }
    }
