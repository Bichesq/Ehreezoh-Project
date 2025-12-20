"""
Ehreezoh - Driver API
Driver registration, location updates, and availability management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from geoalchemy2.functions import ST_DWithin, ST_Distance
from geoalchemy2.elements import WKTElement
import logging

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_driver
from app.models.user import User
from app.models.driver import Driver

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drivers", tags=["Drivers"])


# Pydantic models
class DriverRegistration(BaseModel):
    """Driver registration request"""
    driver_license_number: str = Field(..., max_length=50)
    vehicle_type: str = Field(..., description="moto or car")
    vehicle_plate_number: str = Field(..., max_length=20)
    vehicle_make: Optional[str] = Field(None, max_length=50)
    vehicle_model: Optional[str] = Field(None, max_length=50)
    vehicle_year: Optional[int] = None
    vehicle_color: Optional[str] = Field(None, max_length=30)


class LocationUpdate(BaseModel):
    """Driver location update"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class DriverStatusUpdate(BaseModel):
    """Driver status update"""
    is_online: Optional[bool] = None
    is_available: Optional[bool] = None


class DriverResponse(BaseModel):
    """Driver profile response"""
    id: str
    user_id: str
    driver_license_number: str
    vehicle_type: str
    vehicle_plate_number: str
    vehicle_make: Optional[str]
    vehicle_model: Optional[str]
    vehicle_color: Optional[str]
    is_online: bool
    is_available: bool
    is_verified: bool
    verification_status: str
    average_rating: float
    total_rides: int
    completed_rides: int


class NearbyDriverResponse(BaseModel):
    """Nearby driver response"""
    driver_id: str
    user_id: str
    full_name: Optional[str]
    vehicle_type: str
    vehicle_plate_number: str
    vehicle_color: Optional[str]
    average_rating: float
    total_rides: int
    distance_km: float
    current_latitude: Optional[float]
    current_longitude: Optional[float]


