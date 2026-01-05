"""
Ehreezoh - Rides API
Ride requests, tracking, and lifecycle management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import sqlalchemy
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from geoalchemy2.elements import WKTElement
import logging
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_driver
from app.core.websocket import broadcast_ride_update, EventType, notify_passenger, notify_driver
from app.models.user import User
from app.models.ride import Ride
from app.models.driver import Driver
from app.services.redis_service import redis_service

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


class RatingRequest(BaseModel):
    """Rating submission"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review: Optional[str] = Field(None, description="Optional review comment")


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
        
        # Notify each matched driver
        for driver_data in matched_drivers:
            # We need the User ID to notify via WebSocket (driver_data has 'user_id')
            driver_user_id = str(driver_data.get("user_id"))
            if driver_user_id:
                await notify_driver(
                    driver_user_id=driver_user_id,
                    event_type=EventType.NEW_RIDE_OFFER,
                    data={
                        "ride_id": new_ride.id,
                        "pickup_address": new_ride.pickup_address,
                        "dropoff_address": new_ride.dropoff_address,
                        "estimated_fare": float(new_ride.estimated_fare),
                        "distance_km": float(new_ride.estimated_distance_km),
                        "pickup_dist_km": float(driver_data.get("distance_km", 0))
                    }
                )
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
    
    # Update Redis with active ride so location updates are broadcasted
    redis_service.set_driver_current_ride(str(driver.user_id), str(ride.id))

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
    
    # Broadcast ride update via WebSocket
    await broadcast_ride_update(
        ride_id=str(ride.id),
        event_type=EventType.RIDE_STARTED,
        ride_data={
            "id": str(ride.id),
            "status": ride.status,
            "started_at": ride.started_at.isoformat() if ride.started_at else None
        }
    )
    
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
    
    # Broadcast ride update via WebSocket
    await broadcast_ride_update(
        ride_id=str(ride.id),
        event_type=EventType.RIDE_COMPLETED,
        ride_data={
            "id": str(ride.id),
            "status": ride.status,
            "final_fare": ride.final_fare,
            "completed_at": ride.completed_at.isoformat() if ride.completed_at else None
        }
    )
    
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
    
    # Broadcast ride update via WebSocket
    await broadcast_ride_update(
        ride_id=str(ride.id),
        event_type=EventType.RIDE_CANCELLED,
        ride_data={
            "id": str(ride.id),
            "status": ride.status,
            "cancelled_by": ride.cancelled_by,
            "cancellation_reason": ride.cancellation_reason
        }
    )
    
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


@router.post("/{ride_id}/rate")
async def rate_ride(
    ride_id: str,
    rating: RatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rate a ride (Passenger -> Driver or Driver -> Passenger)
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if ride.status != "completed":
         raise HTTPException(status_code=400, detail="Ride must be completed to rate")

    # Determine who is rating whom
    is_passenger = ride.passenger_id == current_user.id
    
    # Check if driver
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    is_driver = driver and ride.driver_id == driver.id

    if not is_passenger and not is_driver:
        raise HTTPException(status_code=403, detail="Not a participant")

    if is_passenger:
        if ride.driver_rating:
             raise HTTPException(status_code=400, detail="Already rated driver")
        ride.driver_rating = rating.rating
        ride.driver_review = rating.review
        
        # Update Driver Average Rating
        driver_to_update = db.query(Driver).filter(Driver.id == ride.driver_id).first()
        if driver_to_update:
            # Simple average update logic (better to do aggregation query in real app)
            # New Avg = ((Old Avg * Count) + New Rating) / (Count + 1)
            # We use float() for calculation
            current_avg = float(driver_to_update.average_rating or 0)
            total_ratings_count = db.query(Ride).filter(
                Ride.driver_id == driver_to_update.id, 
                Ride.driver_rating.isnot(None)
            ).count()
            
            # Since we just set the rating on this ride but didn't commit, it's counted? 
            # No, commit happens later. So count is Count_Before.
            # But simpler: Just re-calculate average from DB after commit?
            # Optimization: Let's do it after commit or trust simple math.
            pass 

    elif is_driver:
        if ride.passenger_rating:
             raise HTTPException(status_code=400, detail="Already rated passenger")
        ride.passenger_rating = rating.rating
        ride.passenger_review = rating.review

    db.commit()
    
    # Recalculate averages (robust way)
    if is_passenger:
         # Update Driver Average
         avg = db.query(Ride).filter(Ride.driver_id == ride.driver_id, Ride.driver_rating.isnot(None)).with_entities(
             func.avg(Ride.driver_rating)
         ).scalar()
         if avg:
             driver_profile = db.query(Driver).filter(Driver.id == ride.driver_id).first()
             driver_profile.average_rating = float(avg)
             db.commit()

    return {"message": "Rating submitted successfully"}


# Payment Endpoint
from app.models.payment import Payment, PaymentStatus, PaymentProvider
from app.services.payment_provider import payment_provider
from pydantic import BaseModel

class PaymentRequest(BaseModel):
    provider: str
    phone_number: str

@router.post("/{ride_id}/pay")
async def pay_ride(
    ride_id: str, 
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
        
    # Check if already paid
    existing_payment = db.query(Payment).filter(
        Payment.ride_id == ride_id, 
        Payment.status == PaymentStatus.SUCCESS
    ).first()
    
    if existing_payment:
         return {"message": "Ride already paid", "status": "success"}

    # Calculate amount (use final fare or estimated)
    amount = ride.final_fare if ride.final_fare else ride.estimated_fare
    
    if not amount:
         raise HTTPException(status_code=400, detail="Fare amount not set")

    try:
        # Validate Provider
        if request.provider.lower() not in [p.value for p in PaymentProvider]:
             # Allow fuzzy match for demo
             pass

        # 1. Create Payment Record (Pending)
        payment = Payment(
            ride_id=ride_id,
            amount=amount,
            provider=request.provider,
            phone_number=request.phone_number,
            status=PaymentStatus.PENDING
        )
        db.add(payment)
        db.commit()
        
        # 2. Call Provider
        if request.provider.lower() == 'cash':
             payment.status = PaymentStatus.SUCCESS
             payment.transaction_id = "CASH-HANDOVER"
        else:
             tx_id = await payment_provider.initiate_payment(request.phone_number, float(amount), request.provider)
             payment.transaction_id = tx_id
             payment.status = PaymentStatus.SUCCESS # In real app, this would be PENDING
        
        db.commit()
        
        return {
            "message": "Payment successful",
            "status": payment.status,
            "transaction_id": payment.transaction_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{ride_id}/debug_broadcast_completion")
async def debug_broadcast_completion(
    ride_id: str,
    db: Session = Depends(get_db)
):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
        
    await broadcast_ride_update(
        ride_id=str(ride.id),
        event_type=EventType.RIDE_COMPLETED,
        ride_data={
            "id": str(ride.id),
            "status": "completed",
            "final_fare": ride.final_fare or ride.estimated_fare,
            "completed_at": datetime.utcnow().isoformat()
        }
    )
    return {"message": "Broadcast sent"}
