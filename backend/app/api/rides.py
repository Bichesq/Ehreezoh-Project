"""
Ehreezoh - Rides API
Ride requests, tracking, and lifecycle management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from geoalchemy2.elements import WKTElement
import logging
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_driver
from app.core.websocket import broadcast_ride_update, EventType, notify_passenger
from app.models.user import User
from app.models.driver import Driver
from app.models.ride import Ride

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rides", tags=["Rides"])


# Pydantic models
class RideRequest(BaseModel):
    """Ride request from passenger"""
    ride_type: str = Field(..., description="moto or car")
    pickup_latitude: float = Field(..., ge=-90, le=90)
    pickup_longitude: float = Field(..., ge=-180, le=180)
    pickup_address: Optional[str] = None
    dropoff_latitude: float = Field(..., ge=-90, le=90)
    dropoff_longitude: float = Field(..., ge=-180, le=180)
    dropoff_address: Optional[str] = None
    offered_fare: Optional[float] = Field(None, ge=0, description="Passenger's offered fare (XAF)")


class RideResponse(BaseModel):
    """Ride details response"""
    id: str
    passenger_id: str
    driver_id: Optional[str]
    ride_type: str
    status: str
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: Optional[str]
    dropoff_latitude: float
    dropoff_longitude: float
    dropoff_address: Optional[str]
    estimated_fare: Optional[float]
    offered_fare: Optional[float] = None
    final_fare: Optional[float]
    payment_method: Optional[str]
    payment_status: str
    requested_at: datetime
    accepted_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class RideAction(BaseModel):
    """Generic ride action (accept, start, complete, cancel)"""
    reason: Optional[str] = Field(None, description="Reason for cancellation")


@router.post("/request", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def request_ride(
    ride_request: RideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a new ride
    
    **Ride Types:**
    - `moto` - Moto-taxi (motorcycle)
    - `car` - Car
    
    **Process:**
    1. Passenger submits ride request
    2. System calculates estimated fare
    3. System finds nearby available drivers
    4. Nearby drivers are notified (via push notifications - to be implemented)
    5. Driver accepts ride
    6. Ride begins
    
    **Status Flow:**
    requested → accepted → started → completed
    """
    # Validate ride type
    if ride_request.ride_type not in ["moto", "car"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride type must be 'moto' or 'car'"
        )
    
    # Calculate estimated fare (simplified - you can enhance this)
    # Base fare: Moto 500 XAF, Car 1000 XAF
    # Per km: Moto 200 XAF, Car 400 XAF
    base_fare = 500 if ride_request.ride_type == "moto" else 1000
    per_km_rate = 200 if ride_request.ride_type == "moto" else 400
    
    # Simple distance calculation (you can use PostGIS ST_Distance for accuracy)
    import math
    lat1, lon1 = ride_request.pickup_latitude, ride_request.pickup_longitude
    lat2, lon2 = ride_request.dropoff_latitude, ride_request.dropoff_longitude
    
    # Haversine formula for distance
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_km = R * c
    
    estimated_fare = base_fare + (per_km_rate * distance_km)
    
    # Create ride
    new_ride = Ride(
        passenger_id=current_user.id,
        ride_type=ride_request.ride_type,
        status="requested",
        pickup_location=WKTElement(f'POINT({ride_request.pickup_longitude} {ride_request.pickup_latitude})', srid=4326),
        pickup_latitude=ride_request.pickup_latitude,
        pickup_longitude=ride_request.pickup_longitude,
        pickup_address=ride_request.pickup_address,
        dropoff_location=WKTElement(f'POINT({ride_request.dropoff_longitude} {ride_request.dropoff_latitude})', srid=4326),
        dropoff_latitude=ride_request.dropoff_latitude,
        dropoff_longitude=ride_request.dropoff_longitude,
        dropoff_address=ride_request.dropoff_address,
        estimated_fare=estimated_fare,
        offered_fare=ride_request.offered_fare,
        estimated_distance_km=round(distance_km, 2),
        payment_status="pending"
    )
    
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    logger.info(f"🚕 New ride requested: {new_ride.id} by {current_user.phone_number} ({ride_request.ride_type})")
    
    # Find and match nearby drivers
    from app.services.matching_service import matching_service
    matched_drivers = matching_service.match_ride_to_drivers(
        db=db,
        ride=new_ride,
        max_drivers=5
    )
    
    if matched_drivers:
        logger.info(f"🎯 Matched {len(matched_drivers)} drivers for ride {new_ride.id}")
        # TODO: Send push notifications to matched drivers
        # This will be implemented when we add Firebase Cloud Messaging
    else:
        logger.warning(f"⚠️ No drivers available for ride {new_ride.id}")
    
    return new_ride.to_dict()
    
    return new_ride.to_dict()


