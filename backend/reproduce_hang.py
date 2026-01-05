
import logging
from app.services.redis_service import redis_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_redis_connection():
    print("\n--- Testing Redis Connection ---")
    try:
        ping = redis_service.ping()
        print(f"Ping result: {ping}")
        if ping:
            print("✅ Redis connection successful!")
        else:
            print("❌ Redis connection failed.")
    except Exception as e:
        print(f"❌ Exception during ping: {e}")

def test_geospatial_query():
    print("\n--- Testing Geospatial Query ---")
    try:
        # 1. Add a dummy driver
        driver_id = "test_driver_123"
        lat, lon = 3.8480, 11.5021  # Yaounde, Cameroon
        
        print(f"Adding driver {driver_id} at {lat}, {lon}...")
        redis_service.update_driver_location(driver_id, lat, lon)
        
        # 2. Query nearby drivers
        print(f"Querying nearby drivers around {lat}, {lon}...")
        drivers = redis_service.find_nearby_drivers(lat, lon, radius_km=5.0)
        
        print(f"Found {len(drivers)} drivers.")
        for d in drivers:
            print(f" - Driver: {d['driver_id']}, Dist: {d['distance_km']}km")
            
        if any(d['driver_id'] == driver_id for d in drivers):
            print("✅ Geospatial query successful!")
        else:
            print("❌ Driver not found in query results.")
            
        # Cleanup
        redis_service.remove_driver_location(driver_id)
        
    except Exception as e:
        print(f"❌ Exception during geospatial query: {e}")

if __name__ == "__main__":
    test_redis_connection()
    test_geospatial_query()
