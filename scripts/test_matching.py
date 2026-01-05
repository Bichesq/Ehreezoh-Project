import sys
import os
import json
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))

from app.core.database import SessionLocal
from app.services.matching_service import matching_service
from app.models.ride import Ride

def test_matching():
    db = SessionLocal()
    try:
        print("🚕 Testing Matching Algorithm...")
        
        # 1. Test basic driver discovery
        pickup_lat = 4.0511
        pickup_lng = 9.7679
        ride_type = "moto"
        
        print(f"Finding {ride_type} drivers near {pickup_lat}, {pickup_lng}...")
        
        drivers = matching_service.find_available_drivers(
            db=db,
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lng,
            ride_type=ride_type,
            radius_km=5.0
        )
        
        if drivers:
            print(f"✅ Found {len(drivers)} drivers:")
            for d in drivers:
                print(f"   - Driver: {d['full_name']} (Plate: {d['vehicle_plate_number']})")
                print(f"     Distance: {d['distance_km']} km")
                print(f"     Rating: {d['average_rating']}")
        else:
            print("❌ No drivers found! (Check if driver is online and near location)")

        # 2. Test Ride Matching Flow (with Redis Queue)
        if drivers:
            print("\n🔄 Testing Queue Integration...")
            # Mock a ride object
            ride = Ride(
                id="test_ride_123",
                passenger_id="test_passenger_123", # Mock ID
                pickup_latitude=pickup_lat,
                pickup_longitude=pickup_lng,
                ride_type=ride_type,
                offered_fare=1500
            )
            
            matched = matching_service.match_ride_to_drivers(db, ride)
            if matched:
                print(f"✅ matched_ride_to_drivers returned {len(matched)} candidates.")
                
            # Verify Redis Queue
            import redis
            from app.core.config import settings
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            queue = r.zrange("ride_requests:pending", 0, -1)
            print(f"Redis Pending Queue: {queue}")
            
            if "test_ride_123" in queue:
                print("✅ Ride request successfully added to Redis pending queue.")
                # Cleanup
                r.zrem("ride_requests:pending", "test_ride_123")
            else:
                print("❌ Ride request NOT found in Redis queue.")
                
    except Exception as e:
        print(f"❌ Error testing matching: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_matching()
