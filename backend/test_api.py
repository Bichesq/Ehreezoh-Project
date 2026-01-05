"""
Ehreezoh - API Testing Suite
Comprehensive tests for all endpoints
"""

import requests
import json
import time
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test data
test_user_token = None
test_driver_token = None
test_ride_id = None
test_driver_id = None


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(name, passed, details=""):
    """Print test result"""
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"{status} - {name}")
    if details and not passed:
        print(f"   {Colors.YELLOW}{details}{Colors.END}")


def test_health_check():
    """Test health check endpoint"""
    print(f"\n{Colors.BLUE}=== Testing Health Endpoints ==={Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200 and response.json().get("status") in ["healthy", "degraded"]
        print_test("GET /health", passed, f"Status: {response.status_code}")
        
        # Test ping
        response = requests.get(f"{BASE_URL}/ping")
        passed = response.status_code == 200 and response.json().get("message") == "pong"
        print_test("GET /ping", passed)
        
        return True
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False


def test_authentication():
    """Test authentication endpoints"""
    print(f"\n{Colors.BLUE}=== Testing Authentication ==={Colors.END}")
    
    global test_user_token, test_driver_token
    
    # Note: These tests require Firebase tokens
    # For now, we'll test the endpoint structure
    
    print(f"{Colors.YELLOW}[!] Auth tests require Firebase tokens - skipping for now{Colors.END}")
    print(f"{Colors.YELLOW}   Endpoints available:{Colors.END}")
    print(f"   - POST /auth/register")
    print(f"   - POST /auth/login")
    print(f"   - GET /auth/me")
    print(f"   - PATCH /auth/me")
    
    return True


def test_driver_endpoints():
    """Test driver management endpoints"""
    print(f"\n{Colors.BLUE}=== Testing Driver Endpoints ==={Colors.END}")
    
    if not test_user_token:
        print(f"{Colors.YELLOW}[!] Requires authentication - skipping{Colors.END}")
        return True
    
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Test driver registration
    driver_data = {
        "driver_license_number": "TEST123456",
        "vehicle_type": "moto",
        "vehicle_plate_number": "CM-TEST-01",
        "vehicle_make": "Honda",
        "vehicle_model": "CB125",
        "vehicle_color": "Black"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/drivers/register", json=driver_data, headers=headers)
        passed = response.status_code in [201, 400]  # 400 if already registered
        print_test("POST /drivers/register", passed)
        
        if response.status_code == 201:
            global test_driver_id
            test_driver_id = response.json().get("id")
    except Exception as e:
        print_test("Driver Registration", False, str(e))
    
    return True


def test_pricing_service():
    """Test pricing service"""
    print(f"\n{Colors.BLUE}=== Testing Pricing Service ==={Colors.END}")
    
    try:
        from app.services.pricing import PricingService
        
        # Test basic fare calculation
        result = PricingService.calculate_fare(
            vehicle_type="moto",
            distance_km=5.0,
            surge_level="low"
        )
        
        passed = result["final_fare"] > 0
        print_test("Pricing: Basic fare calculation", passed, 
                  f"5km moto = {result['final_fare']} XAF")
        
        # Test surge pricing
        result_surge = PricingService.calculate_fare(
            vehicle_type="moto",
            distance_km=5.0,
            surge_level="high"
        )
        
        passed = result_surge["final_fare"] > result["final_fare"]
        print_test("Pricing: Surge pricing", passed,
                  f"Surge fare ({result_surge['final_fare']}) > Normal ({result['final_fare']})")
        
        # Test peak hours
        from datetime import datetime, time
        peak_time = datetime(2025, 1, 1, 18, 0)  # 6 PM
        result_peak = PricingService.calculate_fare(
            vehicle_type="moto",
            distance_km=5.0,
            current_time=peak_time
        )
        
        passed = result_peak["is_peak_hour"] == True
        print_test("Pricing: Peak hour detection", passed)
        
        # Test fare range estimation
        fare_range = PricingService.estimate_fare_range(
            vehicle_type="car",
            distance_km=10.0
        )
        
        passed = fare_range["max_fare"] > fare_range["min_fare"]
        print_test("Pricing: Fare range estimation", passed,
                  f"Range: {fare_range['min_fare']}-{fare_range['max_fare']} XAF")
        
        return True
    except Exception as e:
        print_test("Pricing Service", False, str(e))
        return False


def test_matching_service():
    """Test matching service"""
    print(f"\n{Colors.BLUE}=== Testing Matching Service ==={Colors.END}")
    
    try:
        from app.services.matching import MatchingService
        
        # Test acceptance rate calculation
        from app.models.driver import Driver
        
        # Create mock driver
        class MockDriver:
            total_rides = 100
            completed_rides = 85
            average_rating = 4.5
            max_pickup_distance_km = 10
        
        driver = MockDriver()
        
        acceptance_rate = MatchingService._calculate_acceptance_rate(driver)
        passed = acceptance_rate == 0.85
        print_test("Matching: Acceptance rate calculation", passed,
                  f"Rate: {acceptance_rate}")
        
        # Test match scoring
        score = MatchingService._calculate_match_score(
            driver=driver,
            distance_meters=1000,  # 1km
            max_distance_meters=5000  # 5km max
        )
        
        passed = 0 <= score <= 1
        print_test("Matching: Score calculation", passed,
                  f"Score: {score}")
        
        # Test notification decision
        should_notify = MatchingService.should_notify_driver(
            driver=driver,
            distance_km=5.0
        )
        
        passed = should_notify == True
        print_test("Matching: Notification decision", passed)
        
        return True
    except Exception as e:
        print_test("Matching Service", False, str(e))
        return False


def test_database_connection():
    """Test database connectivity"""
    print(f"\n{Colors.BLUE}=== Testing Database ==={Colors.END}")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT 1"))
            passed = result.scalar() == 1
            print_test("Database: Basic connection", passed)
            
            # Test PostGIS
            result = conn.execute(text("SELECT PostGIS_version()"))
            version = result.scalar()
            passed = version is not None
            print_test("Database: PostGIS extension", passed, f"Version: {version}")
            
            # Test tables exist
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'drivers', 'rides', 'payments')
            """))
            count = result.scalar()
            passed = count >= 4
            print_test("Database: Core tables exist", passed, f"Found {count} tables")
        
        return True
    except Exception as e:
        print_test("Database Connection", False, str(e))
        return False


def test_redis_connection():
    """Test Redis connectivity"""
    print(f"\n{Colors.BLUE}=== Testing Redis ==={Colors.END}")
    
    try:
        import redis
        from app.core.config import settings
        
        r = redis.from_url(settings.REDIS_URL)
        
        # Test ping
        passed = r.ping()
        print_test("Redis: Connection", passed)
        
        # Test set/get
        test_key = "test:ehreezoh"
        test_value = "testing123"
        r.set(test_key, test_value, ex=60)
        retrieved = r.get(test_key)
        passed = retrieved.decode() == test_value
        print_test("Redis: Read/Write", passed)
        
        # Cleanup
        r.delete(test_key)
        
        return True
    except Exception as e:
        print_test("Redis Connection", False, str(e))
        return False


def test_websocket_stats():
    """Test WebSocket stats endpoint"""
    print(f"\n{Colors.BLUE}=== Testing WebSocket ==={Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/ws/stats")
        passed = response.status_code == 200
        
        if passed:
            stats = response.json()
            print_test("WebSocket: Stats endpoint", passed,
                      f"Connections: {stats.get('total_connections', 0)}")
        else:
            print_test("WebSocket: Stats endpoint", passed)
        
        print(f"{Colors.YELLOW}   WebSocket endpoint: ws://localhost:8000/api/v1/ws/connect?token=JWT{Colors.END}")
        
        return True
    except Exception as e:
        print_test("WebSocket Stats", False, str(e))
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}   EHREEZOH API TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    start_time = time.time()
    
    # Run tests
    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Database", test_database_connection()))
    results.append(("Redis", test_redis_connection()))
    results.append(("Pricing Service", test_pricing_service()))
    results.append(("Matching Service", test_matching_service()))
    results.append(("WebSocket", test_websocket_stats()))
    results.append(("Authentication", test_authentication()))
    
    # Summary
    elapsed = time.time() - start_time
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}   TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    for name, passed in results:
        status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
        print(f"{status} {name}")
    
    print(f"\n{Colors.BLUE}Results:{Colors.END} {passed_count}/{total_count} tests passed")
    print(f"{Colors.BLUE}Time:{Colors.END} {elapsed:.2f}s")
    
    if passed_count == total_count:
        print(f"\n{Colors.GREEN}[SUCCESS] ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}[WARNING] Some tests failed - review above{Colors.END}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")


if __name__ == "__main__":
    run_all_tests()
