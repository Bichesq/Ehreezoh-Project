import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.redis_service import redis_service

print("Testing Redis...")
try:
    print(f"Ping: {redis_service.ping()}")
    
    uid = "test-driver-1"
    lat, lng = 4.05, 9.70
    
    print(f"Updating location for {uid}...")
    success = redis_service.update_driver_location(uid, lat, lng)
    print(f"Update success: {success}")
    
    print("Finding nearby...")
    nearby = redis_service.find_nearby_drivers(lat, lng)
    print(f"Nearby: {nearby}")
    
    found = any(d['driver_id'] == uid for d in nearby)
    print(f"Found test driver: {found}")

except Exception as e:
    print(f"Error: {e}")
