import sys
import os
import json
import redis
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.ride import Ride

def check_pending_rides():
    try:
        # 1. Check Redis Queue
        print("🔍 Checking Redis 'ride_requests:pending'...")
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        pending_ids = r.zrange("ride_requests:pending", 0, -1)
        
        if not pending_ids:
            print("❌ No pending requests found in Redis.")
        else:
            print(f"✅ Found {len(pending_ids)} pending requests: {pending_ids}")

        # 2. Check Database Details for these IDs
        if pending_ids:
            db = SessionLocal()
            print("\n📊 Ride Details from DB:")
            rides = db.query(Ride).filter(Ride.id.in_(pending_ids)).all()
            for ride in rides:
                print(f"   - ID: {ride.id}")
                print(f"     Passenger: {ride.passenger_id}")
                print(f"     Status: {ride.status}")
                print(f"     Type: {ride.ride_type}")
                print(f"     Pickup: {ride.pickup_address} ({ride.pickup_location})")
                print("------------------------------------------------")
            db.close()
            
    except Exception as e:
        print(f"❌ Error checking rides: {e}")

if __name__ == "__main__":
    check_pending_rides()
