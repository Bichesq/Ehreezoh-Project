"""
Ehreezoh - Matching Service
Advanced driver-passenger matching algorithm
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from geoalchemy2.elements import WKTElement
from typing import List, Optional, Dict
import logging

from app.models.driver import Driver
from app.models.user import User

logger = logging.getLogger(__name__)


class MatchingService:
    """
    Advanced driver matching algorithm
    
    Factors considered:
    - Distance (closest drivers first)
    - Driver rating (higher rated drivers prioritized)
    - Acceptance rate (drivers who accept more rides)
    - Vehicle type match
    - Driver preferences
    """
    
    # Scoring weights
    WEIGHT_DISTANCE = 0.5
    WEIGHT_RATING = 0.3
    WEIGHT_ACCEPTANCE_RATE = 0.2
    
    @classmethod
    def find_best_drivers(
        cls,
        db: Session,
        pickup_latitude: float,
        pickup_longitude: float,
        vehicle_type: str,
        radius_km: float = 10.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find best matching drivers using advanced algorithm
        
        Args:
            db: Database session
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            vehicle_type: Required vehicle type (moto/car)
            radius_km: Search radius in kilometers
            limit: Maximum number of drivers to return
        
        Returns:
            List of drivers sorted by match score (best first)
        """
        # Create pickup point
        pickup_point = WKTElement(
            f'POINT({pickup_longitude} {pickup_latitude})',
            srid=4326
        )
        
        # Query nearby available drivers
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
                Driver.vehicle_type == vehicle_type,
                Driver.current_location.isnot(None),
                func.ST_DWithin(
                    Driver.current_location,
                    pickup_point,
                    radius_km * 1000  # Convert to meters
                )
            )
        )
        
        results = query.all()
        
        if not results:
            logger.info(f"🔍 No drivers found within {radius_km}km")
            return []
        
        # Calculate match scores
        scored_drivers = []
        for driver, user, distance_meters in results:
            score = cls._calculate_match_score(
                driver=driver,
                distance_meters=distance_meters,
                max_distance_meters=radius_km * 1000
            )
            
            scored_drivers.append({
                "driver": driver,
                "user": user,
                "distance_km": round(distance_meters / 1000, 2),
                "distance_meters": distance_meters,
                "match_score": score,
                "driver_data": {
                    "driver_id": driver.id,
                    "user_id": user.id,
                    "full_name": user.full_name,
                    "vehicle_type": driver.vehicle_type,
                    "vehicle_plate_number": driver.vehicle_plate_number,
                    "vehicle_color": driver.vehicle_color,
                    "average_rating": float(driver.average_rating) if driver.average_rating else 0.0,
                    "total_rides": driver.total_rides,
                    "completed_rides": driver.completed_rides,
                    "acceptance_rate": cls._calculate_acceptance_rate(driver)
                }
            })
        
        # Sort by match score (highest first)
        scored_drivers.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Return top matches
        top_matches = scored_drivers[:limit]
        
        logger.info(
            f"🎯 Found {len(top_matches)} matching drivers "
            f"(best score: {top_matches[0]['match_score']:.2f})"
        )
        
        return top_matches
    
    @classmethod
    def _calculate_match_score(
        cls,
        driver: Driver,
        distance_meters: float,
        max_distance_meters: float
    ) -> float:
        """
        Calculate match score for a driver
        
        Score components:
        - Distance score (0-1): Closer is better
        - Rating score (0-1): Higher rating is better
        - Acceptance rate score (0-1): Higher acceptance is better
        
        Returns:
            Match score (0-1, higher is better)
        """
        # Distance score (inverse - closer is better)
        # Normalize to 0-1 range
        distance_score = 1.0 - (distance_meters / max_distance_meters)
        distance_score = max(0.0, min(1.0, distance_score))
        
        # Rating score (0-5 normalized to 0-1)
        rating = float(driver.average_rating) if driver.average_rating else 0.0
        rating_score = rating / 5.0
        
        # Acceptance rate score
        acceptance_rate = cls._calculate_acceptance_rate(driver)
        acceptance_score = acceptance_rate
        
        # Weighted total score
        total_score = (
            (distance_score * cls.WEIGHT_DISTANCE) +
            (rating_score * cls.WEIGHT_RATING) +
            (acceptance_score * cls.WEIGHT_ACCEPTANCE_RATE)
        )
        
        return round(total_score, 3)
    
    @classmethod
    def _calculate_acceptance_rate(cls, driver: Driver) -> float:
        """
        Calculate driver's acceptance rate
        
        Acceptance rate = completed_rides / total_rides
        """
        if driver.total_rides == 0:
            return 0.5  # Neutral score for new drivers
        
        acceptance_rate = driver.completed_rides / driver.total_rides
        return round(acceptance_rate, 2)
    
    @classmethod
    def should_notify_driver(
        cls,
        driver: Driver,
        distance_km: float,
        max_pickup_distance_km: Optional[int] = None
    ) -> bool:
        """
        Determine if driver should be notified about ride request
        
        Considers:
        - Driver's max pickup distance preference
        - Distance to pickup location
        """
        # Use driver's preference or default
        max_distance = max_pickup_distance_km or driver.max_pickup_distance_km or 10
        
        # Check if within acceptable range
        return distance_km <= max_distance
