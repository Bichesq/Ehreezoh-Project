"""
Ehreezoh - Redis Service
Driver location caching, ride request queue, and geospatial queries
"""

import redis
from typing import List, Dict, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)
from app.core.debug import debug_log


class RedisService:
    """Redis service for caching and geospatial operations"""
    
    def __init__(self):
        """Initialize Redis connection"""
        # Determine if using SSL (rediss://)
        use_ssl = settings.REDIS_URL.startswith("rediss://")
        
        ssl_kwargs = {}
        if use_ssl:
            ssl_kwargs = {"ssl_cert_reqs": None}
            
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            **ssl_kwargs
        )
        logger.info("✅ Redis service initialized")
    
    def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    # ===== DRIVER LOCATION CACHING =====
    
    def update_driver_location(
        self,
        driver_id: str,
        latitude: float,
        longitude: float,
        ttl_seconds: int = 300
    ) -> bool:
        """
        Update driver's current location in Redis geospatial index
        
        Args:
            driver_id: Driver's unique ID
            latitude: Driver's latitude
            longitude: Driver's longitude
            ttl_seconds: Time to live (default 30 seconds)
        
        Returns:
            True if successful
        """
        try:
            # Add to geospatial index
            self.redis_client.geoadd(
                "drivers:online:locations",
                (longitude, latitude, driver_id)
            )
            
            # Set expiry on the main key
            self.redis_client.expire("drivers:online:locations", ttl_seconds)
            
            # Store detailed location data
            location_data = {
                "latitude": latitude,
                "longitude": longitude,
                "updated_at": datetime.utcnow().isoformat()
            }
            self.redis_client.setex(
                f"driver:{driver_id}:location",
                ttl_seconds,
                json.dumps(location_data)
            )
            
            debug_log(f"📍 Updated location for driver {driver_id}: ({latitude}, {longitude}) in Redis")
            return True
        except Exception as e:
            debug_log(f"❌ Failed to update driver location: {e}")
            logger.error(f"Failed to update driver location: {e}")
            return False
    
    def get_driver_location(self, driver_id: str) -> Optional[Dict]:
        """
        Get driver's current location
        
        Returns:
            Dict with latitude, longitude, updated_at or None
        """
        try:
            location_json = self.redis_client.get(f"driver:{driver_id}:location")
            if location_json:
                return json.loads(location_json)
            return None
        except Exception as e:
            logger.error(f"Failed to get driver location: {e}")
            return None
    
    def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find nearby drivers using Redis geospatial search
        
        Args:
            latitude: Search center latitude
            longitude: Search center longitude
            radius_km: Search radius in kilometers
            limit: Maximum number of drivers to return
        
        Returns:
            List of dicts with driver_id and distance_km
        """
        try:
            # Use GEORADIUS to find nearby drivers
            results = self.redis_client.georadius(
                "drivers:online:locations",
                longitude,
                latitude,
                radius_km,
                unit="km",
                withdist=True,
                sort="ASC",
                count=limit
            )
            
            nearby_drivers = []
            for driver_id, distance_km in results:
                nearby_drivers.append({
                    "driver_id": driver_id,
                    "distance_km": round(float(distance_km), 2)
                })
            
            
            logger.info(f"🔍 Found {len(nearby_drivers)} drivers within {radius_km}km")
            debug_log(f"🔍 Redis: Found {len(nearby_drivers)} drivers near ({latitude}, {longitude}): {nearby_drivers}")
            return nearby_drivers
        except Exception as e:
            logger.error(f"Failed to find nearby drivers: {e}")
            return []
    
    def remove_driver_location(self, driver_id: str) -> bool:
        """
        Remove driver from online locations (when going offline)
        
        Args:
            driver_id: Driver's unique ID
        
        Returns:
            True if successful
        """
        try:
            # Remove from geospatial index
            self.redis_client.zrem("drivers:online:locations", driver_id)
            
            # Delete location data
            self.redis_client.delete(f"driver:{driver_id}:location")
            
            logger.info(f"🚫 Removed driver {driver_id} from online locations")
            return True
        except Exception as e:
            logger.error(f"Failed to remove driver location: {e}")
            return False
    
    # ===== DRIVER STATUS CACHING =====
    
    def set_driver_status(
        self,
        driver_id: str,
        is_online: bool,
        is_available: bool,
        ttl_seconds: int = 300
    ) -> bool:
        """
        Cache driver's online/available status
        
        Args:
            driver_id: Driver's unique ID
            is_online: Is driver online
            is_available: Is driver available for rides
            ttl_seconds: Time to live (default 5 minutes)
        
        Returns:
            True if successful
        """
        try:
            status_data = {
                "is_online": is_online,
                "is_available": is_available,
                "updated_at": datetime.utcnow().isoformat()
            }
            self.redis_client.setex(
                f"driver:{driver_id}:status",
                ttl_seconds,
                json.dumps(status_data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set driver status: {e}")
            return False
    
    def get_driver_status(self, driver_id: str) -> Optional[Dict]:
        """Get driver's cached status"""
        try:
            status_json = self.redis_client.get(f"driver:{driver_id}:status")
            if status_json:
                return json.loads(status_json)
            return None
        except Exception as e:
            logger.error(f"Failed to get driver status: {e}")
            return None
    
    # ===== RIDE REQUEST QUEUE =====
    
    def add_ride_request(
        self,
        ride_id: str,
        passenger_id: str,
        pickup_lat: float,
        pickup_lng: float,
        ride_type: str,
        offered_fare: Optional[float] = None,
        ttl_seconds: int = 300
    ) -> bool:
        """
        Add ride request to pending queue
        
        Args:
            ride_id: Ride's unique ID
            passenger_id: Passenger's user ID
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            ride_type: Type of ride (moto/car)
            offered_fare: Passenger's offered fare
            ttl_seconds: Time to live (default 5 minutes)
        
        Returns:
            True if successful
        """
        try:
            request_data = {
                "ride_id": ride_id,
                "passenger_id": passenger_id,
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "ride_type": ride_type,
                "offered_fare": offered_fare,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Add to sorted set with timestamp as score
            timestamp = datetime.utcnow().timestamp()
            self.redis_client.zadd(
                "ride_requests:pending",
                {ride_id: timestamp}
            )
            
            # Store request details
            self.redis_client.setex(
                f"ride:{ride_id}:request",
                ttl_seconds,
                json.dumps(request_data)
            )
            
            logger.info(f"🚕 Added ride request {ride_id} to queue")
            return True
        except Exception as e:
            logger.error(f"Failed to add ride request: {e}")
            return False
    
    def get_ride_request(self, ride_id: str) -> Optional[Dict]:
        """Get ride request details"""
        try:
            request_json = self.redis_client.get(f"ride:{ride_id}:request")
            if request_json:
                return json.loads(request_json)
            return None
        except Exception as e:
            logger.error(f"Failed to get ride request: {e}")
            return None
    
    def remove_ride_request(self, ride_id: str) -> bool:
        """Remove ride request from queue (when matched or expired)"""
        try:
            self.redis_client.zrem("ride_requests:pending", ride_id)
            self.redis_client.delete(f"ride:{ride_id}:request")
            logger.info(f"✅ Removed ride request {ride_id} from queue")
            return True
        except Exception as e:
            logger.error(f"Failed to remove ride request: {e}")
            return False
    
    def get_pending_ride_requests(self, limit: int = 50) -> List[str]:
        """Get list of pending ride request IDs"""
        try:
            # Get oldest requests first
            ride_ids = self.redis_client.zrange(
                "ride_requests:pending",
                0,
                limit - 1
            )
            return list(ride_ids)
        except Exception as e:
            logger.error(f"Failed to get pending ride requests: {e}")
            return []
    
    # ===== RIDE DETAILS CACHING =====
    
    def cache_ride_details(
        self,
        ride_id: str,
        ride_data: Dict,
        ttl_seconds: int = 7200
    ) -> bool:
        """
        Cache active ride details
        
        Args:
            ride_id: Ride's unique ID
            ride_data: Ride details dict
            ttl_seconds: Time to live (default 2 hours)
        
        Returns:
            True if successful
        """
        try:
            self.redis_client.setex(
                f"ride:{ride_id}:details",
                ttl_seconds,
                json.dumps(ride_data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cache ride details: {e}")
            return False
    
    def get_ride_details(self, ride_id: str) -> Optional[Dict]:
        """Get cached ride details"""
        try:
            ride_json = self.redis_client.get(f"ride:{ride_id}:details")
            if ride_json:
                return json.loads(ride_json)
            return None
        except Exception as e:
            logger.error(f"Failed to get ride details: {e}")
            return None
    
    # ===== DRIVER'S CURRENT RIDE =====
    
    def set_driver_current_ride(
        self,
        driver_id: str,
        ride_id: str,
        ttl_seconds: int = 7200
    ) -> bool:
        """Set driver's current active ride"""
        try:
            self.redis_client.setex(
                f"driver:{driver_id}:current_ride",
                ttl_seconds,
                ride_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set driver current ride: {e}")
            return False
    
    def get_driver_current_ride(self, driver_id: str) -> Optional[str]:
        """Get driver's current ride ID"""
        try:
            return self.redis_client.get(f"driver:{driver_id}:current_ride")
        except Exception as e:
            logger.error(f"Failed to get driver current ride: {e}")
            return None
    
    def clear_driver_current_ride(self, driver_id: str) -> bool:
        """Clear driver's current ride (when ride completes)"""
        try:
            self.redis_client.delete(f"driver:{driver_id}:current_ride")
            return True
        except Exception as e:
            logger.error(f"Failed to clear driver current ride: {e}")
            return False
    
    # ===== PASSENGER'S CURRENT RIDE =====
    
    def set_passenger_current_ride(
        self,
        passenger_id: str,
        ride_id: str,
        ttl_seconds: int = 7200
    ) -> bool:
        """Set passenger's current active ride"""
        try:
            self.redis_client.setex(
                f"passenger:{passenger_id}:current_ride",
                ttl_seconds,
                ride_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set passenger current ride: {e}")
            return False
    
    def get_passenger_current_ride(self, passenger_id: str) -> Optional[str]:
        """Get passenger's current ride ID"""
        try:
            return self.redis_client.get(f"passenger:{passenger_id}:current_ride")
        except Exception as e:
            logger.error(f"Failed to get passenger current ride: {e}")
            return None
    
    def clear_passenger_current_ride(self, passenger_id: str) -> bool:
        """Clear passenger's current ride (when ride completes)"""
        try:
            self.redis_client.delete(f"passenger:{passenger_id}:current_ride")
            return True
        except Exception as e:
            logger.error(f"Failed to clear passenger current ride: {e}")
            return False


# Global Redis service instance
redis_service = RedisService()
