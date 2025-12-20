"""
Ehreezoh - Pricing Service
Dynamic fare calculation with surge pricing and time-based rates
"""

from datetime import datetime, time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PricingService:
    """
    Dynamic pricing service for ride fare calculation
    
    Features:
    - Base fare by vehicle type
    - Distance-based pricing
    - Time-based pricing (peak hours)
    - Surge pricing (high demand)
    - Minimum fare guarantee
    """
    
    # Base fares (XAF)
    BASE_FARE_MOTO = 500
    BASE_FARE_CAR = 1000
    
    # Per kilometer rates (XAF/km)
    RATE_PER_KM_MOTO = 200
    RATE_PER_KM_CAR = 400
    
    # Minimum fares
    MIN_FARE_MOTO = 500
    MIN_FARE_CAR = 1000
    
    # Peak hours multiplier (6-9 AM, 5-8 PM)
    PEAK_HOURS_MULTIPLIER = 1.3
    
    # Surge pricing levels
    SURGE_LEVELS = {
        "low": 1.0,      # Normal demand
        "medium": 1.5,   # Moderate demand
        "high": 2.0,     # High demand
        "very_high": 2.5 # Very high demand
    }
    
    @classmethod
    def calculate_fare(
        cls,
        vehicle_type: str,
        distance_km: float,
        surge_level: str = "low",
        current_time: Optional[datetime] = None
    ) -> dict:
        """
        Calculate ride fare with dynamic pricing
        
        Args:
            vehicle_type: "moto" or "car"
            distance_km: Distance in kilometers
            surge_level: Surge pricing level (low, medium, high, very_high)
            current_time: Current datetime (defaults to now)
        
        Returns:
            Dictionary with fare breakdown
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Get base fare and rate
        if vehicle_type == "moto":
            base_fare = cls.BASE_FARE_MOTO
            rate_per_km = cls.RATE_PER_KM_MOTO
            min_fare = cls.MIN_FARE_MOTO
        else:  # car
            base_fare = cls.BASE_FARE_CAR
            rate_per_km = cls.RATE_PER_KM_CAR
            min_fare = cls.MIN_FARE_CAR
        
        # Calculate base price
        distance_fare = distance_km * rate_per_km
        subtotal = base_fare + distance_fare
        
        # Apply peak hours multiplier
        is_peak_hour = cls._is_peak_hour(current_time)
        peak_multiplier = cls.PEAK_HOURS_MULTIPLIER if is_peak_hour else 1.0
        
        # Apply surge pricing
        surge_multiplier = cls.SURGE_LEVELS.get(surge_level, 1.0)
        
        # Calculate total
        total_multiplier = peak_multiplier * surge_multiplier
        total_fare = subtotal * total_multiplier
        
        # Ensure minimum fare
        final_fare = max(total_fare, min_fare)
        
        # Round to nearest 50 XAF
        final_fare = round(final_fare / 50) * 50
        
        logger.info(
            f"💰 Fare calculated: {vehicle_type} {distance_km}km = {final_fare} XAF "
            f"(surge: {surge_level}, peak: {is_peak_hour})"
        )
        
        return {
            "base_fare": base_fare,
            "distance_fare": round(distance_fare, 2),
            "distance_km": distance_km,
            "subtotal": round(subtotal, 2),
            "peak_hour_multiplier": peak_multiplier,
            "is_peak_hour": is_peak_hour,
            "surge_multiplier": surge_multiplier,
            "surge_level": surge_level,
            "total_multiplier": total_multiplier,
            "final_fare": final_fare,
            "minimum_fare": min_fare,
            "currency": "XAF"
        }
    
    @classmethod
    def _is_peak_hour(cls, dt: datetime) -> bool:
        """
        Check if given time is during peak hours
        
        Peak hours:
        - Morning: 6:00 AM - 9:00 AM
        - Evening: 5:00 PM - 8:00 PM
        """
        current_time = dt.time()
        
        # Morning peak: 6:00 - 9:00
        morning_start = time(6, 0)
        morning_end = time(9, 0)
        
        # Evening peak: 17:00 - 20:00
        evening_start = time(17, 0)
        evening_end = time(20, 0)
        
        is_morning_peak = morning_start <= current_time < morning_end
        is_evening_peak = evening_start <= current_time < evening_end
        
        return is_morning_peak or is_evening_peak
    
    @classmethod
    def determine_surge_level(
        cls,
        active_rides_count: int,
        available_drivers_count: int
    ) -> str:
        """
        Determine surge pricing level based on supply/demand
        
        Args:
            active_rides_count: Number of active ride requests
            available_drivers_count: Number of available drivers
        
        Returns:
            Surge level: low, medium, high, or very_high
        """
        if available_drivers_count == 0:
            return "very_high"
        
        # Calculate demand ratio
        demand_ratio = active_rides_count / available_drivers_count
        
        if demand_ratio >= 3.0:
            return "very_high"
        elif demand_ratio >= 2.0:
            return "high"
        elif demand_ratio >= 1.0:
            return "medium"
        else:
            return "low"
    
    @classmethod
    def estimate_fare_range(
        cls,
        vehicle_type: str,
        distance_km: float
    ) -> dict:
        """
        Estimate fare range (min to max with surge)
        
        Useful for showing passengers estimated cost before requesting
        """
        # Calculate base fare (no surge, no peak)
        base_calc = cls.calculate_fare(
            vehicle_type=vehicle_type,
            distance_km=distance_km,
            surge_level="low",
            current_time=datetime(2025, 1, 1, 12, 0)  # Non-peak time
        )
        
        # Calculate max fare (peak + high surge)
        max_calc = cls.calculate_fare(
            vehicle_type=vehicle_type,
            distance_km=distance_km,
            surge_level="very_high",
            current_time=datetime(2025, 1, 1, 18, 0)  # Peak time
        )
        
        return {
            "min_fare": base_calc["final_fare"],
            "max_fare": max_calc["final_fare"],
            "typical_fare": base_calc["final_fare"],
            "currency": "XAF",
            "distance_km": distance_km,
            "vehicle_type": vehicle_type
        }
