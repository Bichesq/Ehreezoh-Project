
import pytest
from datetime import datetime
from app.services.pricing import PricingService
from app.services.matching import MatchingService

# Mock driver for Matching Service tests
class MockDriver:
    total_rides = 100
    completed_rides = 85
    average_rating = 4.5
    max_pickup_distance_km = 10

def test_pricing_basic():
    result = PricingService.calculate_fare(
        vehicle_type="moto",
        distance_km=5.0,
        surge_level="low"
    )
    assert result["final_fare"] > 0
    assert result["currency"] == "XAF"

def test_pricing_surge():
    normal_result = PricingService.calculate_fare(
        vehicle_type="moto",
        distance_km=5.0,
        surge_level="low"
    )
    surge_result = PricingService.calculate_fare(
        vehicle_type="moto",
        distance_km=5.0,
        surge_level="high"
    )
    assert surge_result["final_fare"] > normal_result["final_fare"]

def test_pricing_peak_hour():
    # 6 PM
    peak_time = datetime(2025, 1, 1, 18, 0)
    result = PricingService.calculate_fare(
        vehicle_type="moto",
        distance_km=5.0,
        current_time=peak_time
    )
    assert result["is_peak_hour"] is True

def test_matching_acceptance_rate():
    driver = MockDriver()
    rate = MatchingService._calculate_acceptance_rate(driver)
    assert rate == 0.85

def test_matching_score():
    driver = MockDriver()
    score = MatchingService._calculate_match_score(
        driver=driver,
        distance_meters=1000,
        max_distance_meters=5000
    )
    assert 0 <= score <= 1

def test_matching_notification_decision():
    driver = MockDriver()
    should_notify = MatchingService.should_notify_driver(
        driver=driver,
        distance_km=5.0
    )
    assert should_notify is True
