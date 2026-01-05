import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.driver import Driver
from app.services.redis_service import redis_service

def check_driver(phone_number):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            print(f"❌ User {phone_number} not found")
            return

        print(f"User ID: {user.id}")
        print(f"Is Driver: {user.is_driver}")
        
        driver = db.query(Driver).filter(Driver.user_id == user.id).first()
        if not driver:
            print("❌ No Driver Profile found!")
        else:
            print("✅ Driver Profile Found:")
            print(f"  - Vehicle: {driver.vehicle_type}")
            print(f"  - Online: {driver.is_online}")
            print(f"  - Available: {driver.is_available}")
            print(f"  - Verified: {driver.is_verified}")
            print(f"  - Lat/Lng: {driver.current_latitude}, {driver.current_longitude}")

        # Check Redis
        print("\nChecking Redis Geo:")
        nearby = redis_service.find_nearby_drivers(4.05, 9.70, radius_km=10.0)
        print(f"DEBUG: Nearby drivers in Redis: {nearby}")
        found_in_redis = False
        for d in nearby:
            if d['driver_id'] == str(user.id):
                found_in_redis = True
                print(f"  ✅ Found in Redis! Dist: {d['distance_km']}km")
                break
        
        if not found_in_redis:
            print("  ❌ NOT FOUND in Redis Geo Index!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_driver("+237611223344")