@router.post("/register", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def register_driver(
    registration: DriverRegistration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register current user as a driver
    
    **Requirements:**
    - Valid JWT token
    - User not already registered as driver
    - Valid driver license and vehicle info
    
    **Vehicle Types:**
    - `moto` - Motorcycle/Moto-taxi
    - `car` - Car
    """
    # Check if user is already a driver
    existing_driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already registered as a driver"
        )
    
    # Validate vehicle type
    if registration.vehicle_type not in ["moto", "car"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle type must be 'moto' or 'car'"
        )
    
    # Check for duplicate license or plate
    duplicate = db.query(Driver).filter(
        (Driver.driver_license_number == registration.driver_license_number) |
        (Driver.vehicle_plate_number == registration.vehicle_plate_number)
    ).first()
    
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver license or vehicle plate number already registered"
        )
    
    # Create driver profile
    new_driver = Driver(
        user_id=current_user.id,
        driver_license_number=registration.driver_license_number,
        vehicle_type=registration.vehicle_type,
        vehicle_plate_number=registration.vehicle_plate_number,
        vehicle_make=registration.vehicle_make,
        vehicle_model=registration.vehicle_model,
        vehicle_year=registration.vehicle_year,
        vehicle_color=registration.vehicle_color,
        is_online=False,
        is_available=True,
        is_verified=False,
        verification_status="pending"
    )
    
    db.add(new_driver)
    
    # Update user to mark as driver
    current_user.is_driver = True
    
    db.commit()
    db.refresh(new_driver)
    
    logger.info(f"✅ New driver registered: {new_driver.id} ({current_user.phone_number})")
    
    return new_driver.to_dict()


@router.get("/me", response_model=DriverResponse)
async def get_driver_profile(
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Get current driver's profile
    
    **Requires:** User must be registered as a driver
    """
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    return driver.to_dict()


@router.patch("/status")
async def update_driver_status(
    status_update: DriverStatusUpdate,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Update driver online/available status
    
    **Status Options:**
    - `is_online`: Driver is online and can receive requests
    - `is_available`: Driver is available for new rides (not currently on a ride)
    """
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    if status_update.is_online is not None:
        driver.is_online = status_update.is_online
        if status_update.is_online:
            driver.last_online_at = datetime.utcnow()
        else:
            # Remove driver from Redis when going offline
            from app.services.redis_service import redis_service
            redis_service.remove_driver_location(driver.id)
    
    if status_update.is_available is not None:
        driver.is_available = status_update.is_available
    
    db.commit()
    db.refresh(driver)
    
    # Update status in Redis
    from app.services.redis_service import redis_service
    redis_service.set_driver_status(
        driver_id=driver.id,
        is_online=driver.is_online,
        is_available=driver.is_available,
        ttl_seconds=300  # 5 minutes
    )
    
    logger.info(f"✅ Driver status updated: {driver.id} (online={driver.is_online}, available={driver.is_available})")
    
    return driver.to_dict()


@router.post("/location")
async def update_location(
    location: LocationUpdate,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Update driver's current location
    
    **Usage:**
    - Send location updates every 10-30 seconds while online
    - Location is stored in PostgreSQL (PostGIS) and Redis (geospatial index)
    - Used for nearby driver search
    """
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Update location in PostgreSQL using PostGIS
    point_wkt = f'POINT({location.longitude} {location.latitude})'
    driver.current_location = WKTElement(point_wkt, srid=4326)
    driver.current_latitude = location.latitude
    driver.current_longitude = location.longitude
    driver.last_location_update = datetime.utcnow()
    
    db.commit()
    
    # Update location in Redis for fast geospatial queries
    from app.services.redis_service import redis_service
    if driver.is_online:
        redis_service.update_driver_location(
            driver_id=driver.id,
            latitude=location.latitude,
            longitude=location.longitude,
            ttl_seconds=60  # 1 minute TTL
        )
    
    logger.info(f"📍 Driver location updated: {driver.id} ({location.latitude}, {location.longitude})")
    
    return {
        "success": True,
        "message": "Location updated",
        "latitude": location.latitude,
        "longitude": location.longitude,
        "updated_at": driver.last_location_update
    }


@router.get("/nearby", response_model=List[NearbyDriverResponse])
async def find_nearby_drivers(
    latitude: float = Query(..., ge=-90, le=90, description="Pickup latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Pickup longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=50, description="Search radius in kilometers"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type (moto/car)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of drivers to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find nearby available drivers using geospatial search
    
    **Parameters:**
    - `latitude`, `longitude`: Pickup location
    - `radius_km`: Search radius (default 5km, max 50km)
    - `vehicle_type`: Filter by 'moto' or 'car' (optional)
    - `limit`: Max results (default 10, max 50)
    
    **Returns:**
    - List of nearby drivers sorted by distance
    - Includes distance in kilometers
    - Only returns online and available drivers
    """
    # Create pickup point
    pickup_point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
    
    # Build query with geospatial filter
    query = db.query(
        Driver,
        User,
        func.ST_Distance(
            Driver.current_location,
            pickup_point
        ).label('distance_meters')
    ).join(
        User, Driver.user_id == User.id
    ).filter(
        and_(
            Driver.is_online == True,
            Driver.is_available == True,
            Driver.is_verified == True,
            Driver.current_location.isnot(None),
            func.ST_DWithin(
                Driver.current_location,
                pickup_point,
                radius_km * 1000  # Convert km to meters
            )
        )
    )
    
    # Filter by vehicle type if specified
    if vehicle_type:
        if vehicle_type not in ["moto", "car"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle type must be 'moto' or 'car'"
            )
        query = query.filter(Driver.vehicle_type == vehicle_type)
    
    # Order by distance and limit results
    results = query.order_by('distance_meters').limit(limit).all()
    
    # Format response
    nearby_drivers = []
    for driver, user, distance_meters in results:
        nearby_drivers.append({
            "driver_id": driver.id,
            "user_id": user.id,
            "full_name": user.full_name,
            "vehicle_type": driver.vehicle_type,
            "vehicle_plate_number": driver.vehicle_plate_number,
            "vehicle_color": driver.vehicle_color,
            "average_rating": float(driver.average_rating) if driver.average_rating else 0.0,
            "total_rides": driver.total_rides,
            "distance_km": round(distance_meters / 1000, 2),  # Convert to km
            "current_latitude": float(driver.current_latitude) if driver.current_latitude else None,
            "current_longitude": float(driver.current_longitude) if driver.current_longitude else None
        })
    
    logger.info(f"🔍 Found {len(nearby_drivers)} nearby drivers within {radius_km}km")
    
    return nearby_drivers
