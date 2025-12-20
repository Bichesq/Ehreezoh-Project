"""
Ehreezoh - Matching Service
Driver-passenger matching algorithm using geospatial queries
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
from datetime import datetime

from app.models.driver import Driver
from app.models.user import User
from app.models.ride import Ride
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class MatchingService:
    """Service for matching passengers with nearby drivers"""
    
    def __init__(self):
        self.redis = redis_service
    
    def find_available_drivers(
        self,
        db: Session,
        pickup_latitude: float,
        pickup_longitude: float,
        ride_type: str,
        radius_km: float = 10.0,
        max_drivers: int = 5
    ) -> List[Dict]:
        """
        Find available drivers near pickup location
        
        Args:
            db: Database session
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            ride_type: Type of ride (moto/car)
            radius_km: Search radius in kilometers
            max_drivers: Maximum number of drivers to return
        
        Returns:
            List of driver dicts with distance and details
        """
        try:
            # Step 1: Get nearby drivers from Redis geospatial index
            logger.info(f"🔎 Redis: Finding nearby drivers for {pickup_latitude}, {pickup_longitude}")
            nearby_driver_ids = self.redis.find_nearby_drivers(
                latitude=pickup_latitude,
                longitude=pickup_longitude,
                radius_km=radius_km,
                limit=max_drivers * 2  # Get more than needed for filtering
            )
            logger.info(f"🔎 Redis: Found {len(nearby_driver_ids)} nearby driver candidates")
            
            if not nearby_driver_ids:
                logger.warning(f"No drivers found within {radius_km}km")
                return []
            
            driver_ids = [d["driver_id"] for d in nearby_driver_ids]
            
            # Step 2: Query database for driver details and filter
            logger.info(f"🔎 DB: Querying details for {len(driver_ids)} drivers")
            drivers = db.query(Driver, User).join(
                User, Driver.user_id == User.id
            ).filter(
                and_(
                    Driver.id.in_(driver_ids),
                    Driver.is_online == True,
                    Driver.is_available == True,
                    Driver.is_verified == True,
                    Driver.vehicle_type == ride_type
                )
            ).all()
            logger.info(f"🔎 DB: Found {len(drivers)} eligible drivers")
            
            # Step 3: Combine Redis distance data with database details
            available_drivers = []
            distance_map = {d["driver_id"]: d["distance_km"] for d in nearby_driver_ids}
            
            for driver, user in drivers:
                # Check if driver has an active ride
                # logger.info(f"🔎 Redis: Checking active ride for driver {driver.id}")
                current_ride = self.redis.get_driver_current_ride(driver.id)
                if current_ride:
                    continue  # Skip drivers on active rides
                
                available_drivers.append({
                    "driver_id": driver.id,
                    "user_id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "vehicle_type": driver.vehicle_type,
                    "vehicle_make": driver.vehicle_make,
                    "vehicle_model": driver.vehicle_model,
                    "vehicle_color": driver.vehicle_color,
                    "vehicle_plate_number": driver.vehicle_plate_number,
                    "average_rating": float(driver.average_rating) if driver.average_rating else 0.0,
                    "total_rides": driver.total_rides,
                    "distance_km": distance_map.get(driver.id, 0.0),
                    "current_latitude": float(driver.current_latitude) if driver.current_latitude else None,
                    "current_longitude": float(driver.current_longitude) if driver.current_longitude else None
                })
            
            # Step 4: Sort by distance and rating
            available_drivers.sort(
                key=lambda d: (d["distance_km"], -d["average_rating"])
            )
            
            # Step 5: Return top N drivers
            matched_drivers = available_drivers[:max_drivers]
            
            logger.info(f"✅ Matched {len(matched_drivers)} drivers for ride (type: {ride_type})")
            return matched_drivers
            
        except Exception as e:
            logger.error(f"Error finding available drivers: {e}", exc_info=True)
            return []
    
    def match_ride_to_drivers(
        self,
        db: Session,
        ride: Ride,
        max_drivers: int = 5
    ) -> List[Dict]:
        """
        Match a ride request to nearby available drivers
        
        Args:
            db: Database session
            ride: Ride object
            max_drivers: Maximum number of drivers to notify
        
        Returns:
            List of matched driver dicts
        """
        try:
            # Find available drivers
            matched_drivers = self.find_available_drivers(
                db=db,
                pickup_latitude=float(ride.pickup_latitude),
                pickup_longitude=float(ride.pickup_longitude),
                ride_type=ride.ride_type,
                radius_km=10.0,  # 10km search radius
                max_drivers=max_drivers
            )
            
            if not matched_drivers:
                logger.warning(f"No drivers available for ride {ride.id}")
                return []
            
            # Add ride request to Redis queue
            self.redis.add_ride_request(
                ride_id=ride.id,
                passenger_id=ride.passenger_id,
                pickup_lat=float(ride.pickup_latitude),
                pickup_lng=float(ride.pickup_longitude),
                ride_type=ride.ride_type,
                offered_fare=float(ride.offered_fare) if ride.offered_fare else None,
                ttl_seconds=300  # 5 minutes
            )
            
            # Cache ride details
            self.redis.cache_ride_details(
                ride_id=ride.id,
                ride_data=ride.to_dict(),
                ttl_seconds=7200  # 2 hours
            )
            
            # Set passenger's current ride
            self.redis.set_passenger_current_ride(
                passenger_id=ride.passenger_id,
                ride_id=ride.id,
                ttl_seconds=7200
            )
            
            logger.info(f"🎯 Matched ride {ride.id} to {len(matched_drivers)} drivers")
            return matched_drivers
            
        except Exception as e:
            logger.error(f"Error matching ride to drivers: {e}", exc_info=True)
            return []
    
    def accept_ride(
        self,
        db: Session,
        ride_id: str,
        driver_id: str
    ) -> bool:
        """
        Process driver accepting a ride
        
        Args:
            db: Database session
            ride_id: Ride ID
            driver_id: Driver ID
        
        Returns:
            True if successful
        """
        try:
            # Set driver's current ride
            self.redis.set_driver_current_ride(
                driver_id=driver_id,
                ride_id=ride_id,
                ttl_seconds=7200
            )
            
            # Remove ride from pending queue
            self.redis.remove_ride_request(ride_id)
            
            # Update ride cache
            ride = db.query(Ride).filter(Ride.id == ride_id).first()
            if ride:
                self.redis.cache_ride_details(
                    ride_id=ride_id,
                    ride_data=ride.to_dict(),
                    ttl_seconds=7200
                )
            
            logger.info(f"✅ Driver {driver_id} accepted ride {ride_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting ride: {e}", exc_info=True)
            return False
    
    def complete_ride(
        self,
        ride_id: str,
        driver_id: str,
        passenger_id: str
    ) -> bool:
        """
        Process ride completion
        
        Args:
            ride_id: Ride ID
            driver_id: Driver ID
            passenger_id: Passenger ID
        
        Returns:
            True if successful
        """
        try:
            # Clear driver's current ride
            self.redis.clear_driver_current_ride(driver_id)
            
            # Clear passenger's current ride
            self.redis.clear_passenger_current_ride(passenger_id)
            
            # Remove ride from cache (will be in database)
            self.redis.redis_client.delete(f"ride:{ride_id}:details")
            
            logger.info(f"✅ Ride {ride_id} completed")
            return True
            
        except Exception as e:
            logger.error(f"Error completing ride: {e}", exc_info=True)
            return False
    
    def cancel_ride(
        self,
        ride_id: str,
        driver_id: Optional[str] = None,
        passenger_id: Optional[str] = None
    ) -> bool:
        """
        Process ride cancellation
        
        Args:
            ride_id: Ride ID
            driver_id: Driver ID (if assigned)
            passenger_id: Passenger ID
        
        Returns:
            True if successful
        """
        try:
            # Clear driver's current ride if assigned
            if driver_id:
                self.redis.clear_driver_current_ride(driver_id)
            
            # Clear passenger's current ride
            if passenger_id:
                self.redis.clear_passenger_current_ride(passenger_id)
            
            # Remove from pending queue
            self.redis.remove_ride_request(ride_id)
            
            # Remove ride from cache
            self.redis.redis_client.delete(f"ride:{ride_id}:details")
            
            logger.info(f"❌ Ride {ride_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling ride: {e}", exc_info=True)
            return False
    
    def calculate_eta(
        self,
        driver_latitude: float,
        driver_longitude: float,
        pickup_latitude: float,
        pickup_longitude: float,
        average_speed_kmh: float = 30.0
    ) -> int:
        """
        Calculate estimated time of arrival (ETA) in minutes
        
        Args:
            driver_latitude: Driver's current latitude
            driver_longitude: Driver's current longitude
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            average_speed_kmh: Average speed in km/h (default 30 km/h)
        
        Returns:
            ETA in minutes
        """
        import math
        
        # Haversine formula for distance
        R = 6371  # Earth radius in km
        dlat = math.radians(pickup_latitude - driver_latitude)
        dlon = math.radians(pickup_longitude - driver_longitude)
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(driver_latitude)) * 
             math.cos(math.radians(pickup_latitude)) * 
             math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance_km = R * c
        
        # Calculate ETA
        eta_hours = distance_km / average_speed_kmh
        eta_minutes = int(eta_hours * 60)
        
        return max(1, eta_minutes)  # Minimum 1 minute


# Global matching service instance
matching_service = MatchingService()