@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ride details
    
    **Access:**
    - Passenger who requested the ride
    - Driver assigned to the ride
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if user has access to this ride
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    driver_id = driver.id if driver else None
    
    if ride.passenger_id != current_user.id and ride.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this ride"
        )
    
    return ride.to_dict()


@router.patch("/{ride_id}/accept")
async def accept_ride(
    ride_id: str,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Driver accepts a ride request
    
    **Requirements:**
    - User must be a verified driver
    - Driver must be online and available
    - Ride must be in 'requested' status
    """
    # Get driver
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    
    if not driver or not driver.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver not verified"
        )
    
    if not driver.is_online or not driver.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver must be online and available"
        )
    
    # Get ride
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.status != "requested":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ride cannot be accepted (current status: {ride.status})"
        )
    
    # Accept ride
    ride.driver_id = driver.id
    ride.status = "accepted"
    ride.accepted_at = datetime.utcnow()
    
    # Mark driver as unavailable
    driver.is_available = False
    
    db.commit()
    db.refresh(ride)
    
    logger.info(f"✅ Ride accepted: {ride.id} by driver {driver.id}")
    
    # Broadcast ride update via WebSocket
    await broadcast_ride_update(
        ride_id=str(ride.id),
        event_type=EventType.RIDE_ACCEPTED,
        ride_data={
            "id": str(ride.id),
            "status": ride.status,
            "driver": {
                "full_name": driver.user.full_name if driver.user else "Driver",
                "phone_number": driver.user.phone_number if driver.user else None,
                "vehicle_type": driver.vehicle_type,
            }
        }
    )
    
    return ride.to_dict()


@router.patch("/{ride_id}/start")
async def start_ride(
    ride_id: str,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Driver starts the ride (passenger picked up)
    
    **Requirements:**
    - Driver must be assigned to this ride
    - Ride must be in 'accepted' status
    """
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.driver_id != driver.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this ride"
        )
    
    if ride.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ride cannot be started (current status: {ride.status})"
        )
    
    ride.status = "started"
    ride.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ride)
    
    logger.info(f"🏁 Ride started: {ride.id}")
    
    return ride.to_dict()


@router.patch("/{ride_id}/complete")
async def complete_ride(
    ride_id: str,
    final_fare: Optional[float] = Query(None, description="Final fare amount (XAF)"),
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Driver completes the ride (passenger dropped off)
    
    **Requirements:**
    - Driver must be assigned to this ride
    - Ride must be in 'started' status
    """
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.driver_id != driver.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this ride"
        )
    
    if ride.status != "started":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ride cannot be completed (current status: {ride.status})"
        )
    
    ride.status = "completed"
    ride.completed_at = datetime.utcnow()
    ride.final_fare = final_fare or ride.estimated_fare
    
    # Update driver stats
    driver.is_available = True
    driver.total_rides += 1
    driver.completed_rides += 1
    
    db.commit()
    db.refresh(ride)
    
    logger.info(f"🎉 Ride completed: {ride.id}")
    
    return ride.to_dict()


@router.patch("/{ride_id}/cancel")
async def cancel_ride(
    ride_id: str,
    action: RideAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a ride
    
    **Can be cancelled by:**
    - Passenger (before driver arrives)
    - Driver (before starting ride)
    
    **Cancellation fees may apply**
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if user can cancel
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    driver_id = driver.id if driver else None
    
    can_cancel = (
        ride.passenger_id == current_user.id or
        ride.driver_id == driver_id
    )
    
    if not can_cancel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot cancel this ride"
        )
    
    if ride.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ride cannot be cancelled (current status: {ride.status})"
        )
    
    ride.status = "cancelled"
    ride.cancelled_at = datetime.utcnow()
    ride.cancelled_by = "passenger" if ride.passenger_id == current_user.id else "driver"
    ride.cancellation_reason = action.reason
    
    # Free up driver if assigned
    if ride.driver_id and driver:
        driver.is_available = True
        driver.cancelled_rides += 1
    
    db.commit()
    db.refresh(ride)
    
    logger.info(f"❌ Ride cancelled: {ride.id} by {ride.cancelled_by}")
    
    return ride.to_dict()


@router.get("/", response_model=List[RideResponse])
async def get_my_rides(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's rides
    
    **Returns:**
    - All rides as passenger
    - All rides as driver (if user is a driver)
    
    **Filter by status:**
    - requested, accepted, started, completed, cancelled
    """
    # Get driver if user is a driver
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    driver_id = driver.id if driver else None
    
    # Build query
    query = db.query(Ride).filter(
        or_(
            Ride.passenger_id == current_user.id,
            Ride.driver_id == driver_id
        )
    )
    
    if status:
        query = query.filter(Ride.status == status)
    
    rides = query.order_by(Ride.requested_at.desc()).limit(limit).all()
    
    return [ride.to_dict() for ride in rides]
